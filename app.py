from flask import Flask, render_template, request, jsonify
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mysql.connector
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
import re

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables del .env
load_dotenv()

app = Flask(__name__)

# Configuración base de datos
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', ''),
    'database': os.getenv('DB_NAME', 'colegio'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': True
}

def validar_email(email):
    """Validar formato de email"""
    if not email:
        return False
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def test_db_connection():
    """Probar conexión a la base de datos"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        logger.info("✅ Conexión a base de datos exitosa")
        return True
    except Exception as e:
        logger.error(f"❌ Error conectando a base de datos: {e}")
        return False

class EmailService:
    """Servicio para envío de correos con Gmail"""
    
    def __init__(self):
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.username = os.getenv('MAIL_USER', '').strip()
        self.password = os.getenv('MAIL_PASS', '').strip()
        self.admin_email = os.getenv('MAIL_ADMIN', '').strip()
        
        # Validar configuración
        if not self.username:
            raise ValueError("MAIL_USER requerido en archivo .env")
        
        if not self.password:
            raise ValueError("MAIL_PASS requerido en archivo .env")
        
        if not validar_email(self.username):
            raise ValueError("MAIL_USER debe ser un email válido")
        
        logger.info(f"✅ EmailService configurado para: {self.username}")
    
    def test_smtp_connection(self):
        """Probar conexión SMTP con Gmail"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                logger.info("✅ Conexión SMTP exitosa con Gmail")
                return True
        except Exception as e:
            logger.error(f"❌ Error conectando a Gmail: {e}")
            return False
    
    def crear_mensaje_inscripcion(self, data):
        """Crear mensaje HTML para inscripción"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Confirmación de Inscripción</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .info-card {{ background: #f8f9ff; padding: 20px; border-radius: 8px; margin: 15px 0; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎓 Colegio XYZ</h1>
                    <h2>✅ Inscripción Confirmada</h2>
                </div>
                
                <div class="content">
                    <h2>Estimados Padres de Familia,</h2>
                    <p>Nos complace confirmar que hemos recibido la inscripción de su hijo(a).</p>
                    
                    <div class="info-card">
                        <h3>📋 Datos del Estudiante</h3>
                        <p><strong>Nombre:</strong> {data.get('nombres', 'N/A')} {data.get('apellidos', 'N/A')}</p>
                        <p><strong>Fecha de nacimiento:</strong> {data.get('fechaNacimiento', 'N/A')}</p>
                        <p><strong>Grado:</strong> {data.get('grado', 'N/A')}°</p>
                        <p><strong>Año escolar:</strong> {data.get('anoEscolar', 'N/A')}</p>
                    </div>
                    
                    <div class="info-card">
                        <h3>👨‍👩‍👧‍👦 Datos de los Padres</h3>
                        <p><strong>Padre:</strong> {data.get('padreNombres', 'N/A')}</p>
                        <p><strong>Madre:</strong> {data.get('madreNombres', 'N/A')}</p>
                        <p><strong>Dirección:</strong> {data.get('direccion', 'N/A')}</p>
                    </div>
                    
                    <div class="info-card">
                        <h3>📞 Próximos Pasos</h3>
                        <ul>
                            <li>Recibirán una llamada en los próximos 2-3 días hábiles</li>
                            <li>Se coordinará una visita a nuestras instalaciones</li>
                            <li>Entrevista con el departamento académico</li>
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <h3>Colegio XYZ</h3>
                    <p>📧 {self.admin_email or 'admisiones@colegio-xyz.edu.pe'}</p>
                    <p>📱 (01) 234-5678</p>
                    <p>Enviado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_content
    
    def enviar_correo_masivo(self, destinatarios, asunto, contenido_html):
        """Enviar correo a múltiples destinatarios"""
        try:
            destinatarios_validos = [email.strip() for email in destinatarios if validar_email(email.strip())]
            
            if not destinatarios_validos:
                return {"exitos": [], "errores": [], "total_enviados": 0, "total_errores": 0}
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                
                exitos = []
                errores = []
                
                for destinatario in destinatarios_validos:
                    try:
                        mensaje = MIMEMultipart('alternative')
                        mensaje['From'] = f"Colegio XYZ <{self.username}>"
                        mensaje['To'] = destinatario
                        mensaje['Subject'] = asunto
                        
                        parte_html = MIMEText(contenido_html, 'html', 'utf-8')
                        mensaje.attach(parte_html)
                        
                        server.send_message(mensaje)
                        exitos.append(destinatario)
                        logger.info(f"✅ Correo enviado a: {destinatario}")
                        
                    except Exception as e:
                        errores.append({"email": destinatario, "error": str(e)})
                        logger.error(f"❌ Error enviando a {destinatario}: {e}")
                
                return {
                    "exitos": exitos,
                    "errores": errores,
                    "total_enviados": len(exitos),
                    "total_errores": len(errores)
                }
                
        except Exception as e:
            logger.error(f"❌ Error general en envío: {e}")
            return {"exitos": [], "errores": [], "total_enviados": 0, "total_errores": len(destinatarios)}

# Intentar inicializar el servicio de email
email_service = None
try:
    email_service = EmailService()
    if email_service.test_smtp_connection():
        logger.info("✅ Servicio de email listo")
    else:
        logger.warning("⚠️ Email configurado pero no se puede conectar")
        email_service = None
except Exception as e:
    logger.warning(f"⚠️ Email no configurado: {e}")
    email_service = None

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/test_email', methods=['GET'])
def test_email():
    """Endpoint para probar configuración de email"""
    if not email_service:
        return jsonify({
            "success": False, 
            "message": "❌ Servicio de email no disponible",
            "help": "Configura MAIL_USER y MAIL_PASS en .env"
        }), 500
    
    try:
        conexion_ok = email_service.test_smtp_connection()
        return jsonify({
            "success": conexion_ok,
            "message": "✅ Gmail configurado correctamente" if conexion_ok else "❌ Error de conexión Gmail",
            "username": email_service.username
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/test_db', methods=['GET'])
def test_db():
    """Endpoint para probar conexión a base de datos"""
    try:
        conexion_ok = test_db_connection()
        return jsonify({
            "success": conexion_ok,
            "message": "✅ Base de datos OK" if conexion_ok else "❌ Error de conexión DB"
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/enviar_inscripcion', methods=['POST'])
def enviar_inscripcion():
    try:
        # Obtener datos
        data = request.get_json(force=True)
        logger.info(f"📝 Procesando inscripción: {data.get('nombres')} {data.get('apellidos')}")

        # Validar campos obligatorios
        campos_obligatorios = ['nombres', 'apellidos', 'fechaNacimiento', 'grado', 'anoEscolar', 'direccion']
        for campo in campos_obligatorios:
            if not data.get(campo):
                return jsonify({
                    "success": False,
                    "message": f"El campo {campo} es obligatorio"
                }), 400

        # Validar emails
        emails = []
        if data.get('emailPadre') and validar_email(data.get('emailPadre')):
            emails.append(data.get('emailPadre').strip())
        if data.get('emailMadre') and validar_email(data.get('emailMadre')):
            emails.append(data.get('emailMadre').strip())

        # Guardar en base de datos
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            query = """
                INSERT INTO inscripciones 
                (nombres, apellidos, fecha_nacimiento, grado, ano_escolar, 
                 padre_nombres, madre_nombres, padre_telefono, madre_telefono, 
                 email_padre, email_madre, direccion, profesion, fecha_registro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            valores = (
                data.get('nombres', ''), data.get('apellidos', ''),
                data.get('fechaNacimiento', ''), data.get('grado', ''),
                data.get('anoEscolar', ''), data.get('padreNombres', ''),
                data.get('madreNombres', ''), data.get('padreTelefono', ''),
                data.get('madreTelefono', ''), data.get('emailPadre', ''),
                data.get('emailMadre', ''), data.get('direccion', ''),
                data.get('profesion', ''), datetime.now()
            )
            
            cursor.execute(query, valores)
            inscripcion_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"💾 Inscripción guardada con ID: {inscripcion_id}")
            
        except mysql.connector.Error as e:
            logger.error(f"❌ Error de base de datos: {e}")
            return jsonify({
                "success": False,
                "message": f"Error guardando en base de datos: {str(e)}"
            }), 500

        # Intentar enviar correos
        mensaje_final = ""
        correos_enviados = 0
        
        if email_service and emails:
            try:
                asunto = f"✅ Confirmación de Inscripción - {data.get('nombres', '')} {data.get('apellidos', '')} - Colegio XYZ"
                contenido_html = email_service.crear_mensaje_inscripcion(data)
                resultado_envio = email_service.enviar_correo_masivo(emails, asunto, contenido_html)
                
                correos_enviados = resultado_envio["total_enviados"]
                
                if correos_enviados > 0:
                    mensaje_final = f"🎉 ¡Inscripción registrada exitosamente! Se enviaron {correos_enviados} correos de confirmación."
                else:
                    mensaje_final = f"✅ Inscripción registrada (ID: {inscripcion_id}) pero hubo problemas enviando los correos."
                    
            except Exception as e:
                logger.error(f"❌ Error enviando correos: {e}")
                mensaje_final = f"✅ Inscripción registrada correctamente (ID: {inscripcion_id}) pero no se pudieron enviar los correos."
        
        elif not email_service:
            mensaje_final = f"✅ Inscripción registrada correctamente (ID: {inscripcion_id}). Para recibir emails, configure el servicio de correo en .env"
        
        elif not emails:
            mensaje_final = f"✅ Inscripción registrada correctamente (ID: {inscripcion_id}). No se proporcionaron emails válidos."

        return jsonify({
            "success": True,
            "message": mensaje_final,
            "inscripcion_id": inscripcion_id,
            "correos_enviados": correos_enviados
        }), 200

    except Exception as e:
        logger.error(f"❌ Error general: {e}")
        return jsonify({
            "success": False,
            "message": f"Error interno del servidor: {str(e)}"
        }), 500

@app.route('/consultar_inscripciones')
def consultar_inscripciones():
    """Consultar inscripciones registradas"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, nombres, apellidos, fecha_nacimiento, grado, ano_escolar,
                   padre_nombres, madre_nombres, email_padre, email_madre, 
                   fecha_registro
            FROM inscripciones 
            ORDER BY fecha_registro DESC 
            LIMIT 50
        """)
        inscripciones = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convertir datetime a string
        for inscripcion in inscripciones:
            if inscripcion['fecha_registro']:
                inscripcion['fecha_registro'] = inscripcion['fecha_registro'].strftime('%d/%m/%Y %H:%M:%S')
            if inscripcion['fecha_nacimiento']:
                inscripcion['fecha_nacimiento'] = inscripcion['fecha_nacimiento'].strftime('%d/%m/%Y')
        
        return jsonify({
            "success": True,
            "inscripciones": inscripciones,
            "total": len(inscripciones)
        })
    
    except Exception as e:
        logger.error(f"❌ Error consultando inscripciones: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Iniciando aplicación...")
    
    # Mostrar estado
    logger.info(f"📋 DB: {os.getenv('DB_NAME', 'colegio')} | Mail: {os.getenv('MAIL_USER', 'NO CONFIGURADO')}")
    
    # Probar conexiones
    db_ok = test_db_connection()
    email_ok = email_service is not None
    
    if db_ok and email_ok:
        logger.info("✅ Sistema completamente funcional")
    elif db_ok:
        logger.info("⚠️ Sistema funcional (sin emails)")
    else:
        logger.error("❌ Problemas de configuración")
    
    app.run(debug=True, host='0.0.0.0', port=5000)