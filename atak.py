import numpy as np
import galois
from alg_gao import gao
from McEliece import McElieceRS

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

# GF11 = galois.GF(11)
# B_example = GF11([[3, 1, 0, 5, 7], [7, 3, 1, 0, 4]])
# s_param = 1
    
# recovered_x, recovered_z, recovered_H = sidelnikov_shestakov_attack(B_example, s_param, GF11)
    
# print("Odzyskane punkty x:", recovered_x)
# print("Odzyskane wagi z:  ", recovered_z)
# print("Odzyskana macierz H:\n", recovered_H)

def recover_message_final(ciphertext, x, z, H, k, GF):
    """
    ciphertext: szyfrogram z błędami
    x, z, H: wyniki funkcji sidelnikov_shestakov_attack
    k: wymiar kodu
    GF: ciało galois
    """
    n = len(x)
    c = GF(ciphertext)
    
    c_norm = c / GF(z)
    m_hat_coeffs = gao(c_norm, n, k, GF, GF(x))
    
    if m_hat_coeffs is None:
        raise ValueError("Algorytm Gao nie poradził sobie z błędami. Sprawdź parametry t i n-k.")

    m_prime = GF(m_hat_coeffs[::-1])
    try:
        H_inv = np.linalg.inv(H)
        m = m_prime @ H_inv
        return m
    except np.linalg.LinAlgError:
        raise ValueError("Macierz H odzyskana w ataku jest osobliwa (nieodwracalna)!")


# --- PRZYKŁAD DZIAŁANIA ---

# # 1. Inicjalizacja systemu 
# n, k, q = 10, 4, 13 # k=4 oznacza s=3 w ataku
# system = McElieceRS(n, k, q)
# GF = system.GF
# private_key, public_key = system.generate_keys()
# G_pub, t = public_key

# # 2. Szyfrowanie wiadomości
# m_original = GF([4, 2, 2, 0])
# print(f"Oryginalna wiadomość: {m_original}")

# ciphertext = system.encrypt(m_original, public_key)
# print(f"Szyfrogram (z {t} błędami): {ciphertext}")

# # 3. ATAK Sidelnikova-Shestakova
# # B to macierz publiczna, s = k-1
# print("\n--- Rozpoczynam atak... ---")
# x_recovered, z_recovered, H_recovered = sidelnikov_shestakov_attack(G_pub, k-1, GF)
# print("Atak zakończony. Odzyskano x, z oraz H.")

# # 4. ODZYSKIWANIE WIADOMOŚCI
# print("\n--- Dekodowanie wiadomości... ---")
# m_recovered = recover_message_final(ciphertext, x_recovered, z_recovered, H_recovered, k, GF)

# print(f"Odzyskana wiadomość: {m_recovered}")

# if np.array_equal(m_original, m_recovered):
#     print("\nSUKCES! Wiadomość odzyskana bezbłędnie mimo braku klucza prywatnego.")
# else:
#     print("\nCoś poszło nie tak. Sprawdź kolejność potęg lub orientację macierzy H.")