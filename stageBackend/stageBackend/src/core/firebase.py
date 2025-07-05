import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("stage2025-51a1d-firebase-adminsdk-fbsvc-53ac8d354d.json")
firebase_admin.initialize_app(cred)

db = firestore.client()  # client Firestore
