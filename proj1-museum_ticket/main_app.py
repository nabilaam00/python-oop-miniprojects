# main_app.py
import streamlit as st
import datetime
import pandas as pd
import locale
import time

try: locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
except locale.Error:
    try: locale.setlocale(locale.LC_ALL, 'Indonesian_Indonesia.1252')
    except: print("Locale id_ID/Indonesian tidak tersedia")

def format_rp(angka):
    try: return locale.currency(angka or 0, grouping=True, symbol='Rp')[:-3]
    except: return f"Rp {angka or 0:,.0f}".replace(",",".")
try: 
    from model import Transaksi, DetailTransaksi
    from manajer_transaksi import TransaksiPembeli
    from konfigurasi import KATEGORI_TIKET # Ambil list kategori
except ImportError as e:
    st.error(f"Gagal mengimpor modul: {e}. Pastikan file .py lain ada")
    st.stop()

st.set_page_config(page_title="Pembelian Tiket Museum H", layout="wide", initial_sidebar_state="expanded")

# ---- Inisialisasi Pengelola Transaksi Pembelian ---
@st.cache_resource
def get_transaksi_pembeli():
    print(">>> STREAMLIT: (Cache Resource) Menginisialisasi TransaksiPembeli dan DetailTransaksi...")
    return TransaksiPembeli() # Memicu cek DB/Tabel di __init__
transaksi = get_transaksi_pembeli()

# ---Fungsi Halaman/UI ---
def halaman_input(transaksi: TransaksiPembeli):
    st.header("🏦 Lakukan Pembelian Tiket")

    with st.form("form_transaksi_baru", clear_on_submit=True):
        nama_pelanggan = st.text_input("Nama Pelanggan*", placeholder="Masukkan Nama Anda")
        tanggal = st.date_input("Tanggal Kunjungan*", min_value=datetime.date.today())

        st.markdown("### 🎫 Jumlah Tiket per Kategori")
        detail_list = []
        for kategori in KATEGORI_TIKET:
            jumlah = st.number_input(
                f"{kategori}", min_value=0, step=1, value=0, key=f"jumlah_{kategori}"
            )
            if jumlah > 0:
                detail_list.append(DetailTransaksi(kategori, jumlah))

        submitted = st.form_submit_button("Simpan Transaksi")

        if submitted:
            if not nama_pelanggan:
                st.warning("Nama Wajib Diisi!", icon="⚠️")
            elif not detail_list:
                st.warning("Pilih minimal 1 kategori dengan jumlah > 0!", icon="⚠️")
            else:
                with st.spinner("Menyimpan..."):
                    tx = Transaksi(nama_pelanggan, tanggal)
                    tx.tambah_detail_transaksi(detail_list)
                    id_terakhir = transaksi.tambah_transaksi(tx)
                    if id_terakhir:
                        st.success(f"Transaksi berhasil disimpan! Silahkan menuju ke halaman Ringkasan Pembelian🙏")
                        st.session_state["id_terakhir"] = id_terakhir
                    else:
                        st.error("Gagal menyimpan transaksi")

def tampilkan_struk(transaksi: TransaksiPembeli, id_transaksi: int):
    st.markdown("### 🧾 Struk Transaksi")
    tx = transaksi.get_transaksi_by_id(id_transaksi)
    
    if not tx:
        st.error("Gagal memuat struk transaksi")
        return
    tanggal_str = tx.tanggal.strftime('%d %B %Y')
    st.write(f"**Nama:** {tx.nama_pelanggan}")
    st.write(f"**Tanggal Kunjungan:** {tanggal_str}")
    st.markdown("**Detail Tiket:**")
    
    data = []
    for d in tx.detail_transaksi_list:
        data.append({
            "Kategori": d.kategori,
            "Jumlah": d.jumlah,
            "Harga Satuan": format_rp(transaksi.get_harga_kategori(d.kategori)),
            "Total": format_rp(transaksi.get_harga_kategori(d.kategori) * d.jumlah)
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, hide_index=True, use_container_width=True)

    total_semua = sum([transaksi.get_harga_kategori(d.kategori) * d.jumlah for d in tx.detail_transaksi_list])
    st.write(f"**Total Pembayaran:** {format_rp(total_semua)}")


def halaman_ringkasan(transaksi: TransaksiPembeli):
    st.subheader("Ringkasan Transaksi")
    if "id_terakhir" in st.session_state:
        tampilkan_struk(transaksi, st.session_state["id_terakhir"])

        if st.button("🛑 Akhiri Transaksi"):
            st.toast("🎉 Terima kasih telah melakukan transaksi. Sampai bertemu di museum H!", icon="🙏")
            time.sleep(3)
            menu_tujuan = "Tentang Museum H"

            st.session_state.clear()
            st.session_state["menu_utama"] = menu_tujuan
            st.rerun()

    else: 
        st.write("Silahkan lakukan pembelian tiket terlebih dahulu🙏")


def halaman_info_harga(transaksi: TransaksiPembeli):
    st.header("🏛️ Informasi Museum & Harga Tiket")

    st.subheader("Tentang Museum H")
    st.markdown("""
    Museum H adalah tempat wisata edukatif yang menampilkan sejarah budaya lokal.
    
    **Jam Buka:**  
    Selasa - Minggu, pukul 08.00 - 16.00  
    (Senin Tutup)

    **Alamat:**  
    Jl. Sejarah No. 123, Kota Pendidikan

    **Kontak:**  
    museumHadministrator@msh.org | (021) 123-4567
    
    **Informasi Tiket**<br>
    Museum kami menyediakan beberapa kategori tiket yang dapat Anda pilih sesuai kebutuhan Anda
    - **Tiket Reguler**: Mendapatkan akses ke area museum standar
    - **Tiket VIP**: Mendapatkan fasilitas kategori reguler + Pemandu wisata dan akses ke beberapa area khusus
    - **Tiket VVIP**: Mendapatkan fasilitas kategori VIP + akses ke seluruh area khusus dan ruang koleksi museum  
    """, unsafe_allow_html=True)

    st.subheader("💰 Daftar Harga Tiket")
    harga_dict = transaksi.get_harga_kategori()
    for kategori, harga in harga_dict.items():
        st.markdown(f"- **{kategori}**: {format_rp(harga)}")

# --- Fungsi Utama Aplikasi Streamlit ---
def main():
    st.sidebar.title("🏦Pembelian Tiket Museum")
    menu_pilihan = st.sidebar.radio("Pilih Menu:", ["Tentang Museum H","Pembelian", "Ringkasan Pembelian"], key="menu_utama")
    st.sidebar.markdown("---")
    st.sidebar.info("Aplikasi Pembelian Tiket Museum")
    #manajer_transaksi = get_transaksi_pembeli()
    if menu_pilihan == "Tentang Museum H": halaman_info_harga(transaksi)
    elif menu_pilihan == "Pembelian": halaman_input(transaksi)
    elif menu_pilihan == "Ringkasan Pembelian": halaman_ringkasan(transaksi)
    st.markdown("---")
    st.caption("Pengembangan Aplikasi Berbasis OOP")

if __name__ == "__main__":
    main()
