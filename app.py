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
    try:
        texto = str(valor_csv).upper().strip()

        # Detectar paridad
        solo_par = "PAR" in texto
        solo_impar = "IMPAR" in texto

        # Quitar palabras
        texto = (
            texto.replace("PAR", "")
                 .replace("IMPAR", "")
                 .strip()
        )

        # Verificar paridad del número ingresado
        if solo_par and altura_ingresada % 2 != 0:
            return False
        if solo_impar and altura_ingresada % 2 == 0:
            return False

        # Rango o número
        if "-" in texto:
            desde, hasta = texto.split("-")
            desde = int(desde.strip())
            hasta = int(hasta.strip())
            return desde <= altura_ingresada <= (hasta + 99)
        else:
            desde = int(texto)
            return desde <= altura_ingresada <= (desde + 99)

    except:
        return False


# -----------------------
# Carga de datos
# -----------------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv(
        "DOMICILIO Y TERRITORIAL - Hoja 2.csv",
        skiprows=1,
        encoding="utf-8"
    )

    df = df.rename(columns={
        "CALLE": "calle",
        "ALTURA": "altura",
        "EQUIPO TERRITORIAL": "equipo"
    })

    df["calle"] = df["calle"].astype(str)
    df["calle_norm"] = df["calle"].apply(normalizar_texto)

    return df

df = cargar_datos()

# -----------------------
# Interfaz
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
# Búsqueda
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

