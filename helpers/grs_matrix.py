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