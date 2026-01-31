import numpy as np
import galois
from alg_gao import gao

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
        G = self.generate_matrix_G_RS()
    
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
        S, G, P = private_key
        c_hat = ciphertext @ P.T
        
        alpha = self.GF.primitive_element
        points = alpha**np.arange(self.n) 
        
        m_hat_raw = gao(c_hat, self.n, self.k, self.GF, points)
        
        if m_hat_raw is None: return None
        
        m_hat = self.GF(m_hat_raw)

        m = m_hat[::-1] @ np.linalg.inv(S)
        
        return m

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