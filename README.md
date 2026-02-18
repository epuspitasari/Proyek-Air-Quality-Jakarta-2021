# Air Quality Classification Project - Jakarta

Project ini bertujuan untuk memprediksi kategori kualitas udara di Jakarta menggunakan berbagai algoritma Machine Learning. Model terbaik yang dihasilkan mampu mengklasifikasikan kualitas udara menjadi **BAIK, SEDANG,** atau **TIDAK SEHAT** berdasarkan parameter polutan.

## Hasil Eksperimen
Berdasarkan benchmarking terhadap 7 model, **Decision Tree Classifier** terpilih sebagai model terbaik dengan performa:
- **Validation F1-Score:** 0.98
- **Test F1-Score:** 0.94
- **Status:** Produksi (Ready for Inference)



## Struktur Folder
- `config/`: File konfigurasi `.yaml` untuk pengaturan path dan parameter.
- `data/`:
    - `raw/`: Data asli dari sumber.
    - `processed/`: Data yang sudah siap untuk modeling (setelah scaling & encoding).
- `models/`: Menyimpan file biner model (`.pkl`), scaler, dan label encoder.
- `notebooks/`: File Jupyter Notebook untuk Eksplorasi (EDA) dan Modeling.
- `src/`: Script Python untuk otomasi pipeline data.

## Cara Penggunaan

1. **Siapkan Lingkungan Kerja (Install Library):**
   Ketik perintah ini di terminal untuk menginstal semua kebutuhan:
   ```bash
   pip install -r requirements.txt