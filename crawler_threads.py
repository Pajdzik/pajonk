#!/usr/bin/env python3

import argparse
import logging
import requests
from bs4 import BeautifulSoup, Tag
import threading
import os
from typing import Optional
import time

logger = logging.getLogger(__name__)


def download(url: str) -> str:
    logger.info(f"Downloading {url}")

    response = requests.get(url)
    response.raise_for_status()

    logger.debug(f"Downloaded {len(response.text)} characters from {url}")
    return response.text


def extract_comments(page_content: str) -> list[Tag]:
    logger.info("Extracting comments")

    soup = BeautifulSoup(page_content, "html.parser")
    comments = soup.find_all("span", class_="commtext")

    logger.info(f"Found {len(comments)} comments")
    return comments


def url_to_filename(url: str) -> str:
    return url.replace("https://", "").replace("/", "-")


def download_external_pages(output_dir: str, comment: Tag) -> None:
    logger.info("Downloading external page")

    url = extract_url(comment)
    if not url:
        logger.debug("No URL found")
        return

    page_content = download(url)
    filename = os.path.join(output_dir, f"{url_to_filename(url)}.html")
    with open(filename, "w") as file:
        file.write(page_content)

    logger.info(f"Downloaded external page to {filename}")


def extract_url(comment: Tag) -> Optional[str]:
    link = comment.find("a")
    if link:
        return link.get("href")
    return None


def crawl(url: str) -> None:
    logger.info(f"Crawling {url}")

    comment_page = download(url)
    comments = extract_comments(comment_page)

    output_dir = f"output/{time.strftime('%Y-%m-%d_%H-%M-%S')}"
    os.makedirs(output_dir, exist_ok=True)

    threads = []
    for comment in comments:
        thread = threading.Thread(
            target=download_external_pages,
            args=(
                output_dir,
                comment,
            ),
        )

        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)

    # parser = argparse.ArgumentParser(description="Your script description")
    # parser.add_argument('url', type=str, help='Hacker News address')
    # args = parser.parse_args()
    url = "https://news.ycombinator.com/item?id=40099344"

    crawl(url)
