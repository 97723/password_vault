# 🔐 Şifre Kasası / Password Vault

**[Türkçe](#-türkçe) | [English](#-english)**


---

## 🇹🇷 Türkçe

Basit ve sade arayüzlü, açık kaynaklı bir şifre oluşturucu ve yerel şifre kasası. Güçlü şifreni oluştur, hangi hesaba ait olduğunu yazıp kendi bilgisayarında **şifreli** olarak sakla. İnternet bağlantısı gerekmez, hiçbir veri dışarı gönderilmez.

### Özellikler

- **Şifre üretimi:** 8-64 karakter arası uzunluk, küçük harf, büyük harf, rakam ve sembol seçenekleri. İstersen karıştırılan karakterleri (`O`, `0`, `l`, `1`) hariç tutabilirsin.
- **Güvenli rastgelelik:** Şifreler Python'un `secrets` modülüyle üretilir. Seçilen her karakter türünden en az bir tane bulunur.
- **Güç göstergesi:** Şifren **Kötü / Orta / İyi / Kırılamaz** olarak derecelendirilir. Kendi yazdığın şifreyi de test edebilirsin.
- **Şifreli kasa:** Şifreler hesap adıyla birlikte, ana şifrenle şifrelenmiş bir dosyada saklanır.
- **Pano koruması:** Kopyalanan şifre 30 saniye sonra panodan otomatik temizlenir.
- **Çift dil:** Türkçe ve İngilizce. İlk açılışta sistem dili algılanır, istediğin zaman değiştirebilirsin.

### Kurulum

Gereksinimler: **Python 3.10+**

```bash
git clone https://github.com/97723/password_vault.git
cd password_vault
pip install -r requirements.txt
python password_vault.py
```

> Linux'ta `tkinter` eksikse: `sudo apt install python3-tk`

### Kullanım

1. İlk açılışta bir **ana şifre** belirle. Bu şifre kasanın anahtarıdır.
2. Soldaki panelden uzunluğu ve karakter türlerini seçip **Şifre Üret**'e bas.
3. Hesap adını (ör. Gmail) yazıp **Kasaya Kaydet**'e tıkla.
4. Sağdaki listeden şifreyi **Kopyala**, **Göster** veya **Sil**.

### Güvenlik

| Konu | Ayrıntı |
|---|---|
| Şifreleme | Fernet (AES + HMAC-SHA256) |
| Anahtar türetme | PBKDF2-HMAC-SHA256, 600.000 iterasyon, rastgele 16 baytlık tuz |
| Kasa konumu | `~/.password_vault/vault.bin` |
| Ağ kullanımı | Yok, her şey yerelde kalır |

Güç seviyeleri entropi tahminine dayanır (< 40 bit: Kötü, < 65: Orta, < 90: İyi, ≥ 90: Kırılamaz). Bu bir **tahmindir**, mutlak bir garanti değildir.

### ⚠️ Önemli uyarılar

- **Ana şifreni unutursan kasa kurtarılamaz.** Sıfırlama veya yedek anahtar yoktur.
- Bu proje bağımsız bir güvenlik denetiminden geçmemiştir. Çok kritik hesaplar için denetlenmiş şifre yöneticilerini de değerlendir.
- Kasa dosyasını (`vault.bin`) yedeklemeyi unutma.
- Yazılım "olduğu gibi" sunulur, kullanım sorumluluğu sana aittir.

### Tek dosyalı çalıştırılabilir (.exe) oluşturma

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole password_vault.py
```

Çıktı `dist/` klasöründe oluşur.

### Yeni dil ekleme

`password_vault.py` içindeki `STRINGS` sözlüğüne yeni bir dil bloğu (ör. `"de": {...}`) ve `LANG_NAMES` içine bir satır ekleyip pull request gönderebilirsin.

---

## 🇬🇧 English

An open-source password generator and local password vault with a clean, simple interface. Generate a strong password, label it with the account it belongs to, and store it **encrypted** on your own computer. No internet connection is needed and no data ever leaves your machine.

### Features

- **Password generation:** Length from 8 to 64 characters, with lowercase, uppercase, digits and symbols options. You can also exclude look-alike characters (`O`, `0`, `l`, `1`).
- **Secure randomness:** Passwords are generated with Python's `secrets` module. At least one character from each selected type is guaranteed.
- **Strength meter:** Your password is rated **Weak / Medium / Good / Unbreakable**. You can also type your own password to test it.
- **Encrypted vault:** Passwords are stored with their account names in a file encrypted with your master password.
- **Clipboard protection:** A copied password is automatically cleared from the clipboard after 30 seconds.
- **Bilingual:** Turkish and English. The system language is detected on first launch, and you can switch at any time.

### Installation

Requirements: **Python 3.10+**

```bash
git clone https://github.com/97723/password_vault.git
cd password_vault
pip install -r requirements.txt
python password_vault.py
```

> On Linux, if `tkinter` is missing: `sudo apt install python3-tk`

### Usage

1. On first launch, choose a **master password**. It is the key to your vault.
2. In the left panel, pick the length and character types, then click **Generate**.
3. Type an account name (e.g. Gmail) and click **Save to Vault**.
4. From the list on the right, you can **Copy**, **Show** or **Delete** a password.

### Security

| Topic | Details |
|---|---|
| Encryption | Fernet (AES + HMAC-SHA256) |
| Key derivation | PBKDF2-HMAC-SHA256, 600,000 iterations, random 16-byte salt |
| Vault location | `~/.password_vault/vault.bin` |
| Network usage | None, everything stays local |

Strength levels are based on an entropy estimate (< 40 bits: Weak, < 65: Medium, < 90: Good, ≥ 90: Unbreakable). This is an **estimate**, not an absolute guarantee.

### ⚠️ Important notes

- **If you forget your master password, the vault cannot be recovered.** There is no reset or backup key.
- This project has not undergone an independent security audit. For highly critical accounts, consider audited password managers as well.
- Remember to back up your vault file (`vault.bin`).
- The software is provided "as is", and you use it at your own risk.

### Building a standalone executable

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole password_vault.py
```

The output will be in the `dist/` folder.

### Adding a new language

Add a new language block (e.g. `"de": {...}`) to the `STRINGS` dictionary in `password_vault.py` and a line to `LANG_NAMES`, then open a pull request.

---

## 📄 License / Lisans

MIT License. See [LICENSE](LICENSE) for details. / Ayrıntılar için [LICENSE](LICENSE) dosyasına bak.