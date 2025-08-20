from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from pytorch_tabnet.tab_model import TabNetClassifier
from load_preprocessing_artifacts import load_preprocessing_artifacts
import random
import requests
import random
from flask_cors import CORS

# --------------------------
# Flask App
# --------------------------
app = Flask(__name__)
CORS(app)  # Επιτρέπει την πρόσβαση από το Svelte front-end

# ----------------------------
# Φόρτωση μοντέλου & artifacts
# ----------------------------
model = TabNetClassifier()
model.load_model("tabnet_best_model.zip")
encoders, target_encoder, categorical_columns, feature_columns, cat_idxs, cat_dims = load_preprocessing_artifacts()

# -----------------------------------
# Εκτύπωση: Class indices και labels
# -----------------------------------
print("Αντιστοίχιση class index => label:")
for i, class_label in enumerate(target_encoder.classes_):
    print(f"  Index {i}: '{class_label}'")




#-------------------------------------------------------------------------------------
# Dummy data for testing
# Εδώ είναι τα IPs που θα χρησιμοποιηθούν για τις επιθέσεις
# Αυτά τα IPs θα χρησιμοποιηθούν για να δημιουργήσουν τις επιθέσεις
# Είναι σχετικά λίγα για να μην γεμίζει η οθόνη με πολλές επιθέσεις
# Σε πραγματική εφαρμογή, θα χρησιμοποιούσαμε IPs από το δίκτυο
# και θα τα συνδυάζαμε με τα IPs της εταιρείας για να δημιουργήσουμε τις επιθέσεις
#-------------------------------------------------------------------------------------

# network - client IP's
network_ips = ['184.54.50.126','132.142.32.4','193.100.7.45','203.180.175.248','221.174.27.26','185.92.125.50','162.23.67.20','46.173.65.75','76.106.249.139','96.153.181.142',
               '184.54.30.126','132.142.35.6','193.100.10.43','203.180.175.28','221.174.26.27','185.92.125.53','162.23.63.22','46.173.62.77','76.106.335.130','96.153.180.123']
# Company's IP's
company_ips = ['190.100.100.1','190.100.100.2','190.100.100.3','190.100.100.4']
input_csv = "UNSW_NB15_testing-set.csv"
#features = [...]  # same as στον προηγούμενο σου κώδικα

exclude_cols = ['id', 'ï»¿id', 'label', 'attack_cat']  # columns to exclude

df = pd.read_csv(input_csv)
features = [col for col in df.columns if col not in exclude_cols]
df = df.sample(n=5000, random_state=42).reset_index(drop=True)





# --------------------------
# API route
# --------------------------


#----------------------------------------------------------------------------------------------------------------------------
# Αυτό το api θα το χρησιμοποιούμε για να κάνουμε προβλέψεις
# θα δέχεται δεδομένα από τον χρήστη, θα τα επεξεργάζεται και θα επιστρέφει την πρόβλεψη
# Η πρόβλεψη θα είναι η κλάση της επίθεσης (π.χ. 'DoS', 'Normal', κλπ.)
#----------------------------------------------------------------------------------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Λήψη δεδομένων από χρήστη
        data = request.get_json()
        df = pd.DataFrame([data])

        # Check: περιλαμβάνονται όλα τα απαραίτητα features;
        missing = set(feature_columns) - set(df.columns)
        if missing:
            return jsonify({"error": f"Missing features: {list(missing)}"}), 400

        # Ταξινόμηση στη σωστή σειρά
        df = df[feature_columns]

        # Encoding κατηγορικών
        for col in categorical_columns:
            df[col] = df[col].astype(str)
            df[col] = encoders[col].transform(df[col])

        # Μετατροπή σε πίνακα
        input_np = df.values

        # Πρόβλεψη
        pred_class_index = int(model.predict(input_np)[0])
        pred_class_label = target_encoder.inverse_transform([pred_class_index])[0]
        pred_proba = model.predict_proba(input_np)[0].tolist()

        # format pred_probal to 3 decimal places
        pred_proba = [round(p, 3) for p in pred_proba]

        return jsonify({
            "predicted_class_index": pred_class_index,
            "predicted_label": pred_class_label,
            "probabilities": pred_proba
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#----------------------------------------------------------------------------------------------------------------------------
# Αυτό το api θα στέλνει ένα δείγμα επίθεσης
# Θα επιλέγει τυχαία μια γραμμή από το df και θα την στέλνει στο /predict
# Θα επιστρέφει το αποτέλεσμα της πρόβλεψης μαζί με τα IPs                  
# Να σημειωθεί ότι το df έχει ήδη φορτωθεί και περιέχει τα δεδομένα των επιθέσεων αλλά δεν έχει τις στήλες srcIP και dstIP
# Αυτές οι στήλες θα προστεθούν απο εμάς με random επιλογή από τα network_ips και company_ips
# Το αποτέλεσμα θα είναι ένα JSON με τα πεδία srcIP, dstIP, type και confidence
#----------------------------------------------------------------------------------------------------------------------------
@app.route('/sample', methods=['GET'])
def send_attack_sample():
    row = df.sample(n=1).iloc[0]
    json_obj = row.to_dict()

    # handle missing values
    for k, v in json_obj.items():
        if pd.isna(v):
            json_obj[k] = None

    response = requests.post("http://127.0.0.1:5000/predict", json=json_obj)
    res_json = response.json()

    return jsonify({
        "srcIP": random.choice(network_ips),
        "dstIP": random.choice(company_ips),
        "type": res_json.get("predicted_label", "Unknown"),
        "confidence": max(res_json.get("probabilities", [0.0])),
    })





# --------------------------
# Εκκίνηση server
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)
