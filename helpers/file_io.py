import json
import galois

def matrix_to_list(M):
    if M is None:
        return None
    return [[int(x) for x in row] for row in M]

def save_params_to_file(result, q, path):
    S, G, P = result["private_key"]
    G_pub, t = result["public_key"]

    k, n = G_pub.shape

    data = {
        "field": {
            "q": q
        },
        "parameters": {
            "n": n,
            "k": k,
            "t": t
        },
        "public_key": {
            "G_pub": matrix_to_list(G_pub)
        },
        "private_key": {
            "S": matrix_to_list(S),
            "G": matrix_to_list(G),
            "P": matrix_to_list(P)
        }
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_params_from_file(path, private=True):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    q = data["field"]["q"]

    # Pole skończone GF(q)
    GF = galois.GF(q)

    if private:
        S = GF(data["private_key"]["S"]) if data["private_key"]["S"] is not None else None
        G = GF(data["private_key"]["G"]) if data["private_key"]["G"] is not None else None
        P = GF(data["private_key"]["P"]) if data["private_key"]["P"] is not None else None
    else:
        S, G, P = None, None, None

    G_pub = GF(data["public_key"]["G_pub"])
    t = data["parameters"]["t"]

    return {
        "n": data["parameters"]["n"],
        "k": data["parameters"]["k"],
        "t": t,
        "q": q,
        "keys": {
            "private_key": (S, G, P),
            "public_key": (G_pub, t)
        }
    }