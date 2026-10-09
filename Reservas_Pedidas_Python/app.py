import os
import sys
from pathlib import Path
from config import BASE_DIR, SECRET_KEY, DEBUG, HOST, PORT

try:
    from flask import Flask
    from routes.views import views_bp
    from routes.api import api_bp

    def create_app():
        """Fábrica de la aplicación Flask con rutas absolutas."""
        app = Flask(
            __name__,
            static_folder=str(BASE_DIR / "static"),
            template_folder=str(BASE_DIR / "templates")
        )
        app.config["SECRET_KEY"] = SECRET_KEY

        # Registrar Blueprints modulares
        app.register_blueprint(views_bp)
        app.register_blueprint(api_bp)

        return app

    app = create_app()

    if __name__ == "__main__":
        import run
        run.main()

except ImportError:
    # Si no tienen Flask instalado e intentan ejecutar app.py directamente,
    # delega automáticamente al servidor estándar sin dependencias.
    import run
    if __name__ == "__main__":
        run.main()
