# notification-service
Microservicio para notificaciones por email 


Notification Service  
  
Microservicio de notificaciones por email construido con Flask que soporta envío mediante SMTP y AWS SES.  
  
Descripción  
Este servicio recibe solicitudes HTTP POST con datos de usuarios y envía notificaciones por email de forma asíncrona. Soporta dos métodos de envío:  
  
- SMTP: Para proveedores como Gmail [3](#1-2)   
-  AWS SES: Para envío mediante Amazon Simple Email Service [4](#1-3)   
  
Requisitos del Sistema  
  
- Python: 3.9 
- Sistema Operativo: Linux/macOS/Windows  
- Memoria RAM: Mínimo 512MB  
  
Dependencias de Python  
  El archivo `requirements.txt` contiene las siguientes dependencias: 
  	Flask==2.3.3  
Requests==2.31.0  

Instalación
Paso 1: Clonar el Repositorio
git clone https://github.com/infraestructura-2025/notification-service.git  
cd notification-service

Paso 2: Crear Entorno Virtual (Recomendado)
Crear entorno virtual  
python3.9 -m venv venv  
 Activar entorno virtual 
En Linux/macOS:  
source venv/bin/activate  
En Windows: 
venv\Scripts\activate

Paso 3: Instalar Dependencias
Actualizar pip  
python -m pip install --upgrade pip  
  
Instalar dependencias desde requirements.txt 
pip install -r requirements.txt

El servicio se configura mediante variables de entorno:
Ejemplo de Configuración:
Crear un archivo .env (no incluir en git):
Configuración SMTP (Gmail) 
USE_SES=false  
SMTP_HOST=smtp.gmail.com  
SMTP_PORT=587  
SMTP_USER=tu-email@gmail.com  
SMTP_PASS=tu-contraseña-app  
SES_DEST_EMAIL=destinatario@example.com  
  
Configuración del servidor: 
PORT=5000  
FLASK_DEBUG=false  
SEND_SYNC=false


Ejecución Local: python app.py

Ejemplos de Uso
curl http://localhost:5000/health  
  	Enviar notificación 
curl -X POST http://localhost:5000/notify \  
  -H "Content-Type: application/json" \  
  -d '{  
    "name": "Juan Pérez",  
    "email": "juan@example.com",  
    "phone": "123456789",  
    "created_at": "2025-11-20"  
  }'

Arquitectura
El servicio utiliza:
Flask: Framework web ligero app.py:16
Threading: Para envío asíncrono de emails app.py:146-148
Logging: Sistema de logs estructurado app.py:18-20
SMTP/SES: Dos métodos de envío de email intercambiables app.py:23

CI/CD
El repositorio incluye integración con SonarCloud para análisis de calidad de código. sonarcloud.yml:1-6 El workflow se ejecuta automáticamente en:
Push a ramas main o master
Pull requests hacia main o master
