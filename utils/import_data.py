# Dans PotElec/import_data.py
import pandas as pd
import os
from sqlalchemy import create_engine, text
from pathlib import Path

# Configuration de la base de données
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "seeg_poles"

# URI de connexion à la base de données
DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def import_poteaux_data(excel_path):
    """
    Importe les données des poteaux depuis un fichier Excel vers PostgreSQL
    """
    print(f"Tentative d'importation des données depuis {excel_path}")

    if not os.path.exists(excel_path):
        print(f"ERREUR: Le fichier {excel_path} n'existe pas")
        return False

    try:
        # Lire le fichier Excel
        df = pd.read_excel(excel_path)
        print(f"Fichier Excel chargé avec succès. {len(df)} lignes trouvées.")

        # Convertir les virgules en points pour les coordonnées
        df['SUPPORT_X'] = df['SUPPORT_X'].astype(str).str.replace(',', '.').astype(float)
        df['SUPPORT_Y'] = df['SUPPORT_Y'].astype(str).str.replace(',', '.').astype(float)

        # Filtrer les données avec des coordonnées valides
        df_valid = df[(df['SUPPORT_X'] != 0) & (df['SUPPORT_Y'] != 0)]
        print(f"Données filtrées: {len(df_valid)} sur {len(df)} poteaux ont des coordonnées valides")

        # Connexion à la base de données
        print("Connexion à PostgreSQL...")
        engine = create_engine(DATABASE_URI)

        # Créer la table
        print("Création de la table poteaux...")
        df_valid.to_sql('poteaux_temp', engine, if_exists='replace', index=False)

        # Ajouter la colonne géométrique
        print("Ajout de la colonne géométrique...")
        with engine.connect() as conn:
            # Créer une table avec structure complète et colonne géométrique
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS poteaux (
                    id SERIAL PRIMARY KEY,
                    FID INTEGER,
                    OBJECTID INTEGER,
                    EXPL_ID INTEGER,
                    POSTHTABT_ VARCHAR(255),
                    SUPPORT_ID VARCHAR(255),
                    SUPPORT_PL VARCHAR(255),
                    SUPPORT_NU VARCHAR(255),
                    SUPPORT__1 VARCHAR(255),
                    CAR_PHYSIQ VARCHAR(255),
                    SUPPORT_X FLOAT,
                    SUPPORT_Y FLOAT,
                    SUPPORT_SI VARCHAR(255),
                    QUARTIER_C VARCHAR(255),
                    SUPPORT_CH VARCHAR(255),
                    SUPPORT_DI VARCHAR(255),
                    STATUT_COD VARCHAR(255),
                    SUPPORT_DT VARCHAR(255),
                    SUPPORT__2 VARCHAR(255),
                    MODE_FINAN VARCHAR(255),
                    PROJET_ID VARCHAR(255),
                    USER_ID VARCHAR(255),
                    DT_CRE VARCHAR(255),
                    DT_MAJ VARCHAR(255),
                    PROJET_ID_ VARCHAR(255),
                    VILLE VARCHAR(255),
                    EXPLOIT VARCHAR(255),
                    geom geometry(Point, 4326)
                )
            """))

            # Vider la table si elle existe
            conn.execute(text("TRUNCATE TABLE poteaux"))

            # Insérer les données de la table temporaire dans la table définitive
            conn.execute(text("""
                INSERT INTO poteaux (
                    FID, OBJECTID, EXPL_ID, POSTHTABT_, SUPPORT_ID, SUPPORT_PL,
                    SUPPORT_NU, SUPPORT__1, CAR_PHYSIQ, SUPPORT_X, SUPPORT_Y,
                    SUPPORT_SI, QUARTIER_C, SUPPORT_CH, SUPPORT_DI, STATUT_COD,
                    SUPPORT_DT, SUPPORT__2, MODE_FINAN, PROJET_ID, USER_ID, DT_CRE,
                    DT_MAJ, PROJET_ID_, VILLE, EXPLOIT
                )
                SELECT 
                    FID, OBJECTID, EXPL_ID, "POSTHTABT_", SUPPORT_ID, SUPPORT_PL,
                    SUPPORT_NU, "SUPPORT__1", CAR_PHYSIQ, SUPPORT_X, SUPPORT_Y,
                    SUPPORT_SI, QUARTIER_C, SUPPORT_CH, SUPPORT_DI, STATUT_COD,
                    SUPPORT_DT, "SUPPORT__2", MODE_FINAN, PROJET_ID, USER_ID, DT_CRE,
                    DT_MAJ, "PROJET_ID_", VILLE, EXPLOIT
                FROM poteaux_temp
            """))

            # Mettre à jour la colonne géométrique
            conn.execute(text("""
                UPDATE poteaux
                SET geom = ST_SetSRID(ST_MakePoint(SUPPORT_X, SUPPORT_Y), 4326)
            """))

            # Créer un index spatial
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_poteaux_geom ON poteaux USING GIST(geom)"))

            # Supprimer la table temporaire
            conn.execute(text("DROP TABLE poteaux_temp"))

            conn.commit()

        print("Importation terminée avec succès!")

        # Vérifier le nombre de poteaux importés
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM poteaux")).fetchone()
            print(f"Nombre de poteaux importés dans la base de données: {result[0]}")

        return True

    except Exception as e:
        print(f"ERREUR lors de l'importation des données: {str(e)}")
        return False

# Si exécuté directement
if __name__ == "__main__":
    # Chemin vers votre fichier Excel des poteaux
    # Modifier ce chemin pour pointer vers votre fichier réel
    excel_path = "./data/poteaux.xlsx"
    import_poteaux_data(excel_path)
