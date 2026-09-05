# main.py
from searcher import Searcher
from config import CONFIG

def main() -> None:
    print("🚀 Démarrage du scan unique de veille immobilière...")
    searcher = Searcher(searches=CONFIG)
    searcher.run_single_scan()
    print("✅ Scan terminé avec succès.")

if __name__ == "__main__":
    main()