import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import sys
import os

# Menambahkan folder src agar bisa memanggil utils
sys.path.append('src/')
import utils

def run_modeling(config):
    # 1. Load data belajar (Menggunakan path dari config['paths'])
    # Perhatikan: Sekarang kita pakai config['paths']['processed_dataset_dir']
    X_train = utils.pickle_load(os.path.join(config['paths']['processed_dataset_dir'], "X_train_final.pkl"))
    y_train = utils.pickle_load(os.path.join(config['paths']['processed_dataset_dir'], "y_train_final.pkl"))
    
    # 2. Inisialisasi Model (Random Forest)
    # Parameternya sekarang ada di dalam config['params']
    print("Sedang melatih model...")
    rf = RandomForestClassifier(
        n_estimators=config['params']['n_estimators'],
        random_state=config['params']['random_state']
    )
    
    # 3. Training
    rf.fit(X_train, y_train)
    
    return rf

if __name__ == "__main__":
    # 1. Load config
    config = utils.load_config("config/config.yaml")
    
    # 2. Jalankan modeling
    model = run_modeling(config)
    
    # 3. Simpan modelnya ke folder models/
    # Path simpan juga diambil dari config['paths']
    utils.pickle_dump(model, config['paths']['model_path'])
    
    print(f"Selesai! Model berhasil dilatih dan disimpan di: {config['paths']['model_path']}")