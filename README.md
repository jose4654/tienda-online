# Tienda Online - Django

Tienda online completa con panel de administración integrado usando Django Admin.

## Características

- ✅ Sistema de autenticación con dos tipos de usuarios (Cliente y Administrador)
- ✅ Catálogo de productos con categorías
- ✅ Carrito de compras
- ✅ Sistema de pedidos
- ✅ Panel de administración personalizado usando Django Admin
- ✅ Interfaz responsive con Bootstrap 5

## Estructura del Proyecto

```
tienda phyton/
├── tienda/              # Proyecto Django principal
│   ├── manage.py
│   └── tienda/         # Configuración del proyecto
├── tienda_app/         # Aplicación principal
│   ├── models.py       # Modelos (Producto, Categoría, Pedido, etc.)
│   ├── views.py        # Vistas
│   ├── admin.py        # Configuración del panel de administración
│   └── urls.py         # URLs de la aplicación
├── plantillas/         # Templates HTML
├── estaticos/          # Archivos estáticos (CSS, JS)
└── venv/               # Entorno virtual

```

## Instalación y Configuración

### 1. Activar el entorno virtual

En PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

Si tienes problemas de permisos, ejecuta:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Instalar dependencias (si es necesario)

```bash
pip install django
```

### 3. Aplicar migraciones

```powershell
cd tienda
python manage.py migrate
```

### 4. Crear superusuario (Administrador)

```powershell
cd tienda
python manage.py createsuperuser
```

Sigue las instrucciones para crear tu usuario administrador.

### 5. Ejecutar el servidor

**IMPORTANTE**: Debes estar dentro del directorio `tienda/` para ejecutar el servidor.

```powershell
cd tienda
python manage.py runserver
```

O desde la raíz del proyecto:
```powershell
python tienda/manage.py runserver
```

Abre tu navegador en: http://127.0.0.1:8000

## URLs Importantes

- **Tienda principal**: http://127.0.0.1:8000/
- **Panel de administración Django**: http://127.0.0.1:8000/admin/
- **Login**: http://127.0.0.1:8000/ingreso/
- **Registro**: http://127.0.0.1:8000/registro/
- **Mis pedidos (cliente autenticado)**: http://127.0.0.1:8000/mis-pedidos/
- **Retorno de Mercado Pago**: http://127.0.0.1:8000/pago/mercadopago/resultado/

## Pagos con Mercado Pago

El checkout está integrado con Mercado Pago (Checkout Pro). Al confirmar la dirección de envío se crea una preferencia y el usuario es redirigido al `init_point` para completar el pago. El retorno vuelve al endpoint `pago/mercadopago/resultado/`, que actualiza el estado del pedido (aprobado, pendiente o cancelado).

### Variables requeridas

Puedes definirlas como variables de entorno o dejarlas en `tienda/tienda/settings.py` (solo recomendable para desarrollo):

```powershell
$env:MERCADOPAGO_PUBLIC_KEY = "APP_USR-xxxxx"
$env:MERCADOPAGO_ACCESS_TOKEN = "APP_USR-xxxxx"
$env:MERCADOPAGO_SUCCESS_URL = "https://tu-dominio.com/pago/mercadopago/resultado/"
$env:MERCADOPAGO_NOTIFICATION_URL = "https://tu-dominio.com/webhooks/mercadopago/"
```

Valores por defecto (modo prueba) configurados actualmente:

- `MERCADOPAGO_PUBLIC_KEY`: `APP_USR-a14fb7a6-c651-448d-89df-2a11558f760a`
- `MERCADOPAGO_ACCESS_TOKEN`: `APP_USR-6602017134633117-111712-be669b275c23ec1e2e851e87a8c81677-2995220879`
- `MERCADOPAGO_SUCCESS_URL`: si no se define, se usa la URL del request actual. Mercado Pago solo permite auto-retorno cuando esta URL es HTTPS; para entornos locales podés exponer el servidor con una herramienta tipo ngrok.
- `MERCADOPAGO_NOTIFICATION_URL`: opcional, apunta al endpoint que recibirá webhooks si querés procesar notificaciones asincrónicas.

Reemplázalos por tus credenciales de producción cuando despliegues el proyecto.

## Notificaciones a Telegram

Cuando un usuario completa una compra (checkout), se envía automáticamente una notificación a tu bot de Telegram con:

- Datos del pedido (número, fecha, estado, total)
- Datos del comprador (nombre, usuario, email, teléfono, dirección)
- Lista de productos con cantidades y precios
- Método de pago y referencia
- Observaciones del pedido

### Configuración

Las credenciales están configuradas en `tienda/tienda/settings.py` y pueden sobrescribirse con variables de entorno:

```powershell
$env:TELEGRAM_BOT_TOKEN = "7963787924:AAG6Cr_Ymz5ggCFDYvVTLTD3w7Rtqzn5ZxM"
$env:TELEGRAM_CHAT_ID = "-4965361549"
```

**Nota**: Si la notificación falla (por ejemplo, por problemas de red), el checkout continúa normalmente. Los errores se registran en los logs de Django.

## Tipos de Usuarios

### Cliente
- Puede ver productos
- Agregar productos al carrito
- Realizar pedidos
- Ver sus pedidos

### Administrador
- Acceso completo al panel de administración de Django en `/admin/`
- Puede gestionar productos, categorías, pedidos y usuarios

## Modelos Principales

- **Category**: Categorías de productos
- **Product**: Productos de la tienda
- **CustomerProfile**: Perfil extendido del usuario (cliente)
- **Order**: Pedidos realizados
- **OrderItem**: Items individuales de cada pedido

## Personalización del Admin

El panel de administración está personalizado en `tienda_app/admin.py` con:
- Filtros avanzados
- Búsqueda
- Campos editables en línea
- Configuración de visualización optimizada

## Próximos Pasos

1. Agregar productos y categorías desde el panel de administración
2. Crear usuarios de prueba
3. Personalizar los templates según tus necesidades
4. Agregar más funcionalidades (pagos, reviews, etc.)

## Deploy en Render

El proyecto está preparado para desplegarse en Render. Consulta el archivo [DEPLOY.md](DEPLOY.md) para instrucciones detalladas.

### Resumen rápido:

1. Sube el código a GitHub
2. Crea un Web Service en Render
3. Configura las variables de entorno (ver DEPLOY.md)
4. Render ejecutará automáticamente el build y las migraciones

### Archivos de configuración:

- `build.sh`: Script de build para Render
- `render.yaml`: Configuración opcional para Render
- `.gitignore`: Excluye archivos sensibles del repositorio

## Notas

- El proyecto usa SQLite por defecto (base de datos en `tienda/db.sqlite3`)
- Los archivos estáticos están en `estaticos/`
- Los templates están en `plantillas/`
- Las imágenes de productos se guardan en `tienda/media/`
- **IMPORTANTE**: No subas credenciales al repositorio. Usa variables de entorno en producción.

