# Dans utils/check_data.py
import pandas as pd
import os
from pathlib import Path

def check_poteaux_data(excel_path):
    """
    Vérifie la structure et la qualité des données du fichier Excel des poteaux
    """
    if not os.path.exists(excel_path):
        print(f"ERREUR: Le fichier {excel_path} n'existe pas")
        return False

    try:
        df = pd.read_excel(excel_path)
        print(f"Fichier chargé avec succès. {len(df)} lignes trouvées.")

        # Vérifier les colonnes
        required_columns = ["SUPPORT_X", "SUPPORT_Y", "SUPPORT_ID", "CAR_PHYSIQ"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            print(f"ERREUR: Colonnes manquantes: {missing_columns}")
            return False

        # Vérifier les coordonnées
        df['SUPPORT_X'] = df['SUPPORT_X'].astype(str).str.replace(',', '.').astype(float)
        df['SUPPORT_Y'] = df['SUPPORT_Y'].astype(str).str.replace(',', '.').astype(float)

        valid_coords = df[(df['SUPPORT_X'] != 0) & (df['SUPPORT_Y'] != 0)]
        print(f"Coordonnées valides: {len(valid_coords)} sur {len(df)} ({len(valid_coords)/len(df)*100:.2f}%)")

        # Vérifier les ID uniques
        unique_ids = df['SUPPORT_ID'].nunique()
        print(f"IDs uniques: {unique_ids} sur {len(df)} ({unique_ids/len(df)*100:.2f}%)")

        return True

    except Exception as e:
        print(f"ERREUR lors de la vérification du fichier: {str(e)}")
        return False

# Utilisation
if __name__ == "__main__":
    data_path = Path(__file__).parent.parent / "data" / "poteaux.xlsx"
    check_poteaux_data(data_path)
