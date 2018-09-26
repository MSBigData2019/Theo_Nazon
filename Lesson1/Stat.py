import numpy as np
from scipy.linalg import toeplitz
from numpy.linalg import eigh


A = toeplitz([1, 2, 0, 2])
print(A)
[Dint, Uint] = eigh(A)
# use eigh not eig for symmetric matrices
idx = Dint.argsort()[::-1]
D = Dint[idx]
U = Uint[:, idx]

print(np.allclose(U.dot(np.diag(D)).dot(U.T), A))