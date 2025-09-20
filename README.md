# Goodreads "Deep Dive" Scraper (Playwright & BeautifulSoup)

## Objective
This is a professional-grade Python script designed to perform a complex, multi-step scrape of the Goodreads website. It was built to extract a detailed, 10-field dataset for all books on a given shelf, handling the challenges of a modern, dynamic, JavaScript-driven web application.

## Core Technologies
- **Python:** The core language for the script.
- **Playwright:** The primary engine for browser automation. It is essential for navigating the site, handling JavaScript rendering, defeating pop-up overlays, and clicking "Show more" buttons to reveal hidden content.
- **BeautifulSoup4:** Used after all browser interactions are complete to precisely parse the final, fully-rendered HTML and extract the target data.
- **Python `csv` Module:** For writing the scraped and cleaned data into a structured `output.csv` file.

## Key Challenges Solved & Features
- **JavaScript Rendering:** Successfully handles the race condition where page content loads *after* the initial page load event. The script uses a robust `wait_for_selector` strategy to ensure the page is stable before attempting to scrape.
- **Overlay/Modal Handling:** Automatically detects and closes the disruptive sign-up pop-up that appears on the site, allowing the scrape to proceed without interruption.
- **Interactive Content:** Programmatically clicks the "Book details & editions" button to reveal hidden metadata like ISBN, Original Title, and Language.
- **Two-Step "Deep Crawl":** The script does not just scrape the surface of the shelf page. It identifies the unique URL for each book, navigates to that page, and performs a "deep dive" extraction to gather all 10 required data points before moving to the next book.
- **Robust & Reusable:** The code is refactored into a modular `scrape_book_page` function, making it clean, readable, and easy to adapt for other pages or projects.

## How to Run
1.  Ensure you have a Python environment set up.
2.  Install the required libraries:
    ```bash
    pip install playwright beautifulsoup4
    ```
3.  Install the necessary browser binaries for Playwright:
    ```bash
    playwright install
    ```
4.  Execute the script from your terminal:
    ```bash
    python your_script_name.py
    ```
5.  The output will be saved to `goodreads_full_page.csv` in the same directory.
