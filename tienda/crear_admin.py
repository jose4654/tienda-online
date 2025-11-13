"""
Script para crear un superusuario de administración automáticamente.
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django - agregar el directorio padre al path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Datos del administrador
username = 'admin'
email = 'admin@tienda.com'
password = 'admin123'  # Cambiá esta contraseña después

# Verificar si el usuario ya existe
if User.objects.filter(username=username).exists():
    print(f"[!] El usuario '{username}' ya existe.")
    usuario = User.objects.get(username=username)
    usuario.set_password(password)
    usuario.is_staff = True
    usuario.is_superuser = True
    usuario.save()
    print(f"[OK] Contraseña actualizada para el usuario '{username}'")
else:
    # Crear el superusuario
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"[OK] Superusuario '{username}' creado exitosamente!")

print("\n" + "="*50)
print("CREDENCIALES DE ACCESO:")
print("="*50)
print(f"Usuario: {username}")
print(f"Contraseña: {password}")
print("="*50)
print("\n[!] IMPORTANTE: Cambia la contraseña después del primer acceso.")
print("\nAccede a: http://127.0.0.1:8001/admin/")

