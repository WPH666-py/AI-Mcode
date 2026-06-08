# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True
cimport cython
from libc.math cimport sqrt, pow, fabs, exp, log
from libc.string cimport memcpy, memset
from cpython.bytes cimport PyBytes_FromStringAndSize
from cpython.unicode cimport PyUnicode_DecodeUTF8
import numpy as np
cimport numpy as np

np.import_array()

ctypedef np.float64_t DTYPE_t
ctypedef np.int64_t ITYPE_t


cpdef double[:] vector_add(double[:] a, double[:] b):
    cdef Py_ssize_t n = a.shape[0]
    cdef Py_ssize_t i
    cdef double[:] result = np.empty(n, dtype=np.float64)
    for i in range(n):
        result[i] = a[i] + b[i]
    return result


cpdef double vector_dot(double[:] a, double[:] b):
    cdef Py_ssize_t n = a.shape[0]
    cdef Py_ssize_t i
    cdef double s = 0.0
    for i in range(n):
        s += a[i] * b[i]
    return s


cpdef double vector_norm(double[:] a):
    cdef Py_ssize_t n = a.shape[0]
    cdef Py_ssize_t i
    cdef double s = 0.0
    for i in range(n):
        s += a[i] * a[i]
    return sqrt(s)


cpdef double[:, :] matrix_multiply(double[:, :] A, double[:, :] B):
    cdef Py_ssize_t m = A.shape[0]
    cdef Py_ssize_t k = A.shape[1]
    cdef Py_ssize_t n = B.shape[1]
    cdef Py_ssize_t i, j, p
    cdef double s
    cdef double[:, :] C = np.zeros((m, n), dtype=np.float64)
    for i in range(m):
        for p in range(k):
            if A[i, p] == 0:
                continue
            for j in range(n):
                C[i, j] += A[i, p] * B[p, j]
    return C


cpdef double[:] solve_linear_system(double[:, :] A, double[:] b):
    cdef Py_ssize_t n = A.shape[0]
    cdef Py_ssize_t i, j, k
    cdef double factor, s
    cdef double[:, :] aug = np.empty((n, n + 1), dtype=np.float64)
    cdef double[:] x = np.empty(n, dtype=np.float64)

    for i in range(n):
        for j in range(n):
            aug[i, j] = A[i, j]
        aug[i, n] = b[i]

    for i in range(n):
        if fabs(aug[i, i]) < 1e-12:
            for k in range(i + 1, n):
                if fabs(aug[k, i]) > 1e-12:
                    for j in range(n + 1):
                        aug[i, j], aug[k, j] = aug[k, j], aug[i, j]
                    break
        for k in range(i + 1, n):
            factor = aug[k, i] / aug[i, i]
            for j in range(i, n + 1):
                aug[k, j] -= factor * aug[i, j]

    for i in range(n - 1, -1, -1):
        s = aug[i, n]
        for j in range(i + 1, n):
            s -= aug[i, j] * x[j]
        x[i] = s / aug[i, i]

    return x


cpdef double pearson_correlation(double[:] x, double[:] y):
    cdef Py_ssize_t n = x.shape[0]
    cdef Py_ssize_t i
    cdef double mx = 0.0, my = 0.0, sx = 0.0, sy = 0.0, sxy = 0.0
    cdef double dx, dy
    for i in range(n):
        mx += x[i]
        my += y[i]
    mx /= n
    my /= n
    for i in range(n):
        dx = x[i] - mx
        dy = y[i] - my
        sx += dx * dx
        sy += dy * dy
        sxy += dx * dy
    return sxy / (sqrt(sx) * sqrt(sy) + 1e-15)


cpdef double mean_absolute_error(double[:] y_true, double[:] y_pred):
    cdef Py_ssize_t n = y_true.shape[0]
    cdef Py_ssize_t i
    cdef double s = 0.0
    for i in range(n):
        s += fabs(y_true[i] - y_pred[i])
    return s / n


cpdef double rmse(double[:] y_true, double[:] y_pred):
    cdef Py_ssize_t n = y_true.shape[0]
    cdef Py_ssize_t i
    cdef double s = 0.0, d
    for i in range(n):
        d = y_true[i] - y_pred[i]
        s += d * d
    return sqrt(s / n)


cpdef double[:] moving_average(double[:] data, int window):
    cdef Py_ssize_t n = data.shape[0]
    cdef Py_ssize_t i, j
    cdef double s
    cdef double[:] result = np.empty(n, dtype=np.float64)
    cdef int half = window // 2
    for i in range(n):
        s = 0.0
        for j in range(max(0, i - half), min(n, i + half + 1)):
            s += data[j]
        result[i] = s / (min(n, i + half + 1) - max(0, i - half))
    return result


cpdef double interpolate_linear(double[:] x, double[:] y, double xi):
    cdef Py_ssize_t n = x.shape[0]
    cdef Py_ssize_t i
    if xi <= x[0]:
        return y[0]
    if xi >= x[n - 1]:
        return y[n - 1]
    for i in range(n - 1):
        if x[i] <= xi <= x[i + 1]:
            return y[i] + (y[i + 1] - y[i]) * (xi - x[i]) / (x[i + 1] - x[i])
    return y[n - 1]
