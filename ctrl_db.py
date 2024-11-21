import mysql.connector
from typing import Optional
from mysql.connector import Error
from datetime import datetime
from typing import List, Optional

# Función para conectar a la base de datos
def db_connection():
    """Conectar a la base de datos MySQL."""
    connection = None
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",  # Dirección de tu servidor MySQL
            port=3306,  # Puerto de MySQL
            user="root",  # Usuario de MySQL
            password="tu_contraseña",  # Contraseña de MySQL
            database="BlockDeNotas"  # Nombre de tu base de datos
        )
        if connection.is_connected():
            print("Conexión exitosa a la base de datos MySQL")
    except Error as e:
        print(f"Error de conexión: '{e}'")
    return connection

# Función para cerrar la conexión
def close_connection(connection):
    if connection and connection.is_connected():
        connection.close()
        print("Conexión cerrada")

# Obtener todas las notas
def get_all_notes() -> List[dict]:
    connection = db_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notas")
    notes = cursor.fetchall()
    cursor.close()
    close_connection(connection)
    return notes

# Obtener una nota por ID
def get_note_by_id(note_id: int) -> Optional[dict]:
    connection = db_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notas WHERE id = %s", (note_id,))
    note = cursor.fetchone()
    cursor.close()
    close_connection(connection)
    return note

# Crear una nueva nota
def create_note(id_usuario: int, titulo: str, contenido: str) -> Optional[dict]:
    connection = db_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = """
        INSERT INTO notas (id_usuario, titulo, contenido, fecha_creacion, fecha_actualizacion)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (id_usuario, titulo, contenido, fecha_actual, fecha_actual))
    connection.commit()
    new_note_id = cursor.lastrowid
    cursor.execute("SELECT * FROM notas WHERE id = %s", (new_note_id,))
    new_note = cursor.fetchone()
    cursor.close()
    close_connection(connection)
    return new_note

# Actualizar una nota
def update_note(id_note: int, titulo: Optional[str], contenido: Optional[str]) -> Optional[dict]:
    connection = db_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    query = """
        UPDATE notas
        SET titulo = IFNULL(%s, titulo), contenido = IFNULL(%s, contenido), fecha_actualizacion = NOW()
        WHERE id = %s
    """
    cursor.execute(query, (titulo, contenido, id_note))
    connection.commit()
    cursor.execute("SELECT * FROM notas WHERE id = %s", (id_note,))
    updated_note = cursor.fetchone()
    cursor.close()
    close_connection(connection)
    return updated_note

# Eliminar una nota
def delete_note(note_id: int) -> Optional[dict]:
    connection = db_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notas WHERE id = %s", (note_id,))
    note = cursor.fetchone()
    if note:
        cursor.execute("DELETE FROM notas WHERE id = %s", (note_id,))
        connection.commit()
    cursor.close()
    close_connection(connection)
    return note
