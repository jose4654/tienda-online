from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

from .models import Category, Order, OrderItem, Product

admin.site.site_header = "Administración de MiTienda"
admin.site.site_title = "MiTienda"
admin.site.index_title = "Panel de control"


# Personalizar la visualización de Grupos
class GrupoPersonalizadoAdmin(GroupAdmin):
    """
    Personalización del admin de Grupos para hacerlo más amigable.
    """
    list_display = ('name', 'get_user_count', 'get_permissions_count')
    search_fields = ('name',)
    
    def get_user_count(self, obj):
        """Muestra la cantidad de usuarios en el grupo."""
        count = obj.user_set.count()
        return f"{count} usuario{'s' if count != 1 else ''}"
    get_user_count.short_description = "Usuarios"
    
    def get_permissions_count(self, obj):
        """Muestra la cantidad de permisos del grupo."""
        count = obj.permissions.count()
        return f"{count} permiso{'s' if count != 1 else ''}"
    get_permissions_count.short_description = "Permisos"
    
    fieldsets = (
        ('Información del Grupo', {
            'fields': ('name',),
            'description': 'Los grupos te permiten organizar usuarios y asignarles permisos de forma colectiva. Por ejemplo, puedes crear un grupo "Vendedores" con permisos para gestionar productos.'
        }),
        ('Permisos', {
            'fields': ('permissions',),
            'description': 'Selecciona los permisos que tendrán todos los usuarios de este grupo. Puedes buscar permisos por aplicación o modelo.'
        }),
    )


# Desregistrar el GroupAdmin por defecto y registrar el personalizado
admin.site.unregister(Group)
admin.site.register(Group, GrupoPersonalizadoAdmin)


@admin.register(Category)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Configuración de las categorías en el panel de administración.
    """

    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(Product)
class ProductoAdmin(admin.ModelAdmin):
    """
    Configuración de los productos en el panel de administración.
    """

    list_display = ("name", "category", "price", "stock", "is_active", "slug")
    list_filter = ("category", "is_active")
    search_fields = ("name", "description")
    readonly_fields = ("slug", "created_at", "updated_at")
    fieldsets = (
        ("Información básica", {
            "fields": ("name", "category", "slug", "description")
        }),
        ("Precio y Stock", {
            "fields": ("price", "stock", "is_active")
        }),
        ("Imagen", {
            "fields": ("image_url",)
        }),
        ("Fechas", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


class ItemPedidoInline(admin.TabularInline):
    """
    Permite visualizar y editar los items desde la vista de un pedido.
    """

    model = OrderItem
    extra = 0


@admin.register(Order)
class PedidoAdmin(admin.ModelAdmin):
    """
    Panel del administrador para gestionar pedidos.
    """

    list_display = ("id", "user", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email")
    inlines = [ItemPedidoInline]
