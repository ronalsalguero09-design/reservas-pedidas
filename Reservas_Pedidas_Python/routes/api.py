from flask import Blueprint, request, jsonify, session
from datetime import date
import calendar
from models.reserva_service import ReservaService
from models.catalogo import PAQUETES_PEDIDA, HORARIOS_DISPONIBLES

api_bp = Blueprint("api", __name__, url_prefix="/api")

def admin_requerido():
    return session.get("is_admin") is True

@api_bp.route("/paquetes", methods=["GET"])
def obtener_paquetes():
    """Retorna los paquetes y tipos de pedidas configurados."""
    return jsonify({
        "success": True,
        "paquetes": PAQUETES_PEDIDA,
        "horarios": HORARIOS_DISPONIBLES
    })

@api_bp.route("/calendario", methods=["GET"])
def obtener_calendario():
    """
    Retorna la estructura del mes y el estado de reservas para el calendario público.
    """
    hoy = date.today()
    try:
        anio = int(request.args.get("anio", hoy.year))
        mes = int(request.args.get("mes", hoy.month))
    except ValueError:
        anio, mes = hoy.year, hoy.month

    if mes < 1:
        mes = 12
        anio -= 1
    elif mes > 12:
        mes = 1
        anio += 1

    semanas = calendar.monthcalendar(anio, mes)
    reservas_mes = ReservaService.obtener_resumen_publico(anio, mes)

    nombres_meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    matriz_dias = []
    hoy_iso = hoy.isoformat()

    for semana in semanas:
        fila = []
        for dia_num in semana:
            if dia_num == 0:
                fila.append({"vacio": True})
            else:
                fecha_iso = f"{anio:04d}-{mes:02d}-{dia_num:02d}"
                esta_reservado = fecha_iso in reservas_mes
                es_hoy = fecha_iso == hoy_iso
                es_pasado = fecha_iso < hoy_iso

                estado = "disponible"
                if esta_reservado:
                    estado = "reservado"
                elif es_pasado:
                    estado = "pasado"

                fila.append({
                    "vacio": False,
                    "dia": dia_num,
                    "fecha": fecha_iso,
                    "estado": estado,
                    "es_hoy": es_hoy,
                    "es_pasado": es_pasado,
                    "detalle": reservas_mes.get(fecha_iso) if esta_reservado else None
                })
        matriz_dias.append(fila)

    return jsonify({
        "success": True,
        "anio": anio,
        "mes": mes,
        "nombre_mes": nombres_meses[mes - 1],
        "hoy": hoy_iso,
        "calendario": matriz_dias,
        "reservas_conteo": len(reservas_mes)
    })

@api_bp.route("/reservar", methods=["POST"])
def realizar_reserva():
    """Registra una reserva para una pedida de mano."""
    datos = request.get_json() or {}
    fecha = datos.get("fecha")
    nombre = datos.get("nombre")
    telefono = datos.get("telefono")
    hora = datos.get("hora")
    tipo = datos.get("tipo", "Pedida Romántica")
    observaciones = datos.get("observaciones", "")

    exito, mensaje, reserva = ReservaService.crear_reserva(
        fecha=fecha,
        nombre=nombre,
        telefono=telefono,
        hora=hora,
        tipo=tipo,
        observaciones=observaciones
    )

    if not exito:
        return jsonify({"success": False, "message": mensaje}), 400

    return jsonify({
        "success": True,
        "message": mensaje,
        "reserva": reserva
    })

# ================= RUTAS ADMINISTRATIVAS =================

@api_bp.route("/admin/login", methods=["POST"])
def admin_login():
    datos = request.get_json() or {}
    password = datos.get("password", "")

    if ReservaService.verificar_admin(password):
        session["is_admin"] = True
        return jsonify({"success": True, "message": "Acceso concedido."})
    return jsonify({"success": False, "message": "Contraseña incorrecta."}), 401

@api_bp.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("is_admin", None)
    return jsonify({"success": True, "message": "Sesión finalizada."})

@api_bp.route("/admin/estado", methods=["GET"])
def admin_estado():
    return jsonify({"autenticado": admin_requerido()})

@api_bp.route("/admin/reservas", methods=["GET"])
def admin_reservas():
    if not admin_requerido():
        return jsonify({"success": False, "message": "No autorizado."}), 401

    todas = ReservaService.obtener_todas()
    lista = []
    for fecha in sorted(todas.keys()):
        item = dict(todas[fecha])
        item["fecha"] = fecha
        lista.append(item)

    return jsonify({
        "success": True,
        "reservas": lista,
        "metricas": ReservaService.obtener_metricas()
    })

@api_bp.route("/admin/reservas/<fecha>", methods=["DELETE"])
def admin_eliminar_reserva(fecha):
    if not admin_requerido():
        return jsonify({"success": False, "message": "No autorizado."}), 401

    exito, mensaje = ReservaService.eliminar_reserva(fecha)
    if not exito:
        return jsonify({"success": False, "message": mensaje}), 404

    return jsonify({"success": True, "message": mensaje})

@api_bp.route("/admin/reservas", methods=["POST"])
def admin_crear_reserva():
    if not admin_requerido():
        return jsonify({"success": False, "message": "No autorizado."}), 401

    datos = request.get_json() or {}
    exito, mensaje, reserva = ReservaService.crear_reserva(
        fecha=datos.get("fecha"),
        nombre=datos.get("nombre"),
        telefono=datos.get("telefono"),
        hora=datos.get("hora"),
        tipo=datos.get("tipo", "Pedida Romántica"),
        observaciones=datos.get("observaciones", "")
    )

    if not exito:
        return jsonify({"success": False, "message": mensaje}), 400

    return jsonify({
        "success": True,
        "message": mensaje,
        "reserva": reserva
    })
