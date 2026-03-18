# ===============================
# DOCUMENTATION
# ===============================
documentation = """
NUMERICAL METHODS LIBRARY

1. fixed_point
2. bisection
3. regula_falsi
4. newton_raphson
5. secant
6. linear
7. lu_decomposition
8. jacobi_iteration
9. gauss_seidel
10. horner
11. vander_matrix
12. interpolation
13. least_squares
14. differentiation
15. integration
"""

# ===============================
# Fixed Point Iteration
# ===============================
fixed_point = """
def fixed_point_iteration(f, x_init, epsilon=1e-6, n_iter=100):
    x = x_init
    for iter in range(n_iter):
        x_updated = f(x)
        error = abs(x_updated - x)
        x = x_updated
        if error < epsilon:
            print(f"Converged after {iter + 1} iterations")
            return x_updated
    print("Did not converge within the maximum number of iterations.")
    return None
"""

# ===============================
# Bisection Method
# ===============================
bisection = """
def bisection_method(f, a, b, epsilon=1e-6):
    if f(a) * f(b) >= 0:
        print("You have chosen the wrong interval.")
        return None
    while abs(b - a) > epsilon:
        c = (a + b) / 2
        if f(a) * f(c) <= 0:
            b = c
        else:
            a = c
    print(f"approximate value is: {(a + b) / 2 :.6f}")
    return (a + b) / 2
"""

# ===============================
# Regula Falsi Method
# ===============================
regula_falsi = """
def regula_falsi(f, a, b, epsilon=1e-6):
    if f(a) * f(b) >= 0:
        print("You have chosen the wrong interval.")
        return None
    c = b - (f(b) * (b - a)) / (f(b) - f(a))
    while abs(f(c)) > epsilon:
        if f(a) * f(c) < 0:
            b = c
        else:
            a = c
        c = b - (f(b) * (b - a)) / (f(b) - f(a))
    print(f"Approximate value is: {c:.6f}")
    return c
"""

# ===============================
# Newton-Raphson Method
# ===============================
newton_raphson = """
def newton_raphson(f, df, x0, epsilon=1e-6):
    x = x0
    x_updated = x - f(x) / df(x)
    while abs(x_updated - x) > epsilon or abs(f(x_updated)) > epsilon:
        x = x_updated
        x_updated = x - f(x) / df(x)
    print(f"Approximate value is: {x_updated:.6f}")
    return x_updated
"""

# ===============================
# Secant Method
# ===============================
secant = """
def secant_method(f, x0, x1, epsilon=1e-6):
    x_updated = x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))
    while abs(x_updated - x1) > epsilon or abs(f(x_updated)) > epsilon:
        x0 = x1
        x1 = x_updated
        x_updated = x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))
    print(f"Approximate value is: {x_updated:.6f}")
"""

# ===============================
# Row Operations & Linear System Solver
# ===============================
linear = """
def row_swap(matrix, i, j):
    matrix = np.array(matrix)
    matrix[[i, j]] = matrix[[j, i]]
    return matrix

def row_add(matrix, i, j, alpha):
    matrix = np.array(matrix)
    matrix[i] = matrix[i] + alpha * matrix[j]
    return matrix

def row_reduction(matrix):
    matrix = np.array(matrix)
    n = len(matrix)
    for i in range(n):
        if matrix[i][i] == 0:
            for k in range(i+1, n):
                if matrix[k][i] != 0:
                    matrix = row_swap(matrix, i, k)
                    break
        for j in range(i+1, n):
            alpha = -1 * matrix[j][i] / matrix[i][i]
            matrix = row_add(matrix, j, i, alpha)
    return matrix.tolist()

def back_substitution(matrix):
    n = len(matrix)
    x = [0] * n
    for i in range(n-1, -1, -1):
        sum_known = 0
        for j in range(i+1, n):
            sum_known += matrix[i][j] * x[j]
        x[i] = (matrix[i][-1] - sum_known) / matrix[i][i]
    return x

def forward_substitution(matrix):
    n = len(matrix)
    x = [0] * n
    for i in range(n):
        sum_known = 0
        for j in range(i):
            sum_known += matrix[i][j] * x[j]
        x[i] = (matrix[i][-1] - sum_known) / matrix[i][i]
    return x

def solve_linear_system(matrix, triangular=None):
    matrix = np.array(matrix, dtype=float)
    if triangular == "upper":
        return back_substitution(matrix)
    elif triangular == "lower":
        return forward_substitution(matrix)
    else:
        row_reduced = row_reduction(matrix)
        return back_substitution(row_reduced)
"""

# ===============================
# LU Decomposition
# ===============================
lu_decomposition = """
def lu_decomposition(matrix):
    A = np.array(matrix, dtype=float)
    n = len(matrix)
    P = np.eye(n)
    L = np.zeros((n, n))
    U = A.copy()

    for i in range(n):
        max_row = np.argmax(abs(U[i:, i])) + i

        if max_row != i:
            U[[max_row, i]] = U[[i, max_row]]
            P[[max_row, i]] = P[[i, max_row]]

            if i > 0:
                L[[i, max_row], :i] = L[[max_row, i], :i]

        for j in range(i+1, n):
            L[j, i] = U[j, i] / U[i, i]
            U[j] = U[j] - L[j, i] * U[i]

    for i in range(n):
        L[i, i] = 1

    return P, L, U

def solve_with_lu(A, B):
    P, L, U = lu_decomposition(A)
    B_perm = np.dot(P, B)
    y = forward_substitution(np.hstack([L, B_perm.reshape(-1,1)]))
    x = back_substitution(np.hstack([U, np.array(y).reshape(-1,1)]))
    return x, P, L, U
"""

# ===============================
# Jacobi Iteration
# ===============================
jacobi_iteration = """
def jacobi_iteration(A, B, alpha=1e-10, n_iter=1000):
    # A X = B
    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float)
    n = len(B)
    x_old = np.zeros(n)
    x_new = np.zeros(n)

    for iter in range(n_iter):
        for i in range(n):
            sum_others = 0
            for j in range(n):
                if j != i:
                    sum_others += A[i][j] * x_old[j]

            x_new[i] = (B[i] - sum_others) / A[i][i]

        if np.linalg.norm(x_new - x_old) < alpha:
            return x_new.tolist(), iter + 1

        x_old = x_new.copy()

    print("Did not converge")
    return x_new.tolist(), n_iter
"""

# ===============================
# Gauss-Seidel Iteration
# ===============================
gauss_seidel = """
def gauss_seidel(A, B, alpha=1e-10, n_iter=1000):
    # A X = B
    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float)
    n = len(B)
    x_old = np.zeros(n)

    for iter in range(n_iter):
        x_new = x_old.copy()
        for i in range(n):
            sum_others = 0
            for j in range(n):
                if j != i:
                    sum_others += A[i][j] * (x_new[j] if j < i else x_old[j])

            x_new[i] = (B[i] - sum_others) / A[i][i]

        if np.linalg.norm(x_new - x_old, ord=np.inf) < alpha:
            return x_new.tolist(), iter + 1

        x_old = x_new.copy()

    print("Did not converge")
    return x_new.tolist(), n_iter
"""

# ===============================
# Polynomial Evaluation (Horner's Method)
# ===============================
horner = """
def horner_poly(a, x):
    n = len(a)
    result = a[0]
    for i in range(1, n):
        result = result * x + a[i]
    return result

def horner_derivative(a, x):
    d = [a[i] * (len(a) - i - 1) for i in range(len(a) - 1)]
    result = d[0]
    for i in range(1, len(d)):
        result = result * x + d[i]
    return result

def horner_integral(a, x, C=0):
    I = [a[i] / (len(a) - i) for i in range(len(a))]
    result = I[0]
    for i in range(1, len(I)):
        result = result * x + I[i]
    return result * x + C
"""

# ===============================
# Vandermonde Matrix
# ===============================
vander_matrix = """
def vander(x):
    n = len(x)
    vander = np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            vander[i,j] = x[i] ** j
    return vander
"""

# ===============================
# Interpolation Methods
# ===============================
interpolation = """
def L_k(x, x_nodes, k):
    result = 1
    for j in range(len(x_nodes)):
        if j != k:
            result *= (x - x_nodes[j]) / (x_nodes[k] - x_nodes[j])
    return result

def lagrange_poly(x, x_nodes, y_nodes):
    total = 0
    for k in range(len(x_nodes)):
        total += y_nodes[k] * L_k(x, x_nodes, k)
    return total

def divided_diff_table(x, y):
    n = len(x)
    table = np.zeros((n, n))
    table[:, 0] = y

    for j in range(1, n):
        for i in range(j, n):
            table[i][j] = (table[i][j-1] - table[i-1][j-1]) / (x[i] - x[i-j])
    return table

def newton_poly_eval(x, x_nodes, table):
    n = len(x_nodes)
    result = table[0,0]
    term = 1.0
    for k in range(1, n):
        term *= (x - x_nodes[k-1])
        result += table[k, k] * term
    return result
"""

# ===============================
# Least Squares Approximation
# ===============================
least_squares = """
def least_squares_line(x, y):
    N = len(x)
    A = (N * np.sum(x * y) - np.sum(x) * np.sum(y)) / (N * np.sum(x**2) - (np.sum(x))**2)
    B = (np.sum(y) - A * np.sum(x)) / N
    return A, B
"""

# ===============================
# Numerical Differentiation
# ===============================
differentiation = """
def central_difference_2(f, x, h=0.1):
    return (f(x + h) - f(x - h)) / (2 * h)

def central_difference_4(f, x, h=0.1):
    return (-f(x + 2*h) + 8*f(x + h) - 8*f(x - h) + f(x - 2*h)) / (12 * h)

def central_difference_second(f, x, h=0.1, n_iter=20, alpha=1e-8):
    D_prev = 0
    D_curr = (f(x + h) - f(x - h)) / (2 * h)

    for k in range(1, n_iter):
        h_k = 10**(-k) * h
        D_next = (f(x + h_k) - f(x - h_k)) / (2 * h_k)

        if abs(D_next - D_curr) >= abs(D_curr - D_prev) or abs(D_curr - D_prev) < alpha:
            return D_curr

        D_prev, D_curr = D_curr, D_next

    return D_curr

def central_difference_extrapolation(f, x, h=0.1, n_iter=5):
    D = np.zeros((n_iter, n_iter))

    for j in range(n_iter):
        h_j = (2 ** -j) * h
        D[j, 0] = (f(x + h_j) - f(x - h_j)) / (2 * h_j)

        for k in range(1, j + 1):
            D[j, k] = D[j, k - 1] + (D[j, k - 1] - D[j - 1, k - 1]) / (4 ** k - 1)

    return D[n_iter - 1, n_iter - 1].item()

def central_difference_nodes(f, x_nodes):
    n = len(x_nodes)
    f_nodes = [f(x) for x in x_nodes]
    diff = np.zeros((n, n))

    for i in range(n):
        diff[i, 0] = f_nodes[i]

    for j in range(1, n):
        for i in range(j, n):
            diff[i, j] = (diff[i, j - 1] - diff[i - 1, j - 1]) / (x_nodes[i] - x_nodes[i - j])

    derivative = diff[1, 1]
    for k in range(2, n):
        term = diff[k, k]
        for m in range(1, k):
            term *= (x_nodes[0] - x_nodes[m])
        derivative += term

    return derivative.item()
"""

# ===============================
# Numerical Integration
# ===============================
integration = """
def composite_trapezoidal(a, b, n, f):
    h = (b - a) / n
    x = np.linspace(a, b, n + 1)
    y = np.array([f(xi) for xi in x])
    I = (h / 2) * (y[0] + 2 * np.sum(y[1:-1]) + y[-1])
    return I

def composite_simpson(a, b, m, f):
    if m % 2 != 0:
        raise ValueError("m must be even for Simpson's Rule")
    h = (b - a) / m
    x = np.linspace(a, b, m + 1)
    y = np.array([f(xi) for xi in x])
    I = (h / 3) * (y[0] + 4 * np.sum(y[1:-1:2]) + 2 * np.sum(y[2:-2:2]) + y[-1])
    return I

def gauss_legendre_quadrature(a, b, N, f, data):
    wk, xk = zip(*data[N])
    wk = np.array(wk)
    xk = np.array(xk)

    t = 0.5 * (a + b) + 0.5 * (b - a) * xk
    ft = np.array([f(ti) for ti in t])

    I = 0.5 * (b - a) * np.sum(wk * ft)
    return I
"""

# ===============================
# Function to print all code
# ===============================
def full():
    all_codes = [
        fixed_point,
        bisection,
        regula_falsi,
        newton_raphson,
        secant,
        linear,
        lu_decomposition,
        jacobi_iteration,
        gauss_seidel,
        horner,
        vander_matrix,
        interpolation,
        least_squares,
        differentiation,
        integration
    ]
    for code in all_codes:
        print(code)
        print("\n" + "="*50 + "\n")

def doc():
    print(documentation)
