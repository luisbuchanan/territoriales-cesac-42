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
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto

def normalizar_columna(col):
    return normalizar_texto(col).replace(" ", "")

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

    # Normalizar nombres de columnas (anti BOM / espacios / tildes)
    columnas_norm = {col: normalizar_columna(col) for col in df.columns}
    df = df.rename(columns=columnas_norm)

    # Mapeo esperado
    # calle, altura, equipoterritorial
    if not {"calle", "altura", "equipoterritorial"}.issubset(df.columns):
        st.error(f"Columnas encontradas: {list(df.columns)}")
        st.stop()

    df["calle_norm"] = df["calle"].apply(normalizar_texto)
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
        if fila["calle_norm"] == calle_norm:
            if altura_en_rango(fila["altura"], int(altura_input)):
                st.success(f"Equipo territorial: {fila['equipoterritorial']}")
                encontrado = True
                break

    if not encontrado:
        st.error("FUERA DE ÁREA")
