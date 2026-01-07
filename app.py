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
# FUNCIONES AUXILIARES
# -----------------------

def arreglar_encoding(texto):
    """
    Corrige textos mal decodificados desde Excel
    Ej: 'AlbarracÃ­n' -> 'Albarracín'
    """
    try:
        return texto.encode("latin1").decode("utf-8")
    except:
        return texto


def normalizar_texto(texto):
    """
    Normaliza texto para búsquedas:
    - minúsculas
    - sin tildes
    - sin ñ
    """
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto

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

    # Normalizaciones
    df["calle"] = df["calle"].apply(normalizar_visual)
    df["calle_norm"] = df["calle"].apply(normalizar_texto)

    df["calle"] = df["calle"].astype(str).apply(arreglar_encoding)

    return df

df = cargar_datos()

# -----------------------
# SELECTBOX CON AUTOCOMPLETADO
# -----------------------
st.subheader("Buscar domicilio")

calles_unicas = sorted(df["calle"].unique())

calle_seleccionada = st.selectbox(
    "Calle",
    options=calles_unicas,
    index=None,
    placeholder="Escribí el nombre de la calle"
)

altura_input = st.number_input("Altura", min_value=0, step=1)

buscar = st.button("Buscar")

# -----------------------
# BÚSQUEDA
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


