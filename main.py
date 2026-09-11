import os
import shutil
import flet as ft
import urllib.parse
from database import (
    inicializar_db, guardar_cita, obtener_citas, 
    actualizar_estado, eliminar_cita, obtener_resumen_financiero,
    guardar_licencia_db, obtener_licencia_db, DB_NAME
)
from licencia import obtener_device_id, validar_licencia
from datetime import datetime

NOMBRES_MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

def main(page: ft.Page):
    inicializar_db()

    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[ft.Locale("es", "ES"), ft.Locale("es", "CO")],
        current_locale=ft.Locale("es", "ES")
    )

    page.title = "Agenda Citas Pro"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10
    
    COLOR_PRIMARIO = "#ec4899"
    COLOR_FONDO = "#f8fafc"
    page.bgcolor = COLOR_FONDO

    page.window.width = 420
    page.window.height = 750
    page.window.resizable = False

    if not hasattr(page, "anio_activo"):
        page.anio_activo = 2026
    
    if not hasattr(page, "mes_activo"):
        page.mes_activo = 9

    contenedor_principal = ft.Container(expand=True)

    def cerrar_manual(e):
        if manual_container in page.overlay:
            page.overlay.remove(manual_container)
            page.update()

    manual_container = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.AUTO_AWESOME, color=COLOR_PRIMARIO),
                            ft.Text("📖 Manual de Usuario Paso a Paso", weight=ft.FontWeight.BOLD, color=COLOR_PRIMARIO, size=15)
                        ]),
                        ft.IconButton(icon=ft.Icons.CLOSE, icon_color="#64748b", on_click=cerrar_manual)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=5),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Text("1️⃣ 💅 Pestaña 'Citas' (Cómo agendar)", weight=ft.FontWeight.BOLD, size=12, color="#0f172a"),
                            ft.Text(
                                "• **Nombre de la clienta:** Escribe el nombre de quién te visita.\n"
                                "• **Teléfono / WhatsApp:** Escribe su número para poder enviarle recordatorios automáticos.\n"
                                "• **Fecha:** Toca el icono del calendario para elegir el día de la cita.\n"
                                "• **Hora, Min y Jornada:** Selecciona la hora exacta (Ej. 04:00 PM).\n"
                                "• **Servicio:** Selecciona el trabajo que le harás a la clienta.\n"
                                "• **Precio Total ($):** Cuánto le cobrarás en total.\n"
                                "• **Botón 'Guardar Cita':** Guarda la cita en tu lista.\n\n"
                                "📲 **Botones de cada tarjeta de cita:**\n"
                                "• 🟦 **Botón azul:** Marca la cita como 'Confirmada'.\n"
                                "• 🟩 **Botón verde:** Finaliza la cita (suma el dinero a tus ingresos).\n"
                                "• 🟢 **Botón WhatsApp:** Abre un mensaje listo para enviar a la clienta.\n"
                                "• 🟥 **Botón rojo:** Elimina la cita si hubo un error.",
                                size=11, 
                                color="#475569"
                            ),
                            ft.Divider(height=10),
                            ft.Text("2️⃣ 📊 Pestaña 'Ingresos' (Tu Alcancía)", weight=ft.FontWeight.BOLD, size=12, color="#0f172a"),
                            ft.Text("• Aquí ves el dinero acumulado de tu negocio. Puedes usar las flechitas ⬅️ ➡️ para consultar las ganancias exactas de cualquier mes o año pasado.", size=11, color="#475569"),
                            ft.Divider(height=10),
                            ft.Text("3️⃣ 📜 Pestaña 'Historial'", weight=ft.FontWeight.BOLD, size=12, color="#0f172a"),
                            ft.Text("• Muestra el listado de todas las clientas que ya fueron atendidas y pagaron. Puedes buscarlas escribiendo su nombre arriba.", size=11, color="#475569"),
                            ft.Divider(height=10),
                            ft.Text("4️⃣ ⚙️ Pestaña 'Ajustes' (Activación y Respaldo)", weight=ft.FontWeight.BOLD, size=12, color="#0f172a"),
                            ft.Text(
                                "• **¿Cómo activar la app?**\n"
                                "  1. Entra a la pestaña Ajustes.\n"
                                "  2. Verás un código largo en números y letras llamado 'ID de tu Dispositivo'.\n"
                                "  3. Copia ese código o envíaselo por WhatsApp a la persona que te vendió la app.\n"
                                "  4. Te darán una 'Clave de Activación'. Escríbela en la casilla y toca 'Activar Licencia'. ¡Listo!\n\n"
                                "• **¿Cómo hacer una Copia de Seguridad (Cambio de teléfono)?**\n"
                                "  Toca el botón 'Crear Copia de Seguridad'. Esto guarda un archivo seguro con todas tus citas e ingresos para que no pierdas nada si cambias de celular.",
                                size=11, 
                                color="#475569"
                            ),
                        ], scroll=ft.ScrollMode.AUTO, tight=True),
                        height=330
                    ),
                    ft.Divider(height=10),
                    ft.ElevatedButton("¡Entendido, a trabajar! 🚀", bgcolor=COLOR_PRIMARIO, color="white", on_click=cerrar_manual, width=340)
                ], tight=True),
                bgcolor="white",
                padding=15,
                border_radius=15,
                width=370,
                shadow=ft.BoxShadow(spread_radius=2, blur_radius=20, color=ft.Colors.BLACK26)
            )
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor="#80000000",
        expand=True,
        padding=10
    )

    def abrir_ayuda(e):
        if manual_container not in page.overlay:
            page.overlay.append(manual_container)
        page.update()

    header_logo = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Icon(ft.Icons.AUTO_AWESOME, color=COLOR_PRIMARIO, size=24),
                ft.Text("Agenda Citas Pro", size=18, weight=ft.FontWeight.BOLD, color="#0f172a"),
            ]),
            ft.IconButton(
                icon=ft.Icons.HELP_OUTLINE,
                icon_color=COLOR_PRIMARIO,
                tooltip="Manual de Ayuda",
                on_click=abrir_ayuda
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=5
    )

    txt_key = ft.TextField(
        label="Clave de Activación", 
        hint_text="Ej. E13A53549646",
        border_color=COLOR_PRIMARIO
    )

    txt_cliente = ft.TextField(label="Nombre de la clienta", hint_text="Ej. Laura Gómez", border_color=COLOR_PRIMARIO)
    txt_telefono = ft.TextField(label="Teléfono / WhatsApp", hint_text="Ej. 3201234567", keyboard_type=ft.KeyboardType.PHONE)
    
    txt_fecha_display = ft.TextField(
        label="Fecha de la Cita", 
        value=datetime.now().strftime("%Y-%m-%d"), 
        read_only=True,
        expand=True
    )

    def cambiar_fecha(e):
        if date_picker.value:
            txt_fecha_display.value = date_picker.value.strftime("%Y-%m-%d")
            page.update()

    date_picker = ft.DatePicker(
        first_date=datetime(2026, 1, 1),
        last_date=datetime(2036, 12, 31),
        on_change=cambiar_fecha,
        help_text="SELECCIONA LA FECHA",
        cancel_text="CANCELAR",
        confirm_text="ACEPTAR",
        locale=ft.Locale("es", "ES")
    )
    page.overlay.append(date_picker)

    def abrir_calendario(e):
        date_picker.open = True
        page.update()

    btn_calendario = ft.IconButton(
        icon=ft.Icons.CALENDAR_MONTH,
        icon_color=COLOR_PRIMARIO,
        tooltip="Seleccionar Fecha",
        on_click=abrir_calendario
    )

    dd_hora = ft.Dropdown(
        label="Hora",
        value="10",
        options=[ft.dropdown.Option(f"{i:02d}") for i in range(1, 13)],
        width=95
    )

    dd_minuto = ft.Dropdown(
        label="Min",
        value="00",
        options=[
            ft.dropdown.Option("00"),
            ft.dropdown.Option("15"),
            ft.dropdown.Option("30"),
            ft.dropdown.Option("45")
        ],
        width=95
    )

    dd_ampm = ft.Dropdown(
        label="Jornada",
        value="AM",
        options=[
            ft.dropdown.Option("AM"),
            ft.dropdown.Option("PM")
        ],
        width=110
    )

    dd_servicio = ft.Dropdown(
        label="Servicio",
        options=[
            ft.dropdown.Option("Semi Permanente"),
            ft.dropdown.Option("Press On"),
            ft.dropdown.Option("Poligel"),
            ft.dropdown.Option("Buildelgel"),
            ft.dropdown.Option("Acrilica"),
            ft.dropdown.Option("Tradicional"),
            ft.dropdown.Option("Cepillado"),
            ft.dropdown.Option("Keratina"),
        ],
    )
    
    txt_precio = ft.TextField(label="Precio Total ($)", hint_text="Ej. 45000", keyboard_type=ft.KeyboardType.NUMBER)
    txt_notas = ft.TextField(label="Notas adicionales", multiline=True, min_lines=2)

    txt_buscar = ft.TextField(
        label="Buscar clienta...",
        prefix_icon=ft.Icons.SEARCH,
        border_color=COLOR_PRIMARIO,
        dense=True
    )

    def actualizar_busqueda(e):
        contenedor_principal.content = vista_historial()
        page.update()

    txt_buscar.on_change = actualizar_busqueda

    def vista_bloqueada():
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.LOCK_OUTLINED, size=64, color="red"),
                ft.Text("🔒 Función Bloqueada", size=20, weight=ft.FontWeight.BOLD, color="#0f172a"),
                ft.Text(
                    "Para agendar citas, activa tu licencia en la pestaña Ajustes.", 
                    text_align=ft.TextAlign.CENTER, 
                    color="#64748b"
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            expand=True
        )

    def registrar_cita(e):
        if not txt_cliente.value or not dd_servicio.value:
            page.snack_bar = ft.SnackBar(ft.Text("Completa el nombre y el servicio"), open=True)
            page.update()
            return
        
        precio_val = float(txt_precio.value) if txt_precio.value else 0.0
        hora_formateada = f"{dd_hora.value}:{dd_minuto.value} {dd_ampm.value}"

        guardar_cita(
            cliente=txt_cliente.value,
            telefono=txt_telefono.value or "",
            fecha=txt_fecha_display.value,
            hora=hora_formateada,
            servicio=dd_servicio.value,
            precio=precio_val,
            estado="En Proceso",
            notas=txt_notas.value or ""
        )
        
        txt_cliente.value = ""
        txt_telefono.value = ""
        txt_precio.value = ""
        txt_notas.value = ""
        
        page.snack_bar = ft.SnackBar(ft.Text("¡Cita guardada con éxito! 💅"), open=True)
        contenedor_principal.content = vista_citas()
        page.update()

    def cambiar_estado(cita_id, nuevo_estado):
        actualizar_estado(cita_id, nuevo_estado)
        if nuevo_estado == "Terminada":
            page.snack_bar = ft.SnackBar(ft.Text("¡Cita finalizada y registrada en ingresos! 💰"), open=True)
        else:
            page.snack_bar = ft.SnackBar(ft.Text(f"Cita marcada como: {nuevo_estado}"), open=True)
        contenedor_principal.content = vista_citas()
        page.update()

    def borrar_cita(cita_id):
        eliminar_cita(cita_id)
        page.snack_bar = ft.SnackBar(ft.Text("Cita eliminada de la agenda"), open=True)
        contenedor_principal.content = vista_citas()
        page.update()

    def enviar_whatsapp(telefono, cliente, fecha, hora, servicio):
        tel_limpio = "".join(filter(str.isdigit, str(telefono)))
        if not tel_limpio:
            page.snack_bar = ft.SnackBar(ft.Text("Esta cita no tiene un número registrado"), open=True)
            page.update()
            return

        mensaje = f"¡Hola {cliente}! 👋 Te escribimos para recordarte tu cita de {servicio} programada para el {fecha} a las {hora}. ¡Te esperamos con mucho gusto! 💅✨"
        mensaje_enc = urllib.parse.quote(mensaje)
        url = f"https://wa.me/57{tel_limpio}?text={mensaje_enc}" if len(tel_limpio) == 10 else f"https://wa.me/{tel_limpio}?text={mensaje_enc}"
        page.launch_url(url)

    def vista_citas():
        if not validar_licencia(obtener_licencia_db()):
            return vista_bloqueada()

        citas = obtener_citas()
        citas_activas = [c for c in citas if str(c["estado"]).strip() != "Terminada"]
        lista_tarjetas = []

        for cita in citas_activas:
            est = cita["estado"]
            
            if est == "Confirmada":
                bg_estado = "#dbeafe"
                txt_estado_color = "#1d4ed8"
            else:
                bg_estado = "#fef3c7"
                txt_estado_color = "#d97706"

            btn_confirmar = ft.IconButton(
                icon=ft.Icons.TASK_ALT,
                icon_color="white",
                bgcolor="#3b82f6",
                tooltip="Marcar como Confirmada",
                on_click=lambda e, cid=cita["id"]: cambiar_estado(cid, "Confirmada")
            )

            btn_terminar = ft.IconButton(
                icon=ft.Icons.CHECK_CIRCLE_ROUNDED,
                icon_color="white",
                bgcolor="#10b981",
                tooltip="Marcar como Terminada",
                on_click=lambda e, cid=cita["id"]: cambiar_estado(cid, "Terminada")
            )

            tarjeta = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"👤 {cita['cliente']}", weight=ft.FontWeight.BOLD, size=16),
                            ft.Container(
                                content=ft.Text(est, color=txt_estado_color, size=12, weight=ft.FontWeight.BOLD),
                                bgcolor=bg_estado,
                                padding=5,
                                border_radius=5
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(f"💅 {cita['servicio']} - ${cita['precio']:,.0f}", color="#334155"),
                        ft.Text(f"📅 {cita['fecha']} a las {cita['hora']}", color="#64748b", size=13),
                        
                        ft.Divider(height=8, color="transparent"),

                        ft.Row([
                            btn_confirmar if est != "Confirmada" else ft.Container(),
                            btn_terminar,
                            ft.IconButton(
                                icon=ft.Icons.PHONE,
                                icon_color="white",
                                bgcolor="#25D366",
                                tooltip="Enviar WhatsApp",
                                on_click=lambda e, tel=cita["telefono"], cli=cita["cliente"], fec=cita["fecha"], hor=cita["hora"], ser=cita["servicio"]: enviar_whatsapp(tel, cli, fec, hor, ser)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINED,
                                icon_color="white",
                                bgcolor="red",
                                tooltip="Eliminar Cita",
                                on_click=lambda e, cid=cita["id"]: borrar_cita(cid)
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=6)
                    ]),
                    padding=12
                )
            )
            lista_tarjetas.append(tarjeta)

        return ft.Container(
            content=ft.Column([
                header_logo,
                ft.Text("💅 Agendar Cita", size=18, weight=ft.FontWeight.BOLD, color="#0f172a"),
                txt_cliente,
                txt_telefono,
                ft.Row([txt_fecha_display, btn_calendario], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([dd_hora, dd_minuto, dd_ampm], spacing=5, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                dd_servicio,
                txt_precio,
                txt_notas,
                ft.ElevatedButton(
                    "Guardar Cita", 
                    bgcolor=COLOR_PRIMARIO, 
                    color="white", 
                    on_click=registrar_cita,
                    width=400
                ),
                ft.Divider(height=20, color="transparent"),
                ft.Text("📅 Citas Registradas", size=18, weight=ft.FontWeight.BOLD, color="#0f172a"),
                ft.Column(lista_tarjetas) if lista_tarjetas else ft.Text("No hay citas activas programadas.", color="#94a3b8")
            ], scroll=ft.ScrollMode.AUTO),
            padding=10
        )

    def vista_ingresos():
        if not validar_licencia(obtener_licencia_db()):
            return vista_bloqueada()

        anio_actual = int(page.anio_activo)
        mes_actual = int(page.mes_activo)

        datos_financieros = obtener_resumen_financiero(anio_sel=anio_actual, mes_sel=mes_actual)

        lbl_total_acumulado = ft.Text(f"${datos_financieros['total_acumulado']:,.0f}", size=24, weight=ft.FontWeight.BOLD, color="#15803d")
        lbl_total_filtrado = ft.Text(f"${datos_financieros['total_filtrado']:,.0f}", size=22, weight=ft.FontWeight.BOLD, color="#1d4ed8")
        lbl_total_mes = ft.Text(f"${datos_financieros['total_mes']:,.0f}", size=24, weight=ft.FontWeight.BOLD, color="#9333ea")
        
        lbl_anio_mostrado = ft.Text(f"Año: {anio_actual}", size=15, weight=ft.FontWeight.BOLD, color="#0f172a")
        lbl_mes_mostrado = ft.Text(f"Mes: {NOMBRES_MESES[mes_actual - 1]}", size=15, weight=ft.FontWeight.BOLD, color="#0f172a")

        def cambiar_anio(delta):
            nuevo_a = anio_actual + delta
            if 2026 <= nuevo_a <= 2036:
                page.anio_activo = nuevo_a
                contenedor_principal.content = vista_ingresos()
                page.update()

        def cambiar_mes(delta):
            nuevo_m = mes_actual + delta
            if nuevo_m > 12:
                page.mes_activo = 1
                if anio_actual < 2036:
                    page.anio_activo = anio_actual + 1
            elif nuevo_m < 1:
                page.mes_activo = 12
                if anio_actual > 2026:
                    page.anio_activo = anio_actual - 1
            else:
                page.mes_activo = nuevo_m
            
            contenedor_principal.content = vista_ingresos()
            page.update()

        tarjeta_resultado_anio = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"Total del Año {anio_actual}", color="#1e40af", size=12, weight=ft.FontWeight.W_500),
                    lbl_total_filtrado
                ]),
                padding=12,
                bgcolor="#dbeafe",
                border_radius=10
            )
        )

        tarjeta_resultado_mes = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"Total del Mes ({NOMBRES_MESES[mes_actual - 1]} {anio_actual})", color="#6b21a8", size=12, weight=ft.FontWeight.W_500),
                    lbl_total_mes
                ]),
                padding=12,
                bgcolor="#f3e8ff",
                border_radius=10
            )
        )

        return ft.Container(
            content=ft.Column([
                header_logo,
                ft.Text("📊 Reporte de Ingresos Realizados", size=18, weight=ft.FontWeight.BOLD, color="#0f172a"),
                ft.Divider(height=5, color="transparent"),
                
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.SAVINGS, color="#15803d", size=22),
                                ft.Text("Total Acumulado Histórico", color="#166534", size=13, weight=ft.FontWeight.BOLD),
                            ]),
                            lbl_total_acumulado,
                            ft.Text("Suma total de dinero cobrado en la historia del negocio", color="#4b5563", size=11)
                        ]),
                        padding=15,
                        bgcolor="#dcfce7",
                        border_radius=10
                    )
                ),
                
                ft.Divider(height=5, color="transparent"),
                ft.Text("🔍 Consulta por Año", size=15, weight=ft.FontWeight.BOLD, color="#0f172a"),
                ft.Row([
                    ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=lambda e: cambiar_anio(-1), icon_color=COLOR_PRIMARIO),
                    lbl_anio_mostrado,
                    ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, on_click=lambda e: cambiar_anio(1), icon_color=COLOR_PRIMARIO),
                ], alignment=ft.MainAxisAlignment.CENTER),

                tarjeta_resultado_anio,

                ft.Divider(height=5, color="transparent"),
                ft.Text("📅 Consulta por Mes", size=15, weight=ft.FontWeight.BOLD, color="#0f172a"),
                ft.Row([
                    ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=lambda e: cambiar_mes(-1), icon_color=COLOR_PRIMARIO),
                    lbl_mes_mostrado,
                    ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, on_click=lambda e: cambiar_mes(1), icon_color=COLOR_PRIMARIO),
                ], alignment=ft.MainAxisAlignment.CENTER),

                tarjeta_resultado_mes
            ], scroll=ft.ScrollMode.AUTO),
            padding=10
        )

    def vista_historial():
        if not validar_licencia(obtener_licencia_db()):
            return vista_bloqueada()

        citas = obtener_citas()
        terminadas = [c for c in citas if str(c["estado"]).strip() == "Terminada"]
        
        texto_busqueda = (txt_buscar.value or "").lower().strip()
        if texto_busqueda:
            terminadas = [c for c in terminadas if texto_busqueda in c["cliente"].lower()]

        filas_tabla = []
        filas_tabla.append(
            ft.Container(
                content=ft.Row([
                    ft.Text("Clienta", weight=ft.FontWeight.BOLD, size=12, expand=2),
                    ft.Text("Servicio", weight=ft.FontWeight.BOLD, size=12, expand=2),
                    ft.Text("Fecha", weight=ft.FontWeight.BOLD, size=12, expand=2),
                    ft.Text("Precio", weight=ft.FontWeight.BOLD, size=12, expand=1, text_align=ft.TextAlign.RIGHT),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor="#e2e8f0",
                padding=8,
                border_radius=5
            )
        )

        for cita in terminadas:
            fila = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"👤 {cita['cliente']}", size=12, expand=2, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(cita['servicio'], size=12, expand=2, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(cita['fecha'], size=11, color="#64748b", expand=2),
                        ft.Text(f"${cita['precio']:,.0f}", size=12, weight=ft.FontWeight.BOLD, color="#15803d", expand=1, text_align=ft.TextAlign.RIGHT),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=4, color="#f1f5f9")
                ]),
                padding=4
            )
            filas_tabla.append(fila)

        return ft.Container(
            content=ft.Column([
                header_logo,
                ft.Text("📜 Historial de Citas Terminadas", size=18, weight=ft.FontWeight.BOLD, color="#0f172a"),
                ft.Divider(height=5, color="transparent"),
                txt_buscar,
                ft.Divider(height=10, color="transparent"),
                ft.Column(filas_tabla, scroll=ft.ScrollMode.AUTO, spacing=0) if terminadas else ft.Text("No hay registros en el historial.", color="#94a3b8")
            ], scroll=ft.ScrollMode.AUTO),
            padding=10
        )

    def vista_ajustes():
        dev_id = obtener_device_id()
        licencia_actual = obtener_licencia_db()
        esta_activa = validar_licencia(licencia_actual)

        if licencia_actual and not txt_key.value:
            txt_key.value = licencia_actual

        lbl_estado = ft.Text(
            "✅ Licencia Activa" if esta_activa else "❌ App no activada", 
            color="green" if esta_activa else "red", 
            weight=ft.FontWeight.BOLD,
            size=16
        )

        def activar(e):
            clave_ingresada = txt_key.value.strip().upper() if txt_key.value else ""
            if validar_licencia(clave_ingresada):
                guardar_licencia_db(clave_ingresada)
                page.snack_bar = ft.SnackBar(ft.Text("¡App Activada con éxito! 🎉"), open=True)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Clave de activación no válida"), open=True)
            
            contenedor_principal.content = vista_ajustes()
            page.update()

        def exportar_respaldo(e):
            try:
                ruta_respaldo = "citas_copia_seguridad.db"
                shutil.copyfile(DB_NAME, ruta_respaldo)
                page.snack_bar = ft.SnackBar(ft.Text(f"Respaldo creado con éxito: {os.path.abspath(ruta_respaldo)} 📂"), open=True)
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error al respaldar: {ex}"), open=True)
            page.update()

        btn_activar = ft.ElevatedButton(
            "Activar Licencia", 
            bgcolor=COLOR_PRIMARIO, 
            color="white", 
            on_click=activar, 
            width=400
        )

        btn_exportar = ft.ElevatedButton(
            "Crear Copia de Seguridad",
            icon=ft.Icons.BACKUP,
            bgcolor="#0284c7",
            color="white",
            on_click=exportar_respaldo,
            width=360
        )

        elementos_ajustes = [
            ft.Text("🔐 Licencia del Dispositivo", size=16, weight=ft.FontWeight.BOLD, color="#0f172a"),
            ft.Divider(height=10),
            ft.Text("ID de tu Dispositivo:", weight=ft.FontWeight.BOLD, size=13),
            ft.Text(dev_id, size=18, color=COLOR_PRIMARIO, weight=ft.FontWeight.BOLD),
            ft.Text("Envía este ID a soporte para recibir tu clave.", size=12, color="#64748b"),
            ft.Divider(height=10),
            lbl_estado,
            txt_key,
        ]

        if not esta_activa:
            elementos_ajustes.append(btn_activar)
        else:
            elementos_ajustes.append(ft.Text("✨ Tu software está registrado y operando al 100%.", size=12, color="#15803d", italic=True))

        tarjeta_licencia = ft.Card(
            content=ft.Container(
                content=ft.Column(elementos_ajustes),
                padding=15
            )
        )

        tarjeta_backup = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📱 Copia de Seguridad (Cambio de Teléfono)", size=14, weight=ft.FontWeight.BOLD, color="#0f172a"),
                    ft.Text("Crea una copia exacta de tus citas e ingresos para migrar fácilmente de celular.", size=11, color="#64748b"),
                    ft.Divider(height=5),
                    btn_exportar
                ], spacing=8),
                padding=15
            )
        )

        tarjeta_autor = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CODE, color=COLOR_PRIMARIO, size=18),
                        ft.Text("Autor: Luis Diaz", size=12, weight=ft.FontWeight.BOLD, color="#334155")
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([
                        ft.Icon(ft.Icons.CHAT, color="#25D366", size=16),
                        ft.Text("WhatsApp: @luisdiaz9s", size=12, weight=ft.FontWeight.W_500, color="#475569")
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=4),
                padding=12
            )
        )

        return ft.Container(
            content=ft.Column([
                header_logo,
                ft.Text("⚙️ Ajustes y Licencia", size=22, weight=ft.FontWeight.BOLD, color="#0f172a"),
                ft.Divider(height=10, color="transparent"),
                tarjeta_licencia,
                tarjeta_backup,
                tarjeta_autor,
            ], scroll=ft.ScrollMode.AUTO),
            padding=10
        )

    def cambiar_pestana(e):
        indice = e.control.selected_index
        if indice == 0:
            contenedor_principal.content = vista_citas()
        elif indice == 1:
            contenedor_principal.content = vista_ingresos()
        elif indice == 2:
            contenedor_principal.content = vista_historial()
        elif indice == 3:
            contenedor_principal.content = vista_ajustes()
        page.update()

    contenedor_principal.content = vista_citas()

    barra_navegacion = ft.NavigationBar(
        selected_index=0,
        bgcolor="white",
        on_change=cambiar_pestana,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.CALENDAR_MONTH, label="Citas"),
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART, label="Ingresos"),
            ft.NavigationBarDestination(icon=ft.Icons.HISTORY, label="Historial"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Ajustes"),
        ]
    )

    page.add(
        contenedor_principal,
        barra_navegacion
    )

if __name__ == "__main__":
    ft.app(target=main)