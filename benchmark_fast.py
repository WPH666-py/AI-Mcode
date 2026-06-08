import time
import numpy as np

from apps.core import (
    is_accelerated,
    vector_dot,
    vector_norm,
    matrix_multiply,
    pearson_correlation,
    rmse,
    linear_regression,
    topsis,
)


def timer(name, fn):
    start = time.perf_counter()
    result = fn()
    elapsed = time.perf_counter() - start
    print(f"{name}: {elapsed:.6f}s")
    return result


def main():
    print("加速状态:", is_accelerated())

    n = 300_000
    a = np.random.rand(n).astype(np.float64)
    b = np.random.rand(n).astype(np.float64)

    timer("Cython/Python vector_dot", lambda: vector_dot(a, b))
    timer("NumPy dot", lambda: np.dot(a, b))
    timer("Cython/Python vector_norm", lambda: vector_norm(a))
    timer("Cython/Python pearson", lambda: pearson_correlation(a, b))
    timer("Cython/Python rmse", lambda: rmse(a, b))

    X = np.random.rand(20_000, 8).astype(np.float64)
    y = np.random.rand(20_000).astype(np.float64)
    timer("Numba linear_regression", lambda: linear_regression(X, y))

    matrix = np.random.rand(5000, 6).astype(np.float64)
    weights = np.ones(6, dtype=np.float64) / 6
    beneficial = np.array([True, True, False, True, False, True])
    timer("Numba TOPSIS", lambda: topsis(matrix, weights, beneficial))

    A = np.random.rand(300, 300).astype(np.float64)
    B = np.random.rand(300, 300).astype(np.float64)
    timer("Cython/Python matrix_multiply", lambda: matrix_multiply(A, B))


if __name__ == "__main__":
    main()
