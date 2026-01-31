import numpy as np

def random_distinct_elements(field, count, non_zero=False):
    q = field.order

    if non_zero:
        if count > q - 1:
            raise ValueError("Dla non_zero=True: count ≤ q−1")
        candidates = field.elements[1:]   # bez zera
    else:
        if count > q:
            raise ValueError("count ≤ q")
        candidates = field.elements

    idx = np.random.choice(len(candidates), size=count, replace=False)
    return list(candidates[idx])


def GRS_matrix(n, k, x, z, field):
    """
    Generuje macierz generującą kod GRS o parametrach (n, k) nad danym polem skończonym.

    Args:
        n (int): Długość kodu.
        k (int): Wymiar kodu.
        x (galois.GFArray): Punkty ewaluacji (długość n).
        z (galois.GFArray): Współczynniki wagowe (długość n).
        field (galois.GF): Pole skończone, nad którym definiowany jest kod.

    Returns:
        galois.GFArray: Macierz generująca kod GRS o wymiarach (k, n).
    """
    G = field.Zeros((k, n))
    for i in range(k):
        G[i, :] = z * (x ** i)
    return G