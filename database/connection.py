from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from config import DATABASE_URI

# Créer le moteur de base de données
engine = create_engine(DATABASE_URI)

# Créer une fabrique de sessions
Session = sessionmaker(bind=engine)

@contextmanager
def get_session():
    """
    Fournit un contexte pour utiliser une session de base de données
    """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
