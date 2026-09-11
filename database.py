import sqlite3
from datetime import datetime

DB_NAME = "citas.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def inicializar_db():
    conn = conectar()
    cursor = conn.cursor()
    
    # Tabla de Citas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            telefono TEXT,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            servicio TEXT NOT NULL,
            precio REAL NOT NULL,
            estado TEXT NOT NULL,
            notas TEXT
        )
    """)
    
    # Tabla de Licencia
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS licencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clave TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def guardar_cita(cliente, telefono, fecha, hora, servicio, precio, estado, notas):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO citas (cliente, telefono, fecha, hora, servicio, precio, estado, notas)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (cliente, telefono, fecha, hora, servicio, precio, estado, notas))
    conn.commit()
    conn.close()

def obtener_citas():
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM citas ORDER BY id DESC")
    filas = cursor.fetchall()
    conn.close()
    return [dict(fila) for fila in filas]

def actualizar_estado(cita_id, nuevo_estado):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE citas SET estado = ? WHERE id = ?", (nuevo_estado, cita_id))
    conn.commit()
    conn.close()

def eliminar_cita(cita_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM citas WHERE id = ?", (cita_id,))
    conn.commit()
    conn.close()

def obtener_resumen_financiero(anio_sel, mes_sel):
    conn = conectar()
    cursor = conn.cursor()
    
    # Total acumulado histórico (solo citas Terminadas)
    cursor.execute("SELECT SUM(precio) FROM citas WHERE TRIM(estado) = 'Terminada'")
    total_acumulado = cursor.fetchone()[0] or 0.0
    
    # Total filtrado por año
    cursor.execute("SELECT SUM(precio) FROM citas WHERE TRIM(estado) = 'Terminada' AND strftime('%Y', fecha) = ?", (str(anio_sel),))
    total_filtrado = cursor.fetchone()[0] or 0.0
    
    # Total filtrado por mes y año
    mes_str = f"{mes_sel:02d}"
    cursor.execute("SELECT SUM(precio) FROM citas WHERE TRIM(estado) = 'Terminada' AND strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?", (str(anio_sel), mes_str))
    total_mes = cursor.fetchone()[0] or 0.0
    
    conn.close()
    return {
        "total_acumulado": total_acumulado,
        "total_filtrado": total_filtrado,
        "total_mes": total_mes
    }

def guardar_licencia_db(clave):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM licencia")
    cursor.execute("INSERT INTO licencia (clave) VALUES (?)", (clave,))
    conn.commit()
    conn.close()

def obtener_licencia_db():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT clave FROM licencia LIMIT 1")
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else ""