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

# Obtener credenciales de variables de entorno con valores por defecto
admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
admin_email = os.environ.get('ADMIN_EMAIL', 'admin@tienda.com')
admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin123!')

# Si no se proporciona contraseña, usar una por defecto segura
if not admin_password or admin_password == '':
    admin_password = 'Admin123!'
    print("⚠️  Usando contraseña por defecto. Cambia la contraseña desde el panel de admin por seguridad.")

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

