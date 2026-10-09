import json
import threading
from datetime import date, datetime
from pathlib import Path
from config import DATA_FILE, CLAVE_ADMIN

_lock = threading.Lock()

class ReservaService:
    """
    Servicio de gestión y persistencia de reservas para pedidas de mano.
    Almacena las reservas en formato JSON compatible con todas las versiones de Python 3.
    """

    @staticmethod
    def _cargar():
        if not DATA_FILE.exists():
            return {}
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def _guardar(datos):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    @classmethod
    def obtener_todas(cls):
        """Devuelve todas las reservas almacenadas (acceso administrativo)."""
        with _lock:
            return cls._cargar()

    @classmethod
    def obtener_resumen_publico(cls, anio, mes):
        """
        Devuelve el estado de disponibilidad para el mes solicitado.
        Para proteger la privacidad de los clientes, solo expone si la fecha está reservada.
        """
        with _lock:
            todas = cls._cargar()
        
        prefijo = f"{int(anio):04d}-{int(mes):02d}-"
        resultado = {}
        for fecha, info in todas.items():
            if fecha.startswith(prefijo):
                resultado[fecha] = {
                    "reservado": True,
                    "estado": info.get("estado", "Reservado"),
                    "tipo": info.get("tipo", "Pedida Romántica")
                }
        return resultado

    @classmethod
    def obtener_por_fecha(cls, fecha):
        """Obtiene la reserva de una fecha específica."""
        with _lock:
            todas = cls._cargar()
            return todas.get(fecha)

    @classmethod
    def crear_reserva(cls, fecha, nombre, telefono, hora, tipo="Pedida Clásica", observaciones=""):
        """
        Registra una nueva reserva para la fecha dada.
        Retorna (exito, mensaje, datos_reserva).
        """
        nombre = (nombre or "").strip()
        telefono = (telefono or "").strip()
        hora = (hora or "").strip()
        tipo = (tipo or "").strip() or "Pedida Romántica"
        observaciones = (observaciones or "").strip()

        if not fecha:
            return False, "Debes seleccionar una fecha válida.", None

        if not nombre or not telefono or not hora:
            return False, "Por favor completa el nombre de la pareja, teléfono y hora deseada.", None

        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            return False, "El formato de fecha no es válido (debe ser AAAA-MM-DD).", None

        hoy = date.today()
        if fecha_obj < hoy:
            return False, "No es posible reservar fechas pasadas.", None

        with _lock:
            todas = cls._cargar()
            if fecha in todas:
                return False, f"La fecha {fecha} ya se encuentra reservada. Por favor selecciona otro día.", None

            nueva_reserva = {
                "fecha": fecha,
                "nombre": nombre,
                "telefono": telefono,
                "hora": hora,
                "tipo": tipo,
                "observaciones": observaciones,
                "estado": "Reservado",
                "creado_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            todas[fecha] = nueva_reserva
            cls._guardar(todas)

        return True, "¡Reserva confirmada con éxito!", nueva_reserva

    @classmethod
    def eliminar_reserva(cls, fecha):
        """Libera una fecha reservada."""
        with _lock:
            todas = cls._cargar()
            if fecha not in todas:
                return False, f"No se encontró ninguna reserva para la fecha {fecha}."

            del todas[fecha]
            cls._guardar(todas)

        return True, f"La fecha {fecha} ha sido liberada correctamente."

    @classmethod
    def verificar_admin(cls, clave):
        """Verifica la contraseña del panel de administración."""
        return str(clave).strip() == str(CLAVE_ADMIN).strip()

    @classmethod
    def obtener_metricas(cls):
        """Calcula estadísticas generales para el panel administrativo."""
        with _lock:
            todas = cls._cargar()

        hoy_str = date.today().isoformat()
        mes_actual_prefijo = date.today().strftime("%Y-%m")

        total = len(todas)
        este_mes = 0
        proximas = 0
        siguiente_reserva = None

        fechas_ordenadas = sorted(todas.keys())
        for f in fechas_ordenadas:
            if f.startswith(mes_actual_prefijo):
                este_mes += 1
            if f >= hoy_str:
                proximas += 1
                if siguiente_reserva is None:
                    siguiente_reserva = todas[f]

        return {
            "total_reservas": total,
            "reservas_este_mes": este_mes,
            "reservas_futuras": proximas,
            "proxima_reserva": siguiente_reserva
        }
