from __future__ import annotations

from datetime import date, datetime, timedelta
from io import BytesIO
import json
import hashlib

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

# Metas de KPIs
METAS_KPI = {
    "felicitaciones": 2,
    "reclamos": 1,
    "orden": 90,
    "respuesta_cliente": 95,
    "autonomia": 85
}

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
# FUNCIONES DE BASE DE DATOS - TAREAS
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
        
        if "fecha_objetivo" in updates and isinstance(updates["fecha_objetivo"], date):
            updates["fecha_objetivo"] = updates["fecha_objetivo"].isoformat()
        
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
# FUNCIONES DE BASE DE DATOS - KPIs
# ============================================================================

def save_kpi_to_db(kpi_data: dict) -> bool:
    """Guardar KPI en Supabase"""
    try:
        supabase = get_supabase_client()
        supabase.table("kpis").insert(kpi_data).execute()
        return True
    except Exception as e:
        st.error(f"Error guardando KPI: {e}")
        return False


def load_kpis_from_db(start_date: date = None, end_date: date = None) -> pd.DataFrame:
    """Cargar KPIs desde Supabase"""
    try:
        supabase = get_supabase_client()
        query = supabase.table("kpis").select("*")
        
        if start_date:
            query = query.gte("semana", start_date.isoformat())
        if end_date:
            query = query.lte("semana", end_date.isoformat())
        
        response = query.order("semana", desc=True).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            df['semana'] = pd.to_datetime(df['semana']).dt.date
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error cargando KPIs: {e}")
        return pd.DataFrame()


def calcular_autonomia(persona: str, semana_inicio: date, semana_fin: date) -> float:
    """Calcular KPI de autonomía basado en tareas"""
    try:
        df = to_df()
        if df.empty:
            return 0.0
        
        # Filtrar tareas de la semana y persona
        mask = (
            (df['asignado'] == persona) &
            (df['fecha_objetivo'] >= semana_inicio) &
            (df['fecha_objetivo'] <= semana_fin)
        )
        tareas_semana = df[mask]
        
        if len(tareas_semana) == 0:
            return 0.0
        
        # Calcular completadas
        completadas = len(tareas_semana[tareas_semana['estado'] == 'Completada'])
        total = len(tareas_semana)
        
        return round((completadas / total) * 100, 2)
    except Exception as e:
        st.error(f"Error calculando autonomía: {e}")
        return 0.0


def calcular_cumplimiento_kpi(kpi_row: dict) -> float:
    """Calcular el cumplimiento general del KPI"""
    cumplimientos = []
    
    # Felicitaciones (mayor es mejor, meta >2)
    if kpi_row['felicitaciones'] >= METAS_KPI['felicitaciones']:
        cumplimientos.append(100)
    else:
        cumplimientos.append((kpi_row['felicitaciones'] / METAS_KPI['felicitaciones']) * 100)
    
    # Reclamos (menor es mejor, meta <1)
    if kpi_row['reclamos'] <= METAS_KPI['reclamos']:
        cumplimientos.append(100)
    else:
        cumplimientos.append(max(0, 100 - (kpi_row['reclamos'] - METAS_KPI['reclamos']) * 50))
    
    # Orden, Respuesta Cliente, Autonomía (mayor es mejor)
    for campo in ['orden', 'respuesta_cliente', 'autonomia']:
        if kpi_row[campo] >= METAS_KPI[campo]:
            cumplimientos.append(100)
        else:
            cumplimientos.append((kpi_row[campo] / METAS_KPI[campo]) * 100)
    
    return round(sum(cumplimientos) / len(cumplimientos), 2)


# ============================================================================
# FUNCIONES DE AUTENTICACIÓN
# ============================================================================

def hash_password(password: str) -> str:
    """Generar hash simple de contraseña (SHA-256)"""
    return hashlib.sha256(password.encode()).hexdigest()


def verificar_credenciales_db(username: str, password: str) -> dict | None:
    """Verificar credenciales contra Supabase"""
    try:
        supabase = get_supabase_client()
        response = supabase.table("usuarios").select("*").eq("username", username).execute()
        
        if response.data and len(response.data) > 0:
            user = response.data[0]
            stored_password = user['password_hash']
            
            # Si la contraseña almacenada no está hasheada (texto plano), hashearla
            if len(stored_password) < 64:  # No es un hash SHA-256
                if stored_password == password:
                    # Actualizar a hash
                    new_hash = hash_password(password)
                    supabase.table("usuarios").update({"password_hash": new_hash}).eq("username", username).execute()
                    return {
                        "nombre": user['nombre'],
                        "rol": user['rol']
                    }
            else:
                # Ya está hasheada, comparar hashes
                if stored_password == hash_password(password):
                    return {
                        "nombre": user['nombre'],
                        "rol": user['rol']
                    }
        return None
    except Exception as e:
        st.error(f"Error verificando credenciales: {e}")
        return None


def verificar_credenciales(username: str, password: str) -> dict | None:
    """Verificar credenciales (primero DB, luego fallback a hardcoded)"""
    user_info = verificar_credenciales_db(username, password)
    if user_info:
        return user_info
    
    if username in USUARIOS:
        if USUARIOS[username]["password"] == password:
            return USUARIOS[username]
    return None


def cambiar_contraseña(username: str, current_password: str, new_password: str) -> tuple[bool, str]:
    """Cambiar contraseña de usuario"""
    try:
        if not verificar_credenciales_db(username, current_password):
            return False, "La contraseña actual es incorrecta"
        
        supabase = get_supabase_client()
        new_hash = hash_password(new_password)
        supabase.table("usuarios").update({
            "password_hash": new_hash,
            "updated_at": datetime.now().isoformat()
        }).eq("username", username).execute()
        
        return True, "Contraseña actualizada exitosamente"
    except Exception as e:
        return False, f"Error al cambiar contraseña: {e}"


def es_gerente() -> bool:
    """Verificar si el usuario actual es gerente"""
    if "user_info" not in st.session_state:
        return False
    return st.session_state.user_info["rol"] == "Gerencia"


def puede_editar_tarea(tarea: dict) -> bool:
    """Verificar si el usuario puede editar una tarea"""
    if es_gerente():
        return True
    return tarea["asignado"] == st.session_state.user_info["nombre"]


def puede_eliminar_tarea(tarea: dict) -> bool:
    """Verificar si el usuario puede eliminar una tarea"""
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
# GESTIÓN DE TAREAS (GERENTES)
# ============================================================================

def gestion_tareas_gerentes(df: pd.DataFrame) -> None:
    """Vista de gestión de tareas para gerentes"""
    st.markdown(
        """
        <div class='hero'>
            <h1>Gestión de Tareas</h1>
            <p>Panel de administración para gerentes</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # CREAR TAREA
    with st.container(border=True):
        st.subheader("📝 Crear nueva tarea")
        with st.form("form_gerente_crear", clear_on_submit=True):
            descripcion = st.text_area("Descripción")
            cliente = st.text_input("Cliente")
            fecha_objetivo = st.date_input("Fecha objetivo", value=date.today())
            asignado = st.selectbox("Asignado a", JEFES_PROYECTO)
            estado = st.selectbox("Estado inicial", ["Pendiente", "En Proceso"])
            
            if st.form_submit_button("💾 Crear tarea"):
                if descripcion.strip() and cliente.strip():
                    if fecha_objetivo < date.today():
                        st.warning("⚠️ Estás creando una tarea con fecha pasada")
                    
                    nueva_tarea = {
                        "descripcion": descripcion.strip(),
                        "fecha_objetivo": fecha_objetivo,
                        "estado": estado,
                        "autor": st.session_state.user_info["nombre"],
                        "asignado": asignado,
                        "cliente": cliente.strip(),
                        "comentarios": []
                    }
                    
                    if save_task_to_db(nueva_tarea):
                        st.success("✓ Tarea creada exitosamente")
                        refresh_tasks()
                        st.rerun()
                else:
                    st.error("❌ Descripción y cliente son obligatorios")
    
    # FILTROS
    st.subheader("🔍 Filtrar tareas")
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_persona = st.selectbox("Persona", ["Todos"] + JEFES_PROYECTO)
    with col2:
        filtro_estado = st.selectbox("Estado", ["Todos", "Pendiente", "En Proceso", "Completada"])
    with col3:
        search = st.text_input("Buscar", placeholder="Cliente o descripción")
    
    # APLICAR FILTROS
    filtered_df = df.copy()
    
    if filtro_persona != "Todos":
        filtered_df = filtered_df[filtered_df["asignado"] == filtro_persona]
    
    if filtro_estado != "Todos":
        filtered_df = filtered_df[filtered_df["estado"] == filtro_estado]
    
    if search:
        mask = (
            filtered_df['descripcion'].str.contains(search, case=False, na=False) |
            filtered_df['cliente'].str.contains(search, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    # MOSTRAR TAREAS
    st.subheader(f"📋 Tareas ({len(filtered_df)})")
    
    if filtered_df.empty:
        st.info("No hay tareas que coincidan con los filtros")
    else:
        for _, row in filtered_df.sort_values("fecha_objetivo").iterrows():
            task_card(row)
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                new_status = st.selectbox(
                    "Estado",
                    options=ESTADOS,
                    index=ESTADOS.index(row["estado"]),
                    key=f"status_gest_{row['id']}",
                )
                if new_status != row["estado"]:
                    if update_task_in_db(int(row["id"]), {"estado": new_status}):
                        st.success("Estado actualizado")
                        refresh_tasks()
                        st.rerun()
            
            with col2:
                if st.button("✏️ Editar", key=f"edit_btn_gest_{row['id']}"):
                    st.session_state[f"editing_gest_{row['id']}"] = True
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Eliminar", key=f"del_btn_gest_{row['id']}"):
                    if st.session_state.get(f"confirm_del_gest_{row['id']}"):
                        if delete_task_from_db(int(row['id'])):
                            st.session_state.pop(f"confirm_del_gest_{row['id']}")
                            st.success("Tarea eliminada")
                            refresh_tasks()
                            st.rerun()
                    else:
                        st.session_state[f"confirm_del_gest_{row['id']}"] = True
                        st.warning("⚠️ Presiona de nuevo para confirmar")
            
            # EDICIÓN
            if st.session_state.get(f"editing_gest_{row['id']}"):
                with st.expander("✏️ Editar tarea", expanded=True):
                    new_desc = st.text_area("Descripción", value=row['descripcion'], key=f"desc_gest_{row['id']}")
                    new_cliente = st.text_input("Cliente", value=row['cliente'], key=f"cliente_gest_{row['id']}")
                    new_date = st.date_input("Fecha objetivo", value=row['fecha_objetivo'], key=f"date_gest_{row['id']}")
                    new_asignado = st.selectbox("Asignado", JEFES_PROYECTO, 
                                               index=JEFES_PROYECTO.index(row['asignado']) if row['asignado'] in JEFES_PROYECTO else 0, 
                                               key=f"asig_gest_{row['id']}")
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 Guardar cambios", key=f"save_gest_{row['id']}"):
                            updates = {
                                'descripcion': new_desc,
                                'cliente': new_cliente,
                                'fecha_objetivo': new_date,
                                'asignado': new_asignado
                            }
                            if update_task_in_db(int(row['id']), updates):
                                st.session_state.pop(f"editing_gest_{row['id']}")
                                st.success("Cambios guardados")
                                refresh_tasks()
                                st.rerun()
                    
                    with col_cancel:
                        if st.button("❌ Cancelar", key=f"cancel_gest_{row['id']}"):
                            st.session_state.pop(f"editing_gest_{row['id']}")
                            st.rerun()


# ============================================================================
# KPI GERENCIAL
# ============================================================================

def kpi_gerencial() -> None:
    """Dashboard de KPIs gerenciales"""
    st.markdown(
        """
        <div class='hero'>
            <h1>📊 KPI Gerencial</h1>
            <p>Indicadores de desempeño del equipo</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    tabs = st.tabs(["📈 Dashboard Actual", "📝 Ingresar KPIs", "📅 Histórico"])
    
    # TAB 1: DASHBOARD ACTUAL
    with tabs[0]:
        dashboard_kpi_actual()
    
    # TAB 2: INGRESAR KPIs
    with tabs[1]:
        ingresar_kpis()
    
    # TAB 3: HISTÓRICO
    with tabs[2]:
        historico_kpis()


def dashboard_kpi_actual() -> None:
    """Dashboard de KPIs de la semana actual"""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    
    # Cargar KPIs de la semana actual
    kpis_df = load_kpis_from_db(monday, sunday)
    
    if kpis_df.empty:
        st.warning("⚠️ No hay datos de KPI para la semana actual. Ve a 'Ingresar KPIs' para agregar datos.")
        return
    
    # SECCIÓN A: RESUMEN EJECUTIVO
    st.markdown("### 📊 Resumen Ejecutivo")
    
    cumplimiento_promedio = kpis_df['cumplimiento_kpi'].mean()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Cumplimiento KPI Promedio",
            f"{cumplimiento_promedio:.1f}%",
            delta=f"{'✓' if cumplimiento_promedio >= 80 else '✗'} {'Excelente' if cumplimiento_promedio >= 80 else 'Mejorar'}"
        )
    
    with col2:
        personas_bajo_meta = len(kpis_df[kpis_df['cumplimiento_kpi'] < 80])
        st.metric("Personas bajo meta", personas_bajo_meta, delta_color="inverse")
    
    with col3:
        st.metric("Semana", monday.strftime("%d/%m/%Y"))
    
    # Alertas
    for _, row in kpis_df.iterrows():
        if row['autonomia'] < METAS_KPI['autonomia']:
            st.error(f"🚨 {row['persona']}: Autonomía bajo meta ({row['autonomia']:.1f}% < {METAS_KPI['autonomia']}%)")
        if row['reclamos'] > METAS_KPI['reclamos']:
            st.error(f"🚨 {row['persona']}: Reclamos sobre meta ({row['reclamos']} > {METAS_KPI['reclamos']})")
    
    st.divider()
    
    # SECCIÓN B: GRÁFICOS PRINCIPALES
    st.markdown("### 📈 Indicadores por Persona")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico Felicitaciones
        st.subheader("Felicitaciones")
        chart_data = kpis_df[['persona', 'felicitaciones']].copy()
        chart_data['Meta'] = METAS_KPI['felicitaciones']
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('persona:N', title=''),
            y=alt.Y('felicitaciones:Q', title='Cantidad'),
            color=alt.condition(
                alt.datum.felicitaciones >= METAS_KPI['felicitaciones'],
                alt.value('#22c55e'),
                alt.value('#ef4444')
            )
        )
        rule = alt.Chart(pd.DataFrame({'y': [METAS_KPI['felicitaciones']]})).mark_rule(color='#facc15', strokeDash=[5, 5]).encode(y='y:Q')
        st.altair_chart(chart + rule, use_container_width=True)
        
        # Gráfico Orden
        st.subheader("Orden (%)")
        chart_data = kpis_df[['persona', 'orden']].copy()
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('persona:N', title=''),
            y=alt.Y('orden:Q', title='%', scale=alt.Scale(domain=[0, 100])),
            color=alt.condition(
                alt.datum.orden >= METAS_KPI['orden'],
                alt.value('#22c55e'),
                alt.value('#ef4444')
            )
        )
        rule = alt.Chart(pd.DataFrame({'y': [METAS_KPI['orden']]})).mark_rule(color='#facc15', strokeDash=[5, 5]).encode(y='y:Q')
        st.altair_chart(chart + rule, use_container_width=True)
        
        # Gráfico Autonomía
        st.subheader("Autonomía (%)")
        chart_data = kpis_df[['persona', 'autonomia']].copy()
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('persona:N', title=''),
            y=alt.Y('autonomia:Q', title='%', scale=alt.Scale(domain=[0, 100])),
            color=alt.condition(
                alt.datum.autonomia >= METAS_KPI['autonomia'],
                alt.value('#22c55e'),
                alt.value('#ef4444')
            )
        )
        rule = alt.Chart(pd.DataFrame({'y': [METAS_KPI['autonomia']]})).mark_rule(color='#facc15', strokeDash=[5, 5]).encode(y='y:Q')
        st.altair_chart(chart + rule, use_container_width=True)
    
    with col2:
        # Gráfico Reclamos
        st.subheader("Reclamos")
        chart_data = kpis_df[['persona', 'reclamos']].copy()
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('persona:N', title=''),
            y=alt.Y('reclamos:Q', title='Cantidad'),
            color=alt.condition(
                alt.datum.reclamos <= METAS_KPI['reclamos'],
                alt.value('#22c55e'),
                alt.value('#ef4444')
            )
        )
        rule = alt.Chart(pd.DataFrame({'y': [METAS_KPI['reclamos']]})).mark_rule(color='#facc15', strokeDash=[5, 5]).encode(y='y:Q')
        st.altair_chart(chart + rule, use_container_width=True)
        
        # Gráfico Respuesta Cliente
        st.subheader("Respuesta Cliente (%)")
        chart_data = kpis_df[['persona', 'respuesta_cliente']].copy()
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('persona:N', title=''),
            y=alt.Y('respuesta_cliente:Q', title='%', scale=alt.Scale(domain=[0, 100])),
            color=alt.condition(
                alt.datum.respuesta_cliente >= METAS_KPI['respuesta_cliente'],
                alt.value('#22c55e'),
                alt.value('#ef4444')
            )
        )
        rule = alt.Chart(pd.DataFrame({'y': [METAS_KPI['respuesta_cliente']]})).mark_rule(color='#facc15', strokeDash=[5, 5]).encode(y='y:Q')
        st.altair_chart(chart + rule, use_container_width=True)
        
        # Gráfico Cumplimiento KPI
        st.subheader("Cumplimiento KPI (%)")
        chart_data = kpis_df[['persona', 'cumplimiento_kpi']].copy()
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('persona:N', title=''),
            y=alt.Y('cumplimiento_kpi:Q', title='%', scale=alt.Scale(domain=[0, 100])),
            color=alt.condition(
                alt.datum.cumplimiento_kpi >= 80,
                alt.value('#22c55e'),
                alt.value('#ef4444')
            )
        )
        st.altair_chart(chart, use_container_width=True)
    
    st.divider()
    
    # SECCIÓN C: TABLA DETALLADA
    st.markdown("### 📋 Tabla Detallada")
    
    # Preparar datos para la tabla
    tabla_data = []
    
    indicadores = [
        ("Felicitaciones", "felicitaciones", f">{METAS_KPI['felicitaciones']}"),
        ("Reclamos", "reclamos", f"<{METAS_KPI['reclamos']}"),
        ("Orden", "orden", f">{METAS_KPI['orden']}%"),
        ("Autonomía", "autonomia", f">{METAS_KPI['autonomia']}%"),
        ("Respuesta Cliente", "respuesta_cliente", f">{METAS_KPI['respuesta_cliente']}%")
    ]
    
    for indicador_nombre, indicador_key, meta_str in indicadores:
        row_data = {"Indicador": indicador_nombre, "Meta": meta_str}
        for persona in JEFES_PROYECTO:
            persona_data = kpis_df[kpis_df['persona'] == persona]
            if not persona_data.empty:
                valor = persona_data.iloc[0][indicador_key]
                if indicador_key in ['felicitaciones', 'reclamos']:
                    row_data[persona] = f"{valor:.0f}"
                else:
                    row_data[persona] = f"{valor:.0f}%"
            else:
                row_data[persona] = "N/A"
        
        # Promedio
        promedio = kpis_df[indicador_key].mean()
        if indicador_key in ['felicitaciones', 'reclamos']:
            row_data["Promedio Depto"] = f"{promedio:.0f}"
        else:
            row_data["Promedio Depto"] = f"{promedio:.0f}%"
        
        tabla_data.append(row_data)
    
    # Fila de Cumplimiento KPI
    cumpl_row = {"Indicador": "**Cumplimiento KPI**", "Meta": ""}
    for persona in JEFES_PROYECTO:
        persona_data = kpis_df[kpis_df['persona'] == persona]
        if not persona_data.empty:
            cumpl_row[persona] = f"**{persona_data.iloc[0]['cumplimiento_kpi']:.0f}%**"
        else:
            cumpl_row[persona] = "N/A"
    cumpl_row["Promedio Depto"] = f"**{cumplimiento_promedio:.0f}%**"
    tabla_data.append(cumpl_row)
    
    tabla_df = pd.DataFrame(tabla_data)
    st.dataframe(tabla_df, hide_index=True, use_container_width=True)


def ingresar_kpis() -> None:
    """Formulario para ingresar KPIs semanales"""
    st.markdown("### 📝 Ingresar KPIs Semanales")
    
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    
    st.info(f"📅 Ingresando KPIs para la semana del {monday.strftime('%d/%m/%Y')}")
    
    # Seleccionar persona
    persona = st.selectbox("Selecciona persona", JEFES_PROYECTO)
    
    # Verificar si ya existen KPIs para esta semana y persona
    kpis_existentes = load_kpis_from_db(monday, monday)
    if not kpis_existentes.empty and persona in kpis_existentes['persona'].values:
        st.warning(f"⚠️ Ya existen KPIs registrados para {persona} en esta semana. Serán reemplazados.")
    
    with st.form("form_kpis"):
        st.subheader(f"KPIs para {persona}")
        
        felicitaciones = st.number_input(
            f"Felicitaciones (Meta: >{METAS_KPI['felicitaciones']})",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0
        )
        
        reclamos = st.number_input(
            f"Reclamos (Meta: <{METAS_KPI['reclamos']})",
            min_value=0,
            max_value=100,
            value=0,
            step=1
        )
        
        orden = st.number_input(
            f"Orden % (Meta: >{METAS_KPI['orden']}%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0
        )
        
        respuesta_cliente = st.number_input(
            f"Respuesta Cliente % (Meta: >{METAS_KPI['respuesta_cliente']}%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0
        )
        
        # Calcular Autonomía automáticamente
        sunday = monday + timedelta(days=6)
        autonomia = calcular_autonomia(persona, monday, sunday)
        st.metric("Autonomía (calculado automáticamente)", f"{autonomia}%")
        
        if st.form_submit_button("💾 Guardar KPIs"):
            # Calcular cumplimiento KPI
            kpi_data = {
                'felicitaciones': felicitaciones,
                'reclamos': reclamos,
                'orden': orden,
                'respuesta_cliente': respuesta_cliente,
                'autonomia': autonomia
            }
            cumplimiento = calcular_cumplimiento_kpi(kpi_data)
            
            # Preparar para guardar
            kpi_data['semana'] = monday.isoformat()
            kpi_data['persona'] = persona
            kpi_data['cumplimiento_kpi'] = cumplimiento
            
            if save_kpi_to_db(kpi_data):
                st.success(f"✓ KPIs guardados para {persona}")
                st.balloons()
            else:
                st.error("Error al guardar KPIs")


def historico_kpis() -> None:
    """Vista de histórico de KPIs"""
    st.markdown("### 📅 Histórico de KPIs")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        periodo = st.selectbox("Período", ["Semana", "Mes", "Trimestre", "Año"])
    with col2:
        if periodo == "Semana":
            weeks_back = st.number_input("Semanas atrás", min_value=1, max_value=52, value=4)
            end_date = date.today()
            start_date = end_date - timedelta(weeks=weeks_back)
        elif periodo == "Mes":
            months_back = st.number_input("Meses atrás", min_value=1, max_value=12, value=3)
            end_date = date.today()
            start_date = end_date - timedelta(days=months_back*30)
        elif periodo == "Trimestre":
            quarter = st.selectbox("Trimestre", ["Q1", "Q2", "Q3", "Q4"])
            year = st.number_input("Año", min_value=2020, max_value=2030, value=date.today().year)
            q_start = {"Q1": 1, "Q2": 4, "Q3": 7, "Q4": 10}[quarter]
            start_date = date(year, q_start, 1)
            end_date = start_date + timedelta(days=90)
        else:  # Año
            year = st.number_input("Año", min_value=2020, max_value=2030, value=date.today().year)
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
    
    # Cargar datos
    kpis_df = load_kpis_from_db(start_date, end_date)
    
    if kpis_df.empty:
        st.warning("No hay datos de KPI para el período seleccionado")
        return
    
    # Seleccionar persona
    persona_filtro = st.selectbox("Persona", ["Todos"] + JEFES_PROYECTO)
    
    if persona_filtro != "Todos":
        kpis_df = kpis_df[kpis_df['persona'] == persona_filtro]
    
    # Gráficos de tendencia
    st.subheader("📈 Tendencias")
    
    # Gráfico de Cumplimiento KPI
    chart = alt.Chart(kpis_df).mark_line(point=True).encode(
        x=alt.X('semana:T', title='Fecha'),
        y=alt.Y('cumplimiento_kpi:Q', title='Cumplimiento KPI (%)', scale=alt.Scale(domain=[0, 100])),
        color='persona:N',
        tooltip=['persona', 'semana', 'cumplimiento_kpi']
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)
    
    # Gráfico de Autonomía
    chart_autonomia = alt.Chart(kpis_df).mark_line(point=True).encode(
        x=alt.X('semana:T', title='Fecha'),
        y=alt.Y('autonomia:Q', title='Autonomía (%)', scale=alt.Scale(domain=[0, 100])),
        color='persona:N',
        tooltip=['persona', 'semana', 'autonomia']
    ).properties(height=300)
    st.altair_chart(chart_autonomia, use_container_width=True)
    
    # Tabla histórica
    st.subheader("📋 Datos Históricos")
    display_df = kpis_df[['semana', 'persona', 'felicitaciones', 'reclamos', 'orden', 'autonomia', 'respuesta_cliente', 'cumplimiento_kpi']].copy()
    display_df['semana'] = pd.to_datetime(display_df['semana']).dt.strftime('%d/%m/%Y')
    st.dataframe(display_df, hide_index=True, use_container_width=True)


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
                        "autor": st.session_state.user_info["nombre"],
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
            
            # Controles interactivos para tareas atrasadas
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                new_status = st.selectbox(
                    f"Estado",
                    options=ESTADOS,
                    index=ESTADOS.index(row["estado"]),
                    key=f"status_late_{nombre}_{row['id']}",
                )
                if new_status != row["estado"]:
                    if update_task_in_db(int(row["id"]), {"estado": new_status}):
                        st.success("Estado actualizado")
                        refresh_tasks()
                        st.rerun()
            
            with col2:
                if puede_editar_tarea(row.to_dict()):
                    if st.button("✏️ Editar", key=f"edit_btn_late_{row['id']}"):
                        st.session_state[f"editing_late_{row['id']}"] = True
                        st.rerun()
            
            with col3:
                if puede_eliminar_tarea(row.to_dict()):
                    if st.button("🗑️ Eliminar", key=f"del_btn_late_{row['id']}"):
                        if st.session_state.get(f"confirm_del_late_{row['id']}"):
                            if delete_task_from_db(int(row['id'])):
                                st.session_state.pop(f"confirm_del_late_{row['id']}")
                                st.success("Tarea eliminada")
                                refresh_tasks()
                                st.rerun()
                        else:
                            st.session_state[f"confirm_del_late_{row['id']}"] = True
                            st.warning("⚠️ Presiona de nuevo para confirmar")
            
            # EDICIÓN DE TAREA ATRASADA
            if st.session_state.get(f"editing_late_{row['id']}") and puede_editar_tarea(row.to_dict()):
                with st.expander("✏️ Editar tarea", expanded=True):
                    new_desc = st.text_area("Descripción", value=row['descripcion'], key=f"desc_late_{row['id']}")
                    new_cliente = st.text_input("Cliente", value=row['cliente'], key=f"cliente_late_{row['id']}")
                    new_date = st.date_input("Fecha objetivo", value=row['fecha_objetivo'], key=f"date_late_{row['id']}")
                    new_asignado = st.selectbox("Asignado", JEFES_PROYECTO, 
                                               index=JEFES_PROYECTO.index(row['asignado']) if row['asignado'] in JEFES_PROYECTO else 0, 
                                               key=f"asig_late_{row['id']}")
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 Guardar cambios", key=f"save_late_{row['id']}"):
                            updates = {
                                'descripcion': new_desc,
                                'cliente': new_cliente,
                                'fecha_objetivo': new_date,
                                'asignado': new_asignado
                            }
                            if update_task_in_db(int(row['id']), updates):
                                st.session_state.pop(f"editing_late_{row['id']}")
                                st.success("Cambios guardados")
                                refresh_tasks()
                                st.rerun()
                    
                    with col_cancel:
                        if st.button("❌ Cancelar", key=f"cancel_late_{row['id']}"):
                            st.session_state.pop(f"editing_late_{row['id']}")
                            st.rerun()
            
            # COMENTARIOS EN TAREAS ATRASADAS
            task = next((t for t in st.session_state.tasks if t['id'] == int(row['id'])), None)
            if task and task.get('comentarios'):
                with st.expander(f"💬 Comentarios ({len(task['comentarios'])})"):
                    for com in task['comentarios']:
                        com_date = datetime.fromisoformat(com['fecha']).strftime("%d/%m/%Y %H:%M")
                        st.caption(f"**{com['autor']}** - {com_date}")
                        st.write(com['texto'])
                        st.divider()
            
            # Agregar comentario a tarea atrasada
            with st.expander("➕ Agregar comentario"):
                comment_text = st.text_area("Comentario", key=f"comment_late_{row['id']}")
                if st.button("Publicar", key=f"post_comment_late_{row['id']}"):
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
        
        # Opciones para Gerentes
        if es_gerente():
            menu_options.append("Gestión de Tareas")
            menu_options.append("KPI Gerencial")
        
        # Opción personal para Jefes de Proyecto
        if st.session_state.user_info["rol"] == "Jefe de Proyecto":
            menu_options.append(st.session_state.user_info["nombre"])
        
        option = st.radio("Ir a", menu_options)
        
        st.divider()
        st.caption(f"Total de tareas: {len(st.session_state.tasks)}")
        
        # Cambiar contraseña
        with st.expander("🔑 Cambiar contraseña"):
            with st.form("change_password_form"):
                current_pwd = st.text_input("Contraseña actual", type="password")
                new_pwd = st.text_input("Nueva contraseña", type="password")
                confirm_pwd = st.text_input("Confirmar nueva contraseña", type="password")
                
                if st.form_submit_button("Actualizar contraseña"):
                    if not current_pwd or not new_pwd or not confirm_pwd:
                        st.error("Todos los campos son obligatorios")
                    elif new_pwd != confirm_pwd:
                        st.error("Las contraseñas nuevas no coinciden")
                    elif len(new_pwd) < 6:
                        st.error("La contraseña debe tener al menos 6 caracteres")
                    else:
                        success, message = cambiar_contraseña(
                            st.session_state.username,
                            current_pwd,
                            new_pwd
                        )
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        
        st.divider()
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
    
    # Renderizar vista según selección
    if option == "Dashboard Gerencia":
        dashboard_gerencia(df)
    elif option == "Gestión de Tareas":
        gestion_tareas_gerentes(df)
    elif option == "KPI Gerencial":
        kpi_gerencial()
    else:
        jp_view(option, df)


if __name__ == "__main__":
    main()
