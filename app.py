import streamlit as st
import pandas as pd
import unicodedata
import re

st.set_page_config(page_title="Territoriales CESAC 42", layout="centered")
st.title("Territoriales CESAC 42")

# -----------------------------
# UTILIDADES
# -----------------------------

def normalizar(txt):
    txt = str(txt)
    txt = unicodedata.normalize("NFD", txt)
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    return txt.lower().strip()

def parse_desde(altura_txt):
    nums = re.findall(r"\d+", str(altura_txt))
    return int(nums[0]) if nums else 0

def coincide_paridad(altura_txt, altura):
    txt = str(altura_txt).upper()
    if "PAR" in txt and altura % 2 != 0:
        return False
    if "IMPAR" in txt and altura % 2 == 0:
        return False
    return True

# -----------------------------
# CARGA ROBUSTA CSV
# -----------------------------

@st.cache_data
def cargar_datos():
    df = pd.read_csv(
        "DOMICILIO Y TERRITORIAL - Hoja 2.csv",
        header=None,
        encoding="utf-8",
        sep=","
    )

    # Si vino todo en una sola columna
    if df.shape[1] == 1:
        df = df[0].str.split(",", expand=True)

    df = df.iloc[:, :3]
    df.columns = ["CALLE", "ALTURA", "EQUIPO"]

    df["CALLE_ORIG"] = df["CALLE"].astype(str).str.strip()
    df["CALLE_NORM"] = df["CALLE_ORIG"].apply(normalizar)
    df["DESDE"] = df["ALTURA"].apply(parse_desde)

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

altura = st.number_input("Altura", min_value=0, step=1)
buscar = st.button("Buscar")

# -----------------------------
# BUSQUEDA CORRECTA
# -----------------------------

if buscar or altura > 0:
    if not calle or altura == 0:
        st.warning("Completá calle y altura")
    else:
        calle_n = normalizar(calle)
        filas = df[df["CALLE_NORM"] == calle_n].copy()

        # Ordenar por DESDE descendente (más específico primero)
        filas = filas.sort_values("DESDE", ascending=False)

        resultado = None

        for _, f in filas.iterrows():
            if altura >= f["DESDE"] and coincide_paridad(f["ALTURA"], altura):
                resultado = f["EQUIPO"]
                break

        if resultado:
            st.success(f"Equipo territorial: **{resultado}**")
        else:
            st.error("FUERA DE ÁREA")
