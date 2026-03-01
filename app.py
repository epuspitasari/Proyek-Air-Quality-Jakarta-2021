import streamlit as st
import pandas as pd
import joblib
import os

# --- 1. KONFIGURASI & TAMPILAN ---
st.set_page_config(page_title="Sistem Monitoring ISPU", page_icon="🌿", layout="centered")

# Styling CSS 
st.markdown("""
    <style>
    /* Latar belakang aplikasi */
    .stApp { background-color: #f8fafc; }

    /* Membuat kursor tangan (pointer) pada area pilihan stasiun dan input angka */
    div[data-baseweb="select"], .stNumberInput div {
        cursor: pointer !important;
    }

    /* Styling Kotak Input */
    .stNumberInput div div { 
        background-color: white !important; 
        border-radius: 8px !important; 
        border: 1px solid #cbd5e0 !important; 
    }

    /* Styling Tombol Analisis */
    .stButton>button { 
        background-color: #1e293b; color: white; border-radius: 12px; 
        font-weight: bold; width: 100%; height: 3.5em; border: none;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        cursor: pointer !important;
    }
    .stButton>button:hover { 
        background-color: #334155; 
        transform: translateY(-2px); 
        transition: 0.2s; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: REFERENSI ---
with st.sidebar:
    st.title("📊 Referensi ISPU")
    st.write("Klasifikasi standar KLHK RI:")
    data_ref = {
        "Kategori": ["BAIK", "SEDANG", "TIDAK SEHAT"],
        "Indeks": ["0 - 50", "51 - 150", "> 150"],
        "Warna": ["🟢 Hijau", "🟡 Kuning", "🔴 Merah"]
    }
    st.table(pd.DataFrame(data_ref))
    st.info("Status akhir ditentukan oleh parameter dengan nilai indeks tertinggi.")

st.title("🌿 Monitoring Kualitas Udara")
st.write("Analisis data polutan udara secara presisi dan edukatif.")

# --- LOAD MODEL (Hanya jika file ada) ---
model_path = "models/model_final.pkl"
model = joblib.load(model_path) if os.path.exists(model_path) else None

# --- 2. INPUT DATA ---
st.markdown("### 📍 Lokasi & Parameter")
stasiun_pilihan = st.selectbox(
    "Pilih Stasiun Pengukuran:", 
    ["DKI1 (Pusat)", "DKI2 (Utara)", "DKI3 (Selatan)", "DKI4 (Timur)", "DKI5 (Barat)"]
)

col1, col2 = st.columns(2)
with col1:
    pm10 = st.number_input("PM10 (Partikel Debu)", value=0.0, step=0.1)
    pm25 = st.number_input("PM25 (Debu Halus)", value=0.0, step=0.1)
    so2 = st.number_input("SO2 (Sulfur Dioksida)", value=0.0, step=0.1)
with col2:
    co = st.number_input("CO (Karbon Monoksida)", value=0.0, step=0.1)
    o3 = st.number_input("O3 (Ozon)", value=0.0, step=0.1)
    no2 = st.number_input("NO2 (Nitrogen Dioksida)", value=0.0, step=0.1)

# --- 3. PROSES ANALISIS ---
if st.button("🚀 ANALISIS KUALITAS UDARA"):
    # VALIDASI ANTI-NEGATIF
    if any(x < 0 for x in [pm10, pm25, so2, co, o3, no2]):
        st.error("🚫 Kesalahan: Nilai polutan tidak boleh negatif. Silakan periksa kembali.")
    else:
        # Fungsi Logika Kategori & Status
        def cek_status(val, b1, b2):
            if val <= b1: return 1, "Aman"
            elif val <= b2: return 2, "Sedang"
            else: return 3, "Tidak Sehat"

        # Cek status per parameter
        s_pm10, t_pm10 = cek_status(pm10, 50, 150)
        s_pm25, t_pm25 = cek_status(pm25, 15, 55)
        s_so2, t_so2 = cek_status(so2, 52, 180)
        s_co, t_co = cek_status(co, 4000, 8000)
        s_o3, t_o3 = cek_status(o3, 120, 235)
        s_no2, t_no2 = cek_status(no2, 80, 200)

        # Menentukan level dominan (tertinggi)
        level_dominan = max(s_pm10, s_pm25, s_so2, s_co, s_o3, s_no2)
        
        mapping_hasil = {
            1: ("BAIK", "#22c55e", "Udara sangat bersih. Tidak ada risiko kesehatan bagi makhluk hidup."),
            2: ("SEDANG", "#eab308", "Kualitas udara dapat diterima. Waspada bagi kelompok yang sangat sensitif."),
            3: ("TIDAK SEHAT", "#ef4444", "Kualitas udara buruk. Berpotensi merugikan kesehatan manusia.")
        }
        
        rekomendasi_teks = {
            1: "🌟 **Saran:** Sangat baik untuk berolahraga di luar dan membuka semua ventilasi rumah.",
            2: "⚠️ **Saran:** Anak-anak dan lansia sebaiknya membatasi durasi aktivitas di luar ruangan.",
            3: "😷 **Saran:** Gunakan masker medis/N95, tutup jendela, dan hindari aktivitas berat di luar ruangan."
        }
        
        status, warna, msg = mapping_hasil[level_dominan]

        # TAMPILKAN HASIL UTAMA
        st.divider()
        st.write(f"**Laporan Stasiun:** {stasiun_pilihan}")
        st.markdown(f"""
            <div style="background-color:{warna}; padding:25px; border-radius:15px; text-align:center; color:white;">
                <h1 style="margin:0; font-size:40px;">{status}</h1>
                <p style="margin:5px 0 0 0; font-size:18px;">{msg}</p>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.info(rekomendasi_teks[level_dominan])

        # EDUKASI POLUTAN
        with st.expander("🔬 Info Detail Parameter Polutan"):
            st.markdown("""
            * **PM10/PM2.5:** Debu partikel halus hasil pembakaran atau debu jalanan.
            * **CO:** Gas beracun tak berbau hasil pembakaran kendaraan bermotor.
            * **SO2/NO2:** Gas asam hasil industri dan mesin suhu tinggi.
            * **O3:** Ozon permukaan yang memicu iritasi saluran pernapasan.
            """)

        # DATA TEKNIS (METRIK)
        st.write("### 📈 Detail Parameter & Status")
        m1, m2, m3 = st.columns(3)
        
        m1.metric("PM10", f"{pm10}", delta=t_pm10, delta_color="inverse" if s_pm10 > 1 else "normal")
        m1.metric("PM25", f"{pm25}", delta=t_pm25, delta_color="inverse" if s_pm25 > 1 else "normal")
        
        m2.metric("SO2", f"{so2}", delta=t_so2, delta_color="inverse" if s_so2 > 1 else "normal")
        m2.metric("CO", f"{co}", delta=t_co, delta_color="inverse" if s_co > 1 else "normal")
        
        m3.metric("O3", f"{o3}", delta=t_o3, delta_color="inverse" if s_o3 > 1 else "normal")
        m3.metric("NO2", f"{no2}", delta=t_no2, delta_color="inverse" if s_no2 > 1 else "normal")

        # PREDIKSI MACHINE LEARNING (OPSI)
        if model:
            try:
                kolom = model.feature_names_in_
                d_map = {'pm10': pm10, 'pm25': pm25, 'so2': so2, 'co': co, 'o3': o3, 'no2': no2}
                df_ml = pd.DataFrame([[d_map.get(c, 0.0) for c in kolom]], columns=kolom)
                pred_ml = model.predict(df_ml)[0]
                with st.expander("🔬 Prediksi Berbasis AI"):
                    st.write(f"Berdasarkan pola data historis, AI memprediksi: **{pred_ml}**")
            except:
                pass