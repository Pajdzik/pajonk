#!/usr/bin/env python3


def run_with_telemetry(f, id, *args, **kwargs):
    print(f"[{f.__name__}#{id}] Start. <{threading.current_thread().name}>")
    start_time = time.time()
    result = f(*args, **kwargs)
    end_time = time.time()
    print(f"[{f.__name__}#{id}] End. Time: {end_time - start_time} seconds. <{threading.current_thread().name}>")
