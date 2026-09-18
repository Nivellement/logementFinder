# handler.py
import re
import json
import lbc
from typing import Dict, Any, Optional
from geolocalisation import calculer_distance_utc
from base_donnees import sauvegarder_annonce
from extraction_ai import analyser_description_ollama

def extraire_attributs_officiels(ad: lbc.Ad) -> Dict[str, Any]:
    """
    Extrait de manière ultra-robuste les caractéristiques officielles structurées 
    fournies directement par l'API Leboncoin (ad.attributes, ad.square, etc.).
    """
    resultats = {
        "surface": getattr(ad, "square", None),
        "pieces": getattr(ad, "rooms", None),
        "chambres": getattr(ad, "bedrooms", None),
        "meuble": None,
        "etage": None,
        "salles_d_eau": 1,
        "caracteristiques_officielles": []
    }

    if hasattr(ad, "attributes") and ad.attributes:
        for attr in ad.attributes:
            if isinstance(attr, dict):
                key = attr.get("key") or attr.get("name")
                val = attr.get("value")
                val_label = attr.get("value_label") or attr.get("libelle") or val
                
                # 1. Type d'ameublement (Meublé / Non meublé)
                if key == "furnishing":
                    if val_label:
                        resultats["meuble"] = ("meublé" in str(val_label).lower()) and ("non" not in str(val_label).lower())
                
                # 2. Étage
                elif key in ["floor_number", "floor"]:
                    try:
                        resultats["etage"] = int(val)
                    except (TypeError, ValueError):
                        if val_label:
                            match_etage = re.search(r'\d+', str(val_label))
                            if match_etage:
                                resultats["etage"] = int(match_etage.group(0))
                            elif "rez" in str(val_label).lower() or "rdc" in str(val_label).lower():
                                resultats["etage"] = 0

                # 3. Salles d'eau
                elif key == "nb_shower_room":
                    try:
                        resultats["salles_d_eau"] = int(val)
                    except:
                        pass

                # 4. Surface de secours si non trouvée au niveau racine
                elif key == "square" and not resultats["surface"]:
                    try:
                        resultats["surface"] = float(val)
                    except:
                        pass

                # Stockage de tous les labels officiels (ex: Cave, Parking, Balcon, etc.)
                if val_label:
                    resultats["caracteristiques_officielles"].append(str(val_label))

    # Fallback surface par regex dans la description si toujours introuvable
    if not resultats["surface"]:
        desc = getattr(ad, "body", "") or getattr(ad, "description", "") or ""
        texte_global = f"{getattr(ad, 'subject', '')} {desc}"
        match = re.search(r'(\d+(?:[,\.]\d+)?)\s*m[²2]', texte_global, re.IGNORECASE)
        if match:
            try:
                resultats["surface"] = float(match.group(1).replace(',', '.'))
            except:
                resultats["surface"] = 0.0

    return resultats

def nettoyer_et_normaliser_annonce(ad: lbc.Ad) -> Optional[Dict[str, Any]]:
    """Transforme un objet lbc.Ad brut en un JSON standardisé complet et fiable."""
    url = getattr(ad, "url", "")
    if "ventes_immobilieres" in url:
        return None

    # 1. Extraction officielle et structurée (100% fiable)
    infos_officielles = extraire_attributs_officiels(ad)

    # 2. Analyse IA pour le texte non structuré (charges, équipements spécifiques)
    description = getattr(ad, "body", "") or getattr(ad, "description", "") or ""
    texte_complet = f"Caractéristiques officielles : {', '.join(infos_officielles['caracteristiques_officielles'])}\n\nDescription : {description}"
    infos_ia = analyser_description_ollama(texte_complet)

    # Fusion intelligente : La donnée officielle l'emporte toujours sur l'IA si elle existe
    meuble_final = infos_officielles["meuble"] if infos_officielles["meuble"] is not None else infos_ia.get("meuble", False)
    
    prix = float(ad.price) if ad.price else 0.0
    distance_utc = calculer_distance_utc(ad)

    return {
        "id": str(ad.id),
        "titre": ad.subject,
        "url": url,
        "financier": {
            "prix_total": prix,
            "surface": infos_officielles["surface"] or 0.0,
            "salles_d_eau": infos_officielles["salles_d_eau"],
            "pieces": infos_officielles["pieces"],
            "chambres": infos_officielles["chambres"]
        },
        "geographie": {
            "distance_utc": distance_utc,
            "etage": infos_officielles["etage"],
            "tags_officiels": infos_officielles["caracteristiques_officielles"]
        },
        "equipements": {
            "meuble": meuble_final,
            "lave_linge": infos_ia.get("lave_linge", False),
            "lave_vaisselle": infos_ia.get("lave_vaisselle", False),
            "seche_linge": infos_ia.get("seche_linge", False),
            "four": infos_ia.get("four", False)
        },
        "charges_incluses": {
            "eau_froide": infos_ia.get("eau_froide", False),
            "eau_chaude": infos_ia.get("eau_chaude", False),
            "electricite": infos_ia.get("electricite", False),
            "chauffage": infos_ia.get("chauffage", False),
            "internet": infos_ia.get("internet", False),
            "ordures_menageres": infos_ia.get("ordures_menageres", False)
        }
    }

def handle(ad: lbc.Ad, search_name: str) -> None:
    """Filtre les ventes, normalise l'annonce de location et l'enregistre en base."""
    url = getattr(ad, "url", "")
    print(f"[{search_name}] 🔍 Annonce brute détectée - URL : {url}")

    json_annonce = nettoyer_et_normaliser_annonce(ad)
    
    if json_annonce is None:
        print(f"[{search_name}] ⚠️ Annonce ignorée (écartée car identifiée comme une vente immobilière).")
        print("-" * 50)
        return

    print(f"[{search_name}] 🏠 Location validée et normalisée (ID: {ad.id})")
    sauvegarder_annonce(json_annonce)
    
    print(json.dumps(json_annonce, indent=4, ensure_ascii=False))
    print("-" * 50)