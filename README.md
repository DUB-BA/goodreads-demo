# Goodreads "Deep Dive" Scraper Demo (Playwright)

## Objective
This script is a working proof-of-concept demonstrating the technical capability to perform a complex, two-step scrape on the dynamic Goodreads website. It was built to showcase the ability to handle JavaScript-driven content for a detailed data extraction task.

## Core Technologies
- **Python**
- **Playwright:** For browser automation, including handling dynamic pop-up overlays and clicking "Show more" buttons to reveal all hidden content.
- **BeautifulSoup:** For parsing the final, fully-rendered HTML after all browser interactions are complete.

## Demonstrated Workflow
1.  Navigates to a Goodreads shelf page.
2.  Successfully detects and closes any sign-up overlays.
3.  Follows the link to the first book on the shelf.
4.  On the book page, programmatically clicks all necessary "Show more" buttons to expand the description and book details.
5.  Parses the final, fully-revealed page to extract all 10 required metadata fields.

This demo proves the core logic required for a full-scale crawl of the Goodreads site. The final version will expand this logic to loop through all books and pages, saving the data to the required CSV format.
