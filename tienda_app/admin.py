from django.contrib import admin

from .models import Category, Order, OrderItem, Product

admin.site.site_header = "Administración de MiTienda"
admin.site.site_title = "MiTienda"
admin.site.index_title = "Panel de control"


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
