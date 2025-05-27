from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
from functools import wraps
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")

# Service URLs
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")
RESOURCE_SERVICE_URL = os.getenv("RESOURCE_SERVICE_URL", "http://localhost:8001")
STUDENT_SERVICE_URL = os.getenv("STUDENT_SERVICE_URL", "http://localhost:8002")
LOAN_SERVICE_URL = os.getenv("LOAN_SERVICE_URL", "http://localhost:8003")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('login'))
        
        # Validate token
        headers = {'Authorization': f'Bearer {session["token"]}'}
        try:
            response = requests.get(f"{AUTH_SERVICE_URL}/validate-token", headers=headers)
            if response.status_code != 200:
                session.clear()
                return redirect(url_for('login'))
        except:
            session.clear()
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Intento de inicio de sesión - Usuario: {username}")
        
        try:
            print(f"Enviando solicitud a {AUTH_SERVICE_URL}/token")
            # Usar application/x-www-form-urlencoded como espera FastAPI
            response = requests.post(
                f"{AUTH_SERVICE_URL}/token",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            print(f"Respuesta recibida - Status Code: {response.status_code}")
            print(f"Respuesta headers: {response.headers}")
            print(f"Respuesta contenido: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print("Inicio de sesión exitoso")
                print(f"Token recibido: {data['access_token']}")
                session['token'] = data['access_token']
                return redirect(url_for('index'))
            else:
                print(f"Error en inicio de sesión: {response.text}")
                flash('Credenciales inválidas', 'error')
        except Exception as e:
            print(f"Error al conectar con el servicio de autenticación: {str(e)}")
            flash('Service unavailable', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/resources')
@login_required
def resources():
    try:
        response = requests.get(f"{RESOURCE_SERVICE_URL}/resources/")
        resources = response.json() if response.status_code == 200 else []
        return render_template('resources.html', resources=resources)
    except:
        flash('Error al obtener recursos', 'error')
        return render_template('resources.html', resources=[])

@app.route('/resources/add', methods=['GET', 'POST'])
@login_required
def add_resource():
    if request.method == 'POST':
        try:
            data = {
                'name': request.form.get('name'),
                'description': request.form.get('description'),
                'type': request.form.get('type'),
                'quantity': int(request.form.get('quantity', 1)),
                'status': 'disponible'
            }
            
            response = requests.post(
                f"{RESOURCE_SERVICE_URL}/resources/",
                json=data
            )
            
            if response.status_code == 200:
                flash('Recurso agregado exitosamente', 'success')
                return redirect(url_for('resources'))
            else:
                error_detail = response.json().get('detail', 'Error desconocido')
                flash(f'Error al agregar recurso: {error_detail}', 'error')
        except requests.RequestException as e:
            flash('Error de conexión con el servicio', 'error')
        except Exception as e:
            flash(f'Error al agregar recurso: {str(e)}', 'error')
            
    return render_template('add_resource.html')

@app.route('/students')
@login_required
def students():
    try:
        headers = {'Authorization': f'Bearer {session["token"]}'}
        response = requests.get(
            f"{STUDENT_SERVICE_URL}/students/",
            headers=headers
        )
        students = response.json() if response.status_code == 200 else []
        return render_template('students.html', students=students)
    except:
        flash('Error al obtener estudiantes', 'error')
        return render_template('students.html', students=[])

@app.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        try:
            phone = request.form.get('phone')
            data = {
                'name': request.form.get('name'),
                'email': request.form.get('email'),
                'student_id': request.form.get('student_id'),
                'career': request.form.get('career'),
                'semester': int(request.form.get('semester')),
                'phone': phone if phone else None
            }
            
            # Validar datos requeridos
            if not all([data['name'], data['email'], data['student_id'], data['career']]):
                flash('Todos los campos son requeridos', 'error')
                return render_template('add_student.html')
            
            response = requests.post(
                f"{STUDENT_SERVICE_URL}/students/",
                json=data
            )
            
            if response.status_code == 200:
                flash('Estudiante agregado exitosamente', 'success')
                return redirect(url_for('students'))
            else:
                error_detail = response.json().get('detail', 'Error desconocido')
                flash(f'Error al agregar estudiante: {error_detail}', 'error')
        except requests.RequestException as e:
            flash('Error de conexión con el servicio', 'error')
        except ValueError as e:
            flash('El semestre debe ser un número válido', 'error')
        except Exception as e:
            flash(f'Error al agregar estudiante: {str(e)}', 'error')
            
    return render_template('add_student.html')

@app.route('/loans')
@login_required
def loans():
    try:
        headers = {'Authorization': f'Bearer {session["token"]}'}
        
        # Obtener préstamos
        response = requests.get(
            f'{LOAN_SERVICE_URL}/loans/',
            headers=headers
        )
        if response.status_code != 200:
            flash('Error al obtener préstamos', 'error')
            return render_template('loans.html', loans=[], resources={}, students={})
        loans = response.json()
        
        # Obtener recursos
        response_resources = requests.get(
            f'{RESOURCE_SERVICE_URL}/resources/',
            headers=headers
        )
        if response_resources.status_code != 200:
            flash('Error al obtener recursos', 'error')
            return render_template('loans.html', loans=[], resources={}, students={})
        
        # Crear diccionario de recursos usando id como clave
        resources = {}
        for resource in response_resources.json():
            resources[str(resource['id'])] = resource
        
        # Obtener estudiantes
        response_students = requests.get(
            f'{STUDENT_SERVICE_URL}/students/',
            headers=headers
        )
        if response_students.status_code != 200:
            flash('Error al obtener estudiantes', 'error')
            return render_template('loans.html', loans=[], resources={}, students={})
            
        # Crear diccionario de estudiantes usando student_id como clave
        students = {}
        for student in response_students.json():
            students[student['student_id']] = student
        
        # Debug: imprimir información
        print("Loans:", loans)
        print("Resources:", resources)
        print("Students:", students)
        
        return render_template('loans.html', loans=loans, resources=resources, students=students)
    except Exception as e:
        flash(f'Error al cargar los préstamos: {str(e)}', 'error')
        return render_template('loans.html', loans=[], resources={}, students={})

@app.route('/loans/<int:loan_id>/return', methods=['POST'])
@login_required
def return_loan(loan_id):
    try:
        headers = {'Authorization': f'Bearer {session["token"]}'}
        # Obtener el préstamo actual
        response = requests.get(
            f'{LOAN_SERVICE_URL}/loans/{loan_id}',
            headers=headers
        )
        if response.status_code == 404:
            flash('Préstamo no encontrado', 'error')
            return redirect(url_for('loans'))
            
        loan = response.json()
        
        # Actualizar el estado del préstamo
        loan['status'] = 'devuelto'
        loan['return_date'] = datetime.now().isoformat()
        
        # Enviar actualización al servicio de préstamos
        response = requests.put(
            f'{LOAN_SERVICE_URL}/loans/{loan_id}',
            json=loan,
            headers=headers
        )
        if response.status_code == 200:
            # Actualizar el estado del recurso a disponible
            resource_response = requests.put(
                f'{RESOURCE_SERVICE_URL}/resources/{loan["resource_id"]}/status',
                json={"status": "disponible"},
                headers=headers
            )
            if resource_response.status_code == 200:
                flash('Recurso devuelto exitosamente', 'success')
            else:
                flash('Error al actualizar el estado del recurso', 'error')
        else:
            flash('Error al actualizar el préstamo', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('loans'))

@app.route('/loans/create', methods=['GET', 'POST'])
@login_required
def create_loan():
    if request.method == 'POST':
        try:
            resource_id = request.form.get('resource_id')
            student_id = request.form.get('student_id')
            
            if not resource_id or not student_id:
                flash('Por favor seleccione un recurso y un estudiante', 'error')
                return redirect(url_for('create_loan'))
            
            quantity = int(request.form.get('quantity', 1))
            
            data = {
                'resource_id': int(resource_id),
                'student_id': student_id,
                'status': 'prestado',
                'quantity': quantity
            }
            
            # Primero verificamos que el recurso esté disponible
            resource_response = requests.get(
                f"{RESOURCE_SERVICE_URL}/resources/{data['resource_id']}"
            )
            
            if resource_response.status_code != 200:
                flash('Error: El recurso seleccionado no existe', 'error')
                return redirect(url_for('create_loan'))
                
            resource = resource_response.json()
            available_quantity = resource['quantity'] - resource['loaned_quantity']
            if available_quantity < quantity:
                flash(f'Error: Solo hay {available_quantity} unidades disponibles', 'error')
                return redirect(url_for('create_loan'))
            
            # Verificamos que el estudiante exista
            student_response = requests.get(
                f"{STUDENT_SERVICE_URL}/students/by-student-id/{data['student_id']}"
            )
            
            if student_response.status_code != 200:
                flash('Error: El estudiante seleccionado no existe', 'error')
                return redirect(url_for('create_loan'))
            
            # Creamos el préstamo
            response = requests.post(
                f"{LOAN_SERVICE_URL}/loans/",
                json=data
            )
            
            if response.status_code == 200:
                flash('Préstamo creado exitosamente', 'success')
                return redirect(url_for('loans'))
            else:
                error_detail = response.json().get('detail', 'Error desconocido')
                flash(f'Error al crear préstamo: {error_detail}', 'error')
                
        except requests.RequestException as e:
            app.logger.error(f'Error de conexión: {str(e)}')
            flash('Error de conexión con el servicio. Por favor intente más tarde.', 'error')
        except ValueError as e:
            flash('Error: Datos inválidos en el formulario', 'error')
        except Exception as e:
            app.logger.error(f'Error inesperado: {str(e)}')
            flash('Error inesperado. Por favor intente más tarde.', 'error')
    
    # Get available resources and students for the form
    try:
        resources_response = requests.get(f"{RESOURCE_SERVICE_URL}/resources/")
        students_response = requests.get(f"{STUDENT_SERVICE_URL}/students/")
        
        if resources_response.status_code != 200:
            flash('Error al obtener recursos', 'error')
            return render_template('create_loan.html', resources=[], students=[])
            
        if students_response.status_code != 200:
            flash('Error al obtener estudiantes', 'error')
            return render_template('create_loan.html', resources=[], students=[])
        
        resources = resources_response.json()
        students = students_response.json()
        
        # Filter resources that have available units
        available_resources = [r for r in resources if r.get('quantity', 0) > r.get('loaned_quantity', 0)]
        
        return render_template('create_loan.html',
                             resources=available_resources,
                             students=students)
    except requests.RequestException as e:
        app.logger.error(f'Error de conexión: {str(e)}')
        flash('Error al conectar con los servicios. Por favor intente más tarde.', 'error')
    except Exception as e:
        app.logger.error(f'Error inesperado: {str(e)}')
        flash('Error inesperado al cargar el formulario', 'error')
    
    return render_template('create_loan.html', resources=[], students=[])

@app.route('/loans/<int:loan_id>/devolver', methods=['POST'])
@login_required
def devolver_recurso(loan_id):
    try:
        headers = {'Authorization': f'Bearer {session["token"]}'}

        # Usar el endpoint específico para devolver préstamos
        response = requests.put(
            f'{LOAN_SERVICE_URL}/loans/{loan_id}/return',
            headers=headers
        )

        if response.status_code != 200:
            # Si falla la actualización del préstamo, intentar revertir el estado del recurso
            requests.put(
                f'{RESOURCE_SERVICE_URL}/resources/{resource_id}/status',
                json={"status": "prestado"},
                headers=headers
            )
            flash('Error al actualizar el préstamo', 'error')
            return redirect(url_for('loans'))

        flash('Préstamo devuelto exitosamente', 'success')
        return redirect(url_for('loans'))

    except Exception as e:
        flash(f'Error al devolver el préstamo: {str(e)}', 'error')
        return redirect(url_for('loans'))

@app.route('/student/<student_id>/loans')
@login_required
def student_loans(student_id):
    try:
        headers = {'Authorization': f'Bearer {session["token"]}'}
        response = requests.get(
            f"{LOAN_SERVICE_URL}/loans/student/{student_id}",
            headers=headers
        )
        loans = response.json() if response.status_code == 200 else []
        return render_template('student_loans.html', loans=loans, student_id=student_id)
    except:
        flash('Error al obtener préstamos del estudiante', 'error')
        return render_template('student_loans.html', loans=[], student_id=student_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
