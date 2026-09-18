# extraction_ai.py
import ollama
import json
from typing import Dict, Any

def analyser_description_ollama(description: str) -> Dict[str, Any]:
    """
    Utilise un modèle Ollama local avancé (Qwen 2.5) pour extraire les équipements 
    et charges d'une description immobilière sous forme de JSON strict.
    """
    prompt = f"""
    Analyse avec attention cette annonce immobilière. Sois intelligent dans tes déductions :
    
    Règles d'analyse :
    - "meuble": true si le logement est loué meublé.
    - "lave_linge": true si un lave-linge ou une machine à laver est explicitement mentionné.
    - "lave_vaisselle": true si un lave-vaisselle est explicitement mentionné.
    - "seche_linge": true si un sèche-linge est explicitement mentionné.
    - "four": true si le texte mentionne un "four", ou si la mention "cuisine équipée" / "cuisine aménagée" est présente (ce qui implique généralement un four/plaques).
    - "eau_froide": true si l'eau froide est comprise dans les charges.
    - "eau_chaude": true si l'eau chaude est comprise.
    - "electricite": true si l'électricité est comprise.
    - "chauffage": true si le chauffage est compris.
    - "internet": true si internet / wifi / fibre est compris.
    - "ordures_menageres": true si la taxe d'ordures ménagères est comprise.

    Texte de l'annonce :
    """ + description

    try:
        response = ollama.chat(
            model='qwen2.5', 
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.0},
            format='json'
        )
        
        return json.loads(response['message']['content'])
        
    except Exception as e:
        print(f"⚠️ Erreur lors de l'appel à Ollama : gros plan sur {e}")
        return {}