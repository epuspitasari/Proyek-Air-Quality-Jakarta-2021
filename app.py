import streamlit as st
import pandas as pd
import joblib
import os

# --- 1. KONFIGURASI & TAMPILAN ---
st.set_page_config(page_title="ISPU Predictor", page_icon="🌿")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #e0f7fa 0%, #e8f5e9 100%); }
    .stNumberInput div div { background-color: white !important; border-radius: 8px !important; }
    .stButton>button { 
        background-color: #2e7d32; color: white; border-radius: 10px; 
        font-weight: bold; width: 100%; height: 3em; border: none;
    }
    .stButton>button:hover { background-color: #1b5e20; color: white; }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Info Sistem")
    st.write("Standar ISPU: Batas limit angka masuk ke kategori sebelumnya.")
    st.info("Contoh: CO 8000 = SEDANG. 8001 = TIDAK SEHAT.")

st.title("🌿 ISPU Monitoring System")
st.write("Halo User! Masukkan nilai polutan untuk mengecek kualitas udara hari ini.")

# --- LOAD MODEL ---
model_path = "models/model_final.pkl"
if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    st.error("⚠️ Model tidak ditemukan!")

# --- 2. INPUT DATA ---
st.markdown("### 📊 Parameter Polutan")
col1, col2 = st.columns(2)

with col1:
    pm10 = st.number_input("PM10 µg/m³ (Baik: ≤50 | Sedang: ≤150)", value=0.0)
    pm25 = st.number_input("PM25 µg/m³ (Baik: ≤15 | Sedang: ≤55)", value=0.0)
    so2 = st.number_input("SO2 µg/m³ (Baik: ≤52 | Sedang: ≤180)", value=0.0)

with col2:
    co = st.number_input("CO µg/m³ (Baik: ≤4000 | Sedang: ≤8000)", value=0.0)
    o3 = st.number_input("O3 µg/m³ (Baik: ≤120 | Sedang: ≤235)", value=0.0)
    no2 = st.number_input("NO2 µg/m³ (Baik: ≤80 | Sedang: ≤200)", value=0.0)

# --- 3. PROSES PREDIKSI ---
if st.button("🚀 CEK KUALITAS SEKARANG"):
    # VALIDASI ANTI-NEGATIF
    if pm10 < 0 or pm25 < 0 or so2 < 0 or co < 0 or o3 < 0 or no2 < 0:
        st.error("🚫 ERROR: Masukkan angka 0 atau lebih!")
        st.stop() 

    kategori_list = []
    
    # Logika Penentuan Kategori
    # PM10
    if pm10 <= 50: kategori_list.append(1)
    elif pm10 <= 150: kategori_list.append(2)
    else: kategori_list.append(3)

    # PM25
    if pm25 <= 15: kategori_list.append(1)
    elif pm25 <= 55: kategori_list.append(2)
    else: kategori_list.append(3)

    # SO2
    if so2 <= 52: kategori_list.append(1)
    elif so2 <= 180: kategori_list.append(2)
    else: kategori_list.append(3)

    # CO
    if co <= 4000: kategori_list.append(1)
    elif co <= 8000: kategori_list.append(2)
    else: kategori_list.append(3)

    # O3
    if o3 <= 120: kategori_list.append(1)
    elif o3 <= 235: kategori_list.append(2)
    else: kategori_list.append(3)

    # NO2
    if no2 <= 80: kategori_list.append(1)
    elif no2 <= 200: kategori_list.append(2)
    else: kategori_list.append(3)

    terburuk = max(kategori_list)
    
    if terburuk == 1:
        status, warna, msg = "BAIK", "#28a745", "Kualitas udara sangat baik. Aman untuk beraktivitas luar ruangan."
        tips = "🌟 Nikmati udara segar! Ini waktu terbaik untuk berolahraga atau membuka ventilasi rumah."
    elif terburuk == 2:
        status, warna, msg = "SEDANG", "#ffc107", "Kualitas udara dapat diterima. Tetap waspada bagi yang sensitif."
        tips = "⚠️ Kelompok sensitif (lansia/anak-anak) sebaiknya kurangi aktivitas fisik berat yang terlalu lama di luar."
    else:
        status, warna, msg = "TIDAK SEHAT", "#dc3545", "Kualitas udara buruk. Gunakan pelindung jika keluar rumah!"
        tips = "😷 Gunakan masker medis/N95. Tutup jendela rumah dan kurangi aktivitas di luar ruangan sesedikit mungkin."

    # TAMPILKAN HASIL UTAMA
    st.divider()
    st.markdown(f"""
        <div style="background-color:{warna}; padding:25px; border-radius:12px; text-align:center; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
            <h1 style="color:white; margin:0;">{status}</h1>
            <p style="color:white; font-size:18px; margin:0; font-weight:bold;">{msg}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    st.info(f"💡 **Rekomendasi Kesehatan:** {tips}")
    
    # Progress Bar
    st.write("### 📈 Tingkat Keparahan Polutan")
    val_prog = {1: 0.33, 2: 0.66, 3: 1.0}
    st.progress(val_prog[terburuk])

    # --- DETAIL METRIK ---
    st.write("### 🔍 Detail Analisis per Parameter")
    m_col1, m_col2, m_col3 = st.columns(3)
    
    with m_col1:
        st.metric("PM10", f"{pm10}", delta="Aman" if pm10 <= 50 else "Tinggi", delta_color="inverse")
        st.metric("PM25", f"{pm25}", delta="Aman" if pm25 <= 15 else "Tinggi", delta_color="inverse")
    
    with m_col2:
        st.metric("SO2", f"{so2}", delta="Aman" if so2 <= 52 else "Tinggi", delta_color="inverse")
        st.metric("CO", f"{co}", delta="Aman" if co <= 4000 else "Tinggi", delta_color="inverse")
        
    with m_col3:
        st.metric("O3", f"{o3}", delta="Aman" if o3 <= 120 else "Tinggi", delta_color="inverse")
        st.metric("NO2", f"{no2}", delta="Aman" if no2 <= 80 else "Tinggi", delta_color="inverse")

    # --- DETAIL MACHINE LEARNING (DI DALAM EXPANDER) ---
    try:
        mapping = {'pm10':pm10, 'pm25':pm25, 'so2':so2, 'co':co, 'o3':o3, 'no2':no2}
        df_input = pd.DataFrame([[mapping.get(c, 0.0) for c in model.feature_names_in_]], columns=model.feature_names_in_)
        pred_ml = model.predict(df_input)[0]
        
        st.write("")
        with st.expander("🔬 Lihat Detail Analisis Machine Learning"):
            st.write(f"Model Machine Learning memprediksi kategori: **{pred_ml}**")
            st.caption("Analisis ini berdasarkan pola data historis yang dipelajari oleh model AI.")
    except: 
        pass