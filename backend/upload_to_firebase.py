import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

df = pd.read_csv("dataset/blood_donors.csv")

for i, row in df.iterrows():
    db.collection("donors").add({
        "name": row["name"],
        "blood_group": row["blood_group"],
        "age": row["age"],
        "gender": row["gender"],
        "phone": row["phone"],
        "location": row["location"],
        "last_donation_date": row["last_donation_date"]
    })

print("DONE Uploaded!")
