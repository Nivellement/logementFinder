# searcher.py
import json
import os
from typing import List
import lbc
from model import Search

DATA_DIR = "data"
IDS_FILE = os.path.join(DATA_DIR, "id.json")

class Searcher:
    def __init__(self, searches: List[Search]):
        self.searches = searches
        os.makedirs(DATA_DIR, exist_ok=True)
        self.seen_ids = self._load_seen_ids()

    def _load_seen_ids(self) -> List[str]:
        if os.path.exists(IDS_FILE):
            try:
                with open(IDS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_seen_ids(self):
        try:
            with open(IDS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.seen_ids[-2000:], f)  # Conserve les 2000 derniers IDs
        except Exception as e:
            print(f"⚠️ Erreur lors de la sauvegarde des IDs : {e}")

    def run_single_scan(self):
        """Exécute un unique scan pour chaque recherche configurée puis s'arrête."""
        for search in self.searches:
            print(f"[*] Lancement du scan unique : '{search.name}'")
            try:
                # Initialisation du client lbc avec prise en compte du proxy éventuel
                client = lbc.Client(proxy=search.proxy)
                
                params_dict = {}
                p = search.parameters
                if p.text:
                    params_dict["text"] = p.text
                if p.locations:
                    params_dict["locations"] = p.locations
                if p.category:
                    params_dict["category"] = p.category
                if p.real_estate_type is not None:
                    params_dict["real_estate_type"] = p.real_estate_type
                if p.square:
                    params_dict["square"] = p.square
                if p.price:
                    params_dict["price"] = p.price

                result = client.search(**params_dict)
                ads = result.ads if hasattr(result, "ads") else result
                
                new_ads = []
                for ad in ads:
                    if str(ad.id) not in self.seen_ids:
                        new_ads.append(ad)
                        self.seen_ids.append(str(ad.id))

                if new_ads:
                    self._save_seen_ids()
                    print(f"[+] {len(new_ads)} nouvelle(s) annonce(s) détectée(s) pour '{search.name}'.")
                    for ad in reversed(new_ads):
                        try:
                            search.handler(ad, search.name)
                        except Exception as e:
                            print(f"⚠️ Erreur dans le handler pour '{search.name}': {e}")
                else:
                    print(f"[-] Aucune nouvelle annonce par rapport au dernier scan.")

            except Exception as e:
                print(f"[!] Erreur lors de la recherche '{search.name}' : {e}")