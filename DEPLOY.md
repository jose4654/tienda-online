# Guía de Deploy en Render

Esta guía te ayudará a desplegar tu tienda online en Render.

## Prerequisitos

1. Cuenta en [Render](https://render.com)
2. Repositorio en GitHub con el código del proyecto
3. Credenciales de Mercado Pago y Telegram configuradas

## Paso 1: Preparar el repositorio en GitHub

1. Inicializa git (si no lo has hecho):
```bash
cd tienda-online
git init
git add .
git commit -m "Initial commit"
```

2. Crea un repositorio en GitHub y conecta tu proyecto:
```bash
git remote add origin https://github.com/tu-usuario/tu-repositorio.git
git branch -M main
git push -u origin main
```

## Paso 2: Crear servicio en Render

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Click en "New +" → "Web Service"
3. Conecta tu repositorio de GitHub
4. Selecciona el repositorio de tu tienda

## Paso 3: Configurar el servicio

### Configuración básica:
- **Name**: `tienda-online` (o el nombre que prefieras)
- **Environment**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `cd tienda && gunicorn tienda.wsgi:application`

### Variables de entorno

Configura las siguientes variables de entorno en Render:

#### Obligatorias:
```
SECRET_KEY=tu-secret-key-generado-por-render
DEBUG=False
ALLOWED_HOSTS=tu-app.onrender.com
```

#### Mercado Pago:
```
MERCADOPAGO_PUBLIC_KEY=tu-public-key-de-produccion
MERCADOPAGO_ACCESS_TOKEN=tu-access-token-de-produccion
MERCADOPAGO_CURRENCY_ID=ARS
MERCADOPAGO_SUCCESS_URL=https://tu-app.onrender.com/pago/mercadopago/resultado/
MERCADOPAGO_NOTIFICATION_URL=https://tu-app.onrender.com/webhooks/mercadopago/ (opcional)
```

#### Telegram:
```
TELEGRAM_BOT_TOKEN=tu-bot-token
TELEGRAM_CHAT_ID=tu-chat-id
```

## Paso 4: Base de datos (opcional)

Si necesitas una base de datos persistente:

1. En Render, crea un "PostgreSQL" service
2. Obtén la URL de conexión
3. Actualiza `settings.py` para usar PostgreSQL en producción:

```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL')
    )
}
```

Y agrega `dj-database-url` y `psycopg2-binary` a `requirements.txt`.

## Paso 5: Migraciones

Render ejecutará las migraciones automáticamente si agregas esto al `build.sh`:

```bash
python manage.py migrate --no-input
```

O puedes ejecutarlas manualmente desde el shell de Render.

## Paso 6: Crear superusuario

Una vez desplegado, accede al shell de Render y ejecuta:

```bash
cd tienda
python manage.py createsuperuser
```

## Paso 7: Verificar el deploy

1. Visita la URL de tu aplicación: `https://tu-app.onrender.com`
2. Verifica que los archivos estáticos se carguen correctamente
3. Prueba el flujo de compra completo

## Notas importantes

- **Archivos estáticos**: Se recolectan automáticamente con `collectstatic` en el build
- **Media files**: Para producción, considera usar un servicio como AWS S3 o Cloudinary
- **HTTPS**: Render proporciona HTTPS automáticamente
- **Webhooks**: Asegúrate de configurar las URLs de webhook en Mercado Pago con tu dominio de Render

## Troubleshooting

### Error: "No module named 'gunicorn'"
Agrega `gunicorn` a `requirements.txt`:
```
gunicorn==21.2.0
```

### Error: "Static files not found"
Verifica que `STATIC_ROOT` esté configurado y que `collectstatic` se ejecute en el build.

### Error: "ALLOWED_HOSTS"
Asegúrate de incluir tu dominio de Render en `ALLOWED_HOSTS`.

## Soporte

Para más información, consulta la [documentación de Render](https://render.com/docs).

