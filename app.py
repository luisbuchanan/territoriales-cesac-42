import streamlit as st
import pandas as pd
import unicodedata

# -----------------------
# Configuración de página
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
    texto = str(texto).strip().lower()
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
    df = pd.read_csv(
        "DOMICILIO Y TERRITORIAL - Hoja 2.csv",
        skiprows=1,
        encoding="utf-8-sig"
    )

    df = df.rename(columns={
        "CALLE": "calle",
        "ALTURA": "altura",
        "EQUIPO TERRITORIAL": "equipo"
    })

    df["calle_norm"] = df["calle"].apply(normalizar_texto)
    return df

df = cargar_datos()

# -----------------------
# AUTOCOMPLETADO DE CALLES
# -----------------------
st.subheader("Buscar domicilio")

texto_busqueda = st.text_input("Buscar calle")

calles_unicas = sorted(df["calle"].unique())

if texto_busqueda:
    texto_norm = normalizar_texto(texto_busqueda)

    opciones = [
        c for c in calles_unicas
        if texto_norm in normalizar_texto(c)
    ]
else:
    opciones = []

calle_seleccionada = st.selectbox(
    "Seleccionar calle",
    options=opciones,
    index=None,
    placeholder="Escribí arriba para ver opciones"
)

altura_input = st.number_input("Altura", min_value=0, step=1)

buscar = st.button("Buscar")

# -----------------------
# BÚSQUEDA FINAL
# -----------------------
if buscar:
    if not calle_seleccionada:
        st.warning("Seleccioná una calle")
    else:
        calle_norm = normalizar_texto(calle_seleccionada)
        encontrado = False

        for _, fila in df.iterrows():
            if fila["calle_norm"] == calle_norm:
                if altura_en_rango(fila["altura"], int(altura_input)):
                    st.success(f"Equipo territorial: {fila['equipo']}")
                    encontrado = True
                    break

        if not encontrado:
            st.error("FUERA DE ÁREA")
