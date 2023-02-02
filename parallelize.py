import pandas
import functools
import multiprocessing
import numpy


N_PROCESSES = 6


def _parallelize(data, func, n_processes=N_PROCESSES):
    data_split = numpy.array_split(data, n_processes)
    pool = multiprocessing.Pool(n_processes)
    data = pandas.concat(pool.map(func, data_split))
    return data


def _on_subset(func, data_subset):
    return data_subset.apply(func, axis=1)


def on_rows(data, func, n_processes=N_PROCESSES):
    return _parallelize(data, functools.partial(_on_subset, func), n_processes)
