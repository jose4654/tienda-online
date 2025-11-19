#!/usr/bin/env bash
# Script de build para Render

set -o errexit  # Exit on error

echo "Building Django application..."

# Instalar dependencias
pip install -r requirements.txt

# Ir al directorio del proyecto
cd tienda

# Ejecutar migraciones
echo "Running migrations..."
python manage.py migrate --no-input

# Crear o resetear superusuario
echo "Creating/resetting admin user..."
cd ..
python reset_admin_password.py
cd tienda

# Recolectar archivos estáticos
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Configurar el sitio de Django para django-allauth
echo "Configuring Django site..."
cd ..
python configurar_sitio.py
cd tienda

echo "Build completed successfully!"

