import mysql.connector
from mysql.connector import Error
from config.db_config import DB_CONFIG

# Gestor de base de datos que maneja la conexión y operaciones con MariaDB
class GestorBD:
    def __init__(self):
        """Inicializa la conexión con MariaDB"""
        self.conexion = None
        self.cursor = None
        self.conectar()
        self.crear_tabla()
    
    def conectar(self):
        """Establece conexión con MariaDB"""
        try:
            # Crear conexión usando datos de config/db_config.py
            self.conexion = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conexion.cursor()
            print("✓ Conexión exitosa a MariaDB")
        except Error as err:
            if err.errno == 2003:
                print("❌ Error: No se puede conectar a MariaDB. Verifica que el servidor esté corriendo.")
            elif err.errno == 1045:
                print("❌ Error: Usuario o contraseña incorrectos.")
            elif err.errno == 1049:
                print("❌ Error: Base de datos no existe. Créala primero.")
            else:
                print(f"❌ Error de conexión: {err}")
            raise
    
    def crear_tabla(self):
        """Crea la tabla de operaciones si no existe"""
        try:
            # Ejecuta la creación de tabla solo la primera vez
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS operaciones (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    expresion VARCHAR(255) NOT NULL,
                    resultado VARCHAR(255) NOT NULL,
                    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conexion.commit()
            print("✓ Tabla 'operaciones' lista")
        except Error as err:
            print(f"Error al crear tabla: {err}")
    
    def guardar_operacion(self, expresion, resultado):
        """Guarda una operación en la BD"""
        try:
            sql = "INSERT INTO operaciones (expresion, resultado) VALUES (%s, %s)"
            self.cursor.execute(sql, (expresion, resultado))
            self.conexion.commit()
            return True
        except Error as err:
            print(f"Error al guardar operación: {err}")
            return False
    
    def obtener_historial(self, limite=10):
        """Obtiene el historial de operaciones (últimas N operaciones)"""
        try:
            sql = "SELECT expresion, resultado, fecha_hora FROM operaciones ORDER BY id DESC LIMIT %s"
            self.cursor.execute(sql, (limite,))
            return self.cursor.fetchall()
        except Error as err:
            print(f"Error al obtener historial: {err}")
            return []
    
    def obtener_todas_operaciones(self):
        """Obtiene todas las operaciones guardadas"""
        try:
            sql = "SELECT expresion, resultado, fecha_hora FROM operaciones ORDER BY id DESC"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Error as err:
            print(f"Error al obtener operaciones: {err}")
            return []
    
    def limpiar_historial(self):
        """Elimina todo el historial"""
        try:
            sql = "DELETE FROM operaciones"
            self.cursor.execute(sql)
            self.conexion.commit()
            return True
        except Error as err:
            print(f"Error al limpiar historial: {err}")
            return False
    
    def cerrar(self):
        """Cierra la conexión con la BD"""
        if self.cursor:
            self.cursor.close()
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
            print("✓ Conexión cerrada")
