#!/usr/bin/env python3
"""
Herramienta para generar un enlace público de Internet (HTTPS)
Permite que personas de cualquier ciudad y desde cualquier celular puedan entrar al sistema.
No requiere registrarse ni instalar nada adicional (usa el cliente SSH nativo de Windows).
"""

import sys
import os
import subprocess
import re
import socket
import time
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

def verificar_servidor_activo(puerto=5000):
    """Comprueba si el servidor local ya está respondiendo."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", puerto)) == 0

def iniciar_servidor_en_segundo_plano():
    """Si el servidor no está corriendo, lo inicia en un proceso independiente."""
    print("⏳ El servidor local no estaba iniciado. Iniciándolo automáticamente...")
    cmd = [sys.executable, str(BASE_DIR / "run.py")]
    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
    for _ in range(15):
        time.sleep(1)
        if verificar_servidor_activo(5000):
            print("✅ Servidor local iniciado con éxito en el puerto 5000.")
            return True
    return False

def banner_enlace(url):
    print("\n" + "=" * 68)
    print("   💍 ¡TU ENLACE PÚBLICO PARA CUALQUIER CIUDAD ESTÁ LISTO! 📱")
    print("=" * 68)
    print(f"\n  👉 LINK PÚBLICO:  {url}\n")
    print("=" * 68)
    print("  ✨ Copia este link y envíalo por WhatsApp a tus clientes o parejas.")
    print("  📲 Pueden entrar desde cualquier celular, tablet o computadora,")
    print("     en cualquier ciudad o país.")
    print("  ⚠️  IMPORTANTE: Mantén esta ventana abierta mientras quieras que")
    print("     el enlace siga funcionando.")
    print("=" * 68 + "\n")

def conectar_tunel_ssh(puerto=5000):
    print("\n" + "=" * 68)
    print("   GENERANDO ENLACE PÚBLICO Y SEGURO (HTTPS)")
    print("=" * 68)
    print("⏳ Conectando con la red segura para publicar tu web en Internet...\n")

    # Comando SSH usando localhost.run (no requiere registro ni descargas)
    cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=30",
        "-R", f"80:localhost:{puerto}",
        "nokey@localhost.run"
    ]

    try:
        proceso = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace"
        )
    except FileNotFoundError:
        print("❌ No se encontró el comando 'ssh' en tu sistema Windows.")
        print("Por favor utiliza una de las opciones de despliegue en la nube (como Render.com).")
        input("\nPresiona Enter para salir...")
        return

    enlace_encontrado = False

    # Leer la salida en tiempo real buscando el link https://
    for linea in iter(proceso.stdout.readline, ""):
        linea_limpia = linea.strip()
        # Buscar URL con https://
        match = re.search(r"(https://[a-zA-Z0-9\.\-_]+\.(?:lhr\.life|localhost\.run))", linea_limpia)
        if match and not enlace_encontrado:
            url_publica = match.group(1)
            enlace_encontrado = True
            banner_enlace(url_publica)
            # Intentar abrirlo en el navegador para verificar
            try:
                webbrowser.open(url_publica)
            except Exception:
                pass
        elif not enlace_encontrado and linea_limpia:
            # Mostrar progreso
            if "Connect" in linea_limpia or "tunneled" in linea_limpia:
                print(f"  {linea_limpia}")

    proceso.wait()

def main():
    if not verificar_servidor_activo(5000):
        iniciar_servidor_en_segundo_plano()
        time.sleep(2)

    conectar_tunel_ssh(5000)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEnlace público cerrado.")
    except Exception as e:
        print(f"\nError: {e}")
        input("Presiona Enter para salir...")
