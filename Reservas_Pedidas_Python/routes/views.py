from flask import Blueprint, render_template, session, redirect, url_for
from datetime import date

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def index():
    """Página principal pública para las parejas."""
    hoy = date.today()
    return render_template(
        "index.html",
        anio_actual=hoy.year,
        mes_actual=hoy.month,
        hoy_str=hoy.isoformat()
    )

@views_bp.route("/admin")
def admin():
    """Panel de administración y control de fechas."""
    autenticado = session.get("is_admin", False)
    return render_template("admin.html", autenticado=autenticado)
