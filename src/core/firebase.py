import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("stage2025-51a1d-firebase-adminsdk-fbsvc-75ceac9ce7.json")
firebase_admin.initialize_app(cred)

db = firestore.client()  # client Firestore
