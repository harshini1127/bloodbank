import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

df = pd.read_csv("dataset/blood_donors.csv")

for index, row in df.iterrows():

    donor_data = {
        "donor_id": row.get("Donor_ID"),
        "full_name": row.get("Full_Name"),
        "gender": row.get("Gender"),
        "age": int(row.get("Age")),
        "blood_group": row.get("Blood_Group"),
        "contact_num": row.get("Contact_Num") or row.get("Contact_Number") or row.get("Contact No") or row.get("Mobile") or row.get("Phone"),
        "email": row.get("Email")
    }

    db.collection("donors").add(donor_data)

print("DONE")
