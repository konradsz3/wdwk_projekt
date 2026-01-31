import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
from McEliece import McElieceRS
from atak import sidelnikov_shestakov_attack
import helpers.formatting as fmt
from helpers.file_io import load_params_from_file, save_params_to_file
backend = None

class McElieceGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Demonstracja kryptosystemu McEliece")
        self.geometry("900x600")
        self.current_keys = None
        self.current_system = None
        self._build_layout()

    def _build_layout(self):
        # ======= RAMKA PARAMETRÓW =======
        params_frame = tk.LabelFrame(self, text="Parametry kryptosystemu")
        params_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(params_frame, text="n:").pack(side=tk.LEFT)
        self.n_entry = tk.Entry(params_frame, width=6)
        self.n_entry.pack(side=tk.LEFT)

        tk.Label(params_frame, text="k:").pack(side=tk.LEFT)
        self.k_entry = tk.Entry(params_frame, width=6)
        self.k_entry.pack(side=tk.LEFT)

        tk.Label(params_frame, text="q:").pack(side=tk.LEFT)
        self.q_entry = tk.Entry(params_frame, width=6)
        self.q_entry.pack(side=tk.LEFT)

        tk.Button(
            params_frame,
            text="Generuj parametry",
            command=self.generate_parameters
        ).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(
            params_frame,
            text="Zapisz parametry do pliku",
            command=self.save_parameters
        ).pack(side=tk.LEFT, padx=5, pady=5)


        tk.Label(params_frame, text="lub").pack(side=tk.LEFT, padx=15)

        tk.Button(
            params_frame,
            text="Wczytaj parametry z pliku",
            command=self.load_parameters
        ).pack(side=tk.LEFT, padx=15, pady=5)


        # ======= RAMKA WIADOMOŚCI =======
        message_frame = tk.LabelFrame(self, text="Szyfrowanie i deszyfrowanie wiadomości")
        message_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(message_frame, text="Wiadomość (długość k):").pack(side=tk.LEFT, padx=2)
        self.message_entry = tk.Entry(message_frame, width=40)
        self.message_entry.pack(side=tk.LEFT, padx=2)

        tk.Button(message_frame, text="Zaszyfruj", command=self.encrypt_message).pack(side=tk.LEFT, padx=2)
        tk.Button(message_frame, text="Deszyfruj", command=self.decrypt_message).pack(side=tk.LEFT, padx=2)

        tk.Label(message_frame, text="Wynik:").pack(side=tk.LEFT, padx=15)
        self.message_output = tk.Entry(message_frame, width=40)
        self.message_output.pack(side=tk.LEFT, padx=2)

        # ======= RAMKA ATAKU =======
        attack_frame = tk.LabelFrame(self, text="Atak na kryptosystem")
        attack_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(
            attack_frame,
            text="Zapisz klucz publiczny do pliku",
            command=self.save_public_key
        ).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(
            attack_frame,
            text = "Załaduj klucz publiczny z pliku",
            command = self.load_public_key
        ).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(
            attack_frame,
            text="Uruchom atak Sidelnikova–Shestakova",
            command=self.run_attack
        ).pack(side=tk.LEFT, padx=15, pady=5)


        # ======= RAMKA WYJŚCIA =======
        output_frame = tk.LabelFrame(self, text="Przebieg ataku i wynik")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.output_box = scrolledtext.ScrolledText(output_frame)
        self.output_box.pack(fill=tk.BOTH, expand=True)

    # ================================
    # FUNKCJE OBSŁUGI
    # ================================

    def log(self, text):
        self.output_box.insert(tk.END, text + "\n")
        self.output_box.see(tk.END)


    def generate_parameters(self):
        n = self.n_entry.get()
        k = self.k_entry.get()
        q = self.q_entry.get()
        try:
            n = int(n)
            k = int(k)
            q = int(q)
        except ValueError:
            messagebox.showerror("Błąd", "n, k, q muszą być liczbami całkowitymi")
            return
        if n > q - 1:
            messagebox.showerror("Błąd", "n musi być mniejsze lub równe q - 1, aby wiadomość mogła zostać odszyfrowana.")
            return
        self.log("[+] Generowanie parametrów kryptosystemu...")
        try:
            system = McElieceRS(n, k, q)
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas generowania parametrów:\n{e}")
            return
        keys = system.generate_keys()
        private_key, public_key = keys
        result = {
            "private_key": private_key,
            "public_key": public_key
        }
        self.current_system = system
        self.current_keys = result
        pretty_result = fmt.format_keys(result, q)
        self.log("[+] Wygenerowane parametry i klucze:")
        self.log(pretty_result)

    def load_parameters(self):
        path = filedialog.askopenfilename(
            title="Wczytaj parametry",
            filetypes=[("Pliki", "*.*")]
        )
        if not path:
            return
        self.log(f"[+] Wczytywanie parametrów z: {path}")
        try:
            params = load_params_from_file(path)
        except Exception as e:
            params = load_params_from_file(path, private=False)
        keys = params["keys"]
        n = params["n"]
        k = params["k"]
        q = params["q"]
        self.current_keys = keys
        if keys["private_key"][0] is None:
            self.log("[!] Wczytano tylko klucz publiczny. Deszyfrowanie nie będzie możliwe.")
        self.current_system = McElieceRS(n, k, q)
        self.log("[+] Wczytane parametry i klucze:")
        pretty_result = fmt.format_keys(keys, q)
        self.log(pretty_result)

    def save_parameters(self):
        if self.current_keys is None:
            messagebox.showerror(
                "Błąd",
                "Najpierw wygeneruj lub wczytaj parametry"
            )
            return

        folder = filedialog.askdirectory(
            title="Wybierz folder do zapisu parametrów"
        )
        if not folder:
            return

        path = os.path.join(folder, "mceliece_keys.json")

        try:
            save_params_to_file(self.current_keys, self.current_system.q, path)
            self.log(f"[+] Parametry zapisane do pliku: {path}")
        except Exception as e:
            messagebox.showerror("Błąd zapisu", str(e))

    def encrypt_message(self):
        if self.current_keys is None:
            messagebox.showwarning("Uwaga", "Najpierw wygeneruj lub wczytaj parametry")
            return
        public_key = self.current_keys["public_key"]
        system = self.current_system
        k = system.k
        GF = system.GF
        try:
            m = fmt.parse_gf_vector(self.message_entry.get(), GF, k)
        except ValueError as e:
            messagebox.showerror("Błąd danych", str(e))
            return
        try:
            c = system.encrypt(m, public_key)
            self.message_output.delete(0, tk.END)
            self.message_output.insert(0, fmt.format_gf_vector(c))
        except Exception as e:
            messagebox.showerror("Błąd", f"Szyfrowanie nie powiodło się:\n{e}")


    def decrypt_message(self):
        if self.current_keys is None or self.current_system is None:
            messagebox.showwarning("Uwaga", "Najpierw wygeneruj lub wczytaj parametry")
            return
        if self.current_keys["private_key"][0] is None:
            messagebox.showerror("Błąd", "Brak klucza prywatnego do deszyfrowania")
            return
        system = self.current_system
        private_key = self.current_keys["private_key"]
        ciphertext = self.message_entry.get()

        if not ciphertext:
            messagebox.showwarning("Uwaga", "Podaj zaszyfrowaną wiadomość")
            return
        try:
            ciphertext = fmt.parse_gf_vector(ciphertext, system.GF, system.n)
            plaintext = system.decrypt(ciphertext, private_key)
            plaintext = fmt.format_gf_vector(plaintext)
            self.message_output.delete(0, tk.END)
            self.message_output.insert(0, str(plaintext))
            self.log(f"[+] Wiadomość odszyfrowana: {plaintext}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się odszyfrować: {e}")

    
    def save_public_key(self):
        if self.current_keys is None:
            messagebox.showerror(
                "Błąd",
                "Najpierw wygeneruj lub wczytaj parametry"
            )
            return
        folder = filedialog.askdirectory(
            title="Wybierz folder do zapisu klucza publicznego"
        )
        if not folder:
            return
        path = os.path.join(folder, "mceliece_public_key.json")
        try:
            save_params_to_file(
                {
                    "private_key": (None, None, None),
                    "public_key": self.current_keys["public_key"]
                },
                self.current_system.q,
                path
            )
            self.log(f"[+] Klucz publiczny zapisany do pliku: {path}")
        except Exception as e:
            messagebox.showerror("Błąd zapisu", str(e))

    def load_public_key(self):
        path = filedialog.askopenfilename(
            title="Wczytaj klucz publiczny",
            filetypes=[("Pliki", "*.*")]
        )
        if not path:
            return
        self.log(f"[+] Wczytywanie klucza publicznego z: {path}")
        params = load_params_from_file(path, private=False)
        keys = params["keys"]
        n = params["n"]
        k = params["k"]
        q = params["q"]
        if keys["private_key"][0] is not None:
            self.log("[!] Plik zawiera również klucz prywatny, ale zostanie on zignorowany.")
        self.current_keys = keys
        self.current_system = McElieceRS(n, k, q)
        self.log("[+] Wczytany klucz publiczny:")
        pretty_result = fmt.format_keys(keys, q)
        self.log(pretty_result)

        
    def run_attack(self):
        if self.current_keys is None or self.current_system is None:
            messagebox.showwarning("Uwaga", "Najpierw wygeneruj lub wczytaj parametry")
            return
        self.log("[+] Uruchamianie ataku Sidelnikova–Shestakova...")
        public_key = self.current_keys["public_key"]
        B = public_key[0]
        s = (B.shape[0]) - 1
        field = self.current_system.GF
        try:
            x, z, H = sidelnikov_shestakov_attack(B, s, field)
            self.log("[+] Wynik ataku:")
            result = f"Punkty ewaluacji x: {x}\nWspółczynniki z: {z}"
            self.log(str(result))
            self.log(f"Macierz kontrolna H:\n{fmt.format_matrix(H, 'H', field)}")
        except Exception as e:
            self.log("[!] Błąd podczas ataku")
            self.log(str(e))


if __name__ == "__main__":
    app = McElieceGUI()
    app.mainloop()
