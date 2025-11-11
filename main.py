import streamlit as st
import mysql.connector
import qrcode
from datetime import date
import os

# ---------------------------
# Conexión a la base de datos
# ---------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",    # En Streamlit Cloud será remoto (ver abajo)
        user="root",
        password="",
        database="asistencia_qr"
    )

# ---------------------------
# Generar QR si no existe
# ---------------------------
def generar_qr(id_estudiante):
    os.makedirs("qrs", exist_ok=True)
    qr_path = f"qrs/{id_estudiante}.png"
    url = f"https://asistenciaqr.streamlit.app/?scan={id_estudiante}"
    if not os.path.exists(qr_path):
        img = qrcode.make(url)
        img.save(qr_path)
    return qr_path

# ---------------------------
# Registrar asistencia
# ---------------------------
def registrar_asistencia(student_id):
    conn = get_db_connection()
    cur = conn.cursor()
    today = date.today()
    sql = """
    INSERT INTO attendance (student_id, fecha, status)
    VALUES (%s, %s, 'P')
    ON DUPLICATE KEY UPDATE status='P'
    """
    cur.execute(sql, (student_id, today))
    conn.commit()
    conn.close()

# ---------------------------
# Mostrar estudiantes y QR
# ---------------------------
def mostrar_qr():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    conn.close()

    st.header("📋 Lista de estudiantes (con QR)")
    cols = st.columns(3)
    for i, s in enumerate(students):
        with cols[i % 3]:
            qr_path = generar_qr(s["id"])
            st.image(qr_path, width=120)
            st.markdown(f"**{s['nombre']} {s['apellido']}**")

# ---------------------------
# Mostrar asistencia diaria
# ---------------------------
def ver_asistencias():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    today = date.today()
    cur.execute("""
        SELECT s.nombre, s.apellido, a.status
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id AND a.fecha = %s
    """, (today,))
    registros = cur.fetchall()
    conn.close()

    st.header(f"🗓️ Asistencia del {today}")
    st.table(registros)

# ---------------------------
# INTERFAZ STREAMLIT
# ---------------------------
st.set_page_config(page_title="Asistencia QR", page_icon="📱")

menu = st.sidebar.radio("Menú", ["Generar QR", "Ver Asistencia", "Escanear QR"])

if menu == "Generar QR":
    mostrar_qr()

elif menu == "Ver Asistencia":
    ver_asistencias()

elif menu == "Escanear QR":
    student_id = st.query_params.get("scan", [None])[0]
    if student_id:
        registrar_asistencia(student_id)
        st.success(f"✅ Asistencia registrada para ID {student_id}")
    else:
        st.info("Escanee un código QR generado por el sistema.")
