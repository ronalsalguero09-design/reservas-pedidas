# 💍 AMOR ETERNO — Sistema Web de Reservas para Pedidas de Mano

Sistema web moderno, elegante y modular diseñado para la reserva y gestión de fechas de **Pedidas de Mano** y experiencias románticas para parejas.

---

## 🌟 Principales Mejoras Realizadas

1. **Modularización Completa de la Arquitectura**:
   - Se eliminó el código monolítico de un solo archivo.
   - Se estructuró en capas limpias: Configuración (`config.py`), Modelos y Lógica (`models/`), Rutas y Controladores (`routes/`), Plantillas HTML (`templates/`) y Recursos Estáticos (`static/`).
   - La versión anterior de escritorio con Tkinter quedó respaldada de forma segura en `app_legacy_desktop.py`.

2. **Transformación a Página Web (Accesible por Enlace)**:
   - Ahora puedes simplemente **enviar un link** a tus clientes o parejas para que entren desde su teléfono celular, tablet o computadora.
   - Diseño 100% responsivo y adaptado para móviles.

3. **Diseño Visual Moderno, Romántico y de Lujo**:
   - Paleta de colores cálida y romántica (*Velvet Rose*, toques dorados champagne y tipografía elegante *Playfair Display*).
   - Catálogo visual de experiencias:
     - 🕯️ *Cena Romántica a la Luz de las Velas*
     - 💍 *Letras Gigantes 'MARRY ME' & Luces LED*
     - 🧺 *Picnic Sunset Bohemio de Ensueño*
     - ✨ *Terraza Mirador Exclusiva VIP*
     - 💖 *Pedida Personalizada a tu Medida*
   - Calendario mensual en vivo con estados claros: **Disponible**, **Reservado**, **Hoy** y **Pasado**.
   - Integración directa con **WhatsApp**: genera mensajes preformateados para que la pareja confirme los detalles sorpresa con un solo toque.

4. **Panel de Administración Privado (`/admin`)**:
   - Protegido por contraseña (clave inicial: `1234`, configurable en `config.py`).
   - Métricas en tiempo real: Total de reservas, reservas de este mes y próxima pedida agendada.
   - Buscador rápido por pareja, fecha o teléfono.
   - Botón directo para chatear por WhatsApp con el cliente.
   - Capacidad de **liberar fechas** (cancelar reserva) y registrar reservas manuales tomadas por llamada o chat.

---

## 📁 Estructura del Proyecto

```text
Reservas_Pedidas_Python/
│
├── config.py                 # Configuración del servidor, clave de admin y rutas
├── models/
│   ├── __init__.py
│   └── reserva_service.py    # Lógica de datos, validaciones y guardado en JSON
│
├── routes/
│   ├── __init__.py
│   ├── views.py              # Rutas para servir las páginas web (inicio y admin)
│   └── api.py                # Endpoints JSON (/api/calendario, /api/reservar, etc.)
│
├── static/
│   ├── css/
│   │   ├── style.css         # Estilos modernos de la web de clientes
│   │   └── admin.css         # Estilos del panel de control
│   └── js/
│       ├── app.js            # Calendario interactivo, paquetes y modal
│       └── admin.js          # Control de reservas, métricas y filtros
│
├── templates/
│   ├── index.html            # Portal web para clientes y parejas
│   └── admin.html            # Dashboard de administración
│
├── data/
│   └── reservas_pedidas.json # Base de datos JSON de reservas
│
├── app.py                    # Aplicación Flask
├── run.py                    # Lanzador inteligente (Flask o Servidor Estándar sin dependencias)
├── requirements.txt          # Dependencias
├── app_legacy_desktop.py     # Respaldo del programa original de Tkinter
└── README.md                 # Guía del proyecto
```

---

## 🚀 Cómo Iniciar el Programa

### Opción 1: Ejecución Directa (Recomendada)
Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
python run.py
```

> **Nota:** El archivo `run.py` cuenta con compatibilidad dual: si tienes Flask instalado lo ejecutará con Flask; si aún no has instalado paquetes, iniciará automáticamente el servidor HTTP estándar integrado de Python **sin necesidad de instalar nada**.

### Opción 2: Instalar Dependencias de Flask
Si prefieres instalar Flask para el entorno completo:

```bash
pip install -r requirements.txt
python app.py
```

---

## 🔗 Cómo Acceder y Compartir el Enlace

Una vez que el servidor esté corriendo:

- **Para entrar tú en tu computadora**:
  👉 [http://localhost:5000](http://localhost:5000)

- **Para entrar al Panel de Administrador**:
  🔐 [http://localhost:5000/admin](http://localhost:5000/admin) *(Clave: 1234)*

- **Para compartir con clientes en cualquier ciudad del mundo y en celulares**:
  1. Haz doble clic en el archivo **`COMPARTIR_LINK_PUBLICO.bat`**.
  2. En unos segundos te generará un enlace público seguro (HTTPS), por ejemplo:
     `https://tu-reserva-xxxx.lhr.life`
  3. Copias ese enlace y lo mandas por WhatsApp a cualquier persona en otra ciudad. ¡Entrarán directamente desde su celular sin problemas!

- **Para mantener el link activo 24/7 en la nube (incluso con tu PC apagada)**:
  Puedes subir este proyecto gratis a plataformas como **Render.com** o **Railway.app** (el repositorio ya incluye el archivo `Procfile` listo para funcionar).

---

## ⚙️ Configuración Personalizada

Puedes cambiar la contraseña de administración, el puerto o la clave secreta abriendo el archivo [`config.py`](file:///c:/Users/PC/Documents/Reservas_Pedidas_Python/config.py):

```python
CLAVE_ADMIN = "1234"  # Cambia '1234' por la contraseña que desees
PORT = 5000           # Puerto en el que se ejecuta el servidor
```
