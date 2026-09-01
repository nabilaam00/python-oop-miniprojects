# model.py
from datetime import datetime, date, timedelta
from typing import List, Union


class DetailTransaksi:
    def __init__(self, kategori:str, jumlah: int):
        self.kategori = str(kategori) if kategori else "Reguler"
        try:
            jumlah_valid = int(jumlah)
            if jumlah_valid > 0:
                self.jumlah = jumlah_valid
            else:
                self.jumlah = 0
                print(f"Peringatan: Jumlah '{jumlah}' harus positif")
        except (ValueError, TypeError): 
            self.jumlah = 0
            print(f"Peringatan: Jumlah '{jumlah}' tidak valid")
    
    def to_dict(self) -> dict:
        return{"kategori":self.kategori, "jumlah":self.jumlah}

class Transaksi:
    """Merepresentasikan satu entitas transaksi pembelian tiket"""
    def __init__(self, nama_pelanggan: str, tanggal: Union[datetime.date, str], id_transaksi: Union[int, None] = None):
        self.id_transaksi = id_transaksi
        if len(nama_pelanggan.strip()) >= 1:
            self.nama_pelanggan = nama_pelanggan.strip()
        else:
            self.nama_pelanggan = "Pelanggan"
            print("Peringatan: Nama tidak boleh kosong")

        if isinstance(tanggal, date): 
            self.tanggal = tanggal
        elif isinstance(tanggal, str):
            try: 
                self.tanggal = datetime.strptime(tanggal, "%Y-%m-%d").date()
            except ValueError: 
                print("Format tanggal salah! Tanggal otomatis diatur 5 hari setelah hari ini")
                self.tanggal = date.today() + timedelta(days=5)
        else:  
            print(f"Tipe tanggal '{type(tanggal)}' tidak valid. Tanggal otomatis diatur 5 hari setelah hari ini")
            self.tanggal = date.today() + timedelta(days=5)

        self.detail_transaksi_list = []
    
    def tambah_detail_transaksi(self, detail_list: List[DetailTransaksi]):
        if isinstance(detail_list, list):
            self.detail_transaksi_list = detail_list
        else:
            print("[WARNING] Detail transaksi bukan list!")
            self.detail_transaksi_list = []
    
    def to_dict(self) -> dict:
        return {"nama_pelanggan": self.nama_pelanggan, "tanggal":self.tanggal.strftime("%Y-%m-%d"), "detail_transaksi": [d.to_dict() for d in self.detail_transaksi_list]}



        
            