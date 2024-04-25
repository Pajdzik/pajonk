#!/usr/bin/env python3

import threading
import time

from slow import long_running_fuction_for_loop
from telemetry import run_with_telemetry


if __name__ == "__main__":
    start_time = time.time()

    threads = []
    for i in range(10):
        # thread = threading.Thread(target=run_with_telemetry, args=(long_running_function_sleep, i, 1))
        thread = threading.Thread(target=run_with_telemetry, args=(long_running_fuction_for_loop, i, 10**7))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    print("-" * 80)
    print(f"Total time: {end_time - start_time} seconds.")
