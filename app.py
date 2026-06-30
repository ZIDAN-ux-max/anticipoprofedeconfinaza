# -*- coding: utf-8 -*-
import streamlit as st
from groq import Groq
from supabase import create_client
import hashlib
import PyPDF2
import io
from datetime import datetime, timedelta, date

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SERVICE_KEY"])

st.set_page_config(
    page_title="Tu Profe de Confianza",
    page_icon=":notebook:",
    layout="centered"
)

# ============================================================
# SISTEMA DE DISEÑO: "CUADERNO UNIVERSITARIO"
# Paleta: papel crema, tinta café, terracota, verde musgo, azul tinta
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,500&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --papel: #FAF6EC;
        --papel-2: #F2ECDC;
        --tinta: #2B2118;
        --tinta-suave: #6B5D4F;
        --terracota: #C65D32;
        --musgo: #3A6B5C;
        --azul-tinta: #1E5C8C;
        --resaltador: #D4A24C;
        --linea-cuaderno: rgba(43, 33, 24, 0.08);
    }

    .stApp {
        background-color: var(--papel);
        background-image: repeating-linear-gradient(
            transparent, transparent 31px, var(--linea-cuaderno) 32px
        );
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: var(--tinta);
    }

    h1, h2, h3, .display-font {
        font-family: 'Fraunces', serif !important;
        color: var(--tinta) !important;
        font-weight: 600;
    }

    /* Encabezado tipografico (reemplaza banners de imagen) */
    .brand-header {
        text-align: center;
        padding: 28px 10px 18px 10px;
        border-bottom: 2px dashed var(--tinta-suave);
        margin-bottom: 10px;
    }
    .brand-icon {
        font-size: 2.4em;
        display: block;
        margin-bottom: 4px;
    }
    .brand-title {
        font-family: 'Fraunces', serif;
        font-size: 2.1em;
        font-weight: 700;
        color: var(--terracota);
        margin: 0;
        letter-spacing: -0.5px;
    }
    .brand-subtitle {
        font-family: 'Inter', sans-serif;
        color: var(--tinta-suave);
        font-size: 1em;
        margin-top: 4px;
    }
    .sidebar-brand {
        text-align: center;
        padding: 10px 0 16px 0;
        border-bottom: 2px dashed var(--tinta-suave);
        margin-bottom: 14px;
    }
    .sidebar-brand .brand-icon { font-size: 1.8em; }
    .sidebar-brand .brand-title { font-size: 1.3em; }

    /* Sidebar con filo tipo margen de cuaderno */
    [data-testid="stSidebar"] {
        background-color: var(--papel-2);
        border-right: 3px solid var(--terracota);
    }
    [data-testid="stSidebar"] > div:first-child {
        border-left: 6px solid #D9534F;
        padding-left: 14px;
    }

    .stChatMessage {
        border-radius: 10px;
        background-color: #FFFFFF !important;
        border: 1px solid var(--linea-cuaderno);
    }

    /* Fichas de estadisticas: borde izquierdo de color, no tarjeta centrada generica */
    .stat-card {
        background: #FFFFFF;
        border-radius: 6px;
        border-left: 5px solid var(--terracota);
        padding: 18px 20px;
        margin-bottom: 10px;
        box-shadow: 1px 2px 4px rgba(43,33,24,0.06);
    }
    .stat-number {
        font-family: 'Fraunces', serif;
        font-size: 2.3em;
        font-weight: 700;
        color: var(--tinta);
        line-height: 1;
    }
    .stat-label {
        color: var(--tinta-suave);
        font-size: 0.85em;
        margin-top: 4px;
    }

    /* Logros como stickers pegados, con leve rotacion */
    .logro-card {
        background: var(--papel);
        border: 2px solid var(--tinta);
        border-radius: 10px;
        padding: 14px;
        text-align: center;
        color: var(--tinta);
        margin: 6px;
        min-height: 120px;
        box-shadow: 2px 3px 0px var(--terracota);
        transform: rotate(-1.5deg);
    }
    .logro-card:nth-child(2n) { transform: rotate(1.5deg); }
    .logro-card:nth-child(3n) { transform: rotate(-0.5deg); }
    .logro-emoji { font-size: 2em; }
    .logro-nombre { font-family: 'Fraunces', serif; font-weight: 600; font-size: 0.95em; margin-top: 5px; }
    .logro-desc { font-size: 0.75em; color: var(--tinta-suave); }
    .logro-bloqueado {
        background: #EAE3D3;
        border: 2px dashed #B8AD98;
        color: #9C8F7A;
        box-shadow: none;
        transform: none !important;
    }

    /* Racha como "ticket" con borde punteado */
    .racha-card {
        background: var(--papel);
        border: 2px dashed var(--terracota);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        color: var(--tinta);
        margin-bottom: 10px;
    }

    /* Ranking tipo lista de honor */
    .rank-row {
        background: #FFFFFF;
        border-radius: 6px;
        padding: 14px 16px;
        margin-bottom: 8px;
        box-shadow: 1px 2px 4px rgba(43,33,24,0.06);
        border-left: 4px solid var(--musgo);
    }
    .rank-row.es-yo {
        border-left: 4px solid var(--terracota);
        background: #FFF8EC;
    }

    .badge-nivel {
        background: var(--resaltador);
        color: var(--tinta);
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 0.85em;
        font-weight: 600;
    }

    .stButton button {
        font-family: 'Inter', sans-serif;
        border-radius: 6px;
        border: 1.5px solid var(--tinta);
        background-color: var(--papel);
        color: var(--tinta);
    }
    .stButton button:hover {
        background-color: var(--terracota);
        color: white;
        border-color: var(--terracota);
    }
</style>
""", unsafe_allow_html=True)

LOGROS_DISPONIBLES = [
    {"nombre": "Primera Pregunta", "descripcion": "Hiciste tu primera pregunta", "emoji": "🌟", "condicion": "total", "valor": 1},
    {"nombre": "Estudiante Activo", "descripcion": "10 preguntas en total", "emoji": "📚", "condicion": "total", "valor": 10},
    {"nombre": "Crack del Saber", "descripcion": "50 preguntas en total", "emoji": "🏆", "condicion": "total", "valor": 50},
    {"nombre": "Centenario", "descripcion": "100 preguntas en total", "emoji": "💯", "condicion": "total", "valor": 100},
    {"nombre": "Matematico", "descripcion": "10 preguntas de matematicas", "emoji": "📐", "condicion": "matematicas", "valor": 10},
    {"nombre": "Crack de Mates", "descripcion": "50 preguntas de matematicas", "emoji": "🔢", "condicion": "matematicas", "valor": 50},
    {"nombre": "Ingles Basic", "descripcion": "10 preguntas de ingles", "emoji": "🇺🇸", "condicion": "ingles", "valor": 10},
    {"nombre": "English Master", "descripcion": "50 preguntas de ingles", "emoji": "🌍", "condicion": "ingles", "valor": 50},
    {"nombre": "Estudiantazo", "descripcion": "10 preguntas en un dia", "emoji": "⚡", "condicion": "hoy", "valor": 10},
    {"nombre": "Imparable", "descripcion": "20 preguntas en un dia", "emoji": "🔥", "condicion": "hoy", "valor": 20},
    {"nombre": "Primer Parcial", "descripcion": "7 dias seguidos estudiando", "emoji": "🎓", "condicion": "racha", "valor": 7},
    {"nombre": "Aplicado", "descripcion": "30 dias seguidos estudiando", "emoji": "📝", "condicion": "racha", "valor": 30},
    {"nombre": "En Racha", "descripcion": "3 dias seguidos estudiando", "emoji": "🔥", "condicion": "racha", "valor": 3},
    {"nombre": "Madrugador", "descripcion": "Estudio antes de las 7am", "emoji": "⏰", "condicion": "hora", "valor": 7},
    {"nombre": "Noctambulo", "descripcion": "Estudio despues de las 11pm", "emoji": "🌙", "condicion": "hora", "valor": 23},
    {"nombre": "Perseverante", "descripcion": "200 preguntas en total", "emoji": "💪", "condicion": "total", "valor": 200},
    {"nombre": "Bibliofilo", "descripcion": "Subio 5 archivos PDF", "emoji": "📖", "condicion": "pdfs", "valor": 5},
]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login(email, password):
    result = supabase.table("usuarios").select("*").eq("email", email).eq("password", hash_password(password)).execute()
    if result.data:
        return result.data[0]
    return None

def registrar(nombre, email, password):
    try:
        result = supabase.table("usuarios").insert({
            "nombre": nombre,
            "email": email,
            "password": hash_password(password)
        }).execute()
        return result.data[0]
    except:
        return None

def guardar_conversacion(usuario_id, mensaje, respuesta, materia):
    supabase.table("conversaciones").insert({
        "usuario_id": usuario_id,
        "mensaje": mensaje,
        "respuesta": respuesta,
        "materia": materia,
        "fecha": datetime.now().isoformat()
    }).execute()

def cargar_conversaciones(usuario_id, materia):
    result = supabase.table("conversaciones").select("*").eq("usuario_id", usuario_id).eq("materia", materia).execute()
    historial = []
    for conv in result.data:
        historial.append({"role": "user", "content": conv["mensaje"]})
        historial.append({"role": "assistant", "content": conv["respuesta"]})
    return historial

def registrar_asistencia(usuario_id):
    try:
        hoy = date.today().isoformat()
        hora_actual = datetime.now().hour
        existe = supabase.table("asistencia").select("*").eq("usuario_id", usuario_id).eq("fecha", hoy).execute()
        if not existe.data:
            usuario = supabase.table("usuarios").select("*").eq("id", usuario_id).execute().data[0]
            ultima = usuario.get("ultima_visita")
            racha_actual = usuario.get("racha") or 0
            if ultima:
                ultima_date = date.fromisoformat(str(ultima).split("T")[0])
                diferencia = (date.today() - ultima_date).days
                if diferencia == 1:
                    racha_actual += 1
                elif diferencia > 1:
                    racha_actual = 1
            else:
                racha_actual = 1
            supabase.table("asistencia").insert({
                "usuario_id": usuario_id,
                "fecha": hoy,
                "racha": racha_actual,
                "hora": hora_actual
            }).execute()
            supabase.table("usuarios").update({
                "racha": racha_actual,
                "ultima_visita": hoy
            }).eq("id", usuario_id).execute()
        return supabase.table("usuarios").select("racha").eq("id", usuario_id).execute().data[0].get("racha", 0)
    except:
        return 0

def obtener_estadisticas(usuario_id):
    result = supabase.table("conversaciones").select("*").eq("usuario_id", usuario_id).execute()
    total = len(result.data)
    mate = len([c for c in result.data if c["materia"] == "Matematicas"])
    ingles = len([c for c in result.data if c["materia"] == "Ingles"])
    hoy = datetime.now().date()
    semana = datetime.now() - timedelta(days=7)
    hoy_count = 0
    semana_count = 0
    for c in result.data:
        try:
            if c.get("fecha"):
                fecha = datetime.fromisoformat(str(c["fecha"]).replace("Z", "+00:00").split("+")[0])
                if fecha.date() == hoy:
                    hoy_count += 1
                if fecha >= semana.replace(tzinfo=None):
                    semana_count += 1
        except:
            pass
    try:
        racha_result = supabase.table("usuarios").select("racha").eq("id", usuario_id).execute()
        racha_val = racha_result.data[0].get("racha", 0) if racha_result.data else 0
    except:
        racha_val = 0
    hora_actual = datetime.now().hour
    return {
        "total": total,
        "matematicas": mate,
        "ingles": ingles,
        "hoy": hoy_count,
        "semana": semana_count,
        "racha": racha_val,
        "hora": hora_actual,
        "pdfs": 0
    }

def obtener_ranking():
    try:
        result = supabase.table("conversaciones").select("usuario_id").execute()
        conteo = {}
        for c in result.data:
            uid = c["usuario_id"]
            conteo[uid] = conteo.get(uid, 0) + 1
        ranking = []
        for uid, total in sorted(conteo.items(), key=lambda x: x[1], reverse=True)[:10]:
            usuario = supabase.table("usuarios").select("nombre, racha").eq("id", uid).execute()
            if usuario.data:
                logros = supabase.table("logros").select("nombre").eq("usuario_id", uid).execute()
                ranking.append({
                    "nombre": usuario.data[0]["nombre"],
                    "total": total,
                    "racha": usuario.data[0].get("racha", 0),
                    "logros": len(logros.data)
                })
        return ranking
    except:
        return []

def obtener_logros_usuario(usuario_id):
    result = supabase.table("logros").select("nombre").eq("usuario_id", usuario_id).execute()
    return [l["nombre"] for l in result.data]

def otorgar_logro(usuario_id, logro):
    supabase.table("logros").insert({
        "usuario_id": usuario_id,
        "nombre": logro["nombre"],
        "descripcion": logro["descripcion"],
        "emoji": logro["emoji"],
        "fecha": datetime.now().isoformat()
    }).execute()

def verificar_logros(usuario_id, stats):
    logros_actuales = obtener_logros_usuario(usuario_id)
    nuevos_logros = []
    for logro in LOGROS_DISPONIBLES:
        if logro["nombre"] not in logros_actuales:
            condicion = logro["condicion"]
            valor = logro["valor"]
            if condicion == "hora":
                if valor == 7 and stats["hora"] < 7:
                    otorgar_logro(usuario_id, logro)
                    nuevos_logros.append(logro)
                elif valor == 23 and stats["hora"] >= 23:
                    otorgar_logro(usuario_id, logro)
                    nuevos_logros.append(logro)
            elif condicion in stats and stats[condicion] >= valor:
                otorgar_logro(usuario_id, logro)
                nuevos_logros.append(logro)
    return nuevos_logros

def extraer_texto_pdf(archivo):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(archivo.read()))
        texto = ""
        for page in pdf_reader.pages:
            texto += page.extract_text()
        return texto[:3000]
    except:
        return None

def obtener_nivel(total):
    if total < 10:
        return "Principiante 🌱", "var(--musgo)"
    elif total < 50:
        return "Intermedio ⭐", "var(--resaltador)"
    elif total < 100:
        return "Avanzado 🔥", "var(--terracota)"
    else:
        return "Experto 👑", "var(--azul-tinta)"

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    st.markdown("""
    <div class='brand-header'>
        <span class='brand-icon'>📓</span>
        <p class='brand-title'>Tu Profe de Confianza</p>
        <p class='brand-subtitle'>Aprende Matematicas e Ingles a tu ritmo, 24/7 y gratis</p>
    </div>
    """, unsafe_allow_html=True)
    try:
        total_usuarios = supabase.table("usuarios").select("id", count="exact").execute()
        st.markdown(f"<p style='text-align:center; color:var(--tinta-suave)'>🎓 {total_usuarios.count} estudiantes ya aprenden con nosotros</p>", unsafe_allow_html=True)
    except:
        pass
    st.divider()

    tab1, tab2 = st.tabs(["Iniciar Sesion", "Registrarse"])

    with tab1:
        st.subheader("Bienvenido de vuelta")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Contrasena", type="password", key="login_pass")
        if st.button("Entrar", use_container_width=True):
            usuario = login(email, password)
            if usuario:
                st.session_state.usuario = usuario
                st.rerun()
            else:
                st.error("Email o contrasena incorrectos")

    with tab2:
        st.subheader("Crea tu cuenta gratis")
        nombre = st.text_input("Tu nombre", key="reg_nombre")
        email_reg = st.text_input("Email", key="reg_email")
        password_reg = st.text_input("Contrasena", type="password", key="reg_pass")
        if st.button("Registrarse", use_container_width=True):
            if nombre and email_reg and password_reg:
                usuario = registrar(nombre, email_reg, password_reg)
                if usuario:
                    st.session_state.usuario = usuario
                    st.rerun()
                else:
                    st.error("El email ya existe")
            else:
                st.warning("Completa todos los campos")

else:
    usuario = st.session_state.usuario
    racha = registrar_asistencia(usuario["id"])
    stats = obtener_estadisticas(usuario["id"])
    nivel, nivel_color = obtener_nivel(stats["total"])

    with st.sidebar:
        st.markdown("""
        <div class='sidebar-brand'>
            <span class='brand-icon'>📓</span>
            <p class='brand-title'>Tu Profe</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"### Hola, {usuario['nombre']} 👋")
        st.markdown(f"<span class='badge-nivel'>{nivel}</span>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:var(--terracota); font-weight:bold; margin-top:8px'>🔥 Racha: {racha} dias</p>", unsafe_allow_html=True)
        st.divider()
        seccion = st.radio("Menu", ["Chat", "Mis Estadisticas", "Mis Logros", "Ranking", "Acerca de"])
        st.divider()
        if seccion == "Chat":
            modo = st.radio("Que quieres estudiar?", ["Matematicas", "Ingles"])
            st.divider()
            st.markdown("### Sube un archivo")
            archivo = st.file_uploader("PDF o imagen", type=["pdf", "png", "jpg", "jpeg"])
            if archivo:
                st.success(f"Archivo cargado: {archivo.name}")
                st.session_state.archivo = archivo
            else:
                st.session_state.archivo = None
        st.divider()
        if st.button("Cerrar sesion", use_container_width=True):
            st.session_state.usuario = None
            st.session_state.historial = []
            st.rerun()

    if seccion == "Ranking":
        st.markdown("<h1 style='text-align:center;'>🏆 Ranking de Estudiantes</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:var(--tinta-suave)'>Compite con tus compañeros y llega al top!</p>", unsafe_allow_html=True)
        st.divider()
        ranking = obtener_ranking()
        medallas = ["🥇", "🥈", "🥉"]
        for i, est in enumerate(ranking):
            medalla = medallas[i] if i < 3 else f"#{i+1}"
            es_yo = est["nombre"] == usuario["nombre"]
            clase = "rank-row es-yo" if es_yo else "rank-row"
            st.markdown(f"""
            <div class='{clase}'>
                <span style='font-size:1.5em'>{medalla}</span>
                <strong style='margin-left:10px'>{est['nombre']}</strong>
                {'<span style="color:var(--terracota); font-size:0.8em"> (Tu)</span>' if es_yo else ''}
                <span style='float:right; color:var(--tinta-suave)'>
                    💬 {est['total']} preguntas &nbsp;
                    🔥 {est['racha']} dias &nbsp;
                    🏅 {est['logros']} logros
                </span>
            </div>
            """, unsafe_allow_html=True)

    elif seccion == "Acerca de":
        st.markdown("<h1 style='text-align:center;'>Acerca de Tu Profe de Confianza</h1>", unsafe_allow_html=True)
        st.divider()
        st.markdown("""
        <div style='background:#FFFFFF; border-radius:10px; padding:25px; border-left:5px solid var(--terracota); box-shadow:1px 2px 4px rgba(43,33,24,0.06)'>
            <h3>Nuestra Mision</h3>
            <p>Hacer la educacion accesible para todos los estudiantes peruanos,
            con un tutor de IA disponible 24/7 que explica de forma simple y cercana.</p>
            <h3>Que ofrecemos</h3>
            <p>✅ Tutor de Matematicas con explicaciones paso a paso</p>
            <p>✅ Tutor de Ingles con pronunciacion y traduccion</p>
            <p>✅ Analisis de tus documentos y libros</p>
            <p>✅ Sistema de logros para motivarte</p>
            <p>✅ Ranking de competencia entre estudiantes</p>
            <p>✅ Registro de asistencia y racha diaria</p>
            <p>✅ Historial de conversaciones guardado</p>
            <h3>Contacto</h3>
            <p>Tienes sugerencias? Escribenos y mejoramos juntos.</p>
        </div>
        """, unsafe_allow_html=True)

    elif seccion == "Mis Logros":
        st.markdown("<h1 style='text-align:center;'>Mis Logros</h1>", unsafe_allow_html=True)
        st.divider()
        logros_ganados = obtener_logros_usuario(usuario["id"])
        st.markdown(f"### Tienes {len(logros_ganados)} de {len(LOGROS_DISPONIBLES)} logros 🏆")
        if racha > 0:
            st.markdown(f"""
            <div class='racha-card'>
                <div style='font-size:2em'>🔥</div>
                <div style='font-size:1.5em; font-weight:bold'>{racha} dias de racha</div>
                <div style='font-size:0.9em; color:var(--tinta-suave)'>Sigue estudiando cada dia para no perderla!</div>
            </div>
            """, unsafe_allow_html=True)
        st.divider()
        cols = st.columns(3)
        for i, logro in enumerate(LOGROS_DISPONIBLES):
            with cols[i % 3]:
                if logro["nombre"] in logros_ganados:
                    st.markdown(f"""
                    <div class='logro-card'>
                        <div class='logro-emoji'>{logro['emoji']}</div>
                        <div class='logro-nombre'>{logro['nombre']}</div>
                        <div class='logro-desc'>{logro['descripcion']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='logro-card logro-bloqueado'>
                        <div class='logro-emoji'>🔒</div>
                        <div class='logro-nombre'>{logro['nombre']}</div>
                        <div class='logro-desc'>{logro['descripcion']}</div>
                    </div>
                    """, unsafe_allow_html=True)

    elif seccion == "Mis Estadisticas":
        st.markdown("<h1 style='text-align:center;'>Mis Estadisticas</h1>", unsafe_allow_html=True)
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='stat-card'><div class='stat-number'>{stats['total']}</div><div class='stat-label'>Total preguntas</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='stat-card'><div class='stat-number'>{stats['hoy']}</div><div class='stat-label'>Preguntas hoy</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='stat-card'><div class='stat-number'>{stats['semana']}</div><div class='stat-label'>Esta semana</div></div>", unsafe_allow_html=True)
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='stat-card' style='border-left-color:var(--musgo)'><div class='stat-number' style='color:var(--musgo)'>📐 {stats['matematicas']}</div><div class='stat-label'>Matematicas</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='stat-card' style='border-left-color:var(--azul-tinta)'><div class='stat-number' style='color:var(--azul-tinta)'>🇺🇸 {stats['ingles']}</div><div class='stat-label'>Ingles</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='stat-card' style='border-left-color:var(--resaltador)'><div class='stat-number' style='color:var(--resaltador)'>🔥 {stats['racha']}</div><div class='stat-label'>Dias de racha</div></div>", unsafe_allow_html=True)
        st.divider()
        if stats['total'] > 0:
            materia_favorita = "Matematicas" if stats['matematicas'] >= stats['ingles'] else "Ingles"
            st.success(f"Tu materia favorita es: **{materia_favorita}** 🎯")
            if stats['hoy'] == 0:
                st.warning("No has estudiado hoy. Abre el chat!")
            elif stats['hoy'] < 5:
                st.info(f"Llevas {stats['hoy']} preguntas hoy. Sigue asi!")
            else:
                st.success(f"Excelente! Llevas {stats['hoy']} preguntas hoy. Eres un crack!")
        else:
            st.info("Aun no tienes estadisticas. Ve al chat y empieza!")

    else:
        if "modo" not in st.session_state:
            st.session_state.modo = "Matematicas"
        modo = st.session_state.get("modo", "Matematicas")

        st.markdown(f"""
        <div class='brand-header' style='padding-top:6px;'>
            <span class='brand-icon'>📓</span>
            <p class='brand-title' style='font-size:1.6em'>Tu Profe de Confianza</p>
            <p class='brand-subtitle'>
                Estudiando: <strong>{"📐 Matematicas" if modo == "Matematicas" else "🇺🇸 Ingles"}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

        if "historial" not in st.session_state or st.session_state.get("modo_actual") != modo:
            st.session_state.historial = cargar_conversaciones(usuario["id"], modo)
            st.session_state.modo_actual = modo

        texto_pdf = ""
        if st.session_state.get("archivo"):
            if st.session_state.archivo.type == "application/pdf":
                texto_pdf = extraer_texto_pdf(st.session_state.archivo)
                if texto_pdf:
                    st.info("PDF cargado - puedes preguntarme sobre el contenido")

        if modo == "Matematicas":
            system_prompt = """Eres Tu Profe de Confianza, un tutor de matematicas
            para universitarios peruanos. Eres cercano, paciente y explicas paso a paso.
            SIEMPRE usa este formato HTML en tus respuestas:
            - Pasos numerados en verde musgo: <span style='color:#3A6B5C; font-weight:bold'>Paso 1:</span>
            - Resultados finales en terracota: <span style='color:#C65D32; font-weight:bold'>Resultado:</span>
            - Conceptos importantes en azul tinta: <span style='color:#1E5C8C; font-weight:bold'>concepto</span>
            Cuando escribas formulas usa LaTeX: $$formula$$
            Explicas de forma simple con ejemplos de la vida peruana.
            Cuando el usuario se equivoca lo animas y corriges con amabilidad."""
            sugerencias = [
                "Que es una integral?",
                "Explicame las derivadas",
                "Como resuelvo una ecuacion cuadratica?",
                "Que es el limite de una funcion?"
            ]
        else:
            system_prompt = """Eres Tu Profe de Confianza, un tutor de ingles
            para universitarios peruanos. Eres cercano y motivador.
            SIEMPRE usa este formato HTML en tus respuestas:
            - Palabras en ingles en azul tinta: <span style='color:#1E5C8C; font-weight:bold'>word</span>
            - Traduccion en español en verde musgo: <span style='color:#3A6B5C; font-weight:bold'>palabra</span>
            - Pronunciacion en terracota: <span style='color:#C65D32; font-weight:bold'>/pronun/</span>
            - Ejemplos en resaltador: <span style='color:#8A6A1F'>example sentence</span>
            Estructura SIEMPRE tus respuestas asi:
            1. Palabra en ingles (azul tinta)
            2. Traduccion (verde musgo)
            3. Pronunciacion (terracota)
            4. Ejemplo (resaltador)
            Corriges errores con amabilidad."""
            sugerencias = [
                "Como me presento en ingles?",
                "Ensename los verbos mas usados",
                "Como pido la hora en ingles?",
                "Corrige mi pronunciacion"
            ]

        if texto_pdf:
            system_prompt += f"\n\nEl estudiante ha subido este documento:\n{texto_pdf}"

        if not st.session_state.historial:
            with st.chat_message("assistant"):
                if modo == "Matematicas":
                    st.write("Hola! Soy tu profe de confianza. Que tema de matematicas te esta costando?")
                else:
                    st.write("Hola! Soy tu profe de confianza. En que nivel de ingles estas?")

            st.markdown("<p style='text-align:center; color:var(--tinta-suave); font-size:0.9em; margin-top:10px'>Preguntas frecuentes:</p>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            for i, sugerencia in enumerate(sugerencias):
                with col1 if i % 2 == 0 else col2:
                    if st.button(sugerencia, use_container_width=True, key=f"sug_{i}"):
                        st.session_state.historial.append({"role": "user", "content": sugerencia})
                        with st.spinner("Tu profe esta pensando..."):
                            respuesta = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[{"role": "system", "content": system_prompt}] + st.session_state.historial
                            )
                        texto = respuesta.choices[0].message.content
                        st.session_state.historial.append({"role": "assistant", "content": texto})
                        guardar_conversacion(usuario["id"], sugerencia, texto, modo)
                        stats = obtener_estadisticas(usuario["id"])
                        verificar_logros(usuario["id"], stats)
                        st.rerun()

        for mensaje in st.session_state.historial:
            if mensaje["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(mensaje["content"], unsafe_allow_html=True)
            else:
                with st.chat_message("assistant"):
                    st.markdown(mensaje["content"], unsafe_allow_html=True)

        if prompt := st.chat_input("Escribe tu pregunta aqui..."):
            with st.chat_message("user"):
                st.markdown(prompt, unsafe_allow_html=True)

            st.session_state.historial.append({"role": "user", "content": prompt})

            with st.spinner("Tu profe esta pensando..."):
                respuesta = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_prompt}] + st.session_state.historial
                )

            texto = respuesta.choices[0].message.content
            st.session_state.historial.append({"role": "assistant", "content": texto})
            guardar_conversacion(usuario["id"], prompt, texto, modo)

            stats = obtener_estadisticas(usuario["id"])
            nuevos_logros = verificar_logros(usuario["id"], stats)
            for logro in nuevos_logros:
                st.balloons()
                st.success(f"🏆 Nuevo logro: {logro['emoji']} {logro['nombre']} - {logro['descripcion']}")

            with st.chat_message("assistant"):
                st.markdown(texto, unsafe_allow_html=True)

