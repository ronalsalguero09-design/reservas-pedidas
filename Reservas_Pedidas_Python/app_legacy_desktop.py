# =====================================================================
# RESPALDO DEL PROGRAMA DE ESCRITORIO ORIGINAL (TKINTER)
# Guardado para referencia o si deseas seguir usando la versión de escritorio.
# =====================================================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
import calendar
import json
from pathlib import Path

ARCHIVO = Path("reservas_pedidas.json")
CLAVE_ADMIN = "1234"  # Cambia esta clave

MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]
DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


def cargar_reservas():
    if not ARCHIVO.exists():
        return {}
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def guardar_reservas(reservas):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(reservas, f, ensure_ascii=False, indent=2)


class ReservasPedidas:
    def __init__(self, root):
        self.root = root
        self.root.title("Pedidas de Novios - Reserva de Fechas")
        self.root.geometry("950x700")
        self.root.minsize(850, 620)

        self.reservas = cargar_reservas()
        hoy = date.today()
        self.anio = hoy.year
        self.mes = hoy.month

        self.crear_interfaz()
        self.mostrar_calendario()

    def crear_interfaz(self):
        titulo = tk.Label(
            self.root,
            text="💗 PEDIDAS DE NOVIOS 💗",
            font=("Segoe UI", 24, "bold")
        )
        titulo.pack(pady=(15, 2))

        subtitulo = tk.Label(
            self.root,
            text="Calendario de disponibilidad y reservas",
            font=("Segoe UI", 12)
        )
        subtitulo.pack(pady=(0, 12))

        barra = tk.Frame(self.root)
        barra.pack(fill="x", padx=25)

        ttk.Button(barra, text="◀ Mes anterior",
                   command=self.mes_anterior).pack(side="left")
        ttk.Button(barra, text="Mes siguiente ▶",
                   command=self.mes_siguiente).pack(side="right")

        self.titulo_mes = tk.Label(
            barra, text="", font=("Segoe UI", 18, "bold")
        )
        self.titulo_mes.pack()

        leyenda = tk.Frame(self.root)
        leyenda.pack(pady=10)

        self.crear_leyenda(leyenda, "Disponible", "white")
        self.crear_leyenda(leyenda, "Reservado", "#ff8a8a")
        self.crear_leyenda(leyenda, "Hoy", "#ffe58a")

        self.calendario_frame = tk.Frame(self.root)
        self.calendario_frame.pack(fill="both", expand=True, padx=25, pady=5)

        botones = tk.Frame(self.root)
        botones.pack(pady=12)

        ttk.Button(
            botones,
            text="📋 Ver reservas",
            command=self.ver_reservas
        ).pack(side="left", padx=5)

        ttk.Button(
            botones,
            text="🔐 Panel administrador",
            command=self.panel_admin
        ).pack(side="left", padx=5)

    def crear_leyenda(self, padre, texto, color):
        caja = tk.Label(
            padre, text=f"  {texto}  ",
            bg=color, relief="solid", bd=1,
            font=("Segoe UI", 9)
        )
        caja.pack(side="left", padx=5)

    def mostrar_calendario(self):
        for widget in self.calendario_frame.winfo_children():
            widget.destroy()

        self.titulo_mes.config(text=f"{MESES[self.mes - 1]} {self.anio}")

        for columna, dia in enumerate(DIAS):
            lbl = tk.Label(
                self.calendario_frame,
                text=dia,
                font=("Segoe UI", 11, "bold"),
                relief="solid", bd=1,
                padx=5, pady=8
            )
            lbl.grid(row=0, column=columna, sticky="nsew")

        for c in range(7):
            self.calendario_frame.grid_columnconfigure(c, weight=1)

        semanas = calendar.monthcalendar(self.anio, self.mes)

        for fila, semana in enumerate(semanas, start=1):
            self.calendario_frame.grid_rowconfigure(fila, weight=1)

            for columna, numero in enumerate(semana):
                if numero == 0:
                    tk.Label(
                        self.calendario_frame,
                        text="",
                        relief="solid", bd=1
                    ).grid(row=fila, column=columna, sticky="nsew")
                    continue

                fecha = f"{self.anio:04d}-{self.mes:02d}-{numero:02d}"
                reservado = fecha in self.reservas
                hoy = fecha == date.today().isoformat()

                if reservado:
                    color = "#ff8a8a"
                    texto = f"{numero}\nRESERVADO"
                elif hoy:
                    color = "#ffe58a"
                    texto = f"{numero}\nHOY"
                else:
                    color = "white"
                    texto = f"{numero}\nDISPONIBLE"

                boton = tk.Button(
                    self.calendario_frame,
                    text=texto,
                    bg=color,
                    activebackground=color,
                    font=("Segoe UI", 10, "bold"),
                    relief="solid",
                    bd=1,
                    command=lambda f=fecha: self.seleccionar_fecha(f)
                )
                boton.grid(
                    row=fila, column=columna,
                    sticky="nsew", padx=1, pady=1
                )

    def seleccionar_fecha(self, fecha):
        if fecha in self.reservas:
            datos = self.reservas[fecha]
            mensaje = (
                f"Fecha: {fecha}\n\n"
                f"Estado: RESERVADO\n"
                f"Nombre: {datos.get('nombre', '')}\n"
                f"Hora: {datos.get('hora', '')}\n"
            )
            messagebox.showinfo("Fecha reservada", mensaje)
            return

        self.formulario_reserva(fecha)

    def formulario_reserva(self, fecha):
        ventana = tk.Toplevel(self.root)
        ventana.title("Reservar fecha")
        ventana.geometry("430x500")
        ventana.resizable(False, False)
        ventana.transient(self.root)
        ventana.grab_set()

        tk.Label(
            ventana,
            text="💗 Reservar pedida",
            font=("Segoe UI", 19, "bold")
        ).pack(pady=15)

        tk.Label(
            ventana,
            text=f"Fecha seleccionada: {fecha}",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=5)

        formulario = tk.Frame(ventana)
        formulario.pack(fill="x", padx=35, pady=10)

        variables = {}

        campos = [
            ("Nombre de la pareja", "nombre"),
            ("Teléfono / WhatsApp", "telefono"),
            ("Hora", "hora"),
            ("Tipo de pedida", "tipo"),
            ("Observaciones", "observaciones"),
        ]

        for fila, (texto, clave) in enumerate(campos):
            tk.Label(
                formulario, text=texto,
                font=("Segoe UI", 10, "bold")
            ).grid(row=fila, column=0, sticky="w", pady=7)

            if clave == "observaciones":
                entrada = tk.Text(formulario, height=4, width=28)
            else:
                entrada = ttk.Entry(formulario, width=30)

            entrada.grid(row=fila, column=1, pady=7)
            variables[clave] = entrada

        def reservar():
            nombre = variables["nombre"].get().strip()
            telefono = variables["telefono"].get().strip()
            hora = variables["hora"].get().strip()
            tipo = variables["tipo"].get().strip()

            if hasattr(variables["observaciones"], "get"):
                observaciones = variables["observaciones"].get("1.0", "end").strip()

            if not nombre or not telefono or not hora:
                messagebox.showwarning(
                    "Faltan datos",
                    "Completa nombre, teléfono y hora."
                )
                return

            if fecha in self.reservas:
                messagebox.showerror(
                    "No disponible",
                    "Esa fecha acaba de ser reservada."
                )
                ventana.destroy()
                self.mostrar_calendario()
                return

            self.reservas[fecha] = {
                "nombre": nombre,
                "telefono": telefono,
                "hora": hora,
                "tipo": tipo,
                "observaciones": observaciones,
                "estado": "Reservado"
            }

            guardar_reservas(self.reservas)
            self.mostrar_calendario()
            ventana.destroy()

            messagebox.showinfo(
                "Reserva realizada",
                f"¡Reserva registrada!\n\nFecha: {fecha}\nHora: {hora}\n\n"
                "La fecha ahora aparece como RESERVADA."
            )

        ttk.Button(
            ventana,
            text="💗 CONFIRMAR RESERVA",
            command=reservar
        ).pack(pady=18)

    def ver_reservas(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Reservas")
        ventana.geometry("800x500")

        columnas = ("fecha", "nombre", "telefono", "hora", "tipo", "estado")
        tabla = ttk.Treeview(ventana, columns=columnas, show="headings")

        nombres = {
            "fecha": "Fecha",
            "nombre": "Pareja",
            "telefono": "WhatsApp",
            "hora": "Hora",
            "tipo": "Tipo",
            "estado": "Estado"
        }

        for columna in columnas:
            tabla.heading(columna, text=nombres[columna])
            tabla.column(columna, width=120)

        for fecha in sorted(self.reservas):
            d = self.reservas[fecha]
            tabla.insert(
                "", "end",
                values=(
                    fecha,
                    d.get("nombre", ""),
                    d.get("telefono", ""),
                    d.get("hora", ""),
                    d.get("tipo", ""),
                    d.get("estado", "Reservado")
                )
            )

        tabla.pack(fill="both", expand=True, padx=15, pady=15)

    def panel_admin(self):
        login = tk.Toplevel(self.root)
        login.title("Administrador")
        login.geometry("350x220")
        login.resizable(False, False)
        login.transient(self.root)
        login.grab_set()

        tk.Label(
            login,
            text="🔐 Administrador",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=20)

        tk.Label(login, text="Contraseña").pack()

        entrada = ttk.Entry(login, show="*", width=25)
        entrada.pack(pady=8)
        entrada.focus()

        def entrar():
            if entrada.get() == CLAVE_ADMIN:
                login.destroy()
                self.ventana_admin()
            else:
                messagebox.showerror("Error", "Contraseña incorrecta.")

        ttk.Button(login, text="Entrar", command=entrar).pack(pady=10)
        entrada.bind("<Return>", lambda e: entrar())

    def ventana_admin(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Panel de administrador")
        ventana.geometry("850x550")

        tk.Label(
            ventana,
            text="Panel de administración",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=15)

        columnas = ("fecha", "nombre", "telefono", "hora", "tipo")
        tabla = ttk.Treeview(ventana, columns=columnas, show="headings")

        for col, titulo in zip(
            columnas,
            ["Fecha", "Pareja", "WhatsApp", "Hora", "Tipo"]
        ):
            tabla.heading(col, text=titulo)
            tabla.column(col, width=145)

        def cargar_tabla():
            for item in tabla.get_children():
                tabla.delete(item)

            for fecha in sorted(self.reservas):
                d = self.reservas[fecha]
                tabla.insert(
                    "", "end",
                    values=(
                        fecha,
                        d.get("nombre", ""),
                        d.get("telefono", ""),
                        d.get("hora", ""),
                        d.get("tipo", "")
                    )
                )

        tabla.pack(fill="both", expand=True, padx=15, pady=10)

        botones = tk.Frame(ventana)
        botones.pack(pady=10)

        def eliminar():
            seleccion = tabla.selection()
            if not seleccion:
                messagebox.showwarning(
                    "Selecciona una reserva",
                    "Selecciona una reserva para eliminar."
                )
                return

            item = tabla.item(seleccion[0])
            fecha = item["values"][0]

            if messagebox.askyesno(
                "Confirmar",
                f"¿Quieres liberar la fecha {fecha}?"
            ):
                self.reservas.pop(fecha, None)
                guardar_reservas(self.reservas)
                cargar_tabla()
                self.mostrar_calendario()

        ttk.Button(
            botones,
            text="🗑 Liberar fecha seleccionada",
            command=eliminar
        ).pack(side="left", padx=5)

        ttk.Button(
            botones,
            text="🔄 Actualizar",
            command=cargar_tabla
        ).pack(side="left", padx=5)

        cargar_tabla()

    def mes_anterior(self):
        self.mes -= 1
        if self.mes == 0:
            self.mes = 12
            self.anio -= 1
        self.mostrar_calendario()

    def mes_siguiente(self):
        self.mes += 1
        if self.mes == 13:
            self.mes = 1
            self.anio += 1
        self.mostrar_calendario()


if __name__ == "__main__":
    root = tk.Tk()
    app = ReservasPedidas(root)
    root.mainloop()
