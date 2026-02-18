# Blok 1: Import & Tools
import pandas as pd
import joblib # Tambahkan ini agar aman
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler # 1. Tambah StandardScaler di sini
import sys
import os
import logging

# Agar bisa baca folder src
sys.path.append('src/')
import utils

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Blok 2: Fungsi Utama Preprocessing
def run_preprocessing(config):
    # 1. Load data dari folder interim
    path_data = os.path.join(config['interim_dataset_dir'], config['interim_filename'])
    df = joblib.load(path_data)
    logger.info(f"Data dimuat: {path_data}")

    # 2. Pembersihan Target
    target_col = config['label']
    df = df.dropna(subset=[target_col])
    df = df[df[target_col] != 'TIDAK ADA DATA']
    logger.info("Target dibersihkan.")

    # 3. Splitting Awal
    X = df.drop(columns=[target_col])
    y = df[target_col]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.2, random_state=config['seed'], stratify=y 
    )
    X_valid, X_test, y_valid, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=config['seed'], stratify=y_temp
    )

    # 4. Imputasi Mean
    for col in config['impute_mean']:
        mean_val = X_train[col].mean()
        X_train[col] = X_train[col].fillna(mean_val)
        X_valid[col] = X_valid[col].fillna(mean_val)
        X_test[col] = X_test[col].fillna(mean_val)
    logger.info("Imputasi Mean selesai.")

    # 5. Encoding Target
    le = LabelEncoder()
    y_train = le.fit_transform(y_train)
    y_valid = le.transform(y_valid)
    y_test = le.transform(y_test)
    
    # Simpan Label Encoder agar bisa balikkan angka ke teks nanti
    joblib.dump(le, "models/label_encoder.pkl")

    # 6. Feature Encoding
    def encode_features(df_input):
        df_res = df_input.drop(columns=['tanggal', 'max'], errors='ignore')
        return pd.get_dummies(df_res)

    X_train_final = encode_features(X_train)
    X_valid_final = encode_features(X_valid)
    X_test_final = encode_features(X_test)

    # Sinkronisasi kolom
    X_train_final, X_valid_final = X_train_final.align(X_valid_final, join='left', axis=1, fill_value=0)
    X_train_final, X_test_final = X_train_final.align(X_test_final, join='left', axis=1, fill_value=0)

    # --- 7. TAMBAHAN PROSES SCALING DI SINI ---
    logger.info("⚖️ Melakukan Scaling pada fitur numerik...")
    scaler = StandardScaler()
    
    # Fit & Transform Train
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train_final), 
                                  columns=X_train_final.columns, 
                                  index=X_train_final.index)
    # Transform Valid & Test
    X_valid_scaled = pd.DataFrame(scaler.transform(X_valid_final), 
                                  columns=X_valid_final.columns, 
                                  index=X_valid_final.index)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test_final), 
                                 columns=X_test_final.columns, 
                                 index=X_test_final.index)
    
    # Simpan Scaler untuk kebutuhan Deployment nanti
    joblib.dump(scaler, "models/scaler.pkl")
    logger.info("Scaler disimpan di folder models/")
    # ------------------------------------------
    
    return X_train_scaled, X_valid_scaled, X_test_scaled, y_train, y_valid, y_test

# Blok 3: Pintu Gerbang
if __name__ == "__main__":
    config = utils.load_config("config/config.yaml")
    
    # Ambil data hasil scaling
    X_train, X_valid, X_test, y_train, y_valid, y_test = run_preprocessing(config)
    
    target_dir = config['processed_dataset_dir']
    utils.serialize_data(X_train, target_dir, "X_train_final.pkl")
    utils.serialize_data(X_valid, target_dir, "X_valid_final.pkl")
    utils.serialize_data(X_test, target_dir, "X_test_final.pkl")
    utils.serialize_data(y_train, target_dir, "y_train_final.pkl")
    utils.serialize_data(y_valid, target_dir, "y_valid_final.pkl")
    utils.serialize_data(y_test, target_dir, "y_test_final.pkl")
    
    print("\n--- PREPROCESSING + SCALING SELESAI ---")
    print(f"Data tersimpan di: {target_dir}")