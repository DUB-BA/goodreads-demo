from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin


def get_text_if_exists(element, selector):
    """Safely finds an element within another element and returns its text."""
    found = element.select_one(selector)
    return found.get_text(strip=True) if found else "Not Found"


def main():
    with sync_playwright() as p:

        SHELF_URL = "https://www.goodreads.com/shelf/show/autobiography"

        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()

        # Find the link to the FIRST book
        print(f"Fetching shelf page: {SHELF_URL}")
        page.goto(SHELF_URL, timeout=60000)

        # Check for a potential overlay on the shelf page itself.
        close_button_selector = 'button[aria-label="Close"]'
        try:
            if page.locator(close_button_selector).is_visible(timeout=5000):
                page.locator(close_button_selector).click()
        except Exception:
            pass

        book_link_locator = page.locator("div.elementList a.bookTitle").first
        book_relative_url = book_link_locator.get_attribute("href")
        book_full_url = urljoin(SHELF_URL, book_relative_url)
        print(f"Found book link: {book_full_url}")

        # Navigate to the individual book's page

        page.goto(book_full_url, timeout=60000)

        # Neutralize the DELAYED overlay on the book page

        try:
            page.locator(close_button_selector).wait_for(timeout=10000)
            page.locator(close_button_selector).click()

        except Exception:
            print("  - No overlay appeared, proceeding.")

        # "Show More" Button Logic

        try:

            description_more_button = page.locator(
                'div[data-testid="description"] button:has-text("Show more")'
            )
            description_more_button.click(timeout=5000)

        except Exception:
            print("  - Description 'Show more' button not found or already expanded.")

        try:
            details_more_button = page.locator(
                'button:has-text("Book details & editions")'
            )
            details_more_button.click(timeout=5000)

        except Exception:
            print("  - Book details button not found or already expanded.")

        page.wait_for_timeout(2000)

        # Parse the HTML
        html_content = page.content()
        book_soup = BeautifulSoup(html_content, "html.parser")

        # Extraction logic
        title = get_text_if_exists(book_soup, "h1.Text__title1")
        author = get_text_if_exists(book_soup, "span.ContributorLink__name")
        avg_rating_score = get_text_if_exists(book_soup, "div.RatingStatistics__rating")
        num_ratings_raw = get_text_if_exists(
            book_soup, "span[data-testid='ratingsCount']"
        )
        num_reviews_raw = get_text_if_exists(
            book_soup, "span[data-testid='reviewsCount']"
        )

        description = get_text_if_exists(
            book_soup, "div[data-testid='description'] span.Formatted"
        )

        original_title = "Not Found"
        first_publish_date = "Not Found"
        isbn = "Not Found"
        language = "Not Found"

        details_section = book_soup.select_one("div.BookDetails")
        if details_section:
            pub_info_tag = details_section.select_one(
                "p[data-testid='publicationInfo']"
            )
            if pub_info_tag:
                match = re.search(r"First published (.*)", pub_info_tag.get_text())
                if match:
                    first_publish_date = match.group(1).strip()

            for item in details_section.find_all("div", class_="DescListItem"):
                dt = item.find("dt")
                dd = item.find("dd")
                if dt and dd:
                    label = dt.get_text(strip=True).lower()
                    value = dd.get_text(strip=True)
                    if "original title" in label:
                        original_title = value
                    elif "isbn" in label:
                        isbn = value.split()[0]
                    elif "language" in label:
                        language = value

        num_ratings = num_ratings_raw.replace(" ratings", "").strip()
        num_reviews = num_reviews_raw.replace(" reviews", "").strip()

        print("\n--- EXTRACTION COMPLETE ---")
        print(f"  - Book Title: {title}")
        print(f"  - Original Title: {original_title}")
        print(f"  - Author: {author}")
        print(f"  - First Publish Date: {first_publish_date}")
        print(f"  - Number of Ratings: {num_ratings}")
        print(f"  - Number of Reviews: {num_reviews}")
        print(f"  - Average Rating Score: {avg_rating_score}")

        print(f"  - Short Description: {description.strip()}")

        print(f"  - Language: {language}")
        print(f"  - ISBN: {isbn}")

        print("\nDemo script finished. Browser will close in 15 seconds...")
        time.sleep(15)
        browser.close()


if __name__ == "__main__":
    main()
