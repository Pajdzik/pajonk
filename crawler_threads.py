#!/usr/bin/env python3

from calendar import c
from concurrent.futures import ThreadPoolExecutor
import logging
from typing import Callable
from bs4 import Tag
import threading
import os
import time

from crawler import (
    download,
    download_external_pages,
    extract_comments,
)

logger = logging.getLogger(__name__)


def process_with_threads(comments: list[Tag], output_dir: str) -> None:
    threads = []
    for i, comment in enumerate(comments):
        thread = threading.Thread(
            target=download_external_pages,
            name=f"Thread-{i:03}",
            args=(
                output_dir,
                comment,
            ),
        )

        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def process_with_threadpool(comments: list[Tag], output_dir: str) -> None:
    with ThreadPoolExecutor() as executor:
        for comment in comments:
            executor.submit(download_external_pages, output_dir, comment)


async def process_with_async_io(comments: list[Tag], output_dir: str) -> None:
    pass


def measure_time(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        # logger.critical(
        #     f"{func.__name__} Finished in {end_time - start_time:.2f} seconds"
        # )

        return end_time - start_time

    return wrapper


def crawl(
    comments: list[Tag], output_dir: str, process: Callable[[list[Tag], str], None]
) -> float:
    return measure_time(process)(comments, output_dir)


def get_comments(url: str) -> list[Tag]:
    logger.debug(f"Getting comments from {url}")

    page_content = download(url)
    comments = extract_comments(page_content)

    return comments


def create_output_dir() -> str:
    output_dir = f"output/{time.strftime('%Y-%m-%d_%H-%M-%S')}"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


if __name__ == "__main__":
    logging.basicConfig(
        format="%(relativeCreated)6d %(threadName)s %(message)s", level=logging.WARNING
    )

    # parser = argparse.ArgumentParser(description="Your script description")
    # parser.add_argument('url', type=str, help='Hacker News address')
    # args = parser.parse_args()

    url = "https://news.ycombinator.com/item?id=40077533"
    comments = get_comments(url)
    output_dir = create_output_dir()

    for _ in range(2):
        for process in (process_with_threads, process_with_threadpool):
            duration = crawl(
                comments,
                output_dir,
                process,
            )
            print(f"{process.__name__} took {duration:.2f} seconds")
