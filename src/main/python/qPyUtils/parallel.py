# coding=utf-8
import multiprocessing

# noinspection PyCompatibility
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from tqdm import tqdm
from typing import List, Callable, Text, Any

# THANKS: http://danshiebler.com/2016-09-14-parallel-progress-bar/
from qPyUtils.streaming import try_tuple


def para(array, fn, n_jobs=max(1, multiprocessing.cpu_count() - 1),
         use_kwargs=False, front_num=3, pool_type='process',
         is_suppress_progressbar=False):
    # type: (List, Callable, int, bool, int, Text, bool) -> List
    """
        A para version of the map function with a progress bar.
        Args:
            :param array: An array to iterate over.
            :param fn: A python function to apply to the elements of array
            :param n_jobs: The number of cores to use
            :param use_kwargs: Whether to consider the elements of array as dictionaries of
                keyword arguments to function
            :param front_num: The number of iterations to run serially before kicking off the para job.
                Useful for catching bugs
            :param pool_type: process or thread
            :param is_suppress_progressbar: whether suppress the tqdm progress bar
        Returns:
            [function(array[0]), function(array[1]), ...]
    """
    # We run the first few iterations serially to catch bugs
    assert front_num >= 0
    front = [fn(**a) if use_kwargs else fn(*try_tuple(a)) for a in array[:front_num]]  # type: List[Any]
    # If we set n_jobs to 1, just run a list comprehension. This is useful for benchmarking and debugging.
    if n_jobs == 1:
        return front + [fn(**a) if use_kwargs else fn(a) for a in
                        tqdm(array[front_num:], disable=is_suppress_progressbar)]
    # Assemble the workers
    pool = ProcessPoolExecutor if pool_type == 'process' else ThreadPoolExecutor
    with pool(max_workers=n_jobs) as pool:
        # Pass the elements of array into fn
        if use_kwargs:
            futures = [pool.submit(fn, **a) for a in array[front_num:]]
        else:
            futures = [pool.submit(fn, *try_tuple(a)) for a in array[front_num:]]
        kwargs = {
            'total': len(futures),
            'unit': 'it',
            'unit_scale': True,
            'leave': True,
            'disable': is_suppress_progressbar
        }
        # Print out the progress as tasks complete
        for _ in tqdm(as_completed(futures), **kwargs):
            pass
    out = []
    # Get the results from the futures.
    for i, future in tqdm(enumerate(futures), disable=is_suppress_progressbar):
        try:
            out.append(future.result())
        except Exception as e:
            out.append(e)
    return front + out
