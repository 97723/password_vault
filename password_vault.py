"""Şifre Kasası / Password Vault
Secure password generator with local encrypted storage. (TR / EN)

Requirement / Gereksinim:  pip install cryptography
Run / Çalıştır:            python sifre_kasasi.py
"""
import base64
import json
import locale
import math
import os
import secrets
import string
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

VAULT_DIR = Path.home() / ".sifre_kasasi"
VAULT_FILE = VAULT_DIR / "kasa.bin"
CONFIG_FILE = VAULT_DIR / "config.json"
KDF_ITERATIONS = 600_000
CLIPBOARD_CLEAR_MS = 30_000
AMBIGUOUS = "O0Il1|"
COMMON = {"123456", "password", "qwerty", "12345678", "111111", "sifre", "admin", "letmein"}

# ------------------------------------------------------------ Diller / i18n --
LANG_NAMES = {"tr": "Türkçe", "en": "English"}

STRINGS = {
    "tr": {
        "app_title": "Şifre Kasası",
        "language": "Dil:",
        "gen_frame": " Şifre Oluştur ",
        "length": "Uzunluk:",
        "lower": "Küçük harfler (a-z)",
        "upper": "Büyük harfler (A-Z)",
        "digits": "Rakamlar (0-9)",
        "symbols": "Semboller (!@#$...)",
        "ambiguous": "Karıştırılan karakterleri çıkar (O,0,l,1)",
        "generate": "Şifre Üret",
        "pw_label": "Şifre (kendin de yazabilirsin):",
        "account_label": "Hesap adı (ör. Gmail):",
        "save": "Kasaya Kaydet",
        "saved_frame": " Kayıtlı Şifreler ",
        "col_account": "Hesap",
        "col_pass": "Şifre",
        "copy": "Kopyala",
        "show": "Göster",
        "delete": "Sil",
        "warn": "Uyarı",
        "error": "Hata",
        "need_type": "En az bir karakter türü seçmelisin.",
        "len_too_short": "Uzunluk, seçilen tür sayısından az olamaz.",
        "empty_fields": "Hesap adı ve şifre boş olamaz.",
        "overwrite_title": "Üzerine yaz?",
        "overwrite_msg": "'{name}' zaten kayıtlı. Şifresi değiştirilsin mi?",
        "delete_title": "Sil",
        "delete_msg": "'{name}' silinsin mi?",
        "copied_title": "Kopyalandı",
        "copied_msg": "Şifre panoya kopyalandı, 30 saniye sonra temizlenecek.",
        "unlock_title": "Kasayı Aç",
        "unlock_prompt": "Ana şifre:",
        "wrong_master": "Ana şifre yanlış.",
        "create_title": "Kasa Oluştur",
        "create_prompt": "Yeni bir ANA ŞİFRE belirle.\nUnutursan kasa kurtarılamaz!",
        "repeat_prompt": "Ana şifreyi tekrar yaz:",
        "mismatch": "Şifreler eşleşmiyor.",
        "lvl_bad": "Kötü",
        "lvl_medium": "Orta",
        "lvl_good": "İyi",
        "lvl_unbreakable": "Kırılamaz",
    },
    "en": {
        "app_title": "Password Vault",
        "language": "Language:",
        "gen_frame": " Generate Password ",
        "length": "Length:",
        "lower": "Lowercase letters (a-z)",
        "upper": "Uppercase letters (A-Z)",
        "digits": "Digits (0-9)",
        "symbols": "Symbols (!@#$...)",
        "ambiguous": "Exclude look-alike characters (O,0,l,1)",
        "generate": "Generate",
        "pw_label": "Password (you can type your own):",
        "account_label": "Account name (e.g. Gmail):",
        "save": "Save to Vault",
        "saved_frame": " Saved Passwords ",
        "col_account": "Account",
        "col_pass": "Password",
        "copy": "Copy",
        "show": "Show",
        "delete": "Delete",
        "warn": "Warning",
        "error": "Error",
        "need_type": "Select at least one character type.",
        "len_too_short": "Length cannot be less than the number of selected types.",
        "empty_fields": "Account name and password cannot be empty.",
        "overwrite_title": "Overwrite?",
        "overwrite_msg": "'{name}' already exists. Replace its password?",
        "delete_title": "Delete",
        "delete_msg": "Delete '{name}'?",
        "copied_title": "Copied",
        "copied_msg": "Password copied to clipboard. It will be cleared in 30 seconds.",
        "unlock_title": "Unlock Vault",
        "unlock_prompt": "Master password:",
        "wrong_master": "Wrong master password.",
        "create_title": "Create Vault",
        "create_prompt": "Choose a new MASTER PASSWORD.\nIf you forget it, the vault cannot be recovered!",
        "repeat_prompt": "Repeat the master password:",
        "mismatch": "Passwords do not match.",
        "lvl_bad": "Weak",
        "lvl_medium": "Medium",
        "lvl_good": "Good",
        "lvl_unbreakable": "Unbreakable",
    },
}

LANG = "en"


def t(key, **kw):
    text = STRINGS[LANG][key]
    return text.format(**kw) if kw else text


def detect_language() -> str:
    """Kayıtlı ayar > sistem dili > İngilizce."""
    try:
        saved = json.loads(CONFIG_FILE.read_text()).get("lang")
        if saved in STRINGS:
            return saved
    except (OSError, ValueError):
        pass
    try:
        loc = (locale.getlocale()[0] or os.environ.get("LANG", "")).lower()
    except Exception:
        loc = ""
    return "tr" if loc.startswith("tr") or "turkish" in loc else "en"


def save_language(lang: str):
    try:
        VAULT_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps({"lang": lang}))
    except OSError:
        pass


# ---------------------------------------------------------------- Kasa ----
class Vault:
    """Şifrelenmiş dosya: ilk 16 bayt tuz, geri kalanı Fernet token."""

    def __init__(self):
        self.entries: dict[str, str] = {}
        self._salt = b""
        self._fernet: Fernet | None = None

    @staticmethod
    def exists() -> bool:
        return VAULT_FILE.exists()

    def _derive(self, master: str, salt: bytes) -> Fernet:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=KDF_ITERATIONS)
        return Fernet(base64.urlsafe_b64encode(kdf.derive(master.encode())))

    def create(self, master: str):
        self._salt = os.urandom(16)
        self._fernet = self._derive(master, self._salt)
        self.entries = {}
        self.save()

    def unlock(self, master: str) -> bool:
        raw = VAULT_FILE.read_bytes()
        self._salt, token = raw[:16], raw[16:]
        fernet = self._derive(master, self._salt)
        try:
            self.entries = json.loads(fernet.decrypt(token).decode())
        except (InvalidToken, ValueError):
            return False
        self._fernet = fernet
        return True

    def save(self):
        VAULT_DIR.mkdir(parents=True, exist_ok=True)
        token = self._fernet.encrypt(json.dumps(self.entries).encode())
        VAULT_FILE.write_bytes(self._salt + token)
        try:
            VAULT_FILE.chmod(0o600)
        except OSError:
            pass


# --------------------------------------------------------- Şifre mantığı --
def generate_password(length, use_lower, use_upper, use_digits, use_symbols, no_ambiguous):
    sets = []
    if use_lower:
        sets.append(string.ascii_lowercase)
    if use_upper:
        sets.append(string.ascii_uppercase)
    if use_digits:
        sets.append(string.digits)
    if use_symbols:
        sets.append("!@#$%^&*()-_=+[]{};:,.?/")
    if no_ambiguous:
        sets = ["".join(c for c in s if c not in AMBIGUOUS) for s in sets]
    if not sets:
        raise ValueError(t("need_type"))
    if length < len(sets):
        raise ValueError(t("len_too_short"))
    pool = "".join(sets)
    chars = [secrets.choice(s) for s in sets]  # her türden en az 1 karakter
    chars += [secrets.choice(pool) for _ in range(length - len(chars))]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def evaluate_strength(pw: str):
    """(seviye_anahtarı, renk, 0-1 oran, entropi bit) döndürür."""
    if not pw:
        return None, "#9e9e9e", 0.0, 0
    pool = 0
    if any(c.islower() for c in pw):
        pool += 26
    if any(c.isupper() for c in pw):
        pool += 26
    if any(c.isdigit() for c in pw):
        pool += 10
    if any(not c.isalnum() for c in pw):
        pool += 32
    bits = len(pw) * math.log2(pool) if pool else 0
    bits *= len(set(pw)) / len(pw)  # tekrar eden karakterler gücü düşürür
    if pw.lower() in COMMON:
        bits = 0
    if bits < 40:
        return "bad", "#e53935", 0.25, bits
    if bits < 65:
        return "medium", "#fb8c00", 0.5, bits
    if bits < 90:
        return "good", "#7cb342", 0.75, bits
    return "unbreakable", "#2e7d32", 1.0, bits


# ------------------------------------------------------------------- GUI --
class App(tk.Tk):
    def __init__(self, vault: Vault):
        super().__init__()
        self.vault = vault
        self.geometry("840x540")
        self.minsize(780, 500)
        ttk.Style(self).theme_use("clam")

        self.length = tk.IntVar(value=16)
        self.opt_lower = tk.BooleanVar(value=True)
        self.opt_upper = tk.BooleanVar(value=True)
        self.opt_digits = tk.BooleanVar(value=True)
        self.opt_symbols = tk.BooleanVar(value=True)
        self.opt_ambiguous = tk.BooleanVar(value=False)
        self.password = tk.StringVar()
        self.account = tk.StringVar()
        self.password.trace_add("write", lambda *_: self.update_strength())

        self.build_ui()
        self.on_generate()

    def build_ui(self):
        """Tüm arayüzü seçili dille (yeniden) kurar. Değişkenler korunur."""
        for child in self.winfo_children():
            child.destroy()
        self.title(t("app_title"))

        top = ttk.Frame(self)
        top.pack(fill="x", padx=12, pady=(8, 0))
        self.lang_box = ttk.Combobox(top, values=list(LANG_NAMES.values()),
                                     state="readonly", width=10)
        self.lang_box.set(LANG_NAMES[LANG])
        self.lang_box.pack(side="right")
        self.lang_box.bind("<<ComboboxSelected>>", lambda _e: self.after(10, self.on_language))
        ttk.Label(top, text=t("language")).pack(side="right", padx=6)

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)

        left = ttk.LabelFrame(body, text=t("gen_frame"), padding=12)
        left.pack(side="left", fill="y", padx=12, pady=12)

        ttk.Label(left, text=t("length")).grid(row=0, column=0, sticky="w")
        self.len_label = ttk.Label(left, text=str(int(self.length.get())), width=3)
        self.len_label.grid(row=0, column=1, sticky="e")
        ttk.Scale(left, from_=8, to=64, variable=self.length, command=self.on_len_change,
                  length=250).grid(row=1, column=0, columnspan=2, pady=(0, 8))

        for i, (key, var) in enumerate([
            ("lower", self.opt_lower), ("upper", self.opt_upper),
            ("digits", self.opt_digits), ("symbols", self.opt_symbols),
            ("ambiguous", self.opt_ambiguous),
        ]):
            ttk.Checkbutton(left, text=t(key), variable=var).grid(
                row=2 + i, column=0, columnspan=2, sticky="w", pady=1)

        ttk.Button(left, text=t("generate"), command=self.on_generate).grid(
            row=8, column=0, columnspan=2, sticky="ew", pady=(12, 8))

        ttk.Label(left, text=t("pw_label")).grid(row=9, column=0, columnspan=2, sticky="w")
        ttk.Entry(left, textvariable=self.password, font=("Consolas", 12)).grid(
            row=10, column=0, columnspan=2, sticky="ew", pady=2)

        self.bar = tk.Canvas(left, height=12, bg="#e0e0e0", highlightthickness=0)
        self.bar.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(6, 2))
        self.bar.bind("<Configure>", lambda _e: self.update_strength())
        self.strength_label = ttk.Label(left, text="-", font=("TkDefaultFont", 11, "bold"))
        self.strength_label.grid(row=12, column=0, columnspan=2, sticky="w")

        ttk.Label(left, text=t("account_label")).grid(
            row=13, column=0, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Entry(left, textvariable=self.account).grid(row=14, column=0, columnspan=2, sticky="ew")
        ttk.Button(left, text=t("save"), command=self.on_save).grid(
            row=15, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        right = ttk.LabelFrame(body, text=t("saved_frame"), padding=12)
        right.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=12)

        self.tree = ttk.Treeview(right, columns=("hesap", "sifre"), show="headings", height=15)
        self.tree.heading("hesap", text=t("col_account"))
        self.tree.heading("sifre", text=t("col_pass"))
        self.tree.column("sifre", width=140)
        self.tree.pack(fill="both", expand=True)

        btns = ttk.Frame(right)
        btns.pack(fill="x", pady=(8, 0))
        ttk.Button(btns, text=t("copy"), command=self.on_copy).pack(side="left")
        ttk.Button(btns, text=t("show"), command=self.on_show).pack(side="left", padx=6)
        ttk.Button(btns, text=t("delete"), command=self.on_delete).pack(side="left")

        self.refresh_list()
        self.update_strength()

    # --- olaylar
    def on_language(self):
        global LANG
        LANG = {v: k for k, v in LANG_NAMES.items()}[self.lang_box.get()]
        save_language(LANG)
        self.build_ui()

    def on_len_change(self, _=None):
        self.len_label.config(text=str(int(self.length.get())))

    def on_generate(self):
        try:
            self.password.set(generate_password(
                int(self.length.get()), self.opt_lower.get(), self.opt_upper.get(),
                self.opt_digits.get(), self.opt_symbols.get(), self.opt_ambiguous.get()))
        except ValueError as e:
            messagebox.showwarning(t("warn"), str(e))

    def update_strength(self):
        key, color, ratio, bits = evaluate_strength(self.password.get())
        label = t("lvl_" + key) if key else "-"
        self.strength_label.config(text=f"{label}  ({bits:.0f} bit)" if bits else label,
                                   foreground=color)
        self.bar.delete("all")
        self.bar.create_rectangle(0, 0, self.bar.winfo_width() * ratio, 12, fill=color, width=0)

    def on_save(self):
        name, pw = self.account.get().strip(), self.password.get()
        if not name or not pw:
            messagebox.showwarning(t("warn"), t("empty_fields"))
            return
        if name in self.vault.entries and not messagebox.askyesno(
                t("overwrite_title"), t("overwrite_msg", name=name)):
            return
        self.vault.entries[name] = pw
        self.vault.save()
        self.account.set("")
        self.refresh_list()

    def selected(self):
        sel = self.tree.selection()
        return str(self.tree.item(sel[0])["values"][0]) if sel else None

    def on_copy(self):
        name = self.selected()
        if name is None:
            return
        self.clipboard_clear()
        self.clipboard_append(self.vault.entries[name])
        self.after(CLIPBOARD_CLEAR_MS, self.clipboard_clear)
        messagebox.showinfo(t("copied_title"), t("copied_msg"))

    def on_show(self):
        name = self.selected()
        if name is not None:
            messagebox.showinfo(name, self.vault.entries[name])

    def on_delete(self):
        name = self.selected()
        if name is not None and messagebox.askyesno(t("delete_title"), t("delete_msg", name=name)):
            del self.vault.entries[name]
            self.vault.save()
            self.refresh_list()

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        for name in sorted(self.vault.entries):
            self.tree.insert("", "end", values=(name, "•" * 10))


def main():
    global LANG
    LANG = detect_language()
    root = tk.Tk()
    root.withdraw()
    vault = Vault()
    if vault.exists():
        for _ in range(3):
            master = simpledialog.askstring(t("unlock_title"), t("unlock_prompt"),
                                            show="*", parent=root)
            if master is None:
                return
            if vault.unlock(master):
                break
            messagebox.showerror(t("error"), t("wrong_master"))
        else:
            return
    else:
        master = simpledialog.askstring(t("create_title"), t("create_prompt"),
                                        show="*", parent=root)
        if not master:
            return
        if master != simpledialog.askstring(t("create_title"), t("repeat_prompt"),
                                            show="*", parent=root):
            messagebox.showerror(t("error"), t("mismatch"))
            return
        vault.create(master)
    root.destroy()
    App(vault).mainloop()


if __name__ == "__main__":
    main()