import streamlit as st
import pandas as pd
import qrcode
from datetime import date
from io import BytesIO

# --- Archivos CSV ---
STUDENTS_CSV = "students.csv"
ATTENDANCE_CSV = "attendance.csv"

# --- Cargar alumnos ---
def get_students():
    try:
        return pd.read_csv(STUDENTS_CSV)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["id", "nombre", "apellido"])
        df.to_csv(STUDENTS_CSV, index=False)
        return df

# --- Guardar alumnos ---
def save_students(df):
    df.to_csv(STUDENTS_CSV, index=False)

# --- Registrar asistencia ---
def marcar_presente(student_id):
    try:
        df = pd.read_csv(ATTENDANCE_CSV)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["student_id", "fecha", "status"])

    hoy = str(date.today())
    presente = {"student_id": student_id, "fecha": hoy, "status": "Presente"}

    # Evita duplicar asistencia el mismo día
    if not ((df["student_id"] == student_id) & (df["fecha"] == hoy)).any():
        df = pd.concat([df, pd.DataFrame([presente])], ignore_index=True)
        df.to_csv(ATTENDANCE_CSV, index=False)

# --- Obtener registros ---
def get_attendance():
    try:
        return pd.read_csv(ATTENDANCE_CSV)
    except FileNotFoundError:
        return pd.DataFrame(columns=["student_id", "fecha", "status"])

# --- App principal ---
st.title("📋 Sistema de Asistencia QR - Escuela Agraria Quilmes")

menu = st.sidebar.selectbox(
    "Menú",
    ["Inicio", "Registrar alumno", "Marcar asistencia", "Generar QR", "Ver asistencia"]
)

# --- Inicio ---
if menu == "Inicio":
    st.write("""
    Bienvenido al sistema de asistencia.
    Los alumnos pueden escanear un **único código QR general**
    que los redirige a esta página para marcar su asistencia.
    """)

# --- Registrar alumno ---
elif menu == "Registrar alumno":
    st.subheader("➕ Registrar nuevo alumno")
    nombre = st.text_input("Nombre")
    apellido = st.text_input("Apellido")

    if st.button("Guardar alumno"):
        if nombre and apellido:
            df = get_students()
            nuevo_id = len(df) + 1
            nuevo = pd.DataFrame([[nuevo_id, nombre, apellido]], columns=["id", "nombre", "apellido"])
            df = pd.concat([df, nuevo], ignore_index=True)
            save_students(df)
            st.success(f"Alumno {nombre} {apellido} agregado con ID {nuevo_id}")
        else:
            st.warning("Completa todos los campos.")

    st.markdown("---")
    st.dataframe(get_students())

# --- Marcar asistencia ---
elif menu == "Marcar asistencia":
    st.subheader("🧍 Marcar asistencia desde el QR general")

    students = get_students()
    if students.empty:
        st.warning("No hay alumnos registrados.")
    else:
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

# --- Generar QR ---
elif menu == "Generar QR":
    st.subheader("📱 Generar código QR de acceso a la app")

    # Enlace público fijo de tu app en Streamlit
    link = "https://darobarbaroja-asistencia-qr-streamlit.streamlit.app/"
    st.write("QR generado automáticamente para esta app:")

    # Generar QR
    qr = qrcode.make(link)
    qr_img = qr.get_image()
    st.image(qr_img, caption="Escaneá para acceder a la app", use_container_width=True)

    # Mostrar también el enlace por si alguien quiere copiarlo
    st.write("🔗 Enlace directo:")
    st.code(link, language="text")


# --- Ver asistencia completa ---
elif menu == "Ver asistencia":
    st.subheader("📅 Registro completo de asistencias")
    df = get_attendance()
    students = get_students()

    if df.empty:
        st.info("No hay registros de asistencia aún.")
    else:
        df = df.merge(students, left_on="student_id", right_on="id", how="left")
        st.dataframe(df[["fecha", "nombre", "apellido", "status"]])
