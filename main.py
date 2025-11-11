import streamlit as st
import pandas as pd
from datetime import date
import qrcode
from io import BytesIO
import os

# ---------- CONFIGURACIÓN ----------
st.set_page_config(page_title="Asistencia QR", page_icon="📋", layout="centered")

STUDENTS_FILE = "data/students.csv"
ATTENDANCE_FILE = "data/attendance.csv"

# Crear archivos si no existen
if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.exists(STUDENTS_FILE):
    st.error("⚠️ No se encontró 'students.csv'. Creá el archivo dentro de la carpeta /data")
if not os.path.exists(ATTENDANCE_FILE):
    with open(ATTENDANCE_FILE, "w") as f:
        f.write("student_id,fecha,status\n")

# ---------- FUNCIONES ----------
def get_students():
    return pd.read_csv(STUDENTS_FILE)

def get_attendance():
    return pd.read_csv(ATTENDANCE_FILE)

def marcar_presente(student_id):
    df = get_attendance()
    hoy = str(date.today())
    existe = ((df["student_id"] == student_id) & (df["fecha"] == hoy)).any()

    if not existe:
        nuevo = pd.DataFrame([[student_id, hoy, "P"]], columns=df.columns)
        df = pd.concat([df, nuevo], ignore_index=True)
        df.to_csv(ATTENDANCE_FILE, index=False)
    return df

def generar_qr(data):
    qr = qrcode.make(data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    return buf.getvalue()

# ---------- INTERFAZ ----------
st.title("📋 Sistema de Asistencia con QR (sin base de datos)")

menu = st.sidebar.selectbox("Menú", ["Generar QR", "Marcar asistencia", "Ver registro"])

elif menu == "Generar QR":
    st.subheader("📱 Código QR general de asistencia")

    # URL de tu app en Streamlit Cloud
    app_url = "https://asistenciaqr.streamlit.app/"  # Cambialo por tu URL real

    qr_img = qrcode.make(app_url)
    buf = BytesIO()
    qr_img.save(buf, format="PNG")
    st.image(buf.getvalue(), width=250)

    st.markdown("### Escaneá este QR para registrar asistencia")
    st.code(app_url, language="text")
    st.info("Podés imprimirlo o proyectarlo en clase. Todos los alumnos lo usarán.")

elif menu == "Marcar asistencia":
    st.subheader("🧍 Marcar asistencia desde el QR general")

    students = get_students()
    nombre = st.selectbox("Seleccioná tu nombre", students["nombre"])

    if st.button("Marcar Presente"):
        student_id = int(students.loc[students["nombre"] == nombre, "id"].values[0])
        marcar_presente(student_id)
        st.success(f"✅ Asistencia registrada para {nombre}")

    st.markdown("---")
    st.markdown("### Lista de alumnos presentes hoy")

    df = get_attendance()
    hoy = str(date.today())
    presentes = df[df["fecha"] == hoy]
    if presentes.empty:
        st.info("Aún no hay alumnos registrados hoy.")
    else:
        presentes = presentes.merge(students, left_on="student_id", right_on="id", how="left")
        st.dataframe(presentes[["nombre", "apellido", "fecha", "status"]])



elif menu == "Ver registro":
    st.subheader("📅 Registro de asistencias")
    df = get_attendance()
    if df.empty:
        st.info("Aún no hay asistencias registradas.")
    else:
        students = get_students()
        df = df.merge(students, left_on="student_id", right_on="id", how="left")
        df = df[["fecha", "nombre", "apellido", "status"]]
        st.dataframe(df.sort_values(by="fecha", ascending=False), use_container_width=True)
        st.download_button(
            "📥 Descargar CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"asistencias_{date.today()}.csv",
            mime="text/csv"
        )
