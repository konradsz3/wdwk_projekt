import galois
import numpy as np

def eea(a, b, deg):
    #zwraca g, u, v takie , że u*a + v*b = r i deg(r) < max_deg jest największe możliwe (w senie kończy obliczenia gdy to jest spełnione)
    r0 = a
    r1 = b
    u0 = a.field(1)
    u1 = a.field(0)
    v0 = a.field(0)
    v1 = a.field(1)

    while r1.degree >= deg:
        q = r0 // r1

        r2 = r0 - q * r1
        r0, r1 = r1, r2

        u2 = u0 - q * u1
        u0, u1 = u1, u2

        v2 = v0 - q * v1 
        v0, v1 = v1, v2

    return r1, u1, v1

def gao(c, n, k, GF):
    alpha = GF.primitive_element
    P = GF([alpha ** i for i in range(n)])
    f = GF(c)
    g0 = galois.Poly.Roots(GF.elements[1:])
    g1 = galois.lagrange_poly(P, f)
    deg = (n+k) // 2

    g, u, v = eea(g0, g1, deg)
    print(g0)
    print(g1)
    print(g)
    try:
        msg, r = divmod(g, v)
        print(msg)

        if r !=0:
            print("Error: reszta z dzielenia jest niezerowa")
            return None
        
        if msg.degree >= k+1:
            print("Error: za wysoki stopień wielomianu wiadomości")
            return None
        
        if len(msg.coeffs) < k:
            return np.concatenate([[0] * k - len(msg.coeffs), msg.coeffs])
        else:
            return msg.coeffs[-k:]
        
    except ZeroDivisionError:
        print("Error: Dzielenie przez zero.")
        return None


GF = galois.GF(5)
ciphertext = GF([0,3,2,0])
msg = gao(ciphertext, 4, 2, GF)
print(msg)
#msg = [2,4] czyli 2x+4
#wychodzi -m(x) z przykładu bo interpolacja lagrangea jako g1(x) wyznaczyła -g1(x) z przykładu