
import io
from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ==========================================================
# 1. CONFIGURACIÓN GENERAL
# ==========================================================

st.set_page_config(
    page_title="ALMACÉN 360 | Dashboard OE2",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

AZUL = "#38BDF8"
VERDE = "#34D399"
ROJO = "#FB7185"
AMARILLO = "#FBBF24"

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #09111f, #14243a);
        color: #eaf2ff;
    }
    [data-testid="stSidebar"] {
        background: #0b1526;
    }
    [data-testid="stMetric"] {
        background: #14243a;
        border: 1px solid #28405e;
        border-radius: 15px;
        padding: 15px;
    }
    h1, h2, h3 {
        color: #f3f8ff !important;
    }
    .block-container {
        padding-top: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# 2. FUNCIONES Y DATOS
# ==========================================================

def codigo_ubicacion(zona, pasillo, nivel, posicion):
    return (
        f"{zona}-P{int(pasillo):02d}"
        f"-N{int(nivel):02d}"
        f"-U{int(posicion):02d}"
    )


def crear_diagnostico():
    return pd.DataFrame({
        "zona": ["Zona A", "Zona B", "Zona C"],
        "verificados": [100, 100, 100],
        "correctos": [58, 64, 63],
        "puntaje_5s": [38, 42, 40],
        "problema": [
            "Productos mezclados",
            "Productos sin ubicación asignada",
            "Desorden y pasillos obstruidos",
        ],
        "causa": [
            "Sin codificación",
            "Almacenamiento según espacio disponible",
            "Falta de clasificación y limpieza",
        ],
    })


def crear_productos():
    # Datos demostrativos. No son registros reales.
    productos = []
    familias = [
        "Fertilizantes",
        "Insecticidas",
        "Bioestimulantes",
    ]

    for i in range(1, 31):
        zona = "ABC"[(i - 1) % 3]
        pasillo = ((i - 1) // 3) % 3 + 1
        nivel = ((i - 1) // 9) % 3 + 1
        posicion = ((i - 1) // 27) % 3 + 1

        asignada = codigo_ubicacion(
            zona, pasillo, nivel, posicion
        )

        if i % 5 in (0, 1):
            real = codigo_ubicacion(
                zona, pasillo % 3 + 1, nivel, posicion
            )
        else:
            real = asignada

        productos.append({
            "producto_id": f"PRD-{i:03d}",
            "producto": f"Producto agrícola {i:02d}",
            "familia": familias[(i - 1) % 3],
            "zona": f"Zona {zona}",
            "ubicacion_asignada": asignada,
            "ubicacion_real": real,
            "cantidad": int(10 + i * 2),
        })

    return pd.DataFrame(productos)


PREGUNTAS_5S = {
    "1S - Clasificar": [
        "Se separan los productos necesarios e innecesarios",
        "Se identifican productos dañados o vencidos",
        "Se retiran materiales que obstruyen el almacén",
        "Los productos están clasificados por tipo",
        "Existe un procedimiento para retirar lo innecesario",
    ],
    "2S - Ordenar": [
        "Cada producto tiene una ubicación asignada",
        "Las ubicaciones están codificadas",
        "Los pasillos están despejados",
        "Los productos están en su posición correcta",
        "El mapa de ubicaciones está actualizado",
    ],
    "3S - Limpiar": [
        "El área está libre de residuos",
        "Los estantes se encuentran limpios",
        "Se identifican fuentes de suciedad",
        "Existen herramientas de limpieza",
        "Se registra la limpieza realizada",
    ],
    "4S - Estandarizar": [
        "Existe señalización uniforme",
        "Se utilizan listas de verificación",
        "Las instrucciones están visibles",
        "Se registran las incidencias",
        "Existen responsables definidos",
    ],
    "5S - Disciplina": [
        "Se realizan auditorías periódicas",
        "El personal conoce la metodología 5S",
        "Se ejecutan acciones correctivas",
        "Se cumplen las rutinas establecidas",
        "Se revisan los resultados con el equipo",
    ],
}


def crear_cronograma():
    actividades = [
        ("Recopilación de información", 1, 1,
         "Asistente de inventarios"),
        ("Diagnóstico inicial y auditoría 5S", 1, 2,
         "Jefe de almacén"),
        ("Diseño de zonas y codificación", 2, 3,
         "Asistente de inventarios"),
        ("Clasificación y orden 1S-2S", 3, 4,
         "Almacenero"),
        ("Rotulado y asignación de ubicaciones", 4, 5,
         "Almacenero y asistente"),
        ("Limpieza y estandarización 3S-4S", 5, 6,
         "Almacenero"),
        ("Capacitación y disciplina 5S", 6, 7,
         "Jefe de almacén"),
        ("Auditoría final y evaluación", 7, 8,
         "Jefe de almacén"),
    ]

    return pd.DataFrame(
        actividades,
        columns=[
            "actividad",
            "semana_inicio",
            "semana_fin",
            "responsable",
        ],
    )


def crear_acciones():
    return pd.DataFrame([
        {
            "id": "AC-001",
            "desviacion": "Productos mezclados",
            "accion": "Reubicar y rotular estantes",
            "responsable": "Almacenero",
            "estado": "Pendiente",
            "fecha_limite": str(date.today() + timedelta(days=7)),
        },
        {
            "id": "AC-002",
            "desviacion": "Pasillo obstruido",
            "accion": "Retirar materiales y señalizar",
            "responsable": "Jefe de almacén",
            "estado": "En proceso",
            "fecha_limite": str(date.today() + timedelta(days=4)),
        },
    ])


def mostrar_grafico(fig, altura=370):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=altura,
        margin=dict(l=10, r=10, t=55, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)


def calcular_indicadores(df):
    total = int(df["verificados"].sum())
    correctos = int(df["correctos"].sum())
    porcentaje = 100 * correctos / total if total > 0 else 0
    return total, correctos, porcentaje


def validar_diagnostico(df):
    columnas = ["verificados", "correctos", "puntaje_5s"]
    for columna in columnas:
        df[columna] = pd.to_numeric(
            df[columna], errors="coerce"
        )

    return (
        not df[columnas].isna().any().any()
        and (df["verificados"] >= 0).all()
        and (df["correctos"] >= 0).all()
        and (df["correctos"] <= df["verificados"]).all()
        and df["puntaje_5s"].between(0, 100).all()
    )


def validar_productos(df):
    requeridas = [
        "producto_id",
        "producto",
        "familia",
        "zona",
        "ubicacion_asignada",
        "ubicacion_real",
        "cantidad",
    ]

    if not all(c in df.columns for c in requeridas):
        return False

    if df[requeridas].isna().any().any():
        return False

    if df["producto_id"].astype(str).duplicated().any():
        return False

    cantidades = pd.to_numeric(
        df["cantidad"], errors="coerce"
    )

    return cantidades.notna().all() and (cantidades >= 0).all()


# ==========================================================
# 3. ESTADO DE LA APLICACIÓN
# ==========================================================

if "diagnostico" not in st.session_state:
    st.session_state.diagnostico = crear_diagnostico()

if "productos" not in st.session_state:
    st.session_state.productos = crear_productos()

if "acciones" not in st.session_state:
    st.session_state.acciones = crear_acciones()

if "auditoria" not in st.session_state:
    st.session_state.auditoria = {
        pregunta: 2
        for preguntas in PREGUNTAS_5S.values()
        for pregunta in preguntas
    }

if "historial" not in st.session_state:
    st.session_state.historial = []


# ==========================================================
# 4. BARRA LATERAL
# ==========================================================

st.sidebar.title("🏭 ALMACÉN 360")
st.sidebar.caption("COMERCIAL AGRÍCOLA PROGRESO S.A.C.")
st.sidebar.markdown("### Objetivo Específico 2")
st.sidebar.write(
    "Mejorar la gestión del almacenamiento mediante "
    "la metodología 5S y la codificación de ubicaciones."
)

st.sidebar.divider()

fuente = st.sidebar.radio(
    "Fuente del indicador",
    [
        "Diagnóstico documentado",
        "Catálogo de productos",
    ],
)

meta = st.sidebar.slider(
    "Meta estratégica (%)",
    min_value=80,
    max_value=100,
    value=95,
)

st.sidebar.info(
    "AS-IS planificado: 50% | "
    "TO-BE propuesto: 80% | "
    "Meta estratégica: 95%"
)

st.sidebar.warning(
    "Los productos de ejemplo son demostrativos. "
    "Los cambios se guardan durante la sesión."
)


# ==========================================================
# 5. ENCABEZADO Y PESTAÑAS
# ==========================================================

st.title("🏭 ALMACÉN 360")
st.markdown(
    "### Dashboard inteligente de gestión de almacenamiento"
)
st.caption(
    "OE2 | Metodología 5S + codificación de ubicaciones "
    "| Control y mejora continua"
)

tabs = st.tabs([
    "📊 Dashboard",
    "🔎 Diagnóstico",
    "🗺️ Mapa de ubicaciones",
    "🧹 Auditoría 5S",
    "📅 Cronograma",
    "🛠️ Acciones correctivas",
    "📥 Excel y reportes",
])


# ==========================================================
# 6. DASHBOARD GERENCIAL
# ==========================================================

with tabs[0]:

    st.header("Centro de mando gerencial")

    if fuente == "Diagnóstico documentado":
        total, correctos, porcentaje = calcular_indicadores(
            st.session_state.diagnostico
        )
    else:
        productos = st.session_state.productos
        total = len(productos)
        correctos = int((
            productos["ubicacion_asignada"]
            == productos["ubicacion_real"]
        ).sum())
        porcentaje = (
            100 * correctos / total if total else 0
        )

    incorrectos = total - correctos
    puntaje_auditoria = sum(
        st.session_state.auditoria.values()
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Ubicación correcta",
        f"{porcentaje:.1f}%",
    )

    c2.metric(
        "Productos verificados",
        f"{total:,}",
    )

    c3.metric(
        "Fuera de ubicación",
        f"{incorrectos:,}",
    )

    c4.metric(
        "Auditoría 5S editable",
        f"{puntaje_auditoria}/100",
    )

    st.progress(
        min(porcentaje / meta, 1.0),
        text=(
            f"Avance hacia la meta: "
            f"{porcentaje:.1f}% / {meta}%"
        ),
    )

    if fuente == "Diagnóstico documentado":
        st.info(
            "Diagnóstico inicial: 185 productos correctamente "
            "ubicados de 300 verificados = 61,7%. "
            "El 50% AS-IS corresponde a la planificación."
        )
    else:
        st.warning(
            "Indicador calculado con el catálogo editable. "
            "Los registros iniciales son demostrativos."
        )

    izquierda, derecha = st.columns(2)

    with izquierda:
        hitos = pd.DataFrame({
            "Escenario": [
                "AS-IS planificado",
                "Diagnóstico inicial",
                "TO-BE propuesto",
                "Meta estratégica",
            ],
            "Porcentaje": [
                50,
                185 / 300 * 100,
                80,
                meta,
            ],
        })

        fig = px.bar(
            hitos,
            x="Escenario",
            y="Porcentaje",
            color="Escenario",
            text="Porcentaje",
            title="Comparación de escenarios",
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
        )
        fig.update_yaxes(range=[0, 110])
        mostrar_grafico(fig)

    with derecha:
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=porcentaje,
                number={"suffix": "%"},
                title={"text": "Ubicación correcta"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": VERDE},
                    "steps": [
                        {
                            "range": [0, 50],
                            "color": "#562735",
                        },
                        {
                            "range": [50, 80],
                            "color": "#665126",
                        },
                        {
                            "range": [80, 100],
                            "color": "#175747",
                        },
                    ],
                    "threshold": {
                        "line": {
                            "color": "white",
                            "width": 4,
                        },
                        "value": meta,
                    },
                },
            )
        )
        mostrar_grafico(fig)

    st.subheader("Interpretación de resultados")

    if porcentaje >= meta:
        st.success(
            "La fuente seleccionada alcanza la meta "
            "estratégica establecida."
        )
    else:
        diferencia = meta - porcentaje
        st.warning(
            f"Faltan {diferencia:.1f} puntos porcentuales "
            "para alcanzar la meta."
        )

    st.markdown(
        """
        **KPI 1 — Cumplimiento 5S**

        (Puntaje obtenido / Puntaje máximo) × 100

        **KPI 2 — Ubicación correcta**

        (Productos en su posición asignada /
        Productos verificados) × 100
        """
    )


# ==========================================================
# 7. DIAGNÓSTICO POR ZONAS
# ==========================================================

with tabs[1]:

    st.header("Diagnóstico del almacén")

    st.write(
        "Edita los resultados de verificación y auditoría "
        "de cada zona."
    )

    editado = st.data_editor(
        st.session_state.diagnostico,
        num_rows="fixed",
        hide_index=True,
        use_container_width=True,
        key="editor_diagnostico",
    )

    if st.button("Guardar diagnóstico"):
        nuevo = editado.copy()

        if validar_diagnostico(nuevo):
            st.session_state.diagnostico = nuevo
            st.success("Diagnóstico actualizado.")
            st.rerun()
        else:
            st.error(
                "Revisa los valores. Los correctos no pueden "
                "superar los verificados y el 5S debe estar "
                "entre 0 y 100."
            )

    df = st.session_state.diagnostico.copy()

    df["incorrectos"] = (
        df["verificados"] - df["correctos"]
    )

    df["ubicacion_pct"] = np.where(
        df["verificados"] > 0,
        100 * df["correctos"]
        / df["verificados"].replace(0, np.nan),
        0,
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            df,
            x="zona",
            y=["correctos", "incorrectos"],
            barmode="stack",
            title="Productos correctos e incorrectos",
            labels={"value": "Productos"},
        )
        mostrar_grafico(fig)

    with col2:
        fig = px.bar(
            df,
            x="zona",
            y="ubicacion_pct",
            color="puntaje_5s",
            text="ubicacion_pct",
            title="Ubicación correcta por zona (%)",
            color_continuous_scale="Tealgrn",
        )
        fig.update_traces(
            texttemplate="%{text:.1f}%"
        )
        fig.add_hline(
            y=meta,
            line_dash="dash",
            line_color=ROJO,
        )
        mostrar_grafico(fig)

    st.subheader("Matriz de problemas")

    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True,
    )


# ==========================================================
# 8. MAPA INTERACTIVO DE UBICACIONES
# ==========================================================

with tabs[2]:

    st.header("Mapa lógico del almacén")

    st.info(
        "Codificación: ZONA-PASILLO-NIVEL-POSICIÓN. "
        "Ejemplo: A-P01-N02-U03"
    )

    productos = st.session_state.productos.copy()

    productos["estado"] = np.where(
        productos["ubicacion_asignada"]
        == productos["ubicacion_real"],
        "Correcta",
        "Incorrecta",
    )

    zonas = sorted(
        productos["zona"].dropna().unique().tolist()
    )

    seleccion = st.multiselect(
        "Filtrar zonas",
        zonas,
        default=zonas,
    )

    filtrado = productos[
        productos["zona"].isin(seleccion)
    ].copy()

    if not filtrado.empty:

        fig = px.treemap(
            filtrado,
            path=[
                "zona",
                "ubicacion_asignada",
                "producto_id",
            ],
            values="cantidad",
            color="estado",
            color_discrete_map={
                "Correcta": VERDE,
                "Incorrecta": ROJO,
            },
            hover_data=[
                "producto",
                "ubicacion_real",
            ],
            title="Mapa lógico de ubicaciones",
        )

        mostrar_grafico(fig, 480)

        resumen = (
            filtrado.groupby(
                ["zona", "estado"]
            )
            .size()
            .reset_index(name="productos")
        )

        fig2 = px.bar(
            resumen,
            x="zona",
            y="productos",
            color="estado",
            barmode="stack",
            title="Estado de ubicación por zona",
            color_discrete_map={
                "Correcta": VERDE,
                "Incorrecta": ROJO,
            },
        )

        mostrar_grafico(fig2)

    else:
        st.info("Selecciona al menos una zona.")

    st.subheader("Generador de códigos")

    a, b, c, d = st.columns(4)

    zona = a.selectbox(
        "Zona",
        ["A", "B", "C", "D", "E"],
    )
    pasillo = b.number_input(
        "Pasillo", 1, 99, 1
    )
    nivel = c.number_input(
        "Nivel", 1, 99, 1
    )
    posicion = d.number_input(
        "Posición", 1, 99, 1
    )

    nuevo_codigo = codigo_ubicacion(
        zona, pasillo, nivel, posicion
    )

    st.code(nuevo_codigo)

    st.subheader("Catálogo editable de productos")

    edit_productos = st.data_editor(
        st.session_state.productos,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="editor_productos",
    )

    if st.button("Guardar catálogo"):
        if validar_productos(edit_productos):
            st.session_state.productos = (
                edit_productos.copy()
            )
            st.success("Catálogo actualizado.")
            st.rerun()
        else:
            st.error(
                "Revisa los campos vacíos, códigos "
                "duplicados y cantidades inválidas."
            )


# ==========================================================
# 9. AUDITORÍA 5S
# ==========================================================

with tabs[3]:

    st.header("Auditoría interactiva 5S")

    st.write(
        "Evalúa cada criterio entre 0 y 4 puntos. "
        "Son 25 preguntas, con un máximo de 100 puntos."
    )

    resultados = {}

    for categoria, preguntas in PREGUNTAS_5S.items():

        with st.expander(
            categoria,
            expanded=categoria.startswith("1S"),
        ):

            for pregunta in preguntas:

                resultados[pregunta] = st.slider(
                    pregunta,
                    min_value=0,
                    max_value=4,
                    value=int(
                        st.session_state.auditoria.get(
                            pregunta, 2
                        )
                    ),
                    key="audit_" + pregunta,
                )

    st.session_state.auditoria = resultados

    puntaje_total = sum(resultados.values())

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Puntaje obtenido",
        f"{puntaje_total}/100",
    )

    c2.metric(
        "Cumplimiento 5S",
        f"{puntaje_total}%",
    )

    c3.metric(
        "Diagnóstico histórico",
        "40/100",
    )

    pilares = []

    for categoria, preguntas in PREGUNTAS_5S.items():

        pilares.append({
            "Pilar": categoria,
            "Puntaje": sum(
                resultados[p] for p in preguntas
            ),
            "Máximo": 20,
        })

    df_5s = pd.DataFrame(pilares)

    fig = px.bar(
        df_5s,
        x="Pilar",
        y="Puntaje",
        color="Puntaje",
        text="Puntaje",
        title="Evaluación por pilar 5S",
        color_continuous_scale="Tealgrn",
    )

    fig.update_yaxes(range=[0, 22])
    mostrar_grafico(fig)

    if st.button("Registrar auditoría"):

        st.session_state.historial.append({
            "fecha": str(date.today()),
            "puntaje": puntaje_total,
            "cumplimiento_pct": puntaje_total,
        })

        st.success(
            "Auditoría registrada en la sesión."
        )

    if st.session_state.historial:

        historial = pd.DataFrame(
            st.session_state.historial
        )

        st.subheader("Historial de auditorías")

        st.dataframe(
            historial,
            hide_index=True,
            use_container_width=True,
        )

        fig = px.line(
            historial.reset_index(),
            x="index",
            y="cumplimiento_pct",
            markers=True,
            title="Evolución de auditorías registradas",
        )

        mostrar_grafico(fig)

    st.caption(
        "Los puntajes iniciales de los controles son "
        "demostrativos y no sustituyen la auditoría real."
    )


# ==========================================================
# 10. CRONOGRAMA DE IMPLEMENTACIÓN
# ==========================================================

with tabs[4]:

    st.header("Plan de implementación de 8 semanas")

    inicio = st.date_input(
        "Fecha de inicio del proyecto",
        value=date.today(),
    )

    cronograma = crear_cronograma()

    cronograma["inicio"] = (
        cronograma["semana_inicio"].apply(
            lambda semana:
            inicio + timedelta(weeks=int(semana) - 1)
        )
    )

    cronograma["fin"] = (
        cronograma["semana_fin"].apply(
            lambda semana:
            inicio
            + timedelta(weeks=int(semana))
            - timedelta(days=1)
        )
    )

    fig = px.timeline(
        cronograma,
        x_start="inicio",
        x_end="fin",
        y="actividad",
        color="responsable",
        title="Diagrama de Gantt",
    )

    fig.update_yaxes(autorange="reversed")

    mostrar_grafico(fig, 520)

    st.dataframe(
        cronograma,
        hide_index=True,
        use_container_width=True,
    )

    st.subheader("Plan de sostenimiento 5S")

    rutinas = pd.DataFrame([
        ["1S", "Clasificar productos", "Mensual",
         "Almacenero"],
        ["2S", "Ordenar productos", "Cada ingreso",
         "Almacenero"],
        ["3S", "Limpiar instalaciones", "Diaria",
         "Almacenero"],
        ["4S", "Actualizar señalización",
         "Cuando cambie el layout",
         "Asistente de inventarios"],
        ["5S", "Auditoría de cumplimiento",
         "Semanal", "Jefe de almacén"],
    ], columns=[
        "Etapa",
        "Actividad",
        "Frecuencia",
        "Responsable",
    ])

    st.dataframe(
        rutinas,
        hide_index=True,
        use_container_width=True,
    )


# ==========================================================
# 11. ACCIONES CORRECTIVAS
# ==========================================================

with tabs[5]:

    st.header("Gestión de acciones correctivas")

    acciones = st.session_state.acciones

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Acciones registradas",
        len(acciones),
    )

    c2.metric(
        "Pendientes",
        int((acciones["estado"] == "Pendiente").sum()),
    )

    c3.metric(
        "Cerradas",
        int((acciones["estado"] == "Cerrada").sum()),
    )

    edit_acciones = st.data_editor(
        acciones,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="editor_acciones",
        column_config={
            "estado": st.column_config.SelectboxColumn(
                "Estado",
                options=[
                    "Pendiente",
                    "En proceso",
                    "Cerrada",
                ],
            ),
        },
    )

    if st.button("Guardar acciones"):

        campos = [
            "id",
            "desviacion",
            "accion",
            "responsable",
            "estado",
        ]

        if (
            edit_acciones[campos].isna().any().any()
            or edit_acciones["id"]
            .astype(str).duplicated().any()
        ):
            st.error(
                "Completa los campos y evita IDs duplicados."
            )
        else:
            st.session_state.acciones = (
                edit_acciones.copy()
            )
            st.success("Acciones actualizadas.")
            st.rerun()

    if not acciones.empty:

        fig = px.pie(
            acciones,
            names="estado",
            hole=0.55,
            title="Estado de acciones correctivas",
            color="estado",
            color_discrete_map={
                "Pendiente": ROJO,
                "En proceso": AMARILLO,
                "Cerrada": VERDE,
            },
        )

        mostrar_grafico(fig)


# ==========================================================
# 12. IMPORTACIÓN Y EXPORTACIÓN DE EXCEL
# ==========================================================

with tabs[6]:

    st.header("Centro de datos y reportes")

    st.write(
        "Descarga los registros del dashboard o importa "
        "un Excel con información actualizada."
    )

    salida = io.BytesIO()

    with pd.ExcelWriter(
        salida,
        engine="openpyxl",
    ) as writer:

        st.session_state.productos.to_excel(
            writer,
            sheet_name="Productos",
            index=False,
        )

        st.session_state.diagnostico.to_excel(
            writer,
            sheet_name="Diagnostico",
            index=False,
        )

        pd.DataFrame([
            {
                "pregunta": pregunta,
                "puntaje": puntaje,
            }
            for pregunta, puntaje
            in st.session_state.auditoria.items()
        ]).to_excel(
            writer,
            sheet_name="Auditoria_5S",
            index=False,
        )

        st.session_state.acciones.to_excel(
            writer,
            sheet_name="Acciones",
            index=False,
        )

        crear_cronograma().to_excel(
            writer,
            sheet_name="Cronograma",
            index=False,
        )

        pd.DataFrame(
            st.session_state.historial,
            columns=[
                "fecha",
                "puntaje",
                "cumplimiento_pct",
            ],
        ).to_excel(
            writer,
            sheet_name="Historial_5S",
            index=False,
        )

    st.download_button(
        "⬇️ Descargar reporte Excel completo",
        data=salida.getvalue(),
        file_name="reporte_almacen_360.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

    archivo = st.file_uploader(
        "Sube un archivo Excel",
        type=["xlsx"],
    )

    if archivo is not None:

        try:
            libro = pd.ExcelFile(archivo)

            st.write(
                "Hojas encontradas:",
                ", ".join(libro.sheet_names),
            )

            if "Productos" in libro.sheet_names:

                importados = pd.read_excel(
                    libro,
                    sheet_name="Productos",
                )

                if st.button("Importar productos"):

                    if validar_productos(importados):
                        st.session_state.productos = (
                            importados.copy()
                        )
                        st.success(
                            "Productos importados."
                        )
                        st.rerun()
                    else:
                        st.error(
                            "La hoja Productos tiene columnas "
                            "faltantes o datos inválidos."
                        )

            if "Diagnostico" in libro.sheet_names:

                diag_importado = pd.read_excel(
                    libro,
                    sheet_name="Diagnostico",
                )

                columnas = [
                    "zona",
                    "verificados",
                    "correctos",
                    "puntaje_5s",
                    "problema",
                    "causa",
                ]

                if st.button("Importar diagnóstico"):

                    if not all(
                        c in diag_importado.columns
                        for c in columnas
                    ):
                        st.error(
                            "Faltan columnas en Diagnostico."
                        )
                    elif validar_diagnostico(
                        diag_importado
                    ):
                        st.session_state.diagnostico = (
                            diag_importado[columnas].copy()
                        )
                        st.success(
                            "Diagnóstico importado."
                        )
                        st.rerun()
                    else:
                        st.error(
                            "Hay valores inválidos "
                            "en el diagnóstico."
                        )

        except Exception as error:
            st.error(
                f"No se pudo leer el Excel: {error}"
            )

    st.divider()

    st.subheader("Indicadores AS-IS / TO-BE")

    comparacion = pd.DataFrame({
        "Indicador": [
            "Ubicación correcta",
            "Cumplimiento 5S",
        ],
        "AS-IS planificado (%)": [
            50,
            40,
        ],
        "TO-BE propuesto (%)": [
            80,
            85,
        ],
        "Meta estratégica (%)": [
            meta,
            np.nan,
        ],
    })

    st.dataframe(
        comparacion,
        hide_index=True,
        use_container_width=True,
    )

    st.caption(
        "La meta de 95% corresponde a ubicación correcta. "
        "El diagnóstico documentado registra 61,7% de "
        "ubicación correcta y 40/100 en 5S. "
        "Los datos demostrativos no deben presentarse "
        "como resultados reales de implementación."
    )


# ==========================================================
# FIN DEL PROGRAMA
# ==========================================================
