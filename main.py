from fastapi import FastAPI
from api.routes import router
import uvicorn

# Créer l'application FastAPI
app = FastAPI(
    title="API Poteaux Électriques",
    description="API pour localiser des poteaux électriques à Libreville",
    version="1.0.0"
)

# Ajouter les routes
app.include_router(router, prefix="/api/v1")

# Point d'entrée pour le développement
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
