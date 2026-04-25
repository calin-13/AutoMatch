import joblib
import numpy as np
import os

_regressor = None
_classifier = None
_features = None
_explainer = None
_loaded = False


def _load_models():
    global _regressor, _classifier, _features, _explainer, _loaded
    if _loaded:
        return

    ml_dir = os.path.join(os.path.dirname(__file__), "..", "ml")

    reg_path = os.path.join(ml_dir, "best_regressor.joblib")
    clf_path = os.path.join(ml_dir, "best_classifier.joblib")
    feat_path = os.path.join(ml_dir, "features.joblib")

    if not os.path.exists(reg_path):
        reg_path = os.path.join(ml_dir, "rf_regressor.joblib")
    if not os.path.exists(clf_path):
        clf_path = os.path.join(ml_dir, "rf_classifier.joblib")

    if not all(os.path.exists(p) for p in [reg_path, clf_path, feat_path]):
        print("ML models not found. Using rule-based scoring only.")
        return

    _regressor = joblib.load(reg_path)
    _classifier = joblib.load(clf_path)
    _features = joblib.load(feat_path)

    try:
        import shap
        _explainer = shap.TreeExplainer(_regressor)
        print(f"ML models loaded from {os.path.basename(reg_path)} / {os.path.basename(clf_path)}.")
        print("SHAP explainer initialized.")
    except Exception as e:
        print(f"SHAP explainer failed to initialize: {e}")
        _explainer = None

    _loaded = True


def is_available():
    _load_models()
    return _loaded and _regressor is not None


def _build_features(profile, car, budget, km_zi):
    return {
        "pref_comfort": profile.comfort,
        "pref_sport": profile.sport,
        "pref_siguranta": profile.siguranta,
        "pref_economie": profile.economie,
        "pref_estetica": profile.estetica,
        "budget": budget,
        "km_zi": km_zi,
        "car_pret": car.pret,
        "car_putere_cp": car.putere_cp or 0,
        "car_consum_mediu": car.consum_mediu or 0,
        "car_emisii_co2": car.emisii_co2 or 0,
        "car_volum_portbagaj": car.volum_portbagaj or 0,
        "car_numar_locuri": car.numar_locuri or 5,
        "car_rating_siguranta": car.rating_siguranta or 0,
        "car_rating_comfort": car.rating_comfort or 0,
        "car_rating_sport": car.rating_sport or 0,
        "car_rating_economie": car.rating_economie or 0,
        "car_rating_estetica": car.rating_estetica or 0,
        "car_is_electric": 1 if car.tip_combustibil == "electric" else 0,
        "car_is_hybrid": 1 if car.tip_combustibil == "hybrid" else 0,
        "car_is_suv": 1 if car.tip_caroserie == "suv" else 0,
        "car_is_coupe": 1 if car.tip_caroserie == "coupe" else 0,
        "car_is_sedan": 1 if car.tip_caroserie == "sedan" else 0,
        "price_ratio": round(car.pret / budget if budget > 0 else 1, 3),
    }


def predict_score(profile, car, budget, km_zi):
    if not is_available():
        return None

    features = _build_features(profile, car, budget, km_zi)
    X = np.array([[features[f] for f in _features]])
    score = float(_regressor.predict(X)[0])
    label = int(_classifier.predict(X)[0])

    return {"score": round(np.clip(score, 0, 100), 1), "label": label}


def explain_prediction(profile, car, budget, km_zi, top_n=5):
    if not is_available() or _explainer is None:
        return None

    features = _build_features(profile, car, budget, km_zi)
    X = np.array([[features[f] for f in _features]])

    try:
        shap_values = _explainer.shap_values(X)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        shap_array = shap_values[0]

        base_value = _explainer.expected_value
        if isinstance(base_value, np.ndarray):
            base_value = float(base_value[0])
        else:
            base_value = float(base_value)

        explanations = []
        for i, feat in enumerate(_features):
            explanations.append({
                "feature": feat,
                "value": round(float(features[feat]), 2),
                "shap_value": round(float(shap_array[i]), 3),
                "impact": "positive" if shap_array[i] >= 0 else "negative",
            })

        explanations.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

        return {
            "base_value": round(base_value, 2),
            "top_features": explanations[:top_n],
        }
    except Exception as e:
        print(f"SHAP explanation failed: {e}")
        return None
