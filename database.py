import sqlite3
from datetime import datetime

DB_NAME = "hopitaux.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def initialiser_base():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS hopitaux (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            ville TEXT NOT NULL,
            type TEXT NOT NULL,
            adresse TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS avis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hopital_id INTEGER NOT NULL,
            nom_patient TEXT NOT NULL,
            note_soins INTEGER NOT NULL,
            note_hygiene INTEGER NOT NULL,
            note_accueil INTEGER NOT NULL,
            note_infrastructure INTEGER NOT NULL,
            commentaire TEXT,
            date_avis TEXT NOT NULL,
            FOREIGN KEY (hopital_id) REFERENCES hopitaux(id)
        )
    ''')

    hopitaux = [
        ("Hôpital Central de Yaoundé",       "Yaoundé", "Public",  "Rue Henri Dunant"),
        ("Hôpital Général de Yaoundé",        "Yaoundé", "Public",  "Avenue Charles de Gaulle"),
        ("CHU de Yaoundé",                    "Yaoundé", "Public",  "Rue Joseph Essono Balla"),
        ("Fondation Chantal Biya",            "Yaoundé", "Privé",   "Rue 1818, Melen"),
        ("Clinique Ngousso",                  "Yaoundé", "Privé",   "Quartier Ngousso"),
        ("Hôpital de District de Mbalmayo",   "Mbalmayo","Public",  "Centre-ville Mbalmayo"),
        ("Hôpital de District d'Obala",       "Obala",   "Public",  "Centre-ville Obala"),
        ("Hôpital de District d'Eseka",       "Eséka",   "Public",  "Centre-ville Eséka"),
        ("Clinique La Référence",             "Yaoundé", "Privé",   "Bastos, Yaoundé"),
        ("Hôpital de District de Bafia",      "Bafia",   "Public",  "Centre-ville Bafia"),
    ]

    c.execute("SELECT COUNT(*) FROM hopitaux")
    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO hopitaux (nom, ville, type, adresse) VALUES (?, ?, ?, ?)",
            hopitaux
        )

    conn.commit()
    conn.close()
    print("✅ Base de données initialisée avec succès !")

def get_tous_hopitaux():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM hopitaux ORDER BY nom")
    hopitaux = c.fetchall()
    conn.close()
    return hopitaux

def enregistrer_avis(hopital_id, nom_patient, note_soins, note_hygiene,
                     note_accueil, note_infrastructure, commentaire):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO avis (hopital_id, nom_patient, note_soins, note_hygiene,
                          note_accueil, note_infrastructure, commentaire, date_avis)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (hopital_id, nom_patient, note_soins, note_hygiene,
          note_accueil, note_infrastructure, commentaire,
          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_tous_avis():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT a.*, h.nom, h.ville, h.type
        FROM avis a
        JOIN hopitaux h ON a.hopital_id = h.id
        ORDER BY a.date_avis DESC
    ''')
    avis = c.fetchall()
    conn.close()
    return avis

if __name__ == "__main__":
    initialiser_base()