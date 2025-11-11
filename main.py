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

if menu == "Generar QR":
    st.subheader("📱 Códigos QR de los estudiantes")
    students = get_students()
    for _, row in students.iterrows():
        col1, col2 = st.columns([1, 3])
        with col1:
            qr_img = generar_qr(str(row["id"]))
            st.image(qr_img, width=90)
        with col2:
            st.markdown(f"**{row['nombre']} {row['apellido']}**")
            st.markdown(f"Color: `{row['avatar_color']}`")
    st.info("Podés guardar o imprimir estos QR para los alumnos.")

elif menu == "Marcar asistencia":
    st.subheader("🧍 Marcar asistencia manual o por ID QR")
    students = get_students()
    student_id = st.text_input("Ingresá ID del alumno (del QR):")

    if student_id:
        try:
            student_id = int(student_id)
            alumno = students.loc[students["id"] == student_id]
            if not alumno.empty:
                nombre = alumno.iloc[0]["nombre"]
                marcar_presente(student_id)
                st.success(f"✅ Asistencia registrada para {nombre}")
            else:
                st.error("❌ ID no encontrado en la lista de estudiantes.")
        except ValueError:
            st.error("El ID debe ser un número.")

    st.markdown("---")
    st.markdown("### Lista de alumnos")
    for _, row in students.iterrows():
        if st.button(f"Marcar Presente: {row['nombre']} {row['apellido']}"):
            marcar_presente(row["id"])
            st.success(f"Asistencia registrada para {row['nombre']}")

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
