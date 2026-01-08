import streamlit as st
import pandas as pd
import unicodedata
import re

st.set_page_config(page_title="Territoriales CESAC 42")

# =========================
# Funciones auxiliares
# =========================

def normalizar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto)
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto.upper().strip()

def altura_en_rango(valor_csv, altura_ingresada):
    try:
        texto = str(valor_csv).upper().strip()
        es_par = altura_ingresada % 2 == 0

        if "PAR" in texto:
            if not es_par:
                return False
            texto = texto.replace("PAR", "").strip()

        if "IMPAR" in texto:
            if es_par:
                return False
            texto = texto.replace("IMPAR", "").strip()

        if " - " in texto:
            desde, hasta = texto.split(" - ")
            return int(desde) <= altura_ingresada <= int(hasta)
        else:
            desde = int(texto)
            return desde <= altura_ingresada <= (desde + 99)

    except:
        return False

# =========================
# Carga de datos
# =========================

@st.cache_data
def cargar_datos():
    df = pd.read_csv(
        "DOMICILIO Y TERRITORIAL - Hoja 2.csv",
        encoding="utf-8",
        header=None
    )

    # Usamos solo las 3 columnas reales
    df = df.iloc[:, :3]
    df.columns = ["calle", "altura", "equipo"]

    # Normalización para búsqueda
    df["calle_norm"] = df["calle"].apply(normalizar_texto)

    return df

df = cargar_datos()

# =========================
# Interfaz
# =========================

st.title("Asignación de Equipo Territorial")

with st.form("busqueda"):
    calle_input = st.selectbox(
        "Calle",
        options=sorted(df["calle"].dropna().unique()),
        index=None,
        placeholder="Escribí el nombre de la calle..."
    )

    altura_input = st.text_input("Altura")

    buscar = st.form_submit_button("Buscar")

# =========================
# Lógica principal
# =========================

if buscar:
    if not calle_input or not altura_input.isdigit():
        st.warning("Ingresá una calle y una altura válida")
    else:
        altura_input = int(altura_input)
        calle_norm = normalizar_texto(calle_input)

        # Importante: NO igualdad estricta
        df_calle = df[df["calle_norm"] == calle_norm]

        equipo_encontrado = None

        for _, fila in df_calle.iterrows():
            if altura_en_rango(fila["altura"], altura_input):
                equipo_encontrado = fila["equipo"]
                break

        if equipo_encontrado:
            st.success(f"Equipo territorial: {equipo_encontrado}")
        else:
            st.error("FUERA DE ÁREA")

