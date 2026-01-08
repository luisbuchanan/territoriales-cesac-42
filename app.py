import streamlit as st
import pandas as pd
import unicodedata
import re

st.set_page_config(page_title="Territoriales CESAC 42", layout="centered")
st.title("Territoriales CESAC 42")

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
    Reglas:
    - 1 - 400  => hasta 499
    - 2000 - 2100 => hasta 21099
    - PAR / IMPAR se aplica dentro del rango
    """
    try:
        t = str(texto_altura).upper()

        # Paridad
        if "PAR" in t and altura % 2 != 0:
            return False
        if "IMPAR" in t and altura % 2 == 0:
            return False

        nums = re.findall(r"\d+", t)

        if len(nums) == 2:
            desde = int(nums[0])
            hasta = int(nums[1]) * 10 + 9
            return desde <= altura <= hasta

        if len(nums) == 1:
            desde = int(nums[0])
            hasta = desde * 10 + 9
            return desde <= altura <= hasta

        return False

    except:
        return False

# -----------------------------
# CARGA CSV ROBUSTA
# -----------------------------

@st.cache_data
def cargar_datos():
    df = pd.read_csv(
        "DOMICILIO Y TERRITORIAL - Hoja 2.csv",
        header=None,
        sep=",",
        encoding="utf-8"
    )

    # Si vino todo en una sola columna
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

calle = st.selectbox(
    "Calle",
    calles,
    index=None,
    placeholder="Empezá a escribir la calle…"
)

altura = st.number_input("Altura", min_value=1, step=1)
buscar = st.button("Buscar")

# -----------------------------
# BUSQUEDA
# -----------------------------

if buscar or altura > 0:
    if not calle:
        st.warning("Completá calle y altura")
    else:
        calle_norm = normalizar(calle)
        filas = df[df["CALLE_NORM"] == calle_norm]

        resultado = None

        for _, fila in filas.iterrows():
            if altura_en_rango(fila["ALTURA"], int(altura)):
                resultado = fila["EQUIPO"]
                break

        if resultado:
            st.success(f"Equipo territorial: **{resultado}**")
        else:
            st.error("FUERA DE ÁREA")
