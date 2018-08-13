# coding=utf-8
from typing import List, Callable, Text, Any
from tqdm import tqdm

# noinspection PyCompatibility
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed


# THANKS: http://danshiebler.com/2016-09-14-parallel-progress-bar/

def para(array, fn, n_jobs=16, use_kwargs=False, front_num=3, pool_type='process', desc=''):
    # type: (List, Callable, int, bool, int, Text, Text) -> List
    """
        A para version of the map function with a progress bar.
        Args:
            array (array-like): An array to iterate over.
            fn (function): A python function to apply to the elements of array
            n_jobs (int, default=16): The number of cores to use
            use_kwargs (boolean, default=False): Whether to consider the elements of array as dictionaries of
                keyword arguments to function
            front_num (int, default=3): The number of iterations to run serially before kicking off the para job.
                Useful for catching bugs
            :param pool_type: process or thread
            :param desc: tqdm的标题栏
        Returns:
            [function(array[0]), function(array[1]), ...]
    """
    # We run the first few iterations serially to catch bugs
    if front_num > 0:
        front = [fn(**a) if use_kwargs else fn(a) for a in array[:front_num]]  # type: List[Any]
    # If we set n_jobs to 1, just run a list comprehension. This is useful for benchmarking and debugging.
    if n_jobs == 1:
        return front + [fn(**a) if use_kwargs else fn(a) for a in tqdm(array[front_num:], desc=desc)]
    # Assemble the workers
    pool = ProcessPoolExecutor if pool_type == 'process' else ThreadPoolExecutor
    with pool(max_workers=n_jobs) as pool:
        # Pass the elements of array into fn
        if use_kwargs:
            futures = [pool.submit(fn, **a) for a in array[front_num:]]
        else:
            futures = [pool.submit(fn, a) for a in array[front_num:]]
        kwargs = {
            'total': len(futures),
            'unit': 'it',
            'unit_scale': True,
            'leave': True
        }
        # Print out the progress as tasks complete
        for f in tqdm(as_completed(futures), **kwargs):
            pass
    out = []
    # Get the results from the futures.
    for i, future in tqdm(enumerate(futures)):
        try:
            out.append(future.result())
        except Exception as e:
            out.append(e)
    return front + out
