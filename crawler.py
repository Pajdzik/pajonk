import logging
from typing import Optional
import requests
from bs4 import BeautifulSoup, Tag
import os
import threading

logger = logging.getLogger(__name__)


def download(url: str) -> str:
    logger.debug(f"Downloading {url}")

    response = requests.get(url)
    response.raise_for_status()

    logger.debug(f"Downloaded {len(response.text)} characters from {url}")
    return response.text


def download_external_pages(output_dir: str, comment: Tag) -> None:
    logger.debug(f"{threading.current_thread().getName()} Downloading external page")

    url = extract_url(comment)
    if not url:
        logger.debug("No URL found")
        return

    try:
        page_content = download(url)
    except requests.exceptions.HTTPError as e:
        logger.error(f"Failed to download {url}: {e}")
        return

    filename = os.path.join(output_dir, f"{url_to_filename(url)}.html")
    with open(filename, "w") as file:
        file.write(page_content)

    logger.info(f"Downloaded external page to {filename}")


def url_to_filename(url: str) -> str:
    return url.replace("https://", "").replace("/", "-")


def extract_comments(page_content: str) -> list[Tag]:
    logger.debug("Extracting comments")

    soup = BeautifulSoup(page_content, "html.parser")
    comments = soup.find_all("span", class_="commtext")

    logger.debug(f"Found {len(comments)} comments")
    return comments


def extract_url(comment: Tag) -> Optional[str]:
    link = comment.find("a")
    if link:
        return link.get("href")
    return None
