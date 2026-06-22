"""
Interfaz Streamlit para el Planificador Inteligente de Eventos
Centro de Investigación en IA - Interfaz Web
"""
import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Configurar path para importaciones
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar el planificador
from aplicacion.planificador import Planificador

from dominio.recursos import Recurso, GestorRecursos, crear_recursos_predeterminados
from dominio.eventos import GestorEventos
from infraestructura.persistencia import Persistencia


# Configuración de la página y estilos

st.set_page_config(
    page_title="Planificador IA - Centro de Investigación",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para fondo negro y azul celeste
st.markdown("""
<style>
    /* Fondo negro principal */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Sidebar negro */
    .css-1d391kg, .css-12oz5g7 {
        background-color: #1A1D23 !important;
    }
    
    /* Títulos en azul celeste */
    h1, h2, h3, .stTitle {
        color: #00D4FF !important;
        font-weight: 700;
    }
    
    /* Subtítulos */
    .stSubheader {
        color: #80D8FF !important;
    }
    
    /* Texto normal */
    .stText, .stMarkdown {
        color: #E0E0E0 !important;
    }
    
    /* Botones estilo azul celeste */
    .stButton > button {
        background-color: #00B4D8;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #0096C7;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 180, 216, 0.3);
    }
    
    /* Botones secundarios (eliminar) */
    .stButton > button.danger {
        background-color: #FF4B4B;
    }
    
    .stButton > button.danger:hover {
        background-color: #D63030;
    }
    
    /* Inputs y selects */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input {
        background-color: #2D3748;
        color: white;
        border: 1px solid #4A5568;
        border-radius: 6px;
    }
    
    /* Cards y contenedores */
    .card {
        background: linear-gradient(135deg, #1E293B 0%, #2D3748 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #00D4FF;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Tablas */
    .dataframe {
        background-color: #1A1D23 !important;
        color: white !important;
    }
    
    /* Metricas */
    .stMetric {
        background-color: #1E293B;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #00D4FF;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 2px;
    }
    
    .badge-success {
        background-color: #10B981;
        color: white;
    }
    
    .badge-warning {
        background-color: #F59E0B;
        color: black;
    }
    
    .badge-danger {
        background-color: #EF4444;
        color: white;
    }
    
    .badge-info {
        background-color: #00D4FF;
        color: black;
    }
    
    /* Separadores */
    .separator {
        border-top: 2px solid #00D4FF;
        margin: 30px 0;
    }
    
    /* Animaciones */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 212, 255, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(0, 212, 255, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 212, 255, 0); }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* Sugerencias */
    .sugerencia {
        background: linear-gradient(135deg, #1E293B 0%, #2D3748 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 4px solid #F59E0B;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)


# Funciones auxiliares

def initialize_planificador():
    """Inicializa el planificador """
    if 'planificador' not in st.session_state:
        # Crear instancia limpia (sin recursos predeterminados automáticos)
        st.session_state.planificador = Planificador()
        
        try:
            # Limpiar cualquier recurso que haya cargado el __init__
            st.session_state.planificador.gestor_recursos = GestorRecursos()
            st.session_state.planificador.gestor_eventos = GestorEventos()
            
            # Intentar cargar datos existentes
            datos_cargados = st.session_state.planificador.cargar_datos()
            
            # Si no se cargaron datos, cargar recursos predeterminados
            if not datos_cargados:
                recursos_predeterminados = crear_recursos_predeterminados()
                for recurso in recursos_predeterminados.recursos.values():
                    st.session_state.planificador.gestor_recursos.agregar_recurso(recurso)
                
                # Guardar estado inicial
                st.session_state.planificador.guardar_datos()
                print("✅ Cargados recursos predeterminados y guardados")
            
            # Validar que todos los eventos sean objetos válidos
            eventos_validos = []
            for evento in st.session_state.planificador.gestor_eventos.eventos.values():
                if isinstance(evento, str):
                    st.warning("⚠️ Se encontraron eventos corruptos (strings)")
                    continue
                elif not hasattr(evento, 'fin'):
                    st.warning("⚠️ Evento sin atributo 'fin' encontrado")
                    continue
                eventos_validos.append(evento)
            
            # Reemplazar si hubo cambios
            if len(eventos_validos) < len(st.session_state.planificador.gestor_eventos.eventos):
                st.session_state.planificador.gestor_eventos.eventos = eventos_validos
                st.session_state.planificador.guardar_datos()
                st.toast("⚠️ Algunos eventos corruptos fueron eliminados", icon="⚠️")
            
            # Verificar duplicados (para debug)
            verificar_duplicados(st.session_state.planificador)
                
        except Exception as e:
            st.error(f"❌ Error crítico al inicializar: {str(e)}")
            # Cargar solo recursos predeterminados
            st.session_state.planificador = Planificador()
            # Limpiar y cargar solo predeterminados
            st.session_state.planificador.gestor_recursos = GestorRecursos()
            recursos_pred = crear_recursos_predeterminados()
            for recurso in recursos_pred.recursos.values():
                st.session_state.planificador.gestor_recursos.agregar_recurso(recurso)
    
    return st.session_state.planificador

def verificar_duplicados(planificador):
    """Verifica y elimina recursos duplicados"""
    ids_vistos = set()
    duplicados = []
    
    # Obtener todos los recursos
    recursos = list(planificador.gestor_recursos.recursos.values())
    
    # Verificar duplicados
    for recurso in recursos:
        if recurso.id in ids_vistos:
            duplicados.append(recurso.id)
        else:
            ids_vistos.add(recurso.id)
    
    # Eliminar duplicados si los hay
    if duplicados:
        print(f"⚠️ Encontrados {len(duplicados)} recursos duplicados: {duplicados}")
        
        # Crear nuevo gestor sin duplicados
        nuevo_gestor = GestorRecursos()
        for recurso in recursos:
            if recurso.id not in duplicados:
                nuevo_gestor.agregar_recurso(recurso)
        
        # Reemplazar gestor
        planificador.gestor_recursos = nuevo_gestor
        
        # Guardar cambios
        planificador.guardar_datos()
        print(f"✅ Duplicados eliminados. Recursos únicos: {len(planificador.gestor_recursos)}")
    
    return len(duplicados)

def limpiar_eventos_pasados(planificador, dias_retencion=30):
    """Elimina eventos que terminaron hace más de 'dias_retencion' días"""
    fecha_limite = datetime.now() - timedelta(days=dias_retencion)
    eventos_eliminados = 0
    
    # Obtener copia de la lista para evitar problemas al iterar
    eventos_a_revisar = list(planificador.gestor_eventos.eventos.values())
    
    for evento in eventos_a_revisar:
        if evento.fin < fecha_limite and evento.estado != 'cancelado':
            if planificador.eliminar_evento(evento.id):
                eventos_eliminados += 1
    
    if eventos_eliminados > 0:
        planificador.guardar_datos()
    
    return eventos_eliminados

def badge_for_tipo(tipo):
    """Devuelve un badge HTML para el tipo de evento"""
    colores = {
        'entrenamiento': 'badge-info',
        'procesamiento': 'badge-success',
        'investigación': 'badge-warning',
        'reunión': 'badge-info',
        'seminario': 'badge-success',
        'inferencia': 'badge-warning'
    }
    clase = colores.get(tipo, 'badge-info')
    return f'<span class="badge {clase}">{tipo.upper()}</span>'

def badge_for_estado(estado):
    """Devuelve un badge HTML para el estado del evento"""
    colores = {
        'planificado': 'badge-info',
        'en_curso': 'badge-success',
        'completado': 'badge-warning',
        'cancelado': 'badge-danger'
    }
    clase = colores.get(estado, 'badge-info')
    return f'<span class="badge {clase}">{estado.upper()}</span>'

def badge_for_recurso(recurso):
    """Devuelve un badge HTML para el tipo de recurso"""
    colores = {
        'humano': 'badge-success',
        'computacional': 'badge-info',
        'espacio': 'badge-warning',
        'equipo': 'badge-danger'
    }
    clase = colores.get(recurso.tipo, 'badge-info')
    return f'<span class="badge {clase}">{recurso.tipo.upper()}</span>'

def display_evento_card(evento):
    """Muestra un evento en formato tarjeta"""
    recursos_str = ", ".join([r.nombre for r in evento.recursos[:3]])
    if len(evento.recursos) > 3:
        recursos_str += f" y {len(evento.recursos) - 3} más"
    
    inicio_str = evento.inicio.strftime("%d/%m/%Y %H:%M")
    fin_str = evento.fin.strftime("%H:%M")
    
    st.markdown(f"""
    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0; color: #00D4FF;">{evento.nombre}</h4>
                <p style="margin: 5px 0; color: #80D8FF;">
                    🕐 {inicio_str} - {fin_str} ({evento.duracion_horas:.1f} horas)
                </p>
            </div>
            <div>
                {badge_for_tipo(evento.tipo)}
                {badge_for_estado(evento.estado)}
            </div>
        </div>
        <p style="margin: 10px 0; color: #E0E0E0;">{evento.descripcion or 'Sin descripción'}</p>
        <p style="margin: 5px 0; color: #A0A0A0;">📋 <strong>Recursos:</strong> {recursos_str}</p>
        <p style="margin: 5px 0; color: #A0A0A0;">🎯 <strong>Prioridad:</strong> {"★" * evento.prioridad}</p>
    </div>
    """, unsafe_allow_html=True)

def display_recurso_card(recurso):
    """Muestra un recurso en formato tarjeta"""
    st.markdown(f"""
    <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h4 style="margin: 0; color: #00D4FF;">{recurso.nombre}</h4>
                <p style="margin: 5px 0; color: #80D8FF;">
                    {badge_for_recurso(recurso)}
                </p>
            </div>
            <div>
                <span style="color: #00D4FF; font-weight: bold;">Capacidad: {recurso.capacidad}</span>
            </div>
        </div>
        <p style="margin: 10px 0; color: #E0E0E0;">
            <strong>ID:</strong> <code>{recurso.id}</code>
        </p>
        <div style="margin-top: 10px;">
            <button onclick="window.location.href='#agenda_{recurso.id}'" 
                    style="background: #00B4D8; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer;">
                📅 Ver Agenda
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)


# PÁGINA PRINCIPAL

def main():
    """Función principal de la aplicación"""
    
    # Inicializar planificador
    planificador = initialize_planificador()
    

    # Sidebar
    
    # Logo y cabecera elegante
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 25px 0 30px 0; background: linear-gradient(135deg, #0A0E17 0%, #1A1F2E 100%); 
                border-radius: 0 0 20px 20px; margin: -20px -16px 30px -16px; border-bottom: 2px solid #00D4FF;">
        <div style="width: 70px; height: 70px; margin: 0 auto 15px auto; 
                    background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%); 
                    border-radius: 50%; display: flex; align-items: center; justify-content: center;
                    box-shadow: 0 8px 25px rgba(0, 180, 216, 0.4);">
            <span style="font-size: 32px;">🧠</span>
        </div>
        <h2 style="color: #00D4FF; margin: 0; font-weight: 800; letter-spacing: 1px;">AI CENTER</h2>
        <p style="color: #80D8FF; margin: 5px 0 0 0; font-size: 12px; letter-spacing: 2px; text-transform: uppercase;">
            Planificador Inteligente
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navegación con íconos y efecto hover
    st.sidebar.markdown("""
    <style>
    /* Botones de navegación elegantes */
    .nav-btn {
        display: flex;
        align-items: center;
        width: 100%;
        padding: 14px 20px;
        margin: 8px 0;
        background: transparent;
        border: none;
        border-radius: 12px;
        color: #B0B8C5;
        font-weight: 500;
        font-size: 15px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: left;
        position: relative;
        overflow: hidden;
    }
    
    .nav-btn:hover {
        background: rgba(0, 212, 255, 0.08);
        color: #00D4FF;
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0, 212, 255, 0.15);
    }
    
    .nav-btn.active {
        background: linear-gradient(90deg, rgba(0, 212, 255, 0.15) 0%, transparent 100%);
        color: #00D4FF;
        border-left: 4px solid #00D4FF;
        font-weight: 600;
    }
    
    .nav-btn::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 3px;
        background: #00D4FF;
        transform: scaleY(0);
        transition: transform 0.3s ease;
    }
    
    .nav-btn:hover::before {
        transform: scaleY(1);
    }
    
    .nav-icon {
        margin-right: 12px;
        font-size: 18px;
        width: 24px;
        text-align: center;
    }
    
    /* Badge para notificaciones */
    .nav-badge {
        background: #FF4B4B;
        color: white;
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 10px;
        margin-left: auto;
        animation: pulse 2s infinite;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Menú de navegación principal
    st.sidebar.markdown('<p style="color: #80D8FF; font-size: 13px; font-weight: 600; margin: 20px 0 10px 15px; letter-spacing: 1px;">NAVEGACIÓN PRINCIPAL</p>', unsafe_allow_html=True)
    
    # Sistema de navegación por estado
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # Calcular eventos próximos para el badge
    eventos_proximos = planificador.gestor_eventos.eventos.values()
    num_eventos_proximos = len(eventos_proximos)
    
    # Definir páginas
    pages = {
        "dashboard": {"icon": "📊", "label": "Dashboard", "badge": ""},
        "eventos": {"icon": "📅", "label": "Eventos", "badge": str(num_eventos_proximos) if num_eventos_proximos > 0 else ""},
        "recursos": {"icon": "🔧", "label": "Recursos", "badge": ""},
        "nuevo_evento": {"icon": "✨", "label": "Nuevo Evento", "badge": "NEW"},
        "buscar_huecos": {"icon": "🔍", "label": "Buscar Huecos", "badge": ""},
        "datos": {"icon": "💾", "label": "Gestión de Datos", "badge": ""}
    }
    
    # Crear botones de navegación
    for page_id, page_info in pages.items():
        is_active = st.session_state.current_page == page_id
        active_class = "active" if is_active else ""
        
        col1, col2 = st.sidebar.columns([6, 1])
        with col1:
            if st.button(f"{page_info['icon']} {page_info['label']}", key=f"nav_{page_id}", 
                        use_container_width=True):
                st.session_state.current_page = page_id
                st.rerun()
        
        with col2:
            if page_info['badge']:
                st.markdown(f'<span class="nav-badge">{page_info["badge"]}</span>', unsafe_allow_html=True)
        
        # Aplicar estilo CSS al botón
        st.sidebar.markdown(f"""
        <style>
        div[data-testid="column"]:first-child button[kind="secondary"][id="nav_{page_id}"] {{
            justify-content: flex-start;
            background: {"rgba(0, 212, 255, 0.1)" if is_active else "transparent"} !important;
            color: {"#00D4FF" if is_active else "#B0B8C5"} !important;
            border-left: {"3px solid #00D4FF" if is_active else "none"} !important;
            font-weight: {600 if is_active else 500} !important;
            border-radius: 12px !important;
            padding: 14px 20px !important;
            margin: 4px 0 !important;
            transition: all 0.3s ease !important;
        }}
        
        div[data-testid="column"]:first-child button[kind="secondary"][id="nav_{page_id}"]:hover {{
            background: rgba(0, 212, 255, 0.08) !important;
            color: #00D4FF !important;
            transform: translateX(5px) !important;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    # Separador decorativo
    st.sidebar.markdown("""
    <div style="margin: 30px 0; position: relative; text-align: center;">
        <hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #00D4FF, transparent);">
        <span style="position: absolute; top: -10px; left: 50%; transform: translateX(-50%); 
                    background: #0E1117; padding: 0 15px; color: #80D8FF; font-size: 12px;">
            ESTADÍSTICAS
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Tarjetas de estadísticas 
    # Tarjetas de estadísticas - solo dos tarjetas
    recursos_total = len(planificador.listar_recursos())
    eventos_total = len(planificador.gestor_eventos)

    stats_cards = [
        {"icon": "🔧", "value": recursos_total, "label": "Recursos", "trend": "+2"},
        {"icon": "📅", "value": eventos_total, "label": "Eventos", "trend": "+5"}
    ]

    # Mostrar tarjetas en 2 columnas (2 tarjetas = 1 fila completa)
    for i in range(0, len(stats_cards), 2):
        cols = st.sidebar.columns(2)
        for j in range(2):
            if i + j < len(stats_cards):
                stat = stats_cards[i + j]
                with cols[j]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1A1F2E 0%, #252B3D 100%);
                                border-radius: 12px;
                                padding: 15px;
                                margin: 5px 0;
                                border: 1px solid rgba(0, 212, 255, 0.1);
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
                                transition: transform 0.3s ease;">
                        <div style="display: flex; align-items: center; margin-bottom: 8px;">
                            <div style="background: rgba(0, 212, 255, 0.1); 
                                        width: 36px; height: 36px; 
                                        border-radius: 10px;
                                        display: flex; align-items: center; justify-content: center;
                                        margin-right: 10px;">
                                <span style="font-size: 18px; color: #00D4FF;">{stat['icon']}</span>
                            </div>
                            <div>
                                <div style="font-size: 22px; font-weight: 700; color: #00D4FF;">{stat['value']}</div>
                                <div style="font-size: 11px; color: #A0A0A0; letter-spacing: 0.5px;">{stat['label']}</div>
                            </div>
                        </div>
                        {f'<div style="font-size: 10px; color: #10B981; text-align: right;">{stat["trend"]}</div>' if stat["trend"] else ''}
                    </div>
                    """, unsafe_allow_html=True)
        
    # Acciones rápidas 
    st.sidebar.markdown("""
    <div style="margin: 30px 0; position: relative; text-align: center;">
        <hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #00D4FF, transparent);">
        <span style="position: absolute; top: -10px; left: 50%; transform: translateX(-50%); 
                    background: #0E1117; padding: 0 15px; color: #80D8FF; font-size: 12px;">
            ACCIONES RÁPIDAS
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Botones de acciones con efectos
    action_cols = st.sidebar.columns(3)
    
    with action_cols[0]:
        if st.button("🔄", help="Refrescar datos", key="refresh_action", 
                    use_container_width=True, type="secondary"):
            st.rerun()
    
    with action_cols[1]:
        if st.button("💾", help="Guardar todo", key="save_action", 
                    use_container_width=True, type="secondary"):
            if planificador.guardar_datos():
                st.toast("✅ Datos guardados exitosamente", icon="✅")
            else:
                st.toast("❌ Error al guardar datos", icon="❌")
    
    with action_cols[2]:
        if st.button("🛡️", help="Crear backup", key="backup_action", 
                    use_container_width=True, type="secondary"):
            from infraestructura.persistencia import Persistencia
            try:
                archivo_backup = Persistencia.crear_backup(
                    planificador.gestor_recursos,
                    planificador.gestor_eventos,
                    planificador.restricciones
                )
                st.toast(f"✅ Backup creado: {os.path.basename(archivo_backup)}", icon="✅")
            except Exception as e:
                st.toast(f"❌ Error: {str(e)[:50]}...", icon="❌")
    
    # Estilo para botones de acciones
    st.sidebar.markdown("""
    <style>
    div[data-testid="column"] button[kind="secondary"] {
        background: rgba(0, 212, 255, 0.08) !important;
        color: #00D4FF !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-size: 18px !important;
        transition: all 0.3s ease !important;
    }
    
    div[data-testid="column"] button[kind="secondary"]:hover {
        background: rgba(0, 212, 255, 0.15) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(0, 212, 255, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Footer del sidebar 
    st.sidebar.divider() # Crea una línea horizontal limpia

    st.sidebar.caption("Centro de Investigación en IA")
    st.sidebar.caption("v2.0 • Sistema Inteligente")
    st.sidebar.caption("© 2025 • Todos los derechos reservados")
    
   
    # Contenido principal según página
    
    # Mostrar la página correspondiente
    if st.session_state.current_page == "dashboard":
        show_dashboard(planificador)
    elif st.session_state.current_page == "eventos":
        show_eventos(planificador)
    elif st.session_state.current_page == "recursos":
        show_recursos(planificador)
    elif st.session_state.current_page == "nuevo_evento":
        show_nuevo_evento(planificador)
    elif st.session_state.current_page == "buscar_huecos":
        show_buscar_huecos(planificador)
    elif st.session_state.current_page == "datos":
        show_datos(planificador)


# Secciones de la aplicación

def show_dashboard(planificador):
    """Dashboard principal"""
    st.title("📊 Dashboard - Centro de Investigación IA")
    st.markdown("Vista general de la planificación de recursos y eventos")
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stMetric">
            <div style="font-size: 32px; color: #00D4FF;">🧑‍🔬</div>
            <div style="font-size: 14px;">Recursos Humanos</div>
            <div style="font-size: 24px; font-weight: bold; color: white;">""" + 
            str(len([r for r in planificador.listar_recursos() if r.tipo == 'humano'])) + 
            """</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stMetric">
            <div style="font-size: 32px; color: #00D4FF;">💻</div>
            <div style="font-size: 14px;">Recursos Computacionales</div>
            <div style="font-size: 24px; font-weight: bold; color: white;">""" + 
            str(len([r for r in planificador.listar_recursos() if r.tipo == 'computacional'])) + 
            """</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stMetric">
            <div style="font-size: 32px; color: #00D4FF;">🏢</div>
            <div style="font-size: 14px;">Espacios</div>
            <div style="font-size: 24px; font-weight: bold; color: white;">""" + 
            str(len([r for r in planificador.listar_recursos() if r.tipo == 'espacio'])) + 
            """</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='separator'></div>", unsafe_allow_html=True)
    
    # Eventos próximos
    st.subheader("📅 Eventos Próximos (7 días)")
    eventos = planificador.listar_eventos(dias=7)
    
    if eventos:
        # Filtrar solo eventos futuros (que aún no han terminado)
        ahora = datetime.now()
        eventos_futuros = [e for e in eventos if e.fin > ahora]
        
        if eventos_futuros:
            st.info(f"📋 **Total de eventos próximos:** {len(eventos_futuros)}")
            
            for evento in eventos_futuros[:5]:  # Mostrar solo 5
                display_evento_card(evento)
            
            if len(eventos_futuros) > 5:
                st.info(f"Mostrando 5 de {len(eventos_futuros)} eventos. Ve a la sección 'Eventos' para ver todos.")
            
            # Mostrar eventos pasados filtrados si los hay
            eventos_pasados = len(eventos) - len(eventos_futuros)
            if eventos_pasados > 0:
                st.caption(f"ℹ️ Se omitieron {eventos_pasados} eventos que ya terminaron.")
        else:
            st.warning("No hay eventos futuros programados para los próximos 7 días.")
    else:
        st.warning("No hay eventos programados para los próximos 7 días.")
    
    
def show_eventos(planificador):
    """Gestión COMPLETA de eventos - Incluye todos"""
    st.title("📅 Gestión de Eventos - Vista Completa")
    
    # Filtros
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    with col_filtro1:
        # Selector de vista predefinida
        vista_predefinida = st.selectbox(
            "📋 Vista rápida",
            [
                "Todos los eventos",
                "próximos", 
                "completados",
                "en curso",
                "cancelados",
                "Histórico (más de 7 días)"
            ],
            key="vista_rapida"
        )
    
    with col_filtro2:
        # Slider de días 
        if vista_predefinida == "Todos los eventos":
            dias = st.slider("Días a mostrar", 1, 365, 365, 
                           help="Está función solo aplica para \"próximos\" (días a mostrar en el futuro) y \"completados\" (días a mostrar en el pasado)")
        else:
            dias = st.slider("Días a mostrar", 1, 365, 30)
    
    with col_filtro3:
        # Filtro por tipo
        tipo_filtro = st.selectbox(
            "Filtrar por tipo", 
            ["Todos", "entrenamiento", "procesamiento", "investigación", "reunión", "seminario", "inferencia"]
        )
    
     
    # lista base de todos los eventos primero
    todos_eventos = list(planificador.gestor_eventos.eventos.values())
    ahora = datetime.now()
    
    # Aplicar filtro de vista predefinida
    if vista_predefinida == "Todos los eventos":
        eventos = todos_eventos
    
    elif vista_predefinida == "próximos":
        # Eventos que inician en el futuro (dentro del rango de días)
        fecha_limite = ahora + timedelta(days=dias)
        eventos = [e for e in todos_eventos if ahora <= e.inicio <= fecha_limite]
    
    elif vista_predefinida == "completados":
        # Eventos completados en el rango de días hacia atrás
        fecha_limite = ahora - timedelta(days=dias)
        eventos = [e for e in todos_eventos if e.estado == 'completado' and e.fin >= fecha_limite]
    
    elif vista_predefinida == "en curso":
        # Eventos que están en curso ahora mismo
        eventos = [e for e in todos_eventos if e.estado == 'en_curso']
    
    elif vista_predefinida == "cancelados":
        # Eventos cancelados (sin límite temporal por defecto)
        eventos = [e for e in todos_eventos if e.estado == 'cancelado']
    
    elif vista_predefinida == "Histórico (más de 7 días)":
        # Eventos que terminaron hace más de 7 días
        limite = ahora - timedelta(days=7)
        eventos = [e for e in todos_eventos if e.fin < limite]
    
    else:
        # Caso por defecto (no debería ocurrir)
        eventos = []
        
    # Aplicar filtro de tipo
    if tipo_filtro != "Todos":
        eventos = [e for e in eventos if e.tipo == tipo_filtro]
    
    # Ordenar por fecha de inicio (más reciente primero)
    eventos.sort(key=lambda e: e.inicio, reverse=True)
    
    # Mostrar eventos
    if eventos:
        st.success(f"✅ Encontrados {len(eventos)} eventos")
        
        for evento in eventos:
            # Crear un contenedor para cada evento
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    **Nombre:** {evento.nombre}
                    
                    **Descripción:** {evento.descripcion or "Sin descripción"}
                    
                    **Inicio:** {evento.inicio.strftime('%d/%m/%Y %H:%M')}
                    **Fin:** {evento.fin.strftime('%d/%m/%Y %H:%M')}
                    **Duración:** {evento.duracion_horas:.1f} horas
                    
                    **Recursos:**
                    """)
                    
                    for recurso in evento.recursos:
                        st.markdown(f"- {recurso.nombre} ({recurso.tipo})")
                
                with col2:
                    st.markdown(f"""
                    **Tipo:** {badge_for_tipo(evento.tipo)}
                    **Estado:** {badge_for_estado(evento.estado)}
                    **Prioridad:** {"★" * evento.prioridad}
                    """, unsafe_allow_html=True)
                    
                    # Botones de acción
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if st.button("🗑️", key=f"del_{evento.id}", help="Eliminar evento"):
                            if planificador.eliminar_evento(evento.id):
                                st.success("✅ Evento eliminado")
                                planificador.guardar_datos()
                                st.rerun()
                            else:
                                st.error("❌ Error al eliminar")
                    
                    with col_btn2:
                        if st.button("❌", key=f"cancel_{evento.id}", help="Cancelar evento"):
                            if evento.estado != 'cancelado':
                                evento.cancelar()
                                st.success("✅ Evento cancelado")
                                planificador.guardar_datos()
                                st.rerun()
                            else:
                                st.info("⚠️ El evento ya está cancelado")

                    with col_btn3:
                        if st.button("🔄", key=f"refresh_{evento.id}", help="Reactivar evento"):
                            if evento.estado == 'cancelado':
                                evento.metadata["cancelado"] = False
                                st.success("✅ Evento reactivado")
                                planificador.guardar_datos()
                                st.rerun()
                            else:
                                st.info("⚠️ Solo se pueden reactivar eventos cancelados")
                    
                    # Mostrar información de estado actual
                    ahora = datetime.now()
                    if evento.estado == 'en_curso':
                        tiempo_restante = evento.fin - ahora
                        horas_restantes = tiempo_restante.total_seconds() / 3600
                        st.info(f"⏱️ **Tiempo restante:** {horas_restantes:.1f} horas")
                    
                    elif evento.estado == 'completado':
                        tiempo_transcurrido = ahora - evento.fin
                        dias_transcurridos = tiempo_transcurrido.days
                        if dias_transcurridos == 0:
                            st.success(f"✅ Completado hace {tiempo_transcurrido.seconds // 3600} horas")
                        else:
                            st.success(f"✅ Completado hace {dias_transcurridos} días")
                
                st.markdown("---")
    else:
        st.warning("No hay eventos que coincidan con los filtros.")

def show_recursos(planificador):
    """Gestión de recursos"""
    st.title("🔧 Gestión de Recursos")
    
    # Filtros
    col1, = st.columns(1)  
    with col1:
        tipo_filtro = st.selectbox("Filtrar por tipo", ["Todos", "humano", "computacional", "espacio"])
    
    # Obtener recursos
    recursos = planificador.listar_recursos()
    
    # Aplicar filtros
    if tipo_filtro != "Todos":
        recursos = [r for r in recursos if r.tipo == tipo_filtro]
    
    # Mostrar en pestañas
    tab1, tab2 = st.tabs(["📋 Lista de Recursos", "📊 Agenda por Recurso"])
    
    with tab1:
        if recursos:
            st.success(f"✅ Encontrados {len(recursos)} recursos")
            
            for recurso in recursos:
                with st.expander(f"{recurso.nombre} ({recurso.tipo})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **ID:** `{recurso.id}`
                        
                        **Capacidad:** {recurso.capacidad} unidades
                        
                        **Atributos:**
                        """)
                        
                        if recurso.atributos:
                            for key, value in recurso.atributos.items():
                                st.markdown(f"- **{key}:** {value}")
                        else:
                            st.markdown("Sin atributos adicionales")
                    
                    with col2:
                        st.markdown(f"""
                        **Tipo:** {badge_for_recurso(recurso)}
                        """, unsafe_allow_html=True)
        else:
            st.warning("No hay recursos que coincidan con los filtros.")
    
    with tab2:
        st.subheader("📊 Agenda por Recurso")
        
        if recursos:
            recurso_seleccionado = st.selectbox(
                "Seleccionar recurso para ver agenda",
                [r.nombre for r in recursos],
                key="agenda_selector"
            )
            
            recurso = next((r for r in recursos if r.nombre == recurso_seleccionado), None)
            
            if recurso:
                dias = st.slider("Días a mostrar", 1, 30, 7, key="agenda_dias")
                eventos = planificador.obtener_agenda_recurso(recurso.id, dias=dias)
                
                if eventos:
                    st.info(f"📅 {len(eventos)} eventos programados para {recurso.nombre}")
                    
                    # Crear timeline
                    timeline_data = []
                    for evento in eventos:
                        timeline_data.append({
                            "Evento": evento.nombre,
                            "Inicio": evento.inicio,
                            "Fin": evento.fin,
                            "Tipo": evento.tipo,
                            "Estado": evento.estado,
                            "Duración (h)": evento.duracion_horas
                        })
                    
                    df = pd.DataFrame(timeline_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Visualización gráfica
                    fig = px.timeline(
                        df, 
                        x_start="Inicio", 
                        x_end="Fin", 
                        y="Evento",
                        color="Estado",
                        title=f"Agenda de {recurso.nombre}"
                    )
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.success(f"✅ No hay eventos programados para {recurso.nombre} en los próximos {dias} días.")

def show_nuevo_evento(planificador):
    """Formulario para nuevo evento"""
    st.title("➕ Planificar Nuevo Evento")
    
    # Inicializar estado si no existe
    if 'evento_planificado' not in st.session_state:
        st.session_state.evento_planificado = None
    
    # Formulario principal
    with st.form("nuevo_evento_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("📝 Nombre del Evento *", placeholder="Ej: Entrenamiento modelo CNN")
            descripcion = st.text_area("📄 Descripción", placeholder="Descripción detallada del evento...")
            tipo = st.selectbox("🎯 Tipo de Evento *", ["entrenamiento", "procesamiento", "investigación", "reunión", "seminario", "inferencia"])
            prioridad = st.slider("⭐ Prioridad (1-5)", 1, 5, 3)
        
        with col2:
            # Usar key en los controles para que Streamlit maneje el estado automáticamente
            fecha = st.date_input(
                "📅 Fecha de inicio *", 
                datetime.now().date(),
                key="nuevo_evento_fecha"
            )
            
            hora_inicio = st.time_input(
                "⏰ Hora de inicio *", 
                datetime.now().time(),
                key="nuevo_evento_hora_inicio"
            )
            
            # Fecha y hora de fin
            col_fecha_fin, col_hora_fin = st.columns(2)
            
            with col_fecha_fin:
                fecha_fin = st.date_input(
                    "📅 Fecha de fin *", 
                    datetime.now().date(),
                    key="nuevo_evento_fecha_fin"
                )
            
            with col_hora_fin:
                hora_fin = st.time_input(
                    "⏰ Hora de fin *", 
                    (datetime.now() + timedelta(hours=2)).time(),
                    key="nuevo_evento_hora_fin"
                )
            
            # Calcular inicio y fin completos
            inicio = datetime.combine(fecha, hora_inicio)
            fin = datetime.combine(fecha_fin, hora_fin)
            
            # Calcular duración en horas
            if inicio and fin:
                if fin <= inicio:
                    st.error("❌ La fecha/hora de fin debe ser posterior a la de inicio")
                else:
                    duracion_horas = (fin - inicio).total_seconds() / 3600
                    
                    # Validar duración máxima (7 días = 168 horas)
                    if duracion_horas > 168:
                        st.error("❌ Los eventos no pueden durar más de 7 días (168 horas)")
                        duracion_horas = 168  # Limitar para mostrar correctamente
                    
                    # Mostrar información de duración
                    if duracion_horas >= 24:
                        dias = int(duracion_horas // 24)
                        horas_resto = duracion_horas % 24
                        duracion_str = f"{dias} días y {horas_resto:.1f} horas"
                    else:
                        duracion_str = f"{duracion_horas:.1f} horas"
                    
                    
                    
            # Calcular estado automático
            ahora = datetime.now()
            if inicio > ahora:
                estado_automatico = "planificado"
            elif inicio <= ahora <= fin:
                estado_automatico = "en_curso"
            else:
                estado_automatico = "completado"
            
            st.info(f"**Estado automático:** {estado_automatico.upper()}")
        
        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)
        st.subheader("🔧 Selección de Recursos")
        
        # Listar recursos disponibles por tipo
        recursos_disponibles = planificador.listar_recursos()
        
        col_tipo1, col_tipo2, col_tipo3 = st.columns(3)
        
        recursos_seleccionados = {}
        
        with col_tipo1:
            st.markdown("### 🧑‍🔬 Recursos Humanos")
            humanos = [r for r in recursos_disponibles if r.tipo == "humano"]
            for recurso in humanos:
                cantidad = st.number_input(
                    f"{recurso.nombre} (Cap: {recurso.capacidad})",
                    0, recurso.capacidad, 0, 1,
                    key=f"hum_{recurso.id}"
                )
                if cantidad > 0:
                    recursos_seleccionados[recurso.id] = cantidad
        
        with col_tipo2:
            st.markdown("### 💻 Recursos Computacionales")
            computacionales = [r for r in recursos_disponibles if r.tipo == "computacional"]
            for recurso in computacionales:
                cantidad = st.number_input(
                    f"{recurso.nombre} (Cap: {recurso.capacidad})",
                    0, recurso.capacidad, 0, 1,
                    key=f"comp_{recurso.id}"
                )
                if cantidad > 0:
                    recursos_seleccionados[recurso.id] = cantidad
        
        with col_tipo3:
            st.markdown("### 🏢 Espacios")
            espacios = [r for r in recursos_disponibles if r.tipo == "espacio"]
            for recurso in espacios:
                cantidad = st.number_input(
                    f"{recurso.nombre} (Cap: {recurso.capacidad})",
                    0, recurso.capacidad, 0, 1,
                    key=f"esp_{recurso.id}"
                )
                if cantidad > 0:
                    recursos_seleccionados[recurso.id] = cantidad
        
        # Opciones avanzadas
        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)
        st.subheader("⚙️ Opciones Avanzadas")
        
        cols_avanzadas = st.columns(2)  # Guardar la lista

        with cols_avanzadas[0].container():  # Primera columna
            buscar_hueco = st.checkbox("🔍 Buscar hueco automáticamente si ocupado", True)
        
        # Botón de envío
        submitted = st.form_submit_button("🚀 Planificar Evento", use_container_width=True)
    
    # Procesar el formulario después de enviarlo
    if submitted:
        # Validaciones básicas
        if not nombre:
            st.error("❌ El nombre del evento es obligatorio")
            st.session_state.evento_planificado = False
            return
        
        if not recursos_seleccionados:
            st.error("❌ Debe seleccionar al menos un recurso")
            st.session_state.evento_planificado = False
            return
        
        if inicio >= fin:
            st.error("❌ La hora de inicio debe ser anterior a la de fin")
            st.session_state.evento_planificado = False
            return
        
        # Mostrar resumen
        st.markdown("### 📋 Resumen del Evento")
        col_sum1, col_sum2 = st.columns(2)
        
        with col_sum1:
            st.markdown(f"""
            **Nombre:** {nombre}
            **Tipo:** {tipo}
            **Prioridad:** {prioridad}
            **Descripción:** {descripcion or 'Sin descripción'}
            """)
        
        with col_sum2:
            if duracion_horas >= 24:
                dias = int(duracion_horas // 24)
                horas_resto = duracion_horas % 24
                duracion_str = f"{dias} días y {horas_resto:.1f} horas"
            else:
                duracion_str = f"{duracion_horas} horas"
            
            # Formatear fecha de fin
            if duracion_horas >= 24:
                fin_str = fin.strftime('%d/%m/%Y %H:%M')
            else:
                fin_str = fin.strftime('%H:%M')
            
            st.markdown(f"""
            **Fecha:** {fecha}
            **Inicio:** {hora_inicio}
            **Fin:** {fin_str}
            **Duración:** {duracion_str}
            **Estado inicial:** {estado_automatico.upper()}
            """)
        
        st.markdown("**Recursos seleccionados:**")
        for recurso_id, cantidad in recursos_seleccionados.items():
            recurso = planificador.gestor_recursos.obtener_recurso(recurso_id)
            if recurso:
                st.markdown(f"- {recurso.nombre}: {cantidad} unidad(es)")
        
        # Planificar evento con manejo de errores
        with st.spinner("⏳ Planificando evento..."):
            try:
                resultado = planificador.planificar_evento(
                    nombre=nombre,
                    inicio=inicio,
                    fin=fin,
                    recursos_seleccionados=recursos_seleccionados,
                    tipo=tipo,
                    descripcion=descripcion,
                    prioridad=prioridad,
                    buscar_hueco_si_ocupado=buscar_hueco
                )
            except ValueError as e:
                st.error(f"❌ Error de validación: {str(e)}")
                st.session_state.evento_planificado = False
                return
        
        if resultado["success"]:
            detalles = resultado.get('detalles', {})
            inicio_original = detalles.get('inicio_original')
            inicio_asignado = detalles.get('inicio_asignado')
            
            # Comparar fechas directamente
            if inicio_original and inicio_asignado and inicio_original != inicio_asignado:
                # Evento replanificado
                st.warning("⚠️ **¡Atención! El evento fue movido a otro horario**")
                
                st.markdown(f"""
                | | Original (Solicitado) | Asignado (Real) |
                |-|-----------------------|-----------------|
                | **Fecha** | {inicio_original.strftime('%d/%m/%Y')} | {inicio_asignado.strftime('%d/%m/%Y')} |
                | **Hora** | {inicio_original.strftime('%H:%M')} | {inicio_asignado.strftime('%H:%M')} |
                | **Estado** | ❌ No disponible | ✅ Planificado |
                """)
                
                st.info(f"💡 **Razón:** Recursos ocupados en el horario original")
                
            else:
                # Evento en fecha original
                st.success("✅ Evento planificado en la fecha solicitada")
                if resultado.get("evento"):
                    e = resultado["evento"]
                    st.markdown(f"**Fecha real:** {e.inicio.strftime('%d/%m/%Y %H:%M')}")
                    st.success(f"✅ {resultado['message']}")
                    st.session_state.evento_planificado = True
                    
                    # Guardar tras crear evento
                    planificador.guardar_datos()
                    
                    # Botones adicionales si se creó un evento
            if st.session_state.get('evento_planificado'):
                st.markdown("<div class='separator'></div>", unsafe_allow_html=True)
                col_btn2, = st.columns(1)
                with col_btn2:
                    if st.button("➕ Crear Otro Evento", use_container_width=True):
                        st.session_state.evento_planificado = None
                        st.rerun()
                    
        else:
            error_message = resultado.get('message', 'Error desconocido')
            st.error(f"❌ {error_message}")
            st.session_state.evento_planificado = False
            
            

def show_buscar_huecos(planificador):
    """Búsqueda de huecos disponibles"""
    st.title("🔍 Buscar Huecos Disponibles")
    
    st.markdown("""
    Encuentra espacios disponibles en la agenda para planificar nuevos eventos.
    """)
    
    # Inicializar estado para resultados
    if 'huecos_encontrados' not in st.session_state:
        st.session_state.huecos_encontrados = None
    
    # Inicializar la hora de inicio en el estado de sesión si no existe
    if 'hora_inicio_busqueda' not in st.session_state:
        st.session_state.hora_inicio_busqueda = datetime.now().time()
    
    # Formulario principal
    with st.form("buscar_huecos_form"):
        # Selección de recursos
        st.subheader("1. Selecciona los recursos necesarios")
        
        recursos_disponibles = planificador.listar_recursos()
        recursos_ids = []
        
        col_tipo1, col_tipo2, col_tipo3 = st.columns(3)
        
        with col_tipo1:
            st.markdown("#### 🧑‍🔬 Humanos")
            for recurso in [r for r in recursos_disponibles if r.tipo == "humano"]:
                if st.checkbox(recurso.nombre, key=f"bh_hum_{recurso.id}"):
                    recursos_ids.append(recurso.id)
        
        with col_tipo2:
            st.markdown("#### 💻 Computacionales")
            for recurso in [r for r in recursos_disponibles if r.tipo == "computacional"]:
                if st.checkbox(recurso.nombre, key=f"bh_comp_{recurso.id}"):
                    recursos_ids.append(recurso.id)
        
        with col_tipo3:
            st.markdown("#### 🏢 Espacios")
            for recurso in [r for r in recursos_disponibles if r.tipo == "espacio"]:
                if st.checkbox(recurso.nombre, key=f"bh_esp_{recurso.id}"):
                    recursos_ids.append(recurso.id)
        
        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)
        
        # Parámetros de búsqueda
        st.subheader("2. Especifica los parámetros de búsqueda")
        
        col_params1, col_params2, col_params3 = st.columns(3)
        
        with col_params1:
            duracion_horas = st.number_input("⏱️ Duración necesaria (horas)", 0.5, 24.0, 2.0, 0.5)
        
        with col_params2:
            dias_busqueda = st.slider("📅 Días a buscar", 1, 30, 7)
        
        with col_params3:
            # Usar la hora guardada en el estado de sesión
            hora_inicio_min = st.time_input(
                "⏰ Buscar a partir de", 
                value=st.session_state.hora_inicio_busqueda,
                key="hora_inicio_busqueda_input"
            )
            # Actualizar el estado de sesión con la nueva selección
            st.session_state.hora_inicio_busqueda = hora_inicio_min
        
        # Botón de búsqueda
        submitted = st.form_submit_button("🔎 Buscar Huecos", use_container_width=True)
    
    # Procesar la búsqueda después de enviar el formulario
    if submitted:
        if not recursos_ids:
            st.error("❌ Debe seleccionar al menos un recurso")
            st.session_state.huecos_encontrados = None
            return
        
        with st.spinner(f"🔍 Buscando huecos para {len(recursos_ids)} recursos..."):
            inicio_busqueda = datetime.combine(datetime.now().date(), hora_inicio_min)
            
            # Si la hora seleccionada ya pasó hoy, usar la hora seleccionada para mañana
            if inicio_busqueda < datetime.now():
                inicio_busqueda += timedelta(days=1)
            
            # Llamar al método de búsqueda
            try:
                huecos = planificador.buscar_hueco_disponible(
                    recursos_ids=recursos_ids,
                    duracion_horas=duracion_horas,
                    inicio_busqueda=inicio_busqueda,
                    dias=dias_busqueda
                )
            except Exception as e:
                st.error(f"❌ Error al buscar huecos: {str(e)}")
                huecos = []
        
        st.session_state.huecos_encontrados = huecos
    
    # Mostrar resultados
    if st.session_state.huecos_encontrados is not None:
        huecos = st.session_state.huecos_encontrados
        
        if huecos:
            # Visualización gráfica
            st.subheader("📊 Visualización de Huecos")
            
            fig_data = []
            for hueco in huecos[:10]:  # Mostrar solo 10 en el gráfico
                fig_data.append({
                    "Recursos": f"Hueco {hueco['inicio'].strftime('%H:%M')}",
                    "Inicio": hueco['inicio'],
                    "Fin": hueco['fin']
                })
            
            if fig_data:
                df_fig = pd.DataFrame(fig_data)
                fig = px.timeline(
                    df_fig,
                    x_start="Inicio",
                    x_end="Fin",
                    y="Recursos",
                    title="Huecos Disponibles (Próximos 10)",
                    color_discrete_sequence=['#00D4FF']
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Sugerir planificar en el primer hueco
            if huecos:
                st.markdown("<div class='separator'></div>", unsafe_allow_html=True)
                st.subheader("🚀 Planificar en este hueco")
                
                if st.button(f"📅 Planificar en {huecos[0]['inicio'].strftime('%d/%m %H:%M')}"):
                    st.session_state.hueco_seleccionado = huecos[0]
                    st.session_state.nuevo_evento_precargado = {
                        'hueco': huecos[0],
                        'recursos_ids': recursos_ids
                    }
                    st.session_state.current_page = "nuevo_evento"
                    st.rerun()
        else:
            st.warning("⚠️ No se encontraron huecos disponibles con los criterios especificados.")
            st.info("💡 Prueba con:")
            st.markdown("- Menos recursos seleccionados")
            st.markdown("- Duración más corta")
            st.markdown("- Ampliar el rango de búsqueda")
            
def show_datos(planificador):
    """Gestión de datos y persistencia"""
    st.title("💾 Gestión de Datos")
    
    # Dos pestañas
    tab1, tab2 = st.tabs(["📁 Guardar/Cargar", "🗑️ Limpieza"])
    
    with tab1:
        st.subheader("📁 Guardar y Cargar Datos")
        
        col_save1, col_save2 = st.columns(2)
        
        with col_save1:
            st.markdown("#### 💾 Guardar Datos Actuales")
            nombre_archivo = st.text_input("Nombre del archivo", "datos.json")
            
            if st.button("💾 Guardar Datos", use_container_width=True):
                with st.spinner("Guardando..."):
                    if planificador.guardar_datos(nombre_archivo):
                        st.success(f"✅ Datos guardados en {nombre_archivo}")
                    else:
                        st.error("❌ Error al guardar datos")
        
        with col_save2:
            st.markdown("#### 📂 Cargar Datos")
            archivo_cargar = st.text_input("Archivo a cargar", "datos.json")
            
            if st.button("📂 Cargar Datos", use_container_width=True):
                with st.spinner("Cargando..."):
                    if planificador.cargar_datos(archivo_cargar):
                        st.success("✅ Datos cargados exitosamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al cargar datos")
        
        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)
        
        # Backup
        st.subheader("🔄 Sistema de Backup")
        
        if st.button("🛡️ Crear Backup Automático", use_container_width=True):
            from infraestructura.persistencia import Persistencia
            try:
                archivo_backup = Persistencia.crear_backup(
                    planificador.gestor_recursos,
                    planificador.gestor_eventos,
                    planificador.restricciones
                )
                st.success(f"✅ Backup creado: {os.path.basename(archivo_backup)}")
            except Exception as e:
                st.error(f"❌ Error al crear backup: {e}")
    
    # Pestaña 2 
    with tab2:
        st.subheader("🗑️ Limpieza de Eventos")
        
        st.markdown("""
        <div class="card">
            <h4>📊 Política de Retención</h4>
            <p>Los eventos se conservan para análisis histórico. Puedes limpiar eventos pasados para mantener el sistema ágil.</p>
            <p><strong>Nota:</strong> Los eventos cancelados nunca se eliminan automáticamente.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_limp1, col_limp2 = st.columns(2)
        
        with col_limp1:
            dias_retencion = st.slider(
                "Conservar eventos hasta (días atrás)",
                1, 365, 30,
                help="Eventos más antiguos serán eliminados"
            )
            
            if st.button("🧹 Limpiar eventos pasados", use_container_width=True, type="secondary"):
                with st.spinner("Limpiando eventos..."):
                    eliminados = limpiar_eventos_pasados(planificador, dias_retencion)
                    if eliminados > 0:
                        st.success(f"✅ Se eliminaron {eliminados} eventos de hace más de {dias_retencion} días")
                        st.rerun()
                    else:
                        st.info("ℹ️ No hay eventos para eliminar con estos criterios")
                        


# EJECUCIÓN DE LA APLICACIÓN

if __name__ == "__main__":
    main()