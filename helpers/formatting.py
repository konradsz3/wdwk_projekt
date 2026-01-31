def format_matrix(M, name, field=None):
    rows, cols = M.shape
    lines = []

    header = f"{name} ({rows} × {cols})"
    if field:
        header += f" nad {field}"
    lines.append(header + ":")
    lines.append("")

    for row in M:
        line = "[ " + "  ".join(f"{int(x):2d}" for x in row) + " ]"
        lines.append(line)

    return "\n".join(lines)


def format_keys(keys, q):
    S, G, P = keys["private_key"]
    G_pub, t = keys["public_key"]

    field_str = f"GF({q})"

    k, n = G_pub.shape

    lines = []
    lines.append("=" * 30)
    lines.append("PARAMETRY KRYPTOSYSTEMU McELIECE")
    lines.append("=" * 30)
    lines.append(f"Pole: {field_str}")
    lines.append(f"n = {n}, k = {k}, t = {t}")
    lines.append("")

    # --- Klucz publiczny ---
    lines.append("=== KLUCZ PUBLICZNY ===")
    lines.append("")
    lines.append(format_matrix(G_pub, "Macierz G_pub", field_str))
    lines.append("")

    # --- Klucz prywatny ---
    if S is None or G is None or P is None:
        lines.append("[Brak klucza prywatnego]")
        return "\n".join(lines)
    lines.append("=== KLUCZ PRYWATNY ===")
    lines.append("")
    lines.append(format_matrix(S, "Macierz S", field_str))
    lines.append("")
    lines.append(format_matrix(G, "Macierz G (kod Goppa)", field_str))
    lines.append("")

    # --- Macierz permutacji ---
    lines.append("Macierz permutacji P:")
    perm = []
    for row in P:
        perm.append(next(i for i, x in enumerate(row) if int(x) == 1))
    lines.append("(" + " ".join(map(str, perm)) + ")")

    return "\n".join(lines)


