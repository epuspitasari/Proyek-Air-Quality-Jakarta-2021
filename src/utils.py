import yaml
import joblib
import os
import pandas as pd
import numpy as np

# --- 1. KONFIGURASI & UTILS DASAR ---
def load_config(path_config):
    """Membaca file konfigurasi yaml."""
    with open(path_config, 'r') as file:
        return yaml.safe_load(file)

def pickle_dump(data, path):
    """Menyimpan object (df, model, scaler) ke file pkl."""
    # Membuat folder otomatis jika belum ada
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    joblib.dump(data, path)
    print(f"SUCCESS: Object disimpan di {path}")

def pickle_load(path):
    """Memuat kembali object dari file pkl."""
    try:
        return joblib.load(path)
    except FileNotFoundError:
        print(f"ERROR: File tidak ditemukan di {path}")
        return None

# Fungsi lama serialize_data tetap dipertahankan agar tidak eror jika dipanggil
def serialize_data(df, folder_path, file_name):
    save_path = os.path.join(folder_path, file_name)
    pickle_dump(df, save_path)
    return save_path

# --- 2. DATA PIPELINE FUNCTIONS ---
def gabung_semua_data(folder_path):
    """Menggabungkan 12 file CSV dan konversi ke angka."""
    daftar_file = sorted([f for f in os.listdir(folder_path) if f.endswith('.csv')])
    list_df = []
    kolom_angka = ['pm10', 'pm25', 'so2', 'co', 'o3', 'no2']
    
    for nama_file in daftar_file:
        df_temp = pd.read_csv(os.path.join(folder_path, nama_file))
        # Perbaikan: 'categori' diubah menjadi 'category'
        if 'categori' in df_temp.columns:
            df_temp = df_temp.rename(columns={'categori': 'category'})
        for col in kolom_angka:
            if col in df_temp.columns:
                df_temp[col] = pd.to_numeric(df_temp[col], errors='coerce')
        list_df.append(df_temp)
    
    return pd.concat(list_df, ignore_index=True)

def audit_waktu_data(df_input):
    """Konversi tanggal cerdas agar data Juni dkk tidak hilang."""
    df_clean = df_input.copy()
    df_clean['tanggal'] = pd.to_datetime(df_clean['tanggal'], dayfirst=True, errors='coerce')
    if df_clean['tanggal'].isna().sum() > 0:
        df_clean['tanggal'] = df_clean['tanggal'].fillna(
            pd.to_datetime(df_input['tanggal'], dayfirst=False, errors='coerce')
        )
    df_clean = df_clean.dropna(subset=['tanggal'])
    df_clean['tahun'] = df_clean['tanggal'].dt.year.astype(int)
    df_clean['bulan_angka'] = df_clean['tanggal'].dt.month.astype(int)
    df_clean['nama_bulan'] = df_clean['tanggal'].dt.month_name()
    return df_clean

def validasi_logika_data(df_input):
    """Membersihkan duplikat dan nilai negatif."""
    df_clean = df_input.copy()
    df_clean = df_clean.drop_duplicates()
    kolom_polutan = ['pm10', 'pm25', 'so2', 'co', 'o3', 'no2']
    for col in kolom_polutan:
        if col in df_clean.columns:
            df_clean.loc[df_clean[col] < 0, col] = np.nan
    return df_clean

# --- 3. HELPER UNTUK NOTEBOOK ---
def check_missing_values(df):
    """Menampilkan ringkasan data kosong."""
    null_counts = df.isnull().sum()
    null_percent = (df.isnull().mean() * 100).round(2)
    missing_df = pd.DataFrame({'Jumlah': null_counts, 'Persen (%)': null_percent})
    return missing_df[missing_df['Jumlah'] > 0]