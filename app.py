import streamlit as st
import pandas as pd
import unicodedata

# -----------------------
# Configuración página
# -----------------------
st.set_page_config(
    page_title="Territoriales CESAC 42",
    layout="centered"
)

st.title("Buscador Territorial – CESAC 42")

# -----------------------
# Funciones auxiliares
# -----------------------
def normalizar_texto(texto):
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto

def altura_en_rango(valor_csv, altura_ingresada):
    valor = str(valor_csv).strip()

    if "-" in valor:
        desde, hasta = map(int, valor.split("-"))
        return desde <= altura_ingresada <= (hasta + 99)
    else:
        desde = int(valor)
        return desde <= altura_ingresada <= (desde + 99)

# -----------------------
# Carga de datos
# -----------------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("DOMICILIO Y TERRITORIAL - Hoja 2.csv")
    df["CALLE_NORM"] = df["CALLE"].apply(normalizar_texto)
    return df

df = cargar_datos()

# -----------------------
# Interfaz
# -----------------------
calle_input = st.text_input("Calle")
altura_input = st.number_input("Altura", min_value=0, step=1)

buscar = st.button("Buscar")

# -----------------------
# Búsqueda
# -----------------------
if buscar:
    calle_norm = normalizar_texto(calle_input)
    encontrado = False

    for _, fila in df.iterrows():
        if fila["CALLE_NORM"] == calle_norm:
            if altura_en_rango(fila["ALTURA"], int(altura_input)):
                st.success(f"Equipo territorial: {fila['EQUIPO TERRITORIAL']}")
                encontrado = True
                break

    if not encontrado:
        st.error("FUERA DE ÁREA")
