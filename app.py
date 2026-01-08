import streamlit as st
import pandas as pd
import unicodedata
import re

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(
    page_title="Territoriales CESAC 42",
    layout="centered"
)

st.title("Territoriales CESAC 42")
st.write("Buscador de equipo territorial por calle y altura")

# ----------------------------
# FUNCIONES AUXILIARES
# ----------------------------

def normalizar(texto: str) -> str:
    """
    Normaliza para comparar:
    - sin tildes
    - sin mayúsculas
    """
    texto = str(texto)
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto.lower().strip()


def altura_en_rango(valor_csv, altura):
    """
    Reglas:
    - PAR / IMPAR filtran
    - El rango NO corta hacia arriba
    - El número menor indica desde dónde empieza a aplicar
    """
    try:
        texto = str(valor_csv).upper().strip()
        es_par = altura % 2 == 0

        # PAR / IMPAR
        if "PAR" in texto and not es_par:
            return False
        if "IMPAR" in texto and es_par:
            return False

        texto = texto.replace("PAR", "").replace("IMPAR", "").strip()

        # Caso rango: "2000 - 2100"
        if " - " in texto:
            desde = int(texto.split(" - ")[0])
            return altura >= desde

        # Caso número solo: "1200"
        return altura >= int(texto)

    except:
        return False


@st.cache_data
def cargar_datos():
    df = pd.read_csv("DOMICILIO Y TERRITORIAL - Hoja 2.csv")

    # Normalizamos columnas (por si vienen raras)
    df.columns = [c.strip().upper() for c in df.columns]

    # Esperado:
    # CALLE | ALTURA | EQUIPO TERRITORIAL
    df["CALLE_ORIG"] = df["CALLE"].astype(str)
    df["CALLE_NORM"] = df["CALLE_ORIG"].apply(normalizar)

    return df


# ----------------------------
# CARGA CSV
# ----------------------------
df = cargar_datos()

# ----------------------------
# UI
# ----------------------------

calles_unicas = sorted(df["CALLE_ORIG"].unique())

calle_input = st.selectbox(
    "Calle",
    options=calles_unicas,
    index=None,
    placeholder="Empezá a escribir la calle..."
)

altura_input = st.number_input(
    "Altura",
    min_value=0,
    step=1
)

buscar = st.button("Buscar")

# ----------------------------
# BUSQUEDA
# ----------------------------

if buscar or altura_input:
    if not calle_input or altura_input == 0:
        st.warning("Completá calle y altura")
    else:
        calle_norm = normalizar(calle_input)
        resultado = None

        filas = df[df["CALLE_NORM"] == calle_norm]

        for _, fila in filas.iterrows():
            if altura_en_rango(fila["ALTURA"], int(altura_input)):
                resultado = fila["EQUIPO TERRITORIAL"]
                break

        if resultado:
            st.success(f"Equipo territorial: **{resultado}**")
        else:
            st.error("FUERA DE ÁREA")
