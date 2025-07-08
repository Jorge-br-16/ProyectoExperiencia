import subprocess
import sys
import os

def install_requirements():
    """Instalar todas las dependencias necesarias"""
    
    print("🚀 Instalando dependencias del sistema de inscripciones...")
    
    # Lista de paquetes a instalar
    packages = [
        'Flask==2.3.3',
        'mysql-connector-python==8.1.0',
        'python-dotenv==1.0.0'
    ]
    
    try:
        for package in packages:
            print(f"📦 Instalando {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} instalado correctamente")
        
        print("\n🎉 ¡Todas las dependencias instaladas exitosamente!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def create_env_template():
    """Crear archivo .env template"""
    env_content = """# Configuración de base de datos MySQL
DB_HOST=localhost
DB_USER=root
DB_PASS=
DB_NAME=colegio

# Configuración de Gmail (OBLIGATORIO para envío de correos)
MAIL_USER=tu_email@gmail.com
MAIL_PASS=tu_contraseña_de_aplicacion_gmail
MAIL_ADMIN=admin@colegio-xyz.edu.pe

# INSTRUCCIONES PARA CONFIGURAR GMAIL:
# 1. Ve a tu cuenta de Google (https://myaccount.google.com/)
# 2. Seguridad > Verificación en 2 pasos (ACTIVAR)
# 3. Contraseñas de aplicaciones > Generar nueva contraseña
# 4. Selecciona "Correo" y "Otro (nombre personalizado)"
# 5. Copia la contraseña de 16 caracteres en MAIL_PASS
# 6. NO uses tu contraseña normal de Gmail
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("📄 Archivo .env creado. ¡IMPORTANTE: Edítalo con tus credenciales!")
        print("🔧 Lee las instrucciones dentro del archivo .env")
    else:
        print("📄 Archivo .env ya existe.")

def create_templates_folder():
    """Crear carpeta templates y archivos necesarios"""
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("📁 Carpeta 'templates' creada")
    
    # Verificar si main.html existe
    if not os.path.exists('templates/main.html'):
        print("⚠️  Archivo main.html no encontrado en templates/")
        print("💡 Asegúrate de mover main.html a la carpeta templates/")

def show_setup_instructions():
    """Mostrar instrucciones de configuración"""
    print("\n" + "="*60)
    print("🎯 INSTRUCCIONES DE CONFIGURACIÓN")
    print("="*60)
    
    print("\n1️⃣ CONFIGURAR BASE DE DATOS:")
    print("   - Instala MySQL/XAMPP")
    print("   - Ejecuta el script database.sql")
    print("   - Ajusta credenciales en .env si es necesario")
    
    print("\n2️⃣ CONFIGURAR GMAIL (OBLIGATORIO):")
    print("   - Ve a https://myaccount.google.com/")
    print("   - Seguridad > Verificación en 2 pasos (ACTIVAR)")
    print("   - Contraseñas de aplicaciones > Generar nueva")
    print("   - Selecciona 'Correo' y 'Otro (personalizado)'")
    print("   - Copia la contraseña de 16 caracteres")
    print("   - Pégala en MAIL_PASS del archivo .env")
    
    print("\n3️⃣ ESTRUCTURA DE ARCHIVOS:")
    print("   proyecto/")
    print("   ├── app.py")
    print("   ├── install.py")
    print("   ├── database.sql")
    print("   ├── .env")
    print("   └── templates/")
    print("       └── main.html")
    
    print("\n4️⃣ EJECUTAR:")
    print("   python app.py")
    
    print("\n5️⃣ PROBAR:")
    print("   - Ve a http://localhost:5000")
    print("   - Prueba http://localhost:5000/test_db")
    print("   - Prueba http://localhost:5000/test_email")

if __name__ == "__main__":
    print("🏫 Sistema de Inscripciones - Colegio SAN JUAN BAUTISTA")
    print("=" * 50)
    
    # Instalar dependencias
    if install_requirements():
        # Crear template de .env
        create_env_template()
        
        # Crear carpeta templates
        create_templates_folder()
        
        # Mostrar instrucciones
        show_setup_instructions()
        
        print("\n✅ Configuración inicial completada!")
        print("🔧 Edita el archivo .env y luego ejecuta: python app.py")
    else:
        print("❌ Error en la instalación")