# config/__init__.py
import lbc
from model import Parameters, Search
from handler import handle

# Définition de la zone géographique (Compiègne, rayon 5km)
localisation_compiegne = lbc.City(
    lat=49.4179,
    lng=2.8261,
    radius=5_000,
    city="Compiègne",
)

# -------------------------------------------------------------------------
# CONFIGURATION DU PROXY (Optionnel mais recommandé si bloqué par DataDome)
# -------------------------------------------------------------------------
# Remplacez les valeurs ci-dessous par les identifiants de votre fournisseur de proxy.
# Si vous n'utilisez pas de proxy, laissez 'proxy_config = None'.
proxy_config = None
# Exemple d'activation :
# proxy_config = lbc.Proxy(
#     host="votre_adresse_ip_proxy",
#     port=1234,
#     username="votre_utilisateur",
#     password="votre_mot_de_passe"
# )

CONFIG = [
    Search(
        name="Appartement Compiègne",
        parameters=Parameters(
            locations=[localisation_compiegne],
            category=lbc.Category.IMMOBILIER,
            real_estate_type=["2", "2"],  # Format requis par l'API lbc
        ),
        handler=handle,
        proxy=proxy_config,  # Injection du proxy ici
    )
]