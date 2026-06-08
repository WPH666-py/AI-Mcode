import numpy as np


def vector_add(a, b):
    return a + b


def vector_dot(a, b):
    return np.dot(a, b)


def vector_norm(a):
    return np.linalg.norm(a)


def matrix_multiply(A, B):
    return np.dot(A, B)


def solve_linear_system(A, b):
    return np.linalg.solve(A, b)


def pearson_correlation(x, y):
    return np.corrcoef(x, y)[0, 1]


def mean_absolute_error(y_true, y_pred):
    return np.mean(np.abs(np.array(y_true) - np.array(y_pred)))


def rmse(y_true, y_pred):
    return np.sqrt(np.mean((np.array(y_true) - np.array(y_pred)) ** 2))


def moving_average(data, window):
    return np.convolve(data, np.ones(window) / window, mode='same')


def interpolate_linear(x, y, xi):
    return np.interp(xi, x, y)
