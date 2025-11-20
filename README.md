# notification-service
Microservicio para notificaciones por email 

````md
# Notification Service

## 📝 Descripción
Microservicio encargado del envío de notificaciones.  
Generalmente usado para envío de emails o alertas internas.

## 🔔 Funcionalidades principales
- Envío de notificaciones por email  
- Manejo de plantillas  
- Recepción de solicitudes desde otros microservicios  

## 🧰 Tecnologías
- Python  
- Framework ligero (Flask / FastAPI / Django)  
- SMTP o proveedor de correos externo

## ▶️ Ejecutar localmente

### 1. Crear entorno
```bash
python -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables
Archivo `.env` (ejemplo):

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=usuario
SMTP_PASSWORD=clave
FROM_EMAIL=notificaciones@infraestructura.com
```

### 4. Ejecutar servicio
```bash
python main.py
```

## 📡 Endpoints
Documentar aquí los endpoints cuando estén definidos.

## 🐳 Docker
```bash
docker build -t notification-service .
docker run -p 5000:5000 notification-service
```

## ☁️ Deploy
Listo para desplegar en Kubernetes o EKS.

## 🤝 Contribución
Proceso estándar de PRs.

## 📄 Licencia
MIT.
````
