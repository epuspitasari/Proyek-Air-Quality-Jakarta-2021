# Blok 1: Import Alat & Utils
import os
import sys

# Tambahkan import sys di atas agar sys.path bisa jalan
sys.path.append('src/')
import utils

# Blok 2: Fungsi Utama (The Logic)
def process_data(config):
    # Logika tetap sama, pastikan fungsi-fungsi ini sudah ada di src/utils.py
    df = utils.gabung_semua_data(config['raw_dataset_dir'])
    df_clean = utils.validasi_logika_data(df)
    utils.check_missing_values(df_clean)
    return df_clean

# Blok 3: Pintu Gerbang (__main__)
if __name__ == "__main__":
    config = utils.load_config("config/config.yaml")
    
    print("--- Memulai Pipeline Data ---")
    df_final = process_data(config)
    
    # AMBIL NAMA FILE DARI CONFIG (Jangan diketik manual lagi)
    nama_file = config['interim_filename'] 
    
    # Simpan ke Interim
    utils.serialize_data(df_final, config['interim_dataset_dir'], nama_file)

    # Verifikasi
    path_lengkap = os.path.join(config['interim_dataset_dir'], nama_file)
    utils.verify_serialization(path_lengkap, df_final)