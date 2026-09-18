# base_donnees.py
import sqlite3
import json
import os
from typing import Dict, Any

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "logements.db")

def init_db() -> None:
    """Initialise la base de données SQLite et la table des annonces."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS annonces (
            id TEXT PRIMARY KEY,
            titre TEXT,
            url TEXT,
            prix_total REAL,
            surface REAL,
            salles_d_eau INTEGER,
            distance_utc REAL,
            donnees_json TEXT
        )
    ''')
    conn.commit()
    conn.close()

def annonce_existe(annonce_id: str) -> bool:
    """Vérifie si une annonce est déjà présente en base de données."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM annonces WHERE id = ?", (annonce_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def sauvegarder_annonce(annonce: Dict[str, Any]) -> None:
    """Enregistre ou met à jour un objet annonce normalisé dans SQLite."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO annonces (id, titre, url, prix_total, surface, salles_d_eau, distance_utc, donnees_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        annonce["id"],
        annonce["titre"],
        annonce["url"],
        annonce["financier"]["prix_total"],
        annonce["financier"]["surface"],
        annonce["financier"]["salles_d_eau"],
        annonce["geographie"]["distance_utc"],
        json.dumps(annonce, ensure_ascii=False)
    ))
    
    conn.commit()
    conn.close()