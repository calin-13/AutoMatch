import pandas as pd
import numpy as np
import joblib
import json
import os
import time

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    mean_absolute_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor, XGBClassifier

df = pd.read_csv("ml/training_data.csv")
print(f"Total samples: {len(df)}")

FEATURES = [
    "pref_comfort", "pref_sport", "pref_siguranta", "pref_economie", "pref_estetica",
    "budget", "km_zi",
    "car_pret", "car_putere_cp", "car_consum_mediu", "car_emisii_co2",
    "car_volum_portbagaj", "car_numar_locuri",
    "car_rating_siguranta", "car_rating_comfort", "car_rating_sport",
    "car_rating_economie", "car_rating_estetica",
    "car_is_electric", "car_is_hybrid", "car_is_suv", "car_is_coupe", "car_is_sedan",
    "price_ratio",
]

X = df[FEATURES]
y_score = df["score"]
y_label = df["label"]

X_train, X_test, y_train_score, y_test_score, y_train_label, y_test_label = train_test_split(
    X, y_score, y_label, test_size=0.2, random_state=42
)

print(f"Train: {len(X_train)}, Test: {len(X_test)}")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
X_scaled_full = scaler.transform(X)

regressors = {
    "rf": {
        "name": "RandomForest",
        "model": RandomForestRegressor(
            n_estimators=200, max_depth=15, min_samples_split=5,
            min_samples_leaf=2, random_state=42, n_jobs=-1,
        ),
        "scaled": False,
    },
    "xgb": {
        "name": "XGBoost",
        "model": XGBRegressor(
            n_estimators=200, max_depth=8, learning_rate=0.1,
            random_state=42, n_jobs=-1,
        ),
        "scaled": False,
    },
    "knn": {
        "name": "KNN",
        "model": KNeighborsRegressor(n_neighbors=10, weights="distance", n_jobs=-1),
        "scaled": True,
    },
}

classifiers = {
    "rf": {
        "name": "RandomForest",
        "model": RandomForestClassifier(
            n_estimators=200, max_depth=15, min_samples_split=5,
            min_samples_leaf=2, random_state=42, n_jobs=-1,
        ),
        "scaled": False,
    },
    "xgb": {
        "name": "XGBoost",
        "model": XGBClassifier(
            n_estimators=200, max_depth=8, learning_rate=0.1,
            random_state=42, n_jobs=-1, eval_metric="mlogloss",
        ),
        "scaled": False,
    },
    "logreg": {
        "name": "LogisticRegression",
        "model": LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1),
        "scaled": True,
    },
}

print("\n" + "=" * 60)
print("REGRESSION COMPARISON (Score Prediction)")
print("=" * 60)

regression_results = {}

for key, cfg in regressors.items():
    model = cfg["model"]
    Xtr = X_train_scaled if cfg["scaled"] else X_train
    Xte = X_test_scaled if cfg["scaled"] else X_test
    Xfull = X_scaled_full if cfg["scaled"] else X

    t0 = time.time()
    model.fit(Xtr, y_train_score)
    train_time = time.time() - t0

    t0 = time.time()
    y_pred = model.predict(Xte)
    predict_time = time.time() - t0

    mae = mean_absolute_error(y_test_score, y_pred)
    r2 = r2_score(y_test_score, y_pred)
    cv_r2 = cross_val_score(model, Xfull, y_score, cv=5, scoring="r2")

    regression_results[cfg["name"]] = {
        "mae": round(mae, 2),
        "r2": round(r2, 4),
        "cv_r2_mean": round(cv_r2.mean(), 4),
        "cv_r2_std": round(cv_r2.std(), 4),
        "train_time_sec": round(train_time, 3),
        "predict_time_sec": round(predict_time, 4),
    }

    joblib.dump(model, f"ml/{key}_regressor.joblib")
    print(f"{cfg['name']:20s} MAE={mae:6.2f}  R2={r2:.4f}  CV_R2={cv_r2.mean():.4f} (+/- {cv_r2.std():.4f})")

rule_based_scores = []
for _, row in X_test.iterrows():
    rb = (
        row["car_rating_comfort"] * (row["pref_comfort"] / 100)
        + row["car_rating_sport"] * (row["pref_sport"] / 100)
        + row["car_rating_siguranta"] * (row["pref_siguranta"] / 100)
        + row["car_rating_economie"] * (row["pref_economie"] / 100)
        + row["car_rating_estetica"] * (row["pref_estetica"] / 100)
    )
    rule_based_scores.append((rb / 5.0) * 100)

rule_based_scores = np.array(rule_based_scores)
rb_mae = mean_absolute_error(y_test_score, rule_based_scores)
rb_r2 = r2_score(y_test_score, rule_based_scores)

regression_results["RuleBased"] = {
    "mae": round(rb_mae, 2),
    "r2": round(rb_r2, 4),
    "cv_r2_mean": None,
    "cv_r2_std": None,
    "train_time_sec": 0.0,
    "predict_time_sec": None,
}

print(f"{'RuleBased (baseline)':20s} MAE={rb_mae:6.2f}  R2={rb_r2:.4f}")

print("\n" + "=" * 60)
print("CLASSIFICATION COMPARISON (Recommendation Label)")
print("=" * 60)

classification_results = {}
label_names = ["Not Recommended", "Maybe", "Recommended"]

for key, cfg in classifiers.items():
    model = cfg["model"]
    Xtr = X_train_scaled if cfg["scaled"] else X_train
    Xte = X_test_scaled if cfg["scaled"] else X_test
    Xfull = X_scaled_full if cfg["scaled"] else X

    t0 = time.time()
    model.fit(Xtr, y_train_label)
    train_time = time.time() - t0

    t0 = time.time()
    y_pred = model.predict(Xte)
    predict_time = time.time() - t0

    acc = accuracy_score(y_test_label, y_pred)
    precision = precision_score(y_test_label, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_test_label, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test_label, y_pred, average="weighted", zero_division=0)
    cv_acc = cross_val_score(model, Xfull, y_label, cv=5, scoring="accuracy")
    cm = confusion_matrix(y_test_label, y_pred).tolist()

    classification_results[cfg["name"]] = {
        "accuracy": round(acc, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "cv_accuracy_mean": round(cv_acc.mean(), 4),
        "cv_accuracy_std": round(cv_acc.std(), 4),
        "train_time_sec": round(train_time, 3),
        "predict_time_sec": round(predict_time, 4),
        "confusion_matrix": cm,
    }

    joblib.dump(model, f"ml/{key}_classifier.joblib")
    print(f"{cfg['name']:20s} Acc={acc:.4f}  F1={f1:.4f}  CV_Acc={cv_acc.mean():.4f} (+/- {cv_acc.std():.4f})")

print("\n" + "=" * 60)
print("BEST MODEL SELECTION")
print("=" * 60)

ml_regression_results = {k: v for k, v in regression_results.items() if k != "RuleBased"}
best_reg_name = max(ml_regression_results, key=lambda k: ml_regression_results[k]["r2"])
best_clf_name = max(classification_results, key=lambda k: classification_results[k]["f1"])

name_to_key = {"RandomForest": "rf", "XGBoost": "xgb", "KNN": "knn", "LogisticRegression": "logreg"}
best_reg_key = name_to_key[best_reg_name]
best_clf_key = name_to_key[best_clf_name]

best_reg_model = joblib.load(f"ml/{best_reg_key}_regressor.joblib")
best_clf_model = joblib.load(f"ml/{best_clf_key}_classifier.joblib")

joblib.dump(best_reg_model, "ml/best_regressor.joblib")
joblib.dump(best_clf_model, "ml/best_classifier.joblib")

print(f"Best regressor:  {best_reg_name} (R2={regression_results[best_reg_name]['r2']})")
print(f"Best classifier: {best_clf_name} (F1={classification_results[best_clf_name]['f1']})")

feature_importance = {}
if hasattr(best_reg_model, "feature_importances_"):
    importances = best_reg_model.feature_importances_
    importance_df = pd.DataFrame({
        "feature": FEATURES,
        "importance": importances,
    }).sort_values("importance", ascending=False)
    feature_importance = {row["feature"]: round(row["importance"], 4) for _, row in importance_df.iterrows()}

    print("\n" + "=" * 60)
    print(f"FEATURE IMPORTANCE ({best_reg_name})")
    print("=" * 60)
    for _, row in importance_df.iterrows():
        bar = "#" * int(row["importance"] * 100)
        print(f"{row['feature']:30s} {row['importance']:.4f} {bar}")

joblib.dump(FEATURES, "ml/features.joblib")
joblib.dump(scaler, "ml/scaler.joblib")

metrics = {
    "dataset": {
        "total_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "num_features": len(FEATURES),
        "label_distribution": df["label"].value_counts().sort_index().to_dict(),
    },
    "regression_comparison": regression_results,
    "classification_comparison": classification_results,
    "best_models": {
        "regressor": best_reg_name,
        "classifier": best_clf_name,
    },
    "feature_importance_best_regressor": feature_importance,
}

with open("ml/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print("\nSaved to ml/:")
print("- rf_regressor.joblib, xgb_regressor.joblib, knn_regressor.joblib")
print("- rf_classifier.joblib, xgb_classifier.joblib, logreg_classifier.joblib")
print("- best_regressor.joblib, best_classifier.joblib")
print("- features.joblib, scaler.joblib, metrics.json")
