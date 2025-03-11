from fastapi import APIRouter, Query, HTTPException
from api.services import find_nearest_pole, perpendicular_to_pole

router = APIRouter()

# Dans api/routes.py
@router.get("/nearest-pole/")
async def get_nearest_pole(lat: float = Query(...), lon: float = Query(...)):
    """
    Trouve le poteau électrique le plus proche des coordonnées données
    """
    try:
        result = find_nearest_pole(lat, lon)
        if not result:
            raise HTTPException(status_code=404, detail="Aucun poteau avec des coordonnées valides n'a été trouvé")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/perpendicular-to-pole/")
async def get_perpendicular(
        pole_id: str = Query(...),
        lat: float = Query(...),
        lon: float = Query(...)
):
    """
    Calcule la perpendiculaire depuis un poteau vers un point B
    """
    try:
        result = perpendicular_to_pole(pole_id, lat, lon)
        if not result:
            raise HTTPException(status_code=404, detail="Poteau non trouvé")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nearest-pole-to-incident/")
async def get_nearest_pole_to_incident(lat: float = Query(...), lon: float = Query(...)):
    """
    Indique la position du poteau le plus proche d'un incident
    """
    # Cette fonctionnalité est similaire à nearest-pole, mais pourrait inclure
    # des informations supplémentaires spécifiques aux incidents
    try:
        pole_info = find_nearest_pole(lat, lon)
        return {
            **pole_info,
            "incident_position": {
                "lat": lat,
                "lon": lon
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
