/**
 * AMOR ETERNO - LÓGICA DEL CLIENTE (WEB)
 * Manejo interactivo del calendario, selección de experiencias, modal de reserva y WhatsApp.
 */

document.addEventListener("DOMContentLoaded", () => {
    // Estado de la aplicación
    const estado = {
        anio: new Date().getFullYear(),
        mes: new Date().getMonth() + 1,
        paquetes: [],
        horarios: []
    };

    // Referencias a elementos del DOM
    const tituloMesAnio = document.getElementById("tituloMesAnio");
    const gridDias = document.getElementById("gridDias");
    const btnMesAnterior = document.getElementById("btnMesAnterior");
    const btnMesSiguiente = document.getElementById("btnMesSiguiente");
    const paquetesGrid = document.getElementById("paquetesGrid");

    // Modal de Reserva
    const modalReserva = document.getElementById("modalReserva");
    const btnCerrarModal = document.getElementById("btnCerrarModal");
    const btnCancelarModal = document.getElementById("btnCancelarModal");
    const formReserva = document.getElementById("formReserva");
    const modalFechaTexto = document.getElementById("modalFechaTexto");
    const inputFecha = document.getElementById("inputFecha");
    const selectHora = document.getElementById("selectHora");
    const selectTipo = document.getElementById("selectTipo");
    const btnConfirmarReserva = document.getElementById("btnConfirmarReserva");

    // Modal de Éxito
    const modalExito = document.getElementById("modalExito");
    const btnCerrarExito = document.getElementById("btnCerrarExito");
    const resumenExito = document.getElementById("resumenExito");
    const btnEnviarWhatsappExito = document.getElementById("btnEnviarWhatsappExito");

    // Toast Container
    const toastContainer = document.getElementById("toastContainer");

    // ==========================================
    // INICIALIZACIÓN
    // ==========================================
    cargarPaquetes();
    cargarCalendario(estado.anio, estado.mes);

    // Navegación del Calendario
    btnMesAnterior.addEventListener("click", () => {
        estado.mes--;
        if (estado.mes < 1) {
            estado.mes = 12;
            estado.anio--;
        }
        cargarCalendario(estado.anio, estado.mes);
    });

    btnMesSiguiente.addEventListener("click", () => {
        estado.mes++;
        if (estado.mes > 12) {
            estado.mes = 1;
            estado.anio++;
        }
        cargarCalendario(estado.anio, estado.mes);
    });

    // ==========================================
    // CARGAR PAQUETES Y HORARIOS
    // ==========================================
    async function cargarPaquetes() {
        try {
            const resp = await fetch("/api/paquetes");
            const data = await resp.json();
            if (data.success) {
                estado.paquetes = data.paquetes;
                estado.horarios = data.horarios;
                renderizarPaquetes(data.paquetes);
                poblarSelectores(data.paquetes, data.horarios);
            }
        } catch (err) {
            console.error("Error al cargar paquetes:", err);
        }
    }

    function renderizarPaquetes(paquetes) {
        if (!paquetesGrid) return;
        paquetesGrid.innerHTML = "";

        paquetes.forEach(paq => {
            const card = document.createElement("div");
            card.className = "paquete-card";

            const featuresHtml = paq.incluye
                .map(item => `<li><i class="fa-solid fa-heart"></i> ${item}</li>`)
                .join("");

            card.innerHTML = `
                <div class="paquete-top">
                    <div class="paquete-icon">${paq.icono}</div>
                    <span class="paquete-badge">${paq.tag}</span>
                </div>
                <h3 class="paquete-title">${paq.nombre}</h3>
                <p class="paquete-desc">${paq.descripcion}</p>
                <ul class="paquete-features">
                    ${featuresHtml}
                </ul>
                <button class="btn-select-package" data-paquete="${paq.nombre}">
                    <i class="fa-regular fa-calendar-plus"></i> Reservar con este estilo
                </button>
            `;

            const btnElegir = card.querySelector(".btn-select-package");
            btnElegir.addEventListener("click", () => {
                // Desplazarse al calendario e indicar que elija fecha
                const calSec = document.getElementById("calendario-seccion");
                if (calSec) {
                    calSec.scrollIntoView({ behavior: "smooth" });
                }
                selectTipo.value = paq.nombre;
                mostrarToast(`Has seleccionado: "${paq.nombre}". Elige tu fecha en el calendario.`, "info");
            });

            paquetesGrid.appendChild(card);
        });
    }

    function poblarSelectores(paquetes, horarios) {
        // Horarios
        selectHora.innerHTML = '<option value="">Selecciona un horario sugerido...</option>';
        horarios.forEach(h => {
            const opt = document.createElement("option");
            opt.value = h;
            opt.textContent = h;
            selectHora.appendChild(opt);
        });
        const optCustom = document.createElement("option");
        optCustom.value = "Horario a convenir con asesor";
        optCustom.textContent = "Otro horario (coordinar por WhatsApp)";
        selectHora.appendChild(optCustom);

        // Paquetes
        selectTipo.innerHTML = "";
        paquetes.forEach(p => {
            const opt = document.createElement("option");
            opt.value = p.nombre;
            opt.textContent = `${p.icono} ${p.nombre}`;
            selectTipo.appendChild(opt);
        });
    }

    // ==========================================
    // CARGAR CALENDARIO
    // ==========================================
    async function cargarCalendario(anio, mes) {
        gridDias.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #9ca3af;">
                <i class="fa-solid fa-spinner fa-spin fa-2x"></i>
                <p style="margin-top: 10px;">Consultando fechas disponibles...</p>
            </div>
        `;

        try {
            const resp = await fetch(`/api/calendario?anio=${anio}&mes=${mes}`);
            const data = await resp.json();

            if (!data.success) {
                mostrarToast("No se pudo cargar el calendario.", "error");
                return;
            }

            estado.anio = data.anio;
            estado.mes = data.mes;
            tituloMesAnio.textContent = `${data.nombre_mes} ${data.anio}`;
            renderizarGrid(data.calendario);

        } catch (err) {
            console.error("Error al cargar calendario:", err);
            gridDias.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #ef4444;">
                    <i class="fa-solid fa-triangle-exclamation fa-2x"></i>
                    <p style="margin-top: 10px;">Error al conectar con el servidor.</p>
                </div>
            `;
        }
    }

    function renderizarGrid(semanas) {
        gridDias.innerHTML = "";

        semanas.forEach(semana => {
            semana.forEach(celda => {
                const div = document.createElement("div");

                if (celda.vacio) {
                    div.className = "cal-cell cal-empty";
                    gridDias.appendChild(div);
                    return;
                }

                div.className = "cal-cell";

                // Clases por estado
                if (celda.estado === "disponible") {
                    div.classList.add("cal-disponible");
                } else if (celda.estado === "reservado") {
                    div.classList.add("cal-reservado");
                } else if (celda.estado === "pasado") {
                    div.classList.add("cal-pasado");
                }

                if (celda.es_hoy) {
                    div.classList.add("cal-hoy");
                }

                // Contenido de la celda
                let badgeText = "Disponible";
                let badgeClass = "cal-badge";

                if (celda.estado === "reservado") {
                    badgeText = "Reservado";
                } else if (celda.estado === "pasado") {
                    badgeText = "Pasado";
                }

                const hoyBadge = celda.es_hoy ? '<span class="cal-hoy-indicator">HOY</span>' : '';

                div.innerHTML = `
                    <div class="cal-cell-header">
                        <span class="cal-day-number">${celda.dia}</span>
                        ${hoyBadge}
                        <span class="${badgeClass}">${badgeText}</span>
                    </div>
                    ${celda.estado === "disponible" ? `
                        <div class="cal-action-hint">
                            <i class="fa-solid fa-sparkles"></i> Apartar
                        </div>
                    ` : ""}
                `;

                // Interacción al hacer clic
                if (celda.estado === "disponible") {
                    div.addEventListener("click", () => {
                        abrirModalReserva(celda.fecha);
                    });
                } else if (celda.estado === "reservado") {
                    div.addEventListener("click", () => {
                        mostrarToast(`El día ${celda.fecha} ya ha sido reservado para una pedida exclusiva. Por favor elige otro día disponible. 💍`, "info");
                    });
                }

                gridDias.appendChild(div);
            });
        });
    }

    // ==========================================
    // MODAL DE RESERVA
    // ==========================================
    function abrirModalReserva(fecha) {
        inputFecha.value = fecha;
        modalFechaTexto.textContent = formatearFecha(fecha);
        modalReserva.classList.add("active");
        document.body.style.overflow = "hidden";
        setTimeout(() => document.getElementById("inputNombre").focus(), 100);
    }

    function cerrarModalReserva() {
        modalReserva.classList.remove("active");
        document.body.style.overflow = "auto";
        formReserva.reset();
    }

    btnCerrarModal.addEventListener("click", cerrarModalReserva);
    btnCancelarModal.addEventListener("click", cerrarModalReserva);

    modalReserva.addEventListener("click", (e) => {
        if (e.target === modalReserva) {
            cerrarModalReserva();
        }
    });

    // Enviar Formulario de Reserva
    formReserva.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = {
            fecha: inputFecha.value,
            nombre: document.getElementById("inputNombre").value.trim(),
            telefono: document.getElementById("inputTelefono").value.trim(),
            hora: selectHora.value.trim(),
            tipo: selectTipo.value,
            observaciones: document.getElementById("inputObservaciones").value.trim()
        };

        if (!formData.nombre || !formData.telefono || !formData.hora) {
            mostrarToast("Por favor completa los campos requeridos.", "error");
            return;
        }

        btnConfirmarReserva.disabled = true;
        btnConfirmarReserva.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Registrando...`;

        try {
            const resp = await fetch("/api/reservar", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });

            const data = await resp.json();

            if (!resp.ok || !data.success) {
                mostrarToast(data.message || "Error al realizar la reserva.", "error");
                btnConfirmarReserva.disabled = false;
                btnConfirmarReserva.innerHTML = `<i class="fa-solid fa-heart"></i> Confirmar y Apartar Fecha`;
                return;
            }

            // Éxito: Cerrar modal de reserva, recargar calendario y abrir modal de éxito
            cerrarModalReserva();
            cargarCalendario(estado.anio, estado.mes);
            abrirModalExito(data.reserva);
            mostrarToast("¡Reserva completada con éxito! 💍", "success");

        } catch (err) {
            console.error(err);
            mostrarToast("Error de conexión al guardar reserva.", "error");
        } finally {
            btnConfirmarReserva.disabled = false;
            btnConfirmarReserva.innerHTML = `<i class="fa-solid fa-heart"></i> Confirmar y Apartar Fecha`;
        }
    });

    // ==========================================
    // MODAL DE ÉXITO Y ENLACE WHATSAPP
    // ==========================================
    function abrirModalExito(reserva) {
        resumenExito.innerHTML = `
            <div class="resumen-line">
                <span class="resumen-label">Fecha Reservada:</span>
                <span class="resumen-val">${reserva.fecha}</span>
            </div>
            <div class="resumen-line">
                <span class="resumen-label">Pareja:</span>
                <span class="resumen-val">${reserva.nombre}</span>
            </div>
            <div class="resumen-line">
                <span class="resumen-label">Horario:</span>
                <span class="resumen-val">${reserva.hora}</span>
            </div>
            <div class="resumen-line">
                <span class="resumen-label">Estilo de Pedida:</span>
                <span class="resumen-val">${reserva.tipo}</span>
            </div>
        `;

        // Generar texto para WhatsApp preformateado
        const textoWhatsapp = encodeURIComponent(
            `¡Hola! 💍 Acabo de reservar nuestra Pedida de Mano en su página web:\n\n` +
            `📅 *Fecha:* ${reserva.fecha}\n` +
            `🕒 *Horario:* ${reserva.hora}\n` +
            `👥 *Pareja:* ${reserva.nombre}\n` +
            `✨ *Estilo:* ${reserva.tipo}\n` +
            (reserva.observaciones ? `📝 *Observaciones:* ${reserva.observaciones}\n` : "") +
            `\n¡Queremos afinar todos los detalles sorpresa! Muchas gracias.`
        );

        btnEnviarWhatsappExito.href = `https://wa.me/?text=${textoWhatsapp}`;

        modalExito.classList.add("active");
        document.body.style.overflow = "hidden";
    }

    btnCerrarExito.addEventListener("click", () => {
        modalExito.classList.remove("active");
        document.body.style.overflow = "auto";
    });

    // ==========================================
    // UTILIDADES
    // ==========================================
    function formatearFecha(fechaIso) {
        try {
            const [y, m, d] = fechaIso.split("-");
            const meses = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ];
            return `${d} de ${meses[parseInt(m, 10) - 1]} de ${y}`;
        } catch {
            return fechaIso;
        }
    }

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
