import asyncio
import logging
from typing import Optional, Tuple
from aiohttp import ClientSession
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

    try:
        url = extract_url(comment)
        if not url:
            logger.debug("No URL found")
            return
        page_content = download(url)
        save_to_file(output_dir, url, page_content)
    except Exception as e:
        logger.error(f"Failed to save {url}: {e}")
        return


def save_to_file(output_dir: str, url: str, content: str) -> None:
    logger.debug(f"Saving to file {url}")
    filename = os.path.join(output_dir, f"{url_to_filename(url)}.html")
    with open(filename, "w") as file:
        file.write(content)
    logger.debug(f"Saved external page to {filename}")


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


async def save_to_file_async(output_dir: str, url: str, content: str) -> asyncio.Future:
    logger.debug(f"Async saving to file {url}")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, save_to_file, output_dir, url, content)


async def fetch_external_pages_async(
    session: ClientSession, comment: Tag
) -> Optional[asyncio.Future[Tuple[str, str]]]:
    logger.debug(f"Downloading external page")

    url = extract_url(comment)
    if not url:
        logger.debug("No URL found")
        return None

    try:
        async with session.get(url) as response:
            try:
                content = await response.text()
                return [url, content]
            except Exception as e:
                logger.error(f"Failed to deserialize {url}: {e}")
                return None

    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return None


async def download_external_pages_async(
    session: ClientSession, output_dir: str, comment: Tag
) -> None:
    maybe_content = await fetch_external_pages_async(session, comment)
    if maybe_content is not None:
        url, content = maybe_content
        await save_to_file_async(output_dir, url, content)
        logger.debug(f"Downloaded external page to {url}")
