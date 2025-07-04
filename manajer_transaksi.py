# manajer_transaksi.py
import datetime
import pandas as pd
from model import Transaksi, DetailTransaksi
import database

class TransaksiPembeli:
    _db_setup_done = False # Flag untuk memastika setup DB hanya dicek sekali per sesi
    def __init__(self):
        if not TransaksiPembeli._db_setup_done:
            print("[TransaksiPembeli] Melakukan pengecekan/setup database awal...")
            if database.setup_database_initial(): # Panggil fungsi setup dari database.py
                TransaksiPembeli._db_setup_done = True
                print("[TransaksiPembeli] Database siap")
            else:
                print("[TransaksiPembeli] CRITICAL: Setup database awal GAGAL!")
    
    def get_harga_kategori(self, kategori=None) -> int:
        harga_map = {
            "REGULER": 25000,
            "VIP": 50000,
            "VVIP": 100000,
        }

        if kategori is None:
            return harga_map
        
        return harga_map.get(kategori.upper(), 0)
  
    
    def tambah_transaksi(self, transaksi: Transaksi) -> bool:
        if not isinstance(transaksi, Transaksi):
            print("[ERROR] Transaksi tidak valid")
            return False
        
        sql = "INSERT INTO transaksi (nama_pelanggan, tanggal) VALUES (?, ?)" 
        params = (transaksi.nama_pelanggan, transaksi.tanggal)
        last_id = database.execute_query(sql, params)
        if not last_id:
            print("[ERROR] Gagal menyimpan data utama transaksi")
            return False
        for detail in transaksi.detail_transaksi_list:
            if not isinstance(detail, DetailTransaksi) or detail.jumlah <= 0:
                print(f"[WARNING] Lewatkan detail tidak valid: {detail.to_dict()}")
                return False
        
            sql_detail = "INSERT INTO detail_transaksi (id_transaksi, kategori, jumlah) VALUES (?, ?, ?)"
            params_detail = (last_id, detail.kategori, detail.jumlah)
            result = database.execute_query(sql_detail, params_detail)

            if result is None:
                print(f"[ERROR] Gagal menyimpan detail: {detail.to_dict()}")
                return False

        transaksi.last_id = last_id
        return last_id

    def get_transaksi_by_id(self, id_transaksi: int) -> Transaksi | None:
        sql = """SELECT t.id_transaksi, t.tanggal, t.nama_pelanggan,
           d.kategori, d.jumlah FROM transaksi t JOIN detail_transaksi d ON t.id_transaksi = d.id_transaksi 
           WHERE t.id_transaksi = ?"""
        rows = database.fetch_query(sql, params=(id_transaksi,), fetch_all=True)
        if not rows:
            return None

        row_pertama = rows[0]
        transaksi = Transaksi(
            id_transaksi=row_pertama["id_transaksi"],
            nama_pelanggan=row_pertama["nama_pelanggan"],
            tanggal=row_pertama["tanggal"]
        )
        detail_list = []
        for row in rows:
            kategori = row["kategori"]
            jumlah = row["jumlah"]
            harga = self.get_harga_kategori(kategori)
            total = harga * jumlah

            d = DetailTransaksi(kategori=kategori, jumlah=jumlah)
            d.harga_satuan = harga  
            d.total_harga = total
            detail_list.append(d)
        transaksi.tambah_detail_transaksi(detail_list)

        return transaksi

    
    def get_dataframe_transaksi(self, filter_tanggal: datetime.date | None = None) -> pd.DataFrame:
        query = """
            SELECT 
                t.tanggal, t.nama_pelanggan, d.kategori, d.jumlah FROM transaksi t
                JOIN detail_transaksi d ON t.id_transaksi = d.id_transaksi
        """
        params = None
        if filter_tanggal:
            query += " WHERE t.tanggal = ?"
            params = (filter_tanggal.strftime("%Y-%m-%d"),)
        query += " ORDER BY t.tanggal DESC, t.id_transaksi DESC"

        df = database.get_dataframe(query, params=params)

        if not df.empty:
            # Hitung harga satuan dan total harga
            df['harga_satuan'] = df['kategori'].map(self.get_harga_kategori)
            df['total_harga'] = df['harga_satuan'] * df['jumlah']

            # Format ke Rupiah
            try:
                import locale
                locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
                df['Harga Satuan'] = df['harga_satuan'].map(lambda x: locale.currency(x, grouping=True, symbol='Rp ')[:-3])
                df['Total Harga'] = df['total_harga'].map(lambda x: locale.currency(x, grouping=True, symbol='Rp ')[:-3])
            except:
                df['Harga Satuan'] = df['harga_satuan'].map(lambda x: f"Rp {x:,.0f}".replace(",", "."))
                df['Total Harga'] = df['total_harga'].map(lambda x: f"Rp {x:,.0f}".replace(",", "."))

            df = df[['tanggal', 'nama_pelanggan', 'kategori', 'jumlah', 'Harga Satuan', 'Total Harga']]

        return df
    


    
