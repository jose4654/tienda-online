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

## Notas

- El proyecto usa SQLite por defecto (base de datos en `tienda/db.sqlite3`)
- Los archivos estáticos están en `estaticos/`
- Los templates están en `plantillas/`
- Las imágenes de productos se guardan en `tienda/media/`

