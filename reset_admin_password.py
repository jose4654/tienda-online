#!/usr/bin/env python
"""
Script para resetear la contraseña del admin.
Útil cuando el admin ya existe pero no conoces la contraseña.
"""
import os
import sys
import django
from pathlib import Path

# Obtener el directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Agregar paths necesarios
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

TIENDA_DIR = BASE_DIR / 'tienda'
if str(TIENDA_DIR) not in sys.path:
    sys.path.insert(0, str(TIENDA_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Obtener credenciales de variables de entorno con valores por defecto
admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin123!')

# Buscar el usuario
try:
    user = User.objects.get(username=admin_username)
    # Resetear la contraseña
    user.set_password(admin_password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"✓ Contraseña del usuario '{admin_username}' reseteada exitosamente.")
    print(f"  Nueva contraseña: {admin_password}")
except User.DoesNotExist:
    print(f"El usuario '{admin_username}' no existe. Creando nuevo usuario...")
    try:
        User.objects.create_superuser(
            username=admin_username,
            email=os.environ.get('ADMIN_EMAIL', 'admin@tienda.com'),
            password=admin_password
        )
        print(f"✓ Superusuario '{admin_username}' creado exitosamente.")
        print(f"  Contraseña: {admin_password}")
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        sys.exit(1)
except Exception as e:
    print(f"Error al resetear contraseña: {e}")
    sys.exit(1)

