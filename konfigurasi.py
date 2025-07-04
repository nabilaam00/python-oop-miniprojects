# konfigurasi.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Nama file database
NAME_DB = 'pembelian_tiket_museum.db'

# Path ke database
DB_PATH = os.path.join(BASE_DIR, NAME_DB)

KATEGORI_TIKET = ["Reguler", "VIP", "VVIP"]
KATEGORI_DEFAULT = "Reguler"