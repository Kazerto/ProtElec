from fastapi import FastAPI
from sqlalchemy import create_engine, text
from pydantic import BaseModel

# Configuration de la base de données
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "seeg_poles"

# URI de connexion à la base de données
DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Créer l'application FastAPI
app = FastAPI(
    title="API Poteaux Électriques",
    description="API pour localiser des poteaux électriques à Libreville",
    version="1.0.0"
)
# Modèle pour la réponse de l'API
class NearestPoleResponse(BaseModel):
    nearest_pole: str
    distance: float

# Endpoint pour trouver le poteau le plus proche
@app.get("/nearest-pole", response_model=NearestPoleResponse)
def get_nearest_pole(x: float, y: float):
    """
    Trouve le poteau électrique le plus proche des coordonnées (x, y).
    """
    try:
        # Connexion à la base de données
        engine = create_engine(DATABASE_URI)
        with engine.connect() as conn:
            # Requête SQL pour trouver le poteau le plus proche
            query = text("""
                SELECT support_nu, ST_DistanceSphere(
                    ST_SetSRID(ST_MakePoint(:x, :y), 4326),
                    geom
                ) AS distance, support_x, support_y, quartier_c
                FROM poteaux
                ORDER BY distance
                LIMIT 1;
            """)
            result = conn.execute(query, {"x": x, "y": y}).fetchone()

            if result:
                return {"nearest_pole": result[0], "distance": result[1],"pole_x": result[2],"pole_y": result[3],"quartier": result[4]}
            else:
                return {"nearest_pole": "Aucun poteau trouvé", "distance": 0.0}

    except Exception as e:
        return {"error": str(e)}

# Démarrer l'API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
