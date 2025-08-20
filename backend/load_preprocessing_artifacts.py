import joblib
import os

def load_preprocessing_artifacts(path="artifacts"):
    """
    Φορτώνει όλα τα απαραίτητα αντικείμενα preprocessing για inference με TabNet.

    Επιστρέφει:
        encoders: dict με LabelEncoders για κατηγορικές μεταβλητές
        target_encoder: LabelEncoder για το target
        categorical_columns: λίστα κατηγορικών στηλών
        feature_columns: λίστα με τα ονόματα όλων των features (με τη σωστή σειρά)
        cat_idxs: λίστα index κατηγορικών στηλών
        cat_dims: λίστα με τα cardinalities (π.χ. len(le.classes_))
    """
    encoders = {}
    categorical_columns = joblib.load(os.path.join(path, "categorical_columns.pkl"))
    feature_columns = joblib.load(os.path.join(path, "feature_columns.pkl"))
    cat_idxs = joblib.load(os.path.join(path, "cat_idxs.pkl"))
    cat_dims = joblib.load(os.path.join(path, "cat_dims.pkl"))
    target_encoder = joblib.load(os.path.join(path, "target_encoder.pkl"))

    for col in categorical_columns:
        encoders[col] = joblib.load(os.path.join(path, f"{col}_encoder.pkl"))

    return encoders, target_encoder, categorical_columns, feature_columns, cat_idxs, cat_dims
