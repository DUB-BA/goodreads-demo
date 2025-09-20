import time
import re
from urllib.parse import urljoin
import csv
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def get_text_if_exists(element, selector):
    """Safely finds an element within a BeautifulSoup object and returns its text."""
    found = element.select_one(selector)
    return found.get_text(strip=True) if found else "Not Found"


def scrape_book_page(book_url, page):
    """Performs the deep dive for a SINGLE book URL using a re-usable Page object."""
    print(f"  -- Scraping details from: {book_url}")
    try:
        page.goto(book_url, timeout=60000, wait_until="domcontentloaded")
        close_button_selector = 'button[aria-label="Close"]'
        try:
            page.locator(close_button_selector).click(timeout=7000)
        except Exception:
            pass
        try:
            page.locator('button:has-text("Book details & editions")').click(
                timeout=5000
            )
        except Exception:
            pass
        try:
            page.locator(
                'div[data-testid="description"] button:has-text("...more")'
            ).click(timeout=5000)
        except Exception:
            pass
        page.wait_for_timeout(1000)
        html_content = page.content()
        soup = BeautifulSoup(html_content, "html.parser")

        title = get_text_if_exists(soup, "h1.Text__title1")
        author = get_text_if_exists(soup, "span.ContributorLink__name")
        avg_rating_score = get_text_if_exists(soup, "div.RatingStatistics__rating")
        num_ratings_raw = get_text_if_exists(soup, "span[data-testid='ratingsCount']")
        num_reviews_raw = get_text_if_exists(soup, "span[data-testid='reviewsCount']")
        description = get_text_if_exists(
            soup, "div[data-testid='description'] span.Formatted"
        )
        original_title, first_publish_date, isbn, language = (
            "Not Found",
            "Not Found",
            "Not Found",
            "Not Found",
        )
        details_section = soup.select_one("div.BookDetails")
        if details_section:
            pub_info_tag = details_section.select_one(
                "p[data-testid='publicationInfo']"
            )
            if pub_info_tag and (
                match := re.search(r"First published (.*)", pub_info_tag.get_text())
            ):
                first_publish_date = match.group(1).strip()
            for item in details_section.find_all("div", class_="DescListItem"):
                dt, dd = item.find("dt"), item.find("dd")
                if dt and dd:
                    label = dt.get_text(strip=True).lower()
                    value = dd.get_text(strip=True)
                    if "original title" in label:
                        original_title = value
                    elif "isbn" in label:
                        isbn = value.split()[0]
                    elif "language" in label:
                        language = value
        return {
            "Book Title": title,
            "Original Title": original_title,
            "Author": author,
            "First Publish Date": first_publish_date,
            "Number of Ratings": num_ratings_raw.replace(" ratings", "").strip(),
            "Number of Reviews": num_reviews_raw.replace(" reviews", "").strip(),
            "Average Rating Score": avg_rating_score,
            "Short Description": description.strip(),
            "Language": language,
            "ISBN": isbn,
        }
    except Exception as e:
        print(f"   -!!- ERROR scraping {book_url}. Reason: {e}")
        return None


def main():
    with sync_playwright() as p:
        SHELF_URL = "https://www.goodreads.com/shelf/show/autobiography"
        OUTPUT_FILE = "goodreads_full_page.csv"
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()

        print(f"Fetching shelf page: {SHELF_URL}")
        page.goto(SHELF_URL, timeout=60000)

        print("Waiting for book list container to be present...")
        try:
            main_container_selector = "div.leftContainer"
            page.wait_for_selector(main_container_selector, timeout=20000)
            print("  - Main container found.")
        except Exception as e:
            print(
                f"!! CRITICAL FAILURE: Could not find main content container. Exiting. Error: {e}"
            )
            page.screenshot(path="error_page_load.png")
            browser.close()
            return

        try:
            page.locator('button[aria-label="Close"]').click(timeout=5000)
        except Exception:
            pass

        book_links_locators = page.locator("div.elementList a.bookTitle").all()

        if not book_links_locators:
            print(
                "!! ERROR: No book links found even though main container was present."
            )
            page.screenshot(path="error_no_links.png")
            browser.close()
            return

        book_urls_to_scrape = [
            urljoin(SHELF_URL, link.get_attribute("href"))
            for link in book_links_locators
        ]
        print(
            f"Found {len(book_urls_to_scrape)} potential book links. Beginning scrape..."
        )

        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "Book Title",
                "Original Title",
                "Author",
                "First Publish Date",
                "Number of Ratings",
                "Number of Reviews",
                "Average Rating Score",
                "Short Description",
                "Language",
                "ISBN",
            ]
            csv_writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=",")
            csv_writer.writeheader()

            for index, url in enumerate(book_urls_to_scrape):
                print(f"\nProcessing book {index + 1}/{len(book_urls_to_scrape)}...")
                book_data = scrape_book_page(url, page)
                if book_data and book_data["Book Title"] != "Not Found":
                    csv_writer.writerow(book_data)
                    print("  -> Data saved successfully.")
                else:
                    print("  -> Ghost container found or scrape failed, skipping.")

            time.sleep(1)

        browser.close()
        print(f"\nMISSION COMPLETE. Full first-page data saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
