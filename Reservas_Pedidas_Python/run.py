#!/usr/bin/env python3
"""
Lanzador universal para el Sistema Web de Reservas de Pedidas de Mano.
Inicia el servidor Flask por defecto. Si Flask no está instalado,
activa automáticamente un servidor web integrado de Python estándar (100% independiente).
"""

import sys
import os
import socket
import mimetypes
import webbrowser
import threading
import time
from pathlib import Path

# Asegurar que el directorio de trabajo sea siempre la carpeta de este archivo
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))

from config import HOST, PORT
from models.reserva_service import ReservaService
from models.catalogo import PAQUETES_PEDIDA, HORARIOS_DISPONIBLES

def buscar_puerto_disponible(puerto_base=5000, max_intentos=15):
    """Busca un puerto libre si el 5000 ya está en uso."""
    for offset in range(max_intentos):
        puerto = puerto_base + offset
        for h in [HOST, "127.0.0.1", ""]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((h, puerto))
                    return puerto
            except OSError:
                break
    return puerto_base

def obtener_ip_local():
    """Detecta la IP local de la computadora en la red Wi-Fi/LAN."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def auto_abrir_navegador(url):
    """Abre la página web automáticamente en el navegador predeterminado."""
    def _abrir():
        time.sleep(1.2)
        try:
            webbrowser.open(url)
        except Exception:
            pass
    threading.Thread(target=_abrir, daemon=True).start()

def banner(puerto, modo="Flask"):
    ip_red = obtener_ip_local()
    print("\n" + "=" * 65)
    print("   💍 SISTEMA WEB DE RESERVAS - PEDIDAS DE MANO Y NOVIOS 💗")
    print("=" * 65)
    print(f"  Modo del servidor:   {modo}")
    print(f"  👉 Enlace Local:      http://localhost:{puerto}")
    print(f"  📱 Enlace en tu Red:  http://{ip_red}:{puerto}")
    print(f"  🔐 Panel Admin:       http://localhost:{puerto}/admin (Clave: 1234)")
    print("=" * 65)
    print("  🌐 Abriendo automáticamente en tu navegador web...")
    print("  💡 Para detener el servidor presiona CTRL + C\n")

def iniciar_con_flask(puerto):
    from app import create_app
    app = create_app()
    banner(puerto, "Flask")
    auto_abrir_navegador(f"http://localhost:{puerto}")
    app.run(host=HOST, port=puerto, debug=False)

def iniciar_servidor_estandar(puerto):
    """
    Servidor HTTP de respaldo utilizando exclusivamente la biblioteca estándar de Python.
    No requiere dependencias externas ni pip install.
    """
    import json
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs
    from datetime import date
    import calendar

    class WebHandler(BaseHTTPRequestHandler):
        def _enviar_json(self, codigo, datos):
            cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
            self.send_response(codigo)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)

        def _enviar_archivo(self, ruta_archivo, content_type=None):
            p = BASE_DIR / ruta_archivo
            if not p.exists() or not p.is_file():
                self.send_error(404, f"Archivo no encontrado: {ruta_archivo}")
                return

            if content_type is None:
                str_p = str(p).lower()
                if str_p.endswith(".html"):
                    content_type = "text/html; charset=utf-8"
                elif str_p.endswith(".css"):
                    content_type = "text/css; charset=utf-8"
                elif str_p.endswith(".js"):
                    content_type = "application/javascript; charset=utf-8"
                elif str_p.endswith(".json"):
                    content_type = "application/json; charset=utf-8"
                elif str_p.endswith(".png"):
                    content_type = "image/png"
                elif str_p.endswith(".jpg") or str_p.endswith(".jpeg"):
                    content_type = "image/jpeg"
                elif str_p.endswith(".svg"):
                    content_type = "image/svg+xml"
                else:
                    tipo, _ = mimetypes.guess_type(str(p))
                    content_type = tipo or "application/octet-stream"

            contenido = p.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(contenido)))
            self.end_headers()
            self.wfile.write(contenido)

        def _es_admin(self):
            cookie = self.headers.get("Cookie", "")
            return "admin_session=active" in cookie

        def do_GET(self):
            parsed = urlparse(self.path)
            ruta = parsed.path
            params = parse_qs(parsed.query)

            # Archivos estáticos
            if ruta.startswith("/static/"):
                archivo_relativo = ruta[len("/static/"):]
                self._enviar_archivo(Path("static") / archivo_relativo)
                return

            # Vistas principales
            if ruta == "" or ruta == "/":
                self._enviar_archivo("templates/index.html")
                return

            if ruta == "/admin":
                self._enviar_archivo("templates/admin.html")
                return

            # API endpoints
            if ruta == "/api/paquetes":
                self._enviar_json(200, {
                    "success": True,
                    "paquetes": PAQUETES_PEDIDA,
                    "horarios": HORARIOS_DISPONIBLES
                })
                return

            if ruta == "/api/calendario":
                hoy = date.today()
                anio = int(params.get("anio", [hoy.year])[0])
                mes = int(params.get("mes", [hoy.month])[0])
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
                            estado = "reservado" if esta_reservado else ("pasado" if es_pasado else "disponible")
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

                self._enviar_json(200, {
                    "success": True,
                    "anio": anio,
                    "mes": mes,
                    "nombre_mes": nombres_meses[mes - 1],
                    "hoy": hoy_iso,
                    "calendario": matriz_dias,
                    "reservas_conteo": len(reservas_mes)
                })
                return

            if ruta == "/api/admin/estado":
                self._enviar_json(200, {"autenticado": self._es_admin()})
                return

            if ruta == "/api/admin/reservas":
                if not self._es_admin():
                    self._enviar_json(401, {"success": False, "message": "No autorizado"})
                    return
                todas = ReservaService.obtener_todas()
                lista = [{"fecha": f, **todas[f]} for f in sorted(todas.keys())]
                self._enviar_json(200, {
                    "success": True,
                    "reservas": lista,
                    "metricas": ReservaService.obtener_metricas()
                })
                return

            self.send_error(404, "Página no encontrada")

        def do_POST(self):
            parsed = urlparse(self.path)
            ruta = parsed.path
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                datos = json.loads(body)
            except Exception:
                datos = {}

            if ruta == "/api/reservar":
                exito, mensaje, reserva = ReservaService.crear_reserva(
                    fecha=datos.get("fecha"),
                    nombre=datos.get("nombre"),
                    telefono=datos.get("telefono"),
                    hora=datos.get("hora"),
                    tipo=datos.get("tipo", "Pedida Romántica"),
                    observaciones=datos.get("observaciones", "")
                )
                codigo = 200 if exito else 400
                self._enviar_json(codigo, {"success": exito, "message": mensaje, "reserva": reserva})
                return

            if ruta == "/api/admin/login":
                pwd = datos.get("password", "")
                if ReservaService.verificar_admin(pwd):
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Set-Cookie", "admin_session=active; Path=/; SameSite=Lax")
                    resp = json.dumps({"success": True, "message": "Acceso concedido."}).encode("utf-8")
                    self.send_header("Content-Length", str(len(resp)))
                    self.end_headers()
                    self.wfile.write(resp)
                else:
                    self._enviar_json(401, {"success": False, "message": "Contraseña incorrecta."})
                return

            if ruta == "/api/admin/logout":
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Set-Cookie", "admin_session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT")
                resp = json.dumps({"success": True, "message": "Sesión finalizada."}).encode("utf-8")
                self.send_header("Content-Length", str(len(resp)))
                self.end_headers()
                self.wfile.write(resp)
                return

            if ruta == "/api/admin/reservas":
                if not self._es_admin():
                    self._enviar_json(401, {"success": False, "message": "No autorizado"})
                    return
                exito, mensaje, reserva = ReservaService.crear_reserva(
                    fecha=datos.get("fecha"),
                    nombre=datos.get("nombre"),
                    telefono=datos.get("telefono"),
                    hora=datos.get("hora"),
                    tipo=datos.get("tipo", "Pedida Romántica"),
                    observaciones=datos.get("observaciones", "")
                )
                codigo = 200 if exito else 400
                self._enviar_json(codigo, {"success": exito, "message": mensaje, "reserva": reserva})
                return

            self.send_error(404, "Endpoint no encontrado")

        def do_DELETE(self):
            parsed = urlparse(self.path)
            ruta = parsed.path
            if ruta.startswith("/api/admin/reservas/"):
                if not self._es_admin():
                    self._enviar_json(401, {"success": False, "message": "No autorizado"})
                    return
                fecha = ruta.split("/api/admin/reservas/")[1]
                exito, mensaje = ReservaService.eliminar_reserva(fecha)
                codigo = 200 if exito else 404
                self._enviar_json(codigo, {"success": exito, "message": mensaje})
                return
            self.send_error(404, "Endpoint no encontrado")

        def log_message(self, format, *args):
            sys.stdout.write(f"[{self.log_date_time_string()}] {args[0]} - {args[1]}\n")

    banner(puerto, "Servidor Estándar (Zero Dependencies)")
    auto_abrir_navegador(f"http://localhost:{puerto}")

    # Enlazar en HOST con fallback a 127.0.0.1
    servidor = None
    for h in [HOST, "127.0.0.1", ""]:
        try:
            servidor = HTTPServer((h, puerto), WebHandler)
            break
        except OSError:
            continue

    if servidor is None:
        servidor = HTTPServer(("127.0.0.1", puerto), WebHandler)

    servidor.serve_forever()

def main():
    try:
        puerto_activo = buscar_puerto_disponible(PORT)
        try:
            import flask
            iniciar_con_flask(puerto_activo)
        except Exception:
            # Fallback seguro al servidor nativo sin dependencias
            iniciar_servidor_estandar(puerto_activo)
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    except Exception as e:
        import traceback
        print("\n" + "=" * 50)
        print("ERROR AL INICIAR EL SERVIDOR:")
        print("=" * 50)
        traceback.print_exc()
        print("\nPresiona Enter para cerrar...")
        try:
            input()
        except Exception:
            pass

if __name__ == "__main__":
    main()
