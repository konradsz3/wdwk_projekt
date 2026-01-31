import numpy as np
import galois
from alg_gao import gao
from helpers import grs_matrix as grs


class McElieceRS:
    def __init__(self, n, k, q):
        if not (k < n):
            raise ValueError("k musi być mniejsze niż n!")
        if not galois.is_prime_power(q):
            raise ValueError("q musi być potęgą liczby pierwszej!")
            
        self.n = n
        self.k = k
        self.t = (n - k) // 2
        self.q = q
        self.GF = galois.GF(q)
        
        #print(f"Parametry systemu: n={n}, k={k}, t={self.t} (GF({q}))")

    def generate_matrix_G_RS(self):
        alpha = self.GF.primitive_element
        points = alpha**np.arange(self.n)
        
        G = self.GF.Zeros((self.k, self.n))
        for i in range(self.k):
            G[i, :] = points**i
        return G

    def generate_keys(self):
        x = grs.random_distinct_elements(self.GF, self.n)
        z = grs.random_distinct_elements(self.GF, self.n, non_zero=True)
        G = grs.GRS_matrix(self.n, self.k, self.GF(x), self.GF(z), self.GF)
    
        while True:
            S = self.GF.Random((self.k, self.k))
            if np.linalg.matrix_rank(S) == self.k:
                break
        
        P = self.GF(np.eye(self.n, dtype=int))
        
        G_hat = S @ G @ P
        
        return (S, G, P), (G_hat, self.t)

    def encrypt(self, m, public_key):
            G_hat, t = public_key
            if len(m) != self.k:
                raise ValueError(f"Wiadomość musi mieć długość {self.k}!")
    
            e_index = np.random.choice(self.n, t, replace=False)
            e = self.GF.Zeros(self.n)
            for idx in e_index:
                e[idx] = self.GF.Random(low = 1)

            c = self.GF(m) @ G_hat + e
            return c

    def decrypt(self, ciphertext, private_key):
        H, A, P = private_key
        GF = self.GF
        n = self.n
        k = self.k
        z = A[0]
        x = A[1] / z
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

#Przykład z dokumentacji:
# system = McElieceRS(4, 2, 5)
# private_key, public_key = system.generate_keys()
# G_pub, t_pub = public_key
# S_pv, G_pv, P_pv = private_key
# print(f'G = {G_pv}')

# szyfrogram = system.encrypt([1, 2], public_key)
# print(f'c = {szyfrogram}')

# wiadomosc = system.decrypt(szyfrogram, private_key)
# print(f'm = {wiadomosc}')