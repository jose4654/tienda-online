"""Modelos principales de la tienda online con comentarios en español."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import DecimalField, F, Sum
from django.template.defaultfilters import slugify
from django.urls import reverse


class Category(models.Model):
    """
    Representa una categoría de productos para facilitar la navegación del catálogo.
    """

    name = models.CharField("Nombre", max_length=120, unique=True)
    slug = models.SlugField("Slug", max_length=140, unique=True, editable=False)
    description = models.TextField("Descripción", blank=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("tienda_app:home") + f"?categoria={self.slug}"


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Categoría",
    )
    name = models.CharField("Nombre", max_length=160)
    slug = models.SlugField("Slug", max_length=180, unique=True, editable=False)
    description = models.TextField("Descripción", blank=True)
    price = models.DecimalField("Precio", max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField("Stock", default=0)
    image_url = models.URLField("URL de imagen", blank=True)
    is_active = models.BooleanField("Está activo", default=True)
    created_at = models.DateTimeField("Creado el", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado el", auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self) -> bool:
        return self.stock > 0 and self.is_active

    def get_absolute_url(self):
        return reverse("tienda_app:product_detail", kwargs={"slug": self.slug})


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Usuario",
    )
    full_name = models.CharField("Nombre completo", max_length=180, blank=True)
    phone = models.CharField("Teléfono", max_length=50, blank=True)
    address = models.CharField("Dirección", max_length=250, blank=True)
    city = models.CharField("Ciudad", max_length=120, blank=True)
    postal_code = models.CharField("Código postal", max_length=20, blank=True)

    class Meta:
        verbose_name = "Perfil de cliente"
        verbose_name_plural = "Perfiles de clientes"

    def __str__(self) -> str:
        return f"Perfil de {self.user.get_username()}"


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pendiente"
    PROCESSING = "processing", "En preparación"
    SHIPPED = "shipped", "Enviado"
    COMPLETED = "completed", "Completado"
    CANCELLED = "cancelled", "Cancelado"


class Order(models.Model):
    """
    Encabezado de un pedido realizado por un cliente en la tienda.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Usuario",
    )
    created_at = models.DateTimeField("Creado el", auto_now_add=True)
    updated_at = models.DateTimeField("Actualizado el", auto_now=True)
    status = models.CharField(
        "Estado",
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )
    shipping_address = models.CharField("Dirección de envío", max_length=250, blank=True)
    observations = models.TextField("Observaciones", blank=True)
    payment_provider = models.CharField("Proveedor de pago", max_length=40, blank=True)
    payment_reference = models.CharField("Referencia de pago", max_length=120, blank=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Pedido #{self.pk} de {self.user.get_username()}"

    @property
    def total_items(self) -> int:
        return self.items.aggregate(total=Sum("quantity"))["total"] or 0

    @property
    def total_amount(self) -> Decimal:
        return (
            self.items.aggregate(
                total=Sum(
                    F("quantity") * F("price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )["total"]
            or Decimal("0.00")
        )


class OrderItem(models.Model):
    """
    Línea de producto dentro de un pedido, conserva cantidad y precio pagado.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Pedido",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="Producto",
    )
    quantity = models.PositiveIntegerField("Cantidad", default=1)
    price = models.DecimalField("Precio unitario", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Item de pedido"
        verbose_name_plural = "Items de pedido"

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"

    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.price
