import streamlit as st
import pandas as pd
import unicodedata
import re

st.set_page_config(page_title="Territoriales CESAC 42", layout="centered")
st.markdown("""
<style>
/* Fondo general */
.stApp {
    background-color: #F5F6F7;
}

/* Títulos */
h1, h2, h3 {
    color: #003A8F;
}

/* Botón Buscar */
div.stButton > button {
    background-color: #007BC7;
    color: white;
    border-radius: 6px;
    border: none;
    padding: 0.4em 1.2em;
}

div.stButton > button:hover {
    background-color: #005A9E;
}

/* Inputs */
input, select {
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOGO
# -----------------------------
col1, col2 = st.columns([4, 1])

with col1:
    st.title("Territoriales CESAC 42")

with col2:
    st.image("logo.png", width=90)

# -----------------------------
# INTEGRANTES POR EQUIPO
# -----------------------------
INTEGRANTES = {
    "1 - Norte": [
        "MG: Micaela Ramos",
        "Ped: Carolina Krochik",
        "Enf: Elena Carvallo",
        "TS: Luis Buchanan"
        
    ],
    "2 - Oeste": [
        "MG: Agustina Sestelo",
        "Ped: Ruben Castelli",
        "Enf: Elena Carvallo",
        "TS: Juan Burwiel"
    ],
    "3 - Este": [
        "MG: Daniela Rognoni",
        "Ped: Martha Becerra",
        "Enf: Romina Mamani",
        "TS: Luis Buchanan"
    ],
    "4 - Sur": [
        "MG: Brenda Garcia dos Santos",
        "Ped: Paula Tasso",
        "Enf: Ana Davila",
        "TS: Juan Burwiel"
    ]
}

# -----------------------------
# FUNCIONES AUXILIARES
# -----------------------------
def normalizar(texto):
    texto = str(texto)
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto.lower().strip()

def altura_en_rango(texto_altura, altura):
    """
    1 - 400  => hasta 499
    2000 - 2100 => hasta 2199
    PAR / IMPAR se aplica dentro del rango
    """
    try:
        t = str(texto_altura).upper()
        es_par = altura % 2 == 0

        if re.search(r"\bPAR\b", t) and not es_par:
            return False
        if re.search(r"\bIMPAR\b", t) and es_par:
            return False

        nums = re.findall(r"\d+", t)

        if len(nums) == 2:
            desde = int(nums[0])
            hasta = int(nums[1]) + 99
            return desde <= altura <= hasta

        if len(nums) == 1:
            desde = int(nums[0])
            hasta = desde + 99
            return desde <= altura <= hasta

        return False
    except:
        return False

# -----------------------------
# CARGA CSV
# -----------------------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv(
        "DOMICILIO Y TERRITORIAL - Hoja 2.csv",
        header=None,
        sep=",",
        encoding="utf-8"
    )

    if df.shape[1] == 1:
        df = df[0].str.split(",", expand=True)

    df = df.iloc[:, :3]
    df.columns = ["CALLE", "ALTURA", "EQUIPO"]

    df["CALLE_ORIG"] = df["CALLE"].astype(str).str.strip()
    df["CALLE_NORM"] = df["CALLE_ORIG"].apply(normalizar)

    return df

df = cargar_datos()

# -----------------------------
# UI
# -----------------------------
calles = sorted(df["CALLE_ORIG"].unique())

with st.form("busqueda"):
    calles = sorted(df["CALLE_ORIG"].unique())

    calle = st.selectbox(
        "Calle",
        calles,
        index=None,
        placeholder="Empezá a escribir la calle…"
    )

    altura = st.text_input("Altura")

    buscar = st.form_submit_button("Buscar")

# -----------------------------
# BUSQUEDA
# -----------------------------
if buscar:
    if not calle or not altura:
        st.warning("Completá calle y altura")
    else:
        try:
            altura_int = int(altura)
        except:
            st.warning("La altura debe ser un número")
            st.stop()

        calle_norm = normalizar(calle)
        filas = df[df["CALLE_NORM"] == calle_norm]

        resultado = None

        for _, fila in filas.iterrows():
            if altura_en_rango(fila["ALTURA"], altura_int):
                resultado = fila["EQUIPO"]
                break

        if resultado:
            st.success(f"Equipo territorial: **{resultado}**")

            integrantes = INTEGRANTES.get(resultado)
            if integrantes:
                st.markdown("**Integrantes:**")
                for i in integrantes:
                    st.write(f"• {i}")
        else:
            st.error("FUERA DE ÁREA")


