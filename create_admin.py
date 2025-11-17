#!/usr/bin/env python
"""
Script para crear un superusuario automáticamente durante el deploy.
Se ejecuta después de las migraciones.
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Obtener credenciales de variables de entorno
admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
admin_email = os.environ.get('ADMIN_EMAIL', 'admin@tienda.com')
admin_password = os.environ.get('ADMIN_PASSWORD', '')

if not admin_password:
    print("ADMIN_PASSWORD no está configurado. Saltando creación de admin.")
    sys.exit(0)

# Verificar si el usuario ya existe
if User.objects.filter(username=admin_username).exists():
    print(f"El usuario '{admin_username}' ya existe. Saltando creación.")
    sys.exit(0)

# Crear el superusuario
try:
    User.objects.create_superuser(
        username=admin_username,
        email=admin_email,
        password=admin_password
    )
    print(f"✓ Superusuario '{admin_username}' creado exitosamente.")
except Exception as e:
    print(f"Error al crear superusuario: {e}")
    sys.exit(1)

