# setup_db_tiket_museum.py
import sqlite3
import os
from konfigurasi import DB_PATH # Mengambil path dari konfigurasi

def setup_database():
    print(f"Memeriksa/membuat database di: {DB_PATH}")
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        sql_create_transaksi = """
        CREATE TABLE IF NOT EXISTS transaksi ( 
            id_transaksi INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_pelanggan TEXT NOT NULL,
            tanggal DATE NOT NULL);"""
        print("Membuat tabel 'transaksi' (jika belum ada)...")
        cursor.execute(sql_create_transaksi)

        sql_create_detail_transaksi = """
        CREATE TABLE IF NOT EXISTS detail_transaksi ( 
            id_transaksi INTEGER NOT NULL,
            kategori TEXT NOT NULL,
            jumlah INTEGER NOT NULL CHECK (jumlah > 0),
            PRIMARY KEY (id_transaksi, kategori),
            FOREIGN KEY (id_transaksi) REFERENCES transaksi(id_transaksi)
                ON DELETE CASCADE ON UPDATE CASCADE
        );"""
        print("Membuat tabel 'detail_transaksi' (jika belum ada)...")
        cursor.execute(sql_create_detail_transaksi)

        conn.commit()
        print(" -> Semua tabel siap")
        return True
    except sqlite3.Error as e: print(f" -> Error SQLite saat setup: {e}"); return False
    finally: 
        if conn: conn.close(); print(" ->Koneksi DB setup ditutup")


if __name__ == "__main__":
    print("--- Memulai Setup Database Tiket Museum ---")
    if setup_database():
        print(f"\nSetup database '{os.path.basename(DB_PATH)}' selesai")
    else:
        print("\nSetup database GAGAL")
        print("--- Setup Database Selesai ---")