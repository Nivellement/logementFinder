# handler.py
import lbc

def handle(ad: lbc.Ad, search_name: str) -> None:
    """
    Fonction déclenchée pour chaque annonce inédite découverte lors du scan.
    """
    print(f"[{search_name}] 🏠 Nouvelle annonce détectée !")
    print(f"  - Titre : {ad.subject}")
    print(f"  - Prix  : {ad.price} €" if ad.price else "  - Prix : Non spécifié")
    
    # Récupération des informations clés directement sur l'objet si elles existent
    surface = getattr(ad, "square", "Non spécifiée")
    pieces = getattr(ad, "rooms", "Non spécifiées")
    print(f"  - Surface : {surface} m² | Pièces : {pieces}")

    # Inspection approfondie des attributs (charges, équipements, etc.)
    if hasattr(ad, "attributes") and ad.attributes:
        print("  - Caractéristiques détaillées :")
        for attr in ad.attributes:
            if isinstance(attr, dict):
                # Si c'est un dictionnaire classique
                key = attr.get("key") or attr.get("name") or attr.get("label")
                value = attr.get("value") or attr.get("libelle")
                print(f"    * {key} : {value}")
            elif isinstance(attr, str):
                # Si l'attribut est juste une chaîne (ex: 'elevator', 'annual_charges'), 
                # on va chercher sa valeur directement sur l'objet 'ad'
                valeur_reelle = getattr(ad, attr, "Non renseigné")
                print(f"    * {attr} : {valeur_reelle}")
            else:
                print(f"    * {str(attr)}")
            
    print(f"  - URL   : {ad.url}")
    print("-" * 50)