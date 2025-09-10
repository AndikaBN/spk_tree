
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import math
from collections import Counter

MODEL_DIR = Path(__file__).resolve().parent.parent / "media"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "decision_tree.pkl"

EXPECTED_COLS = ["NILAI KRITERIA", "Unnamed: 3", "Unnamed: 4", "Unnamed: 5", "Unnamed: 6", "JURUSAN"]

def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # If header row contains strings like 'NILAI MTK', drop it; detect by non-numeric in the numeric columns
    df = df.copy()
    # Drop rows fully NaN except 'JURUSAN'
    df = df.dropna(how="all")
    # Fill column names if not present as expected
    cols = df.columns.tolist()
    # Heuristic: when first row contains strings in numeric columns, drop first row
    if not pd.api.types.is_numeric_dtype(df.iloc[0, 2]) or isinstance(df.iloc[0, 2], str):
        df = df.iloc[1:].reset_index(drop=True)

    # Rename columns into canonical names
    # We expect order: [NO, NAMA, NILAI MTK, B.INDO, B.ING, IPA, MINAT, JURUSAN]
    mapper = {df.columns[2]: "nilai_mtk", df.columns[3]: "nilai_bindo", df.columns[4]: "nilai_bing",
              df.columns[5]: "nilai_ipa", df.columns[6]: "minat", df.columns[7]: "jurusan", df.columns[1]: "name"}
    df = df.rename(columns=mapper)
    # Keep only needed
    keep = ["name","nilai_mtk","nilai_bindo","nilai_bing","nilai_ipa","minat","jurusan"]
    df = df[keep]
    # Clean types
    for c in ["nilai_mtk","nilai_bindo","nilai_bing","nilai_ipa"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["minat"] = df["minat"].astype(str).str.strip()
    df["jurusan"] = df["jurusan"].astype(str).str.upper().str.replace("AKUTANSI","AKUNTANSI")
    df = df.dropna()
    return df

def train_from_excel(excel_path: Path):
    xls = pd.ExcelFile(excel_path)
    # Combine first two sheets (or specific names)
    dfs = []
    for sn in xls.sheet_names[:2]:
        df = pd.read_excel(excel_path, sheet_name=sn)
        dfs.append(_normalize_dataframe(df))
    data = pd.concat(dfs, ignore_index=True)
    # Preprocess: categorical 'minat'
    X = data[["nilai_mtk","nilai_bindo","nilai_bing","nilai_ipa","minat"]]
    y = data["jurusan"]

    categorical_features = ["minat"]
    numeric_features = ["nilai_mtk","nilai_bindo","nilai_bing","nilai_ipa"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", "passthrough", numeric_features),
        ]
    )

    clf = Pipeline(steps=[
        ("pre", preprocessor),
        ("dt", DecisionTreeClassifier(criterion="entropy", random_state=42, max_depth=5)),
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    clf.fit(X_train, y_train)
    y_pred = clf.predict_proba(X_test)
    preds = clf.predict(X_test)

    acc = accuracy_score(y_test, preds)
    report = classification_report(y_test, preds, zero_division=0)

    joblib.dump({"model": clf, "accuracy": acc, "report": report}, MODEL_PATH)
    return acc, report, MODEL_PATH

def load_or_train_default(excel_path: Path = None):
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    if excel_path is None or not Path(excel_path).exists():
        raise FileNotFoundError("Model belum dilatih dan dataset tidak tersedia.")
    acc, report, _ = train_from_excel(excel_path)
    return joblib.load(MODEL_PATH)

def predict_single(nilai_mtk: float, nilai_bindo: float, nilai_bing: float, nilai_ipa: float, minat: str):
    bundle = joblib.load(MODEL_PATH)
    clf = bundle["model"]
    X = pd.DataFrame([{
        "nilai_mtk": nilai_mtk,
        "nilai_bindo": nilai_bindo,
        "nilai_bing": nilai_bing,
        "nilai_ipa": nilai_ipa,
        "minat": minat
    }])

    proba = clf.predict_proba(X)[0]
    classes = list(clf.classes_)
    # Pick best
    idx = int(np.argmax(proba))
    return classes[idx], float(proba[idx]), dict(zip(classes, proba))

def calculate_entropy(labels):
    """Menghitung entropy dari sebuah list label"""
    if len(labels) == 0:
        return 0
    
    label_counts = Counter(labels)
    total = len(labels)
    entropy = 0
    
    for count in label_counts.values():
        if count > 0:
            probability = count / total
            entropy -= probability * math.log2(probability)
    
    return entropy

def calculate_information_gain(data, feature, target):
    """Menghitung information gain untuk sebuah feature"""
    total_entropy = calculate_entropy(data[target])
    
    # Hitung weighted entropy setelah split
    weighted_entropy = 0
    total_samples = len(data)
    
    for value in data[feature].unique():
        subset = data[data[feature] == value]
        subset_entropy = calculate_entropy(subset[target])
        weight = len(subset) / total_samples
        weighted_entropy += weight * subset_entropy
    
    return total_entropy - weighted_entropy

def get_calculation_details(nilai_mtk, nilai_bindo, nilai_bing, nilai_ipa, minat):
    """Mendapatkan detail perhitungan untuk input siswa tertentu"""
    if not MODEL_PATH.exists():
        return None
    
    # Load dataset untuk perhitungan
    dataset_path = MODEL_PATH.parent / "dataset.xlsx"
    if not dataset_path.exists():
        return None
    
    try:
        # Load dan normalize dataset
        xls = pd.ExcelFile(dataset_path)
        dfs = []
        for sn in xls.sheet_names[:2]:
            df = pd.read_excel(dataset_path, sheet_name=sn)
            dfs.append(_normalize_dataframe(df))
        data = pd.concat(dfs, ignore_index=True)
        
        # Hitung entropy total dataset
        total_entropy = calculate_entropy(data['jurusan'])
        
        # Hitung information gain untuk setiap feature
        features = ['nilai_mtk', 'nilai_bindo', 'nilai_bing', 'nilai_ipa', 'minat']
        info_gains = {}
        
        for feature in features:
            info_gains[feature] = calculate_information_gain(data, feature, 'jurusan')
        
        # Prediksi untuk data input
        prediction, probability, probabilities = predict_single(nilai_mtk, nilai_bindo, nilai_bing, nilai_ipa, minat)
        
        # Format probabilitas untuk template
        probabilities_detailed = {}
        for class_name, prob_value in probabilities.items():
            probabilities_detailed[class_name] = {
                'value': prob_value,
                'percent': round(prob_value * 100, 2)
            }
        
        # Format information gains untuk template
        info_gains_detailed = {}
        max_gain = max(info_gains.values()) if info_gains.values() else 1
        for feature, gain_value in info_gains.items():
            info_gains_detailed[feature] = {
                'value': gain_value,
                'percent': round((gain_value / max_gain) * 100, 2) if max_gain > 0 else 0
            }
        
        # Analisis data berdasarkan minat yang sama
        same_minat_data = data[data['minat'] == minat]
        minat_entropy = calculate_entropy(same_minat_data['jurusan']) if len(same_minat_data) > 0 else 0
        
        # Hitung statistik nilai
        input_scores = [nilai_mtk, nilai_bindo, nilai_bing, nilai_ipa]
        avg_score = sum(input_scores) / len(input_scores)
        
        return {
            'prediction': prediction,
            'probability': probability,
            'probability_percent': round(probability * 100, 2),
            'probabilities': probabilities,
            'probabilities_detailed': probabilities_detailed,
            'total_entropy': total_entropy,
            'information_gains': info_gains,
            'information_gains_detailed': info_gains_detailed,
            'minat_entropy': minat_entropy,
            'same_minat_count': len(same_minat_data),
            'total_data_count': len(data),
            'input_values': {
                'nilai_mtk': nilai_mtk,
                'nilai_bindo': nilai_bindo,
                'nilai_bing': nilai_bing,
                'nilai_ipa': nilai_ipa,
                'minat': minat,
                'avg_score': avg_score
            },
            'dataset_stats': {
                'akuntansi_count': len(data[data['jurusan'] == 'AKUNTANSI']),
                'perkantoran_count': len(data[data['jurusan'] == 'PERKANTORAN'])
            }
        }
    except Exception as e:
        return {'error': str(e)}
