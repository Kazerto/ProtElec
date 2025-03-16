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

        # Afficher les colonnes du DataFrame
        print("Colonnes du DataFrame:", df.columns.tolist())

        # Renommer les colonnes pour éviter les problèmes de casse et de caractères spéciaux
        df.columns = [
            'fid', 'shape', 'objectid', 'expl_id', 'posthtabt', 'support_id', 'support_pl',
            'support_nu', 'support_1', 'car_physiq', 'support_x', 'support_y', 'support_si',
            'quartier_c', 'support_ch', 'support_di', 'statut_cod', 'support_dt', 'support_2',
            'mode_finan', 'projet_id', 'user_id', 'dt_cre', 'dt_maj', 'projet_id_', 'ville', 'exploit'
        ]

        # Convertir les virgules en points pour les coordonnées
        df['support_x'] = df['support_x'].astype(str).str.replace(',', '.').astype(float)
        df['support_y'] = df['support_y'].astype(str).str.replace(',', '.').astype(float)

        # Filtrer les données avec des coordonnées valides
        df_valid = df[(df['support_x'] != 0) & (df['support_y'] != 0)]
        print(f"Données filtrées: {len(df_valid)} sur {len(df)} poteaux ont des coordonnées valides")

        # Connexion à la base de données
        print("Connexion à PostgreSQL...")
        engine = create_engine(DATABASE_URI)

        # Créer la table temporaire
        print("Création de la table temporaire poteaux_temp...")
        df_valid.to_sql('poteaux_temp', engine, if_exists='replace', index=False)

        # Créer la table définitive avec colonne géométrique
        print("Création de la table définitive poteaux...")
        with engine.connect() as conn:
            # Créer la table poteaux
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS poteaux (
                    id SERIAL PRIMARY KEY,
                    fid INTEGER,
                    shape VARCHAR(255),
                    objectid INTEGER,
                    expl_id INTEGER,
                    posthtabt VARCHAR(255),
                    support_id VARCHAR(255),
                    support_pl VARCHAR(255),
                    support_nu VARCHAR(255),
                    support_1 VARCHAR(255),
                    car_physiq VARCHAR(255),
                    support_x FLOAT,
                    support_y FLOAT,
                    support_si VARCHAR(255),
                    quartier_c VARCHAR(255),
                    support_ch VARCHAR(255),
                    support_di VARCHAR(255),
                    statut_cod VARCHAR(255),
                    support_dt VARCHAR(255),
                    support_2 VARCHAR(255),
                    mode_finan VARCHAR(255),
                    projet_id VARCHAR(255),
                    user_id VARCHAR(255),
                    dt_cre VARCHAR(255),
                    dt_maj VARCHAR(255),
                    projet_id_ VARCHAR(255),
                    ville VARCHAR(255),
                    exploit VARCHAR(255),
                    geom geometry(Point, 4326)
                )
            """))

            # Vider la table si elle existe
            conn.execute(text("TRUNCATE TABLE poteaux"))

            # Insérer les données de la table temporaire dans la table définitive
            conn.execute(text("""
                INSERT INTO poteaux (
                    fid, shape, objectid, expl_id, posthtabt, support_id, support_pl,
                    support_nu, support_1, car_physiq, support_x, support_y, support_si,
                    quartier_c, support_ch, support_di, statut_cod, support_dt, support_2,
                    mode_finan, projet_id, user_id, dt_cre, dt_maj, projet_id_, ville, exploit
                )
                SELECT 
                    fid, shape, objectid, expl_id, posthtabt, support_id, support_pl,
                    support_nu, support_1, car_physiq, support_x, support_y, support_si,
                    quartier_c, support_ch, support_di, statut_cod, support_dt, support_2,
                    mode_finan, projet_id, user_id, dt_cre, dt_maj, projet_id_, ville, exploit
                FROM poteaux_temp
            """))

            # Mettre à jour la colonne géométrique
            conn.execute(text("""
                UPDATE poteaux
                SET geom = ST_SetSRID(ST_MakePoint(support_x, support_y), 4326)
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
    excel_path = "./data/poteaux.xlsx"
    import_poteaux_data(excel_path)
