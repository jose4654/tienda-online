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

# Crear superusuario si no existe
echo "Creating admin user..."
cd ..
python create_admin.py
cd tienda

# Recolectar archivos estáticos
echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Build completed successfully!"

