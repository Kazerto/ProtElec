from sqlalchemy import func, text
from database.connection import get_session
from api.models import Poteau

# Dans api/services.py
def find_nearest_pole(lat, lon):
    """
    Trouve le poteau électrique le plus proche des coordonnées données
    """
    with get_session() as session:
        # Créer un point à partir des coordonnées
        point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)

        # Trouver le poteau le plus proche
        nearest_pole = session.query(
            Poteau,
            func.ST_Distance(Poteau.geom, point).label('distance')
        ).filter(
            # Filtrer les poteaux sans coordonnées valides
            Poteau.SUPPORT_X != 0,
            Poteau.SUPPORT_Y != 0
        ).order_by(func.ST_Distance(Poteau.geom, point)).first()

        if not nearest_pole:
            return None

        return {
            'pole_id': nearest_pole.Poteau.SUPPORT_ID,
            'support_pl': nearest_pole.Poteau.SUPPORT_PL,
            'support_nu': nearest_pole.Poteau.SUPPORT_NU,
            'x': nearest_pole.Poteau.SUPPORT_X,
            'y': nearest_pole.Poteau.SUPPORT_Y,
            'car_physiq': nearest_pole.Poteau.CAR_PHYSIQ,
            'quartier': nearest_pole.Poteau.QUARTIER_C,
            'distance_meters': nearest_pole.distance * 111319.9,  # Conversion approximative degrés -> mètres
        }

def perpendicular_to_pole(pole_id, lat, lon):
    """
    Calcule la perpendiculaire depuis un poteau vers un point B
    """
    with get_session() as session:
        # Récupérer le poteau
        pole = session.query(Poteau).filter(Poteau.SUPPORT_ID == pole_id).first()

        if not pole:
            return None

        # Créer un point à partir des coordonnées
        point_b = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)

        # Calculer le point perpendiculaire
        # Cette requête SQL calcule le point sur la ligne entre le poteau et B
        # qui est le plus proche du poteau (c'est-à-dire perpendiculaire)
        query = text("""
            SELECT 
                ST_X(ST_ClosestPoint(ST_MakeLine(p.geom, :point_b), p.geom)) as perp_x,
                ST_Y(ST_ClosestPoint(ST_MakeLine(p.geom, :point_b), p.geom)) as perp_y
            FROM poteaux p
            WHERE p.SUPPORT_ID = :pole_id
        """)

        result = session.execute(query, {
            'point_b': point_b,
            'pole_id': pole_id
        }).first()

        return {
            'pole_id': pole_id,
            'pole_x': pole.SUPPORT_X,
            'pole_y': pole.SUPPORT_Y,
            'perpendicular_x': result.perp_x,
            'perpendicular_y': result.perp_y
        }
