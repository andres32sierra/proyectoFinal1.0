import sqlite3
import os

def check_sqlite():
    print("Verificando SQLite...")
    print(f"Versión de SQLite: {sqlite3.sqlite_version}")
    
    # Verificar las bases de datos
    dbs = [
        ('resource_service/resources.db', 'resources'),
        ('student_service/students.db', 'students'),
        ('loan_service/loans.db', 'loans')
    ]
    
    for db_path, table_name in dbs:
        if os.path.exists(db_path):
            print(f"\nBase de datos '{db_path}':")
            print("  ✓ Archivo existe")
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  ✓ Tabla '{table_name}' existe")
                print(f"  ✓ Número de registros: {count}")
                
                # Mostrar algunos registros de ejemplo
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                if rows:
                    print("  ✓ Primeros 3 registros:")
                    for row in rows:
                        print(f"    - {row}")
                conn.close()
            except sqlite3.Error as e:
                print(f"  ✗ Error al acceder a la tabla: {e}")
        else:
            print(f"\nBase de datos '{db_path}':")
            print("  ✗ Archivo no existe")

if __name__ == "__main__":
    check_sqlite()
