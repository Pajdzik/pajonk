#!/usr/bin/env python3


import time


def long_running_function_sleep(sleep_time: int):
    time.sleep(sleep_time)

def long_running_fuction_for_loop(n: int):
    i = 0
    for i in range(n):
        i += 1
