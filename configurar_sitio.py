#!/usr/bin/env python
"""
Script para configurar el sitio de Django para django-allauth en producción
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent / 'tienda'
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda.settings')
django.setup()

from django.contrib.sites.models import Site

# Obtener el dominio de Render
render_service_url = os.environ.get('RENDER_EXTERNAL_URL', '')
if render_service_url:
    # Extraer el dominio sin http:// o https://
    domain = render_service_url.replace('https://', '').replace('http://', '')
    site = Site.objects.get(pk=1)
    site.domain = domain
    site.name = 'Tienda Online'
    site.save()
    print(f'✓ Sitio configurado con dominio: {domain}')
else:
    # Si no está en Render, usar el dominio por defecto
    site = Site.objects.get(pk=1)
    if site.domain == 'example.com':
        site.domain = 'localhost:8000'
        site.name = 'Tienda Online'
        site.save()
    print(f'✓ Sitio configurado con dominio: {site.domain}')

