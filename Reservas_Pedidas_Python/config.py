import os
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Configuración del servidor
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 5000))
DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "t")

# Seguridad y Clave de Administrador
SECRET_KEY = os.environ.get("SECRET_KEY", "pedidas_de_novios_secret_key_2026_romance")
CLAVE_ADMIN = os.environ.get("CLAVE_ADMIN", "1234")

# Almacenamiento de datos JSON
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Si existe un reservas_pedidas.json en la raíz (del proyecto anterior), usarlo o migrarlo
DATA_FILE_ROOT = BASE_DIR / "reservas_pedidas.json"
DATA_FILE = DATA_DIR / "reservas_pedidas.json"

if DATA_FILE_ROOT.exists() and not DATA_FILE.exists():
    DATA_FILE = DATA_FILE_ROOT
