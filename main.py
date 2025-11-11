import streamlit as st
import pandas as pd
import qrcode
import io
from datetime import date

# --- Archivo CSV para asistencias ---
ATTENDANCE_CSV = "attendance.csv"

# --- Inicializar CSV si no existe ---
def init_csv():
    try:
        pd.read_csv(ATTENDANCE_CSV)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["nombre", "apellido", "fecha"])
        df.to_csv(ATTENDANCE_CSV, index=False)

# --- Guardar asistencia ---
def guardar_asistencia(nombre, apellido):
    df = pd.read_csv(ATTENDANCE_CSV)
    hoy = str(date.today())
    nuevo = pd.DataFrame([[nombre, apellido, hoy]], columns=["nombre", "apellido", "fecha"])
    df = pd.concat([df, nuevo], ignore_index=True)
    df.to_csv(ATTENDANCE_CSV, index=False)

# --- Obtener asistencias ---
def obtener_asistencias():
    return pd.read_csv(ATTENDANCE_CSV)

# Inicializar archivo si no existe
init_csv()

# --- Interfaz Streamlit ---
st.set_page_config(page_title="Asistencia QR - ASLE", page_icon="📋")
st.title("📋 Sistema de Asistencia QR - ASLE")

menu = st.sidebar.selectbox(
    "Menú",
    ["Inicio", "Marcar asistencia", "Generar QR", "Ver asistencia"]
)

# --- Inicio ---
if menu == "Inicio":
    st.write("""
    Bienvenido al sistema de asistencia de **ASLE**.
    
    🔹 Los alumnos solo deben escanear el **código QR general**  
    🔹 Luego completan su **nombre y apellido**  
    🔹 Y presionan **Enviar asistencia** para registrar su presente del día.
    """)

# --- Marcar asistencia ---
elif menu == "Marcar asistencia":
    st.subheader("🧍 Registro de Asistencia")

    with st.form("asistencia_form"):
        nombre = st.text_input("Nombre:")
        apellido = st.text_input("Apellido:")
        enviar = st.form_submit_button("Enviar asistencia ✅")

        if enviar:
            if nombre.strip() == "" or apellido.strip() == "":
                st.error("Por favor, completá tu nombre y apellido.")
            else:
                guardar_asistencia(nombre.strip(), apellido.strip())
                st.success(f"✅ Asistencia registrada para {nombre} {apellido}")

# --- Generar QR ---
elif menu == "Generar QR":
    st.subheader("📱 Código QR general de acceso a la app")

    # 🔗 Enlace público de tu app (modificar si cambia)
    link = "https://darobarbaroja-asistencia-qr-streamlit.streamlit.app/"

    st.write("Cualquiera puede escanear este código para registrar su asistencia 👇")

    # Crear QR más chico
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,   # tamaño ajustado
        border=2,
    )
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Mostrar QR
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), caption="Escaneá para acceder al formulario", width=250)

    # Mostrar link
    st.write("🔗 Enlace directo:")
    st.code(link, language="text")

# --- Ver asistencia ---
elif menu == "Ver asistencia":
    st.subheader("📅 Lista de asistencias registradas")

    df = obtener_asistencias()
    if df.empty:
        st.info("Aún no hay asistencias registradas.")
    else:
        hoy = str(date.today())
        presentes_hoy = df[df["fecha"] == hoy]
        total_hoy = len(presentes_hoy)

        st.write(f"🗓️ **Presentes hoy ({hoy}): {total_hoy} alumnos**")
        st.dataframe(presentes_hoy.sort_values("nombre"))

        st.markdown("---")
        st.write("📚 **Historial completo:**")
        st.dataframe(df.sort_values("fecha", ascending=False))
