from __future__ import annotations

from datetime import date, datetime, timedelta
from io import BytesIO
import json

import altair as alt
import pandas as pd
import streamlit as st
from supabase import create_client, Client

st.set_page_config(
    page_title="Gestión de Tareas - Sistema Empresarial", 
    layout="wide", 
    initial_sidebar_state="expanded",
    page_icon="📋"
)

# ============================================================================
# CONFIGURACIÓN DE USUARIOS Y AUTENTICACIÓN
# ============================================================================

USUARIOS = {
    "julio.yroba": {
        "password": "jefe123",
        "nombre": "Julio Yroba",
        "rol": "Jefe de Proyecto",
    },
    "jose.quintero": {
        "password": "jefe123",
        "nombre": "José Quintero",
        "rol": "Jefe de Proyecto",
    },
    "matias.riquelme": {
        "password": "jefe123",
        "nombre": "Matías Riquelme",
        "rol": "Jefe de Proyecto",
    },
    "gerente.proyectos": {
        "password": "gerente123",
        "nombre": "Gerente de Proyectos",
        "rol": "Gerencia",
    },
    "gerente.general": {
        "password": "admin123",
        "nombre": "Gerente General",
        "rol": "Gerencia",
    }
}

JEFES_PROYECTO = ["Julio Yroba", "José Quintero", "Matías Riquelme"]
ESTADOS = ["Pendiente", "En Proceso", "Completada"]

# ============================================================================
# CONEXIÓN A SUPABASE
# ============================================================================

@st.cache_resource
def get_supabase_client() -> Client:
    """Obtener cliente de Supabase (con cache para reutilizar conexión)"""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error conectando a Supabase: {e}")
        st.stop()


# ============================================================================
# FUNCIONES DE BASE DE DATOS
# ============================================================================

def load_tasks_from_db() -> list:
    """Cargar tareas desde Supabase"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("tareas").select("*").order("id").execute()
        
        tasks = []
        for row in response.data:
            tasks.append({
                "id": row["id"],
                "descripcion": row["descripcion"],
                "fecha_objetivo": date.fromisoformat(row["fecha_objetivo"]),
                "estado": row["estado"],
                "autor": row["autor"],
                "asignado": row["asignado"],
                "cliente": row["cliente"],
                "comentarios": json.loads(row["comentarios"]) if row["comentarios"] else []
            })
        return tasks
    except Exception as e:
        st.error(f"Error cargando tareas: {e}")
        return []


def save_task_to_db(task: dict) -> bool:
    """Guardar una tarea nueva en Supabase"""
    try:
        supabase = get_supabase_client()
        task_data = {
            "descripcion": task["descripcion"],
            "fecha_objetivo": task["fecha_objetivo"].isoformat(),
            "estado": task["estado"],
            "autor": task["autor"],
            "asignado": task["asignado"],
            "cliente": task["cliente"],
            "comentarios": json.dumps(task.get("comentarios", []), ensure_ascii=False)
        }
        supabase.table("tareas").insert(task_data).execute()
        return True
    except Exception as e:
        st.error(f"Error guardando tarea: {e}")
        return False


def update_task_in_db(task_id: int, updates: dict) -> bool:
    """Actualizar tarea en Supabase"""
    try:
        supabase = get_supabase_client()
        
        # Convertir fecha a string si existe
        if "fecha_objetivo" in updates and isinstance(updates["fecha_objetivo"], date):
            updates["fecha_objetivo"] = updates["fecha_objetivo"].isoformat()
        
        # Convertir comentarios a JSON si existe
        if "comentarios" in updates:
            updates["comentarios"] = json.dumps(updates["comentarios"], ensure_ascii=False)
        
        supabase.table("tareas").update(updates).eq("id", task_id).execute()
        return True
    except Exception as e:
        st.error(f"Error actualizando tarea: {e}")
        return False


def delete_task_from_db(task_id: int) -> bool:
    """Eliminar tarea de Supabase"""
    try:
        supabase = get_supabase_client()
        supabase.table("tareas").delete().eq("id", task_id).execute()
        return True
    except Exception as e:
        st.error(f"Error eliminando tarea: {e}")
        return False


# ============================================================================
# FUNCIONES DE AUTENTICACIÓN
# ============================================================================

def verificar_credenciales(username: str, password: str) -> dict | None:
    """Verificar credenciales de usuario"""
    if username in USUARIOS:
        if USUARIOS[username]["password"] == password:
            return USUARIOS[username]
    return None


def es_gerente() -> bool:
    """Verificar si el usuario actual es gerente"""
    if "user_info" not in st.session_state:
        return False
    return st.session_state.user_info["rol"] == "Gerencia"


def puede_editar_tarea(tarea: dict) -> bool:
    """Verificar si el usuario puede editar una tarea"""
    if es_gerente():
        return True
    # Jefes de proyecto pueden editar tareas asignadas a ellos
    return tarea["asignado"] == st.session_state.user_info["nombre"]


def puede_eliminar_tarea(tarea: dict) -> bool:
    """Verificar si el usuario puede eliminar una tarea"""
    # Solo gerentes pueden eliminar tareas
    return es_gerente()


def login_page() -> None:
    """Página de login"""
    st.markdown(
        """
        <style>
            .stApp {
                background: radial-gradient(circle at 20% 0%, #161b2d 0%, #0c1020 42%, #090d19 100%);
            }
            .login-container {
                max-width: 450px;
                margin: 100px auto;
                padding: 2.5rem;
                background: linear-gradient(135deg, #1d2744, #121a31);
                border: 1px solid #304067;
                border-radius: 20px;
                box-shadow: 0 15px 40px rgba(0,0,0,.4);
            }
            .login-title {
                text-align: center;
                color: #f2f5ff;
                font-size: 2.2rem;
                margin-bottom: 0.5rem;
                font-weight: 600;
            }
            .login-subtitle {
                text-align: center;
                color: #a9b5d1;
                margin-bottom: 2rem;
                font-size: 1rem;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.markdown("<h1 class='login-title'>🔐 Gestión de Tareas</h1>", unsafe_allow_html=True)
        st.markdown("<p class='login-subtitle'>Sistema Empresarial</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("👤 Usuario", placeholder="usuario.apellido")
            password = st.text_input("🔑 Contraseña", type="password", placeholder="********")
            submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if submit:
                user_info = verificar_credenciales(username, password)
                if user_info:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_info = user_info
                    st.success(f"✓ ¡Bienvenido, {user_info['nombre']}!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Información de usuarios demo
        with st.expander("ℹ️ Usuarios de prueba"):
            st.caption("**Jefes de Proyecto:**")
            st.caption("• julio.yroba / jefe123")
            st.caption("• jose.quintero / jefe123")
            st.caption("• matias.riquelme / jefe123")
            st.caption("")
            st.caption("**Gerencia:**")
            st.caption("• gerente.proyectos / gerente123")
            st.caption("• gerente.general / admin123")


def logout() -> None:
    """Cerrar sesión"""
    for key in ['logged_in', 'username', 'user_info']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


# ============================================================================
# INICIALIZACIÓN DE DATOS
# ============================================================================

def init_data() -> None:
    """Inicializar datos desde Supabase"""
    if "tasks_loaded" not in st.session_state:
        st.session_state.tasks = load_tasks_from_db()
        st.session_state.tasks_loaded = True


def refresh_tasks() -> None:
    """Refrescar tareas desde la base de datos"""
    st.session_state.tasks = load_tasks_from_db()


def to_df() -> pd.DataFrame:
    """Convertir tareas a DataFrame"""
    df = pd.DataFrame(st.session_state.tasks)
    if df.empty:
        return pd.DataFrame(columns=["id", "descripcion", "fecha_objetivo", "estado", "autor", "asignado", "cliente", "comentarios"])
    df["fecha_objetivo"] = pd.to_datetime(df["fecha_objetivo"]).dt.date
    return df


# ============================================================================
# ESTILOS CSS
# ============================================================================

def inject_css() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background: radial-gradient(circle at 20% 0%, #161b2d 0%, #0c1020 42%, #090d19 100%);
                color: #e8ebf3;
            }
            .block-container {
                max-width: 1100px;
                padding-top: 1.5rem;
                padding-bottom: 2.5rem;
            }
            .hero {
                background: linear-gradient(135deg, #1d2744, #121a31);
                border: 1px solid #304067;
                border-radius: 18px;
                padding: 1.2rem 1.4rem;
                margin-bottom: 1rem;
                box-shadow: 0 10px 30px rgba(0,0,0,.35);
            }
            .hero h1 { margin: 0; font-size: 2rem; color: #f2f5ff; }
            .hero p { margin: 0.25rem 0 0; color: #a9b5d1; }
            .section {
                background: #10172b;
                border: 1px solid #243453;
                border-radius: 16px;
                padding: 1rem;
                margin-bottom: 0.9rem;
            }
            .section h3 { margin: 0 0 0.6rem; color: #f2f5ff; font-size: 1.1rem; }
            .person {
                background: #0d1324;
                border: 1px solid #2a3a5f;
                border-radius: 12px;
                padding: 0.8rem;
                min-height: unset;
            }
            .task {
                border-left: 5px solid #64748b;
                background: #111a31;
                border-radius: 8px;
                padding: 0.6rem 0.65rem;
                margin-bottom: 0.55rem;
                font-size: 0.91rem;
            }
            .p { border-left-color: #facc15; }
            .e { border-left-color: #fb923c; }
            .c { border-left-color: #4ade80; }
            .risk-yellow { border-left: 5px solid #facc15; }
            .risk-red { border-left: 5px solid #ef4444; }
            .chip {
                display:inline-block;padding:2px 8px;border-radius:999px;
                font-size:.75rem;font-weight:700;margin-right:6px;
            }
            .chip-p { background:#5c4509; color:#ffe9a3; }
            .chip-e { background:#663611; color:#ffd7b4; }
            .chip-c { background:#174229; color:#b4f5cf; }
            .muted { color: #9fb0d3; font-size: .9rem; }
            .person {
                background: #0d1324;
                border: 1px solid #2a3a5f;
                border-radius: 12px;
                padding: 0.8rem;
                min-height: unset;
            }
            .task.available {
                background: #064e3b;
                color: #a7f3d0;
                border-left: 5px solid #22c55e;
                padding: 0.45rem 0.6rem;
                border-radius: 8px;
                font-size: 0.85rem;
                margin-top: 0.4rem;
            }
            
            @media (max-width: 768px) {
                .block-container { 
                    padding: 0.5rem; 
                    max-width: 100%;
                }
                .hero h1 { font-size: 1.5rem; }
                .hero p { font-size: 0.85rem; }
                .task { font-size: 0.85rem; padding: 0.5rem; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# FUNCIONES DE UI
# ============================================================================

def estado_class(estado: str) -> str:
    return {"Pendiente": "p", "En Proceso": "e", "Completada": "c"}[estado]


def chip(estado: str) -> str:
    cls = {"Pendiente": "chip-p", "En Proceso": "chip-e", "Completada": "chip-c"}[estado]
    return f"<span class='chip {cls}'>{estado}</span>"


def task_card(row: pd.Series, include_due: bool = True, risk_class: str = "") -> None:
    due_text = f" · Objetivo: {row['fecha_objetivo'].strftime('%d/%m/%Y')}" if include_due else ""
    st.markdown(
        f"""
        <div class='task {estado_class(row["estado"])} {risk_class}'>
            <strong>{row['descripcion']}</strong><br>
            {chip(row['estado'])}
            <span class='muted'>Cliente: {row['cliente']}{due_text}</span><br>
            <span class='muted'>Autor: <strong>{row['autor']}</strong> · Asignado: <strong>{row['asignado']}</strong></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# DASHBOARD GERENCIA
# ============================================================================

def dashboard_gerencia(df: pd.DataFrame) -> None:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    week_df = df[(df["fecha_objetivo"] >= monday) & (df["fecha_objetivo"] <= friday)]

    dias = {
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miércoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
        "Saturday": "Sábado",
        "Sunday": "Domingo",
    }

    day_en = datetime.now().strftime("%A")
    day_es = dias.get(day_en, day_en)
    fecha_str = datetime.now().strftime("%d/%m/%Y")

    st.markdown(
        f"""
        <div class='hero'>
            <h1>Dashboard Gerencia</h1>
            <p>{day_es} {fecha_str} · Panel de Ejecución Semanal</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ALERTAS Y NOTIFICACIONES
    overdue_count = len(df[(df["fecha_objetivo"] < today) & (df["estado"] != "Completada")])
    if overdue_count > 0:
        st.error(f"⚠️ {overdue_count} tarea(s) atrasada(s) requieren atención inmediata")
    
    # MÉTRICAS VISUALES
    done = int((week_df["estado"] == "Completada").sum())
    progress = int((week_df["estado"] == "En Proceso").sum())
    pending = int((week_df["estado"] == "Pendiente").sum())
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Completadas", done)
    col2.metric("En Proceso", progress)
    col3.metric("Pendientes", pending)
    col4.metric("Total Semana", len(week_df))

    # TAREAS DE HOY
    st.markdown("<div class='section'><h3>Tareas de hoy</h3></div>", unsafe_allow_html=True)
    today_df = df[df["fecha_objetivo"] == today]

    cols = st.columns(3)
    for i, person in enumerate(JEFES_PROYECTO):
        with cols[i]:
            st.markdown(
                f"<div class='person'><h4>{person}</h4>",
                unsafe_allow_html=True,
            )

            person_tasks = today_df[today_df["asignado"] == person]

            if person_tasks.empty:
                st.markdown(
                    "<div class='task available'>✓ Disponible</div>",
                    unsafe_allow_html=True,
                )
            else:
                for _, row in person_tasks.iterrows():
                    task_card(row, include_due=False)

            st.markdown("</div>", unsafe_allow_html=True)

    # SALUD DE LA SEMANA
    st.markdown("<div class='section'><h3>Salud de la semana</h3></div>", unsafe_allow_html=True)
    selected_day = st.select_slider(
        "Selecciona día de la semana para recalcular carga",
        options=[monday + timedelta(days=i) for i in range(5)],
        value=today if monday <= today <= friday else monday,
        format_func=lambda d: d.strftime("%A %d/%m"),
    )
    day_df = df[df["fecha_objetivo"] == selected_day]
    workload = day_df.groupby("asignado").size().reindex(JEFES_PROYECTO, fill_value=0)
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.subheader("Carga por persona")
        st.bar_chart(workload)
    with c2:
        st.subheader("Estado del equipo")

        done_week = int((week_df["estado"] == "Completada").sum())
        progress_week = int((week_df["estado"] == "En Proceso").sum())
        overdue_week = int(((week_df["fecha_objetivo"] < today) & (week_df["estado"] != "Completada")).sum())
        status_df = pd.DataFrame(
            {
                "Estado": ["Verde: Completadas", "Amarillo: En Proceso", "Rojo: Atrasadas"],
                "Total": [done_week, progress_week, overdue_week],
                "Color": ["#22c55e", "#eab308", "#ef4444"],
            }
        )
        total_segmentos = int(status_df["Total"].sum())
        if total_segmentos == 0:
            st.caption("Sin actividad semanal para graficar.")
        else:
            donut = (
                alt.Chart(status_df)
                .mark_arc(innerRadius=65, outerRadius=105)
                .encode(
                    theta=alt.Theta("Total:Q"),
                    color=alt.Color("Estado:N", scale=alt.Scale(domain=status_df["Estado"].tolist(), range=status_df["Color"].tolist()), legend=alt.Legend(title="Estado semanal")),
                    tooltip=[alt.Tooltip("Estado:N"), alt.Tooltip("Total:Q")],
                )
            )
            st.altair_chart(donut, use_container_width=True)

    # RIESGOS / ATRASOS
    st.markdown("<div class='section'><h3>Riesgos / atrasos</h3></div>", unsafe_allow_html=True)
    overdue_df = df[(df["fecha_objetivo"] < today) & (df["estado"] != "Completada")].copy()
    if overdue_df.empty:
        st.info("✓ Sin atrasos detectados. Buen ritmo del equipo.")
    else:
        overdue_df["dias_atraso"] = overdue_df["fecha_objetivo"].apply(lambda d: (today - d).days)
        for _, row in overdue_df.sort_values("dias_atraso", ascending=False).iterrows():
            risk_class = "risk-yellow" if 1 <= row["dias_atraso"] <= 3 else "risk-red"
            st.markdown(
                f"<div class='task {risk_class}'><strong>{row['descripcion']}</strong><br>"
                f"Responsable: <strong>{row['asignado']}</strong> · Días de atraso: <strong>{row['dias_atraso']}</strong></div>",
                unsafe_allow_html=True,
            )

    # AUDITORÍA
    st.markdown("<div class='section'><h3>Auditoría por fecha</h3></div>", unsafe_allow_html=True)
    audit_day = st.date_input("Selecciona un día para auditar", value=today, key="audit_day")
    audit_df = df[df["fecha_objetivo"] == audit_day]
    if audit_df.empty:
        st.caption("No hay tareas en la fecha seleccionada.")
    else:
        st.dataframe(audit_df[["descripcion", "estado", "autor", "asignado", "cliente"]], hide_index=True, use_container_width=True)

    # EXPORTAR KPI
    st.markdown("<div class='section'><h3>Exportar KPI</h3></div>", unsafe_allow_html=True)
    col_i, col_f = st.columns(2)
    with col_i:
        start = st.date_input("Desde", value=monday, key="export_start")
    with col_f:
        end = st.date_input("Hasta", value=today, key="export_end")

    if start <= end:
        export_df = df[(df["fecha_objetivo"] >= start) & (df["fecha_objetivo"] <= end)]
        csv_data = export_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar CSV", data=csv_data, file_name="kpi_tareas.csv", mime="text/csv")

        xlsx_buffer = BytesIO()
        with pd.ExcelWriter(xlsx_buffer, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="KPI")
        st.download_button(
            "📥 Descargar XLSX",
            data=xlsx_buffer.getvalue(),
            file_name="kpi_tareas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.warning("El rango de fechas no es válido.")


# ============================================================================
# VISTA JEFE DE PROYECTO
# ============================================================================

def jp_view(nombre: str, df: pd.DataFrame) -> None:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    st.markdown(f"<div class='hero'><h1>{nombre}</h1><p>Foco operativo semanal</p></div>", unsafe_allow_html=True)

    # CREAR TAREA
    with st.container(border=True):
        st.subheader("Crear tarea")
        with st.form(f"form_{nombre}", clear_on_submit=True):
            descripcion = st.text_area("Descripción")
            cliente = st.text_input("Cliente")
            fecha_objetivo = st.date_input("Fecha objetivo", value=today)
            asignado = st.selectbox("Asignado", JEFES_PROYECTO, index=JEFES_PROYECTO.index(nombre) if nombre in JEFES_PROYECTO else 0)
            estado = st.selectbox("Estado", ["Pendiente", "En Proceso"])
            
            if st.form_submit_button("💾 Guardar tarea"):
                if descripcion.strip() and cliente.strip():
                    if fecha_objetivo < today:
                        st.warning("⚠️ Estás creando una tarea con fecha pasada")
                    
                    nueva_tarea = {
                        "descripcion": descripcion.strip(),
                        "fecha_objetivo": fecha_objetivo,
                        "estado": estado,
                        "autor": st.session_state.user_info["nombre"],  # Autor automático
                        "asignado": asignado,
                        "cliente": cliente.strip(),
                        "comentarios": []
                    }
                    
                    if save_task_to_db(nueva_tarea):
                        st.success("✓ Tarea creada exitosamente")
                        refresh_tasks()
                        st.rerun()
                    else:
                        st.error("Error al crear la tarea")
                else:
                    st.error("❌ Descripción y cliente son obligatorios.")

    # FILTRO DE BÚSQUEDA
    search = st.text_input("🔍 Buscar tarea (descripción o cliente)", key=f"search_{nombre}")
    
    active_df = df[(df["estado"] != "Completada") & (df["asignado"] == nombre)].copy()
    
    # Aplicar filtro de búsqueda
    if search:
        mask = (
            active_df['descripcion'].str.contains(search, case=False, na=False) |
            active_df['cliente'].str.contains(search, case=False, na=False)
        )
        active_df = active_df[mask]
        if active_df.empty:
            st.info(f"No se encontraron tareas con '{search}'")

    # TAREAS DE LA SEMANA ACTUAL
    st.subheader("Tareas de la semana actual")
    week_df = active_df[(active_df["fecha_objetivo"] >= monday) & (active_df["fecha_objetivo"] <= sunday)]
    if week_df.empty:
        st.caption("Sin tareas operativas para esta semana.")
    else:
        for _, row in week_df.sort_values("fecha_objetivo").iterrows():
            task_card(row)
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                new_status = st.selectbox(
                    f"Estado",
                    options=ESTADOS,
                    index=ESTADOS.index(row["estado"]),
                    key=f"status_{nombre}_{row['id']}",
                )
                if new_status != row["estado"]:
                    if update_task_in_db(int(row["id"]), {"estado": new_status}):
                        st.success("Estado actualizado")
                        refresh_tasks()
                        st.rerun()
            
            with col2:
                if puede_editar_tarea(row.to_dict()):
                    if st.button("✏️ Editar", key=f"edit_btn_{row['id']}"):
                        st.session_state[f"editing_{row['id']}"] = True
                        st.rerun()
            
            with col3:
                if puede_eliminar_tarea(row.to_dict()):
                    if st.button("🗑️ Eliminar", key=f"del_btn_{row['id']}"):
                        if st.session_state.get(f"confirm_del_{row['id']}"):
                            if delete_task_from_db(int(row['id'])):
                                st.session_state.pop(f"confirm_del_{row['id']}")
                                st.success("Tarea eliminada")
                                refresh_tasks()
                                st.rerun()
                        else:
                            st.session_state[f"confirm_del_{row['id']}"] = True
                            st.warning("⚠️ Presiona de nuevo para confirmar")
            
            # EDICIÓN DE TAREA
            if st.session_state.get(f"editing_{row['id']}") and puede_editar_tarea(row.to_dict()):
                with st.expander("✏️ Editar tarea", expanded=True):
                    new_desc = st.text_area("Descripción", value=row['descripcion'], key=f"desc_{row['id']}")
                    new_cliente = st.text_input("Cliente", value=row['cliente'], key=f"cliente_{row['id']}")
                    new_date = st.date_input("Fecha objetivo", value=row['fecha_objetivo'], key=f"date_{row['id']}")
                    new_asignado = st.selectbox("Asignado", JEFES_PROYECTO, 
                                               index=JEFES_PROYECTO.index(row['asignado']) if row['asignado'] in JEFES_PROYECTO else 0, 
                                               key=f"asig_{row['id']}")
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 Guardar cambios", key=f"save_{row['id']}"):
                            updates = {
                                'descripcion': new_desc,
                                'cliente': new_cliente,
                                'fecha_objetivo': new_date,
                                'asignado': new_asignado
                            }
                            if update_task_in_db(int(row['id']), updates):
                                st.session_state.pop(f"editing_{row['id']}")
                                st.success("Cambios guardados")
                                refresh_tasks()
                                st.rerun()
                    
                    with col_cancel:
                        if st.button("❌ Cancelar", key=f"cancel_{row['id']}"):
                            st.session_state.pop(f"editing_{row['id']}")
                            st.rerun()
            
            # COMENTARIOS
            task = next((t for t in st.session_state.tasks if t['id'] == int(row['id'])), None)
            if task and task.get('comentarios'):
                with st.expander(f"💬 Comentarios ({len(task['comentarios'])})"):
                    for com in task['comentarios']:
                        com_date = datetime.fromisoformat(com['fecha']).strftime("%d/%m/%Y %H:%M")
                        st.caption(f"**{com['autor']}** - {com_date}")
                        st.write(com['texto'])
                        st.divider()
            
            # Agregar comentario
            with st.expander("➕ Agregar comentario"):
                comment_text = st.text_area("Comentario", key=f"comment_{row['id']}")
                if st.button("Publicar", key=f"post_comment_{row['id']}"):
                    if comment_text.strip():
                        task = next((t for t in st.session_state.tasks if t['id'] == int(row['id'])), None)
                        if task:
                            if 'comentarios' not in task:
                                task['comentarios'] = []
                            task['comentarios'].append({
                                'autor': st.session_state.user_info["nombre"],
                                'fecha': datetime.now().isoformat(),
                                'texto': comment_text.strip()
                            })
                            if update_task_in_db(int(row['id']), {'comentarios': task['comentarios']}):
                                st.success("Comentario agregado")
                                refresh_tasks()
                                st.rerun()

    # PRÓXIMAS SEMANAS (BACKLOG)
    st.subheader("Próximas semanas (backlog)")
    backlog_df = active_df[active_df["fecha_objetivo"] > sunday]
    if backlog_df.empty:
        st.caption("✓ Backlog despejado.")
    else:
        for _, row in backlog_df.sort_values("fecha_objetivo").iterrows():
            task_card(row)

    # TAREAS ATRASADAS
    st.subheader("Tareas atrasadas")
    late_df = active_df[active_df["fecha_objetivo"] < today]
    if late_df.empty:
        st.caption("✓ Sin atrasos.")
    else:
        for _, row in late_df.sort_values("fecha_objetivo").iterrows():
            days = (today - row["fecha_objetivo"]).days
            cls = "risk-yellow" if days <= 3 else "risk-red"
            st.markdown(
                f"<div class='task {cls}'><strong>{row['descripcion']}</strong><br>"
                f"⏰ Días de atraso: <strong>{days}</strong> · Autor: {row['autor']} · Cliente: {row['cliente']}</div>",
                unsafe_allow_html=True,
            )


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    # Verificar autenticación
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login_page()
        return
    
    # Usuario autenticado
    inject_css()
    init_data()
    df = to_df()
    
    # SIDEBAR
    with st.sidebar:
        st.title("📋 Menú")
        st.write(f"👤 **{st.session_state.user_info['nombre']}**")
        st.caption(f"Rol: {st.session_state.user_info['rol']}")
        st.divider()
        
        # Menú dinámico
        menu_options = ["Dashboard Gerencia"]
        
        # Agregar opción personal para Jefes de Proyecto
        if st.session_state.user_info["rol"] == "Jefe de Proyecto":
            menu_options.append(st.session_state.user_info["nombre"])
        
        option = st.radio("Ir a", menu_options)
        
        st.divider()
        st.caption(f"Total de tareas: {len(st.session_state.tasks)}")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
    
    # Renderizar vista según selección
    if option == "Dashboard Gerencia":
        dashboard_gerencia(df)
    else:
        jp_view(option, df)


if __name__ == "__main__":
    main()
