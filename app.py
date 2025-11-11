from flask import Flask, render_template, request
import qrcode
import os
from datetime import date
from asistencia_qr_streamlit.db_config import get_db_connection

app = Flask(__name__)

# --- RUTA: Mostrar lista de alumnos y generar QR ---
@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    conn.close()

    # Crear carpeta si no existe
    os.makedirs('static/qrs', exist_ok=True)

    # Generar QR si no existen
    for s in students:
        qr_path = f'static/qrs/{s["id"]}.png'
        if not os.path.exists(qr_path):
            qr_url = f"http://localhost:5000/scan/{s['id']}"
            img = qrcode.make(qr_url)
            img.save(qr_path)

    return render_template('index.html', students=students)

# --- RUTA: Escanear QR y registrar asistencia ---
@app.route('/scan/<int:student_id>')
def scan(student_id):
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

    return render_template('scan.html', student_id=student_id)

# --- RUTA: Ver asistencia diaria ---
@app.route('/ver_asistencias')
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

    return render_template('ver_asistencias.html', registros=registros, fecha=today)

if __name__ == '__main__':
    app.run(debug=True)
