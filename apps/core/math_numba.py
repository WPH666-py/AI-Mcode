import numpy as np

_HAS_NUMBA = False
try:
    from numba import jit, prange, float64, int64
    _HAS_NUMBA = True
except ImportError:
    def jit(*args, **kwargs):
        def dec(f):
            return f
        return dec
    prange = range
    float64 = float
    int64 = int


@jit(nopython=True, cache=True, parallel=True, fastmath=True)
def _nb_linear_regression(X, y):
    n, p = X.shape
    XtX = np.zeros((p, p), dtype=np.float64)
    Xty = np.zeros(p, dtype=np.float64)
    for i in prange(n):
        xi = X[i]
        yi = y[i]
        for j in range(p):
            Xty[j] += xi[j] * yi
            for k in range(p):
                XtX[j, k] += xi[j] * xi[k]
    try:
        beta = np.linalg.solve(XtX, Xty)
    except np.linalg.LinAlgError:
        beta = np.linalg.lstsq(XtX, Xty)[0]
    return beta


@jit(nopython=True, cache=True, fastmath=True)
def _nb_entropy(prob_array):
    n = len(prob_array)
    ent = 0.0
    for i in range(n):
        p = prob_array[i]
        if p > 0:
            ent -= p * np.log(p)
    return ent


@jit(nopython=True, cache=True, fastmath=True)
def _nb_topsis(matrix, weights, beneficial):
    n, m = matrix.shape
    normed = np.zeros((n, m), dtype=np.float64)
    for j in range(m):
        col_sum = 0.0
        for i in range(n):
            col_sum += matrix[i, j] ** 2
        col_norm = np.sqrt(col_sum)
        if col_norm > 0:
            for i in range(n):
                normed[i, j] = (matrix[i, j] / col_norm) * weights[j]

    ideal_best = np.zeros(m, dtype=np.float64)
    ideal_worst = np.zeros(m, dtype=np.float64)
    for j in range(m):
        col_vals = normed[:, j]
        if beneficial[j]:
            ideal_best[j] = np.max(col_vals)
            ideal_worst[j] = np.min(col_vals)
        else:
            ideal_best[j] = np.min(col_vals)
            ideal_worst[j] = np.max(col_vals)

    scores = np.zeros(n, dtype=np.float64)
    for i in range(n):
        d_best = 0.0
        d_worst = 0.0
        for j in range(m):
            d_best += (normed[i, j] - ideal_best[j]) ** 2
            d_worst += (normed[i, j] - ideal_worst[j]) ** 2
        scores[i] = np.sqrt(d_worst) / (np.sqrt(d_best) + np.sqrt(d_worst) + 1e-15)

    return scores


@jit(nopython=True, cache=True, fastmath=True)
def _nb_lstsq(A, b):
    return np.linalg.lstsq(A, b)[0]


def linear_regression(X, y):
    if not _HAS_NUMBA:
        return np.linalg.lstsq(X, y, rcond=None)[0]
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    return _nb_linear_regression(X.astype(np.float64), y.astype(np.float64))


def entropy(prob_array):
    prob = np.asarray(prob_array, dtype=np.float64)
    prob = prob / prob.sum()
    return _nb_entropy(prob)


def topsis(matrix, weights, beneficial):
    mat = np.asarray(matrix, dtype=np.float64)
    w = np.asarray(weights, dtype=np.float64)
    ben = np.asarray(beneficial, dtype=np.bool_)
    return _nb_topsis(mat, w, ben)


def has_numba():
    return _HAS_NUMBA
