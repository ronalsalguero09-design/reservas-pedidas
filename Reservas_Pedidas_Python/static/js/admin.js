/**
 * AMOR ETERNO - PANEL ADMINISTRATIVO (JS)
 * Control de sesiones, métricas, listado de reservas, liberación de fechas y reservas manuales.
 */

document.addEventListener("DOMContentLoaded", () => {
    // Referencias DOM
    const pantallaLogin = document.getElementById("pantallaLogin");
    const pantallaDashboard = document.getElementById("pantallaDashboard");
    const btnLogout = document.getElementById("btnLogout");
    const formLogin = document.getElementById("formLogin");
    const inputClave = document.getElementById("inputClave");

    // KPIs
    const kpiTotal = document.getElementById("kpiTotal");
    const kpiMes = document.getElementById("kpiMes");
    const kpiFuturas = document.getElementById("kpiFuturas");
    const kpiProximaTexto = document.getElementById("kpiProximaTexto");

    // Tabla y Búsqueda
    const tbodyReservas = document.getElementById("tbodyReservas");
    const inputBuscar = document.getElementById("inputBuscar");
    const sinResultados = document.getElementById("sinResultados");
    const contadorReservas = document.getElementById("contadorReservas");
    const btnRecargar = document.getElementById("btnRecargar");

    // Modal Liberar Fecha
    const modalConfirmarLiberar = document.getElementById("modalConfirmarLiberar");
    const textoFechaLiberar = document.getElementById("textoFechaLiberar");
    const btnCancelarLiberar = document.getElementById("btnCancelarLiberar");
    const btnConfirmarLiberarAccion = document.getElementById("btnConfirmarLiberarAccion");

    // Modal Nueva Reserva Manual
    const modalManual = document.getElementById("modalManual");
    const btnNuevaReservaManual = document.getElementById("btnNuevaReservaManual");
    const btnCerrarManual = document.getElementById("btnCerrarManual");
    const btnCancelarManual = document.getElementById("btnCancelarManual");
    const formManual = document.getElementById("formManual");

    // Toast Container
    const toastContainer = document.getElementById("toastContainer");

    // Estado local
    let reservasGlobales = [];
    let fechaALiberar = null;

    // Inicializar comprobando si ya está autenticado
    verificarEstadoAuth();

    // ==========================================
    // AUTENTICACIÓN
    // ==========================================
    async function verificarEstadoAuth() {
        try {
            const resp = await fetch("/api/admin/estado");
            const data = await resp.json();
            if (data.autenticado) {
                mostrarDashboard();
            } else {
                mostrarLogin();
            }
        } catch {
            mostrarLogin();
        }
    }

    formLogin.addEventListener("submit", async (e) => {
        e.preventDefault();
        const password = inputClave.value;

        try {
            const resp = await fetch("/api/admin/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ password })
            });

            const data = await resp.json();
            if (resp.ok && data.success) {
                mostrarToast("¡Bienvenido al Panel de Administración!", "success");
                mostrarDashboard();
            } else {
                mostrarToast(data.message || "Contraseña incorrecta.", "error");
            }
        } catch (err) {
            mostrarToast("Error al conectar con el servidor.", "error");
        }
    });

    btnLogout.addEventListener("click", async () => {
        try {
            await fetch("/api/admin/logout", { method: "POST" });
            mostrarToast("Sesión cerrada correctamente.", "info");
            mostrarLogin();
        } catch (err) {
            console.error(err);
        }
    });

    function mostrarDashboard() {
        pantallaLogin.style.display = "none";
        pantallaDashboard.style.display = "block";
        btnLogout.style.display = "inline-flex";
        cargarDatosAdmin();
    }

    function mostrarLogin() {
        pantallaLogin.style.display = "flex";
        pantallaDashboard.style.display = "none";
        btnLogout.style.display = "none";
        inputClave.value = "";
    }

    // ==========================================
    // CARGAR DATOS Y MÉTRICAS
    // ==========================================
    async function cargarDatosAdmin() {
        tbodyReservas.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 30px; color: #64748b;">
                    <i class="fa-solid fa-spinner fa-spin fa-2x"></i>
                    <p style="margin-top: 8px;">Cargando reservas...</p>
                </td>
            </tr>
        `;

        try {
            const resp = await fetch("/api/admin/reservas");
            if (!resp.ok) {
                if (resp.status === 401) mostrarLogin();
                return;
            }

            const data = await resp.json();
            if (data.success) {
                reservasGlobales = data.reservas || [];
                actualizarMetricas(data.metricas);
                renderizarTabla(reservasGlobales);
            }
        } catch (err) {
            console.error("Error al cargar datos:", err);
            mostrarToast("Error al cargar las reservas.", "error");
        }
    }

    function actualizarMetricas(metricas) {
        if (!metricas) return;
        kpiTotal.textContent = metricas.total_reservas ?? 0;
        kpiMes.textContent = metricas.reservas_este_mes ?? 0;
        kpiFuturas.textContent = metricas.reservas_futuras ?? 0;

        if (metricas.proxima_reserva) {
            const p = metricas.proxima_reserva;
            kpiProximaTexto.innerHTML = `<strong>${p.fecha}</strong><br><small>${p.nombre}</small>`;
        } else {
            kpiProximaTexto.textContent = "Ninguna próxima";
        }
    }

    function renderizarTabla(reservas) {
        tbodyReservas.innerHTML = "";
        contadorReservas.textContent = `${reservas.length} reserva${reservas.length === 1 ? '' : 's'}`;

        if (reservas.length === 0) {
            sinResultados.style.display = "block";
            return;
        }

        sinResultados.style.display = "none";

        reservas.forEach(r => {
            const tr = document.createElement("tr");

            // Limpiar teléfono para WhatsApp
            const telLimpio = (r.telefono || "").replace(/[^0-9]/g, "");
            const whatsappLink = telLimpio
                ? `<a href="https://wa.me/${telLimpio}" target="_blank" class="btn-whatsapp-cell" title="Abrir chat de WhatsApp">
                     <i class="fa-brands fa-whatsapp"></i> ${r.telefono}
                   </a>`
                : (r.telefono || "No especificado");

            tr.innerHTML = `
                <td><span class="date-pill">${r.fecha}</span></td>
                <td><span class="couple-name">${r.nombre || "Sin nombre"}</span></td>
                <td>${whatsappLink}</td>
                <td><strong>${r.hora || "-"}</strong></td>
                <td><span class="package-tag">${r.tipo || "Pedida Estándar"}</span></td>
                <td><div class="obs-cell" title="${r.observaciones || ''}">${r.observaciones || "Sin notas"}</div></td>
                <td>
                    <button class="btn-liberar" data-fecha="${r.fecha}">
                        <i class="fa-regular fa-trash-can"></i> Liberar
                    </button>
                </td>
            `;

            // Acción Liberar
            const btnLib = tr.querySelector(".btn-liberar");
            btnLib.addEventListener("click", () => {
                abrirModalLiberar(r.fecha);
            });

            tbodyReservas.appendChild(tr);
        });
    }

    // ==========================================
    // BÚSQUEDA Y FILTRADO
    // ==========================================
    inputBuscar.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase().trim();
        if (!query) {
            renderizarTabla(reservasGlobales);
            return;
        }

        const filtradas = reservasGlobales.filter(r => {
            const nombre = (r.nombre || "").toLowerCase();
            const tel = (r.telefono || "").toLowerCase();
            const fecha = (r.fecha || "").toLowerCase();
            const tipo = (r.tipo || "").toLowerCase();
            return nombre.includes(query) || tel.includes(query) || fecha.includes(query) || tipo.includes(query);
        });

        renderizarTabla(filtradas);
    });

    btnRecargar.addEventListener("click", () => {
        cargarDatosAdmin();
        mostrarToast("Datos actualizados.", "info");
    });

    // ==========================================
    // LIBERAR FECHA (ELIMINAR RESERVA)
    // ==========================================
    function abrirModalLiberar(fecha) {
        fechaALiberar = fecha;
        textoFechaLiberar.textContent = fecha;
        modalConfirmarLiberar.classList.add("active");
    }

    function cerrarModalLiberar() {
        modalConfirmarLiberar.classList.remove("active");
        fechaALiberar = null;
    }

    btnCancelarLiberar.addEventListener("click", cerrarModalLiberar);

    btnConfirmarLiberarAccion.addEventListener("click", async () => {
        if (!fechaALiberar) return;

        try {
            const resp = await fetch(`/api/admin/reservas/${fechaALiberar}`, {
                method: "DELETE"
            });
            const data = await resp.json();

            if (resp.ok && data.success) {
                mostrarToast(`La fecha ${fechaALiberar} fue liberada con éxito.`, "success");
                cerrarModalLiberar();
                cargarDatosAdmin();
            } else {
                mostrarToast(data.message || "Error al liberar la fecha.", "error");
            }
        } catch (err) {
            mostrarToast("Error de conexión al liberar la fecha.", "error");
        }
    });

    // ==========================================
    // NUEVA RESERVA MANUAL
    // ==========================================
    btnNuevaReservaManual.addEventListener("click", () => {
        modalManual.classList.add("active");
    });

    function cerrarModalManual() {
        modalManual.classList.remove("active");
        formManual.reset();
    }

    btnCerrarManual.addEventListener("click", cerrarModalManual);
    btnCancelarManual.addEventListener("click", cerrarModalManual);

    formManual.addEventListener("submit", async (e) => {
        e.preventDefault();

        const datos = {
            fecha: document.getElementById("manualFecha").value,
            nombre: document.getElementById("manualNombre").value.trim(),
            telefono: document.getElementById("manualTelefono").value.trim(),
            hora: document.getElementById("manualHora").value.trim(),
            tipo: document.getElementById("manualTipo").value.trim(),
            observaciones: document.getElementById("manualObservaciones").value.trim()
        };

        try {
            const resp = await fetch("/api/admin/reservas", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(datos)
            });

            const resData = await resp.json();
            if (resp.ok && resData.success) {
                mostrarToast("Reserva manual registrada con éxito.", "success");
                cerrarModalManual();
                cargarDatosAdmin();
            } else {
                mostrarToast(resData.message || "No se pudo crear la reserva.", "error");
            }
        } catch (err) {
            mostrarToast("Error al guardar reserva.", "error");
        }
    });

    // ==========================================
    // TOAST
    // ==========================================
    function mostrarToast(mensaje, tipo = "info") {
        const toast = document.createElement("div");
        toast.className = `toast toast-${tipo}`;

        let icono = "fa-circle-info";
        if (tipo === "success") icono = "fa-circle-check";
        if (tipo === "error") icono = "fa-triangle-exclamation";

        toast.innerHTML = `
            <i class="fa-solid ${icono}"></i>
            <span>${mensaje}</span>
        `;

        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateX(20px)";
            toast.style.transition = "all 0.3s ease";
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
});
