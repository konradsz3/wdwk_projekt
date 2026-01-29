import numpy as np
import galois

def sidelnikov_shestakov_attack(B, s, field):
    """
    Implementacja ataku Sidelnikova-Shestakova
    
    Parametry:
    B: publiczna macierz generujaca (s+1) x N
    s: parametr s = k - 1 
    field: cialo skonczone GF(q)
    """
    k, N = B.shape
    x = [None] * N
    
    # 2) Normalizacja punktow ewaluacji
    x[0] = field(1) 
    x[1] = field(0)
    x[2] = "inf"

    # 3) Wyznaczenie c(1) i c(2) 
    idx_c1 = [0] + list(range(s + 1, 2 * s))
    c1 = B[:, idx_c1].T.null_space()[0]
    
    idx_c2 = [1] + list(range(s + 1, 2 * s))
    c2 = B[:, idx_c2].T.null_space()[0]

    # 4) Obliczanie bj 
    b = [field(0)] * N
    target_j_k4 = list(range(2, s + 1)) + list(range(2 * s, N))
    for j in target_j_k4:
        beta1_j = c1 @ B[:, j] 
        beta2_j = c2 @ B[:, j] 
        b[j] = beta1_j / beta2_j 

    # 5) i 6) Wyznaczenie c(3), c(4) oraz b'j
    if s > 1:
        idx_c3 = [0] + list(range(2, s + 1))
        c3 = B[:, idx_c3].T.null_space()[0]
        
        idx_c4 = [1] + list(range(2, s + 1))
        c4 = B[:, idx_c4].T.null_space()[0]
        
        for j in range(s + 1, 2 * s):
            beta3_j = c3 @ B[:, j]
            beta4_j = c4 @ B[:, j]
            beta3_N = c3 @ B[:, N-1]
            beta4_N = c4 @ B[:, N-1]
            b[j] = (b[N-1] * beta4_N / beta3_N) * (beta3_j / beta4_j)

    # 7) Obliczanie punktow ewaluacji
    b3 = b[2]
    for j in range(3, N):
        x[j] = b3 / (b3 - b[j])

    # 8) Przeksztalcanie 
    used_x = [val for val in x if val != "inf" and val is not None]
    alpha = next(a for a in field.elements if a not in used_x)
    for j in range(N):
        if x[j] == "inf":
            x[j] = field(0)
        else:
            x[j] = field(1) / (alpha - x[j]) 

    # 9) Normalizacja wag
    z = [field(0)] * N
    z[0] = field(1) 
    
    # 10) Wyznaczanie wspolczynnikow cj
    sub_B_z = B[:, 0:s+2]
    cj_weights = sub_B_z.null_space()[0]
    
    # 11) Rozwiazywanie ukladu rownan
    matrix_eq = field([[cj_weights[j] * (x[j]**i) for j in range(1, s + 2)] for i in range(s + 1)])
    rhs_eq = field([-(cj_weights[0] * z[0] * (x[0]**i)) for i in range(s + 1)])
    
    z_sol = np.linalg.solve(matrix_eq, rhs_eq) 
    for i in range(len(z_sol)):
        z[i+1] = z_sol[i]

    # 12) Wyznaczanie wspolczynnikow hij
    H = field.Zeros((k, k))
    vander_mat = field([[x[j]**p for p in range(k)] for j in range(k)])
    for i in range(k):
        vander_rhs = field([B[i, j] / z[j] for j in range(k)])
        H[i, :] = np.linalg.solve(vander_mat, vander_rhs)

    # 13) Wyznaczanie zj
    H_inv = np.linalg.inv(H)
    for j in range(s + 2, N):
        z[j] = (H_inv[0, :] @ B[:, j])

    return x, z, H 

GF11 = galois.GF(11)
B_example = GF11([[3, 1, 0, 5, 7], [7, 3, 1, 0, 4]])
s_param = 1
    
recovered_x, recovered_z, recovered_H = sidelnikov_shestakov_attack(B_example, s_param, GF11)
    
print("Odzyskane punkty x:", recovered_x)
print("Odzyskane wagi z:  ", recovered_z)
print("Odzyskana macierz H:\n", recovered_H)