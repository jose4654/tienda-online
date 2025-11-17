from __future__ import annotations

from decimal import Decimal
from typing import Dict

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .formularios import (
    FormularioCheckout,
    FormularioIngreso,
    FormularioRegistroCliente,
)
from .models import Category, Order, OrderItem, OrderStatus, Product
from .services import (
    MercadoPagoError,
    crear_preferencia_para_pedido,
    enviar_notificacion_telegram,
    obtener_pago,
)


def _obtener_carrito(request: HttpRequest) -> Dict[str, Dict[str, Decimal]]:
    """
    Recupera el carrito de compras guardado en la sesión del usuario.
    Si no existe, inicializa una estructura vacía.
    """
    if "carrito" not in request.session:
        request.session["carrito"] = {}
    return request.session["carrito"]


def vista_inicio(request: HttpRequest) -> HttpResponse:
    """
    Página principal de la tienda. Permite filtrar por categoría y por texto.
    """
    categorias = Category.objects.all()
    productos = Product.objects.filter(is_active=True)

    categoria_slug = request.GET.get("categoria")
    if categoria_slug:
        productos = productos.filter(category__slug=categoria_slug)

    busqueda = request.GET.get("buscar")
    if busqueda:
        productos = productos.filter(
            Q(name__icontains=busqueda) | Q(description__icontains=busqueda)
        )

    contexto = {
        "categorias": categorias,
        "productos": productos,
        "categoria_actual": categoria_slug,
        "termino_busqueda": busqueda or "",
    }
    return render(request, "tienda_app/inicio.html", contexto)


def vista_detalle_producto(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Muestra el detalle de un producto específico para facilitar la compra.
    """
    producto = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "tienda_app/detalle_producto.html", {"producto": producto})


@login_required
def agregar_al_carrito(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Agrega un producto al carrito. El stock es validado antes de sumar.
    """
    producto = get_object_or_404(Product, slug=slug, is_active=True)
    cantidad = int(request.POST.get("cantidad", 1))

    if cantidad < 1:
        messages.error(request, "La cantidad debe ser al menos 1.")
        return redirect(producto.get_absolute_url())

    if cantidad > producto.stock:
        messages.error(request, "No hay stock suficiente para la cantidad solicitada.")
        return redirect(producto.get_absolute_url())

    carrito = _obtener_carrito(request)
    clave = str(producto.pk)

    item_actual = carrito.get(clave, {"cantidad": 0})
    nueva_cantidad = item_actual["cantidad"] + cantidad

    if nueva_cantidad > producto.stock:
        messages.error(request, "Ya tienes la cantidad máxima disponible en el carrito.")
        return redirect(producto.get_absolute_url())

    carrito[clave] = {
        "nombre": producto.name,
        "precio": float(producto.price),
        "cantidad": nueva_cantidad,
        "imagen": producto.image_url,
        "slug": producto.slug,
    }
    request.session.modified = True
    messages.success(request, f"{producto.name} se agregó al carrito.")
    
    # Si viene el parámetro seguir_comprando, redirigir a la página principal
    if request.GET.get("seguir_comprando") == "1":
        return redirect("tienda_app:home")
    
    return redirect("tienda_app:ver_carrito")


@login_required
def ver_carrito(request: HttpRequest) -> HttpResponse:
    """
    Visualiza el estado actual del carrito en la sesión.
    """
    carrito = _obtener_carrito(request)
    productos = []
    total = Decimal("0.00")

    for pk, datos in carrito.items():
        subtotal = Decimal(datos["precio"]) * datos["cantidad"]
        total += subtotal
        productos.append(
            {
                "pk": pk,
                "nombre": datos["nombre"],
                "precio": Decimal(datos["precio"]),
                "cantidad": datos["cantidad"],
                "imagen": datos["imagen"],
                "subtotal": subtotal,
                "slug": datos["slug"],
            }
        )

    return render(
        request,
        "tienda_app/carrito.html",
        {"items_carrito": productos, "total": total},
    )


@login_required
def eliminar_del_carrito(request: HttpRequest, pk: str) -> HttpResponse:
    """
    Elimina un producto del carrito.
    """
    carrito = _obtener_carrito(request)
    if pk in carrito:
        producto = carrito.pop(pk)
        request.session.modified = True
        messages.info(request, f"{producto['nombre']} fue retirado del carrito.")
    return redirect("tienda_app:ver_carrito")


@login_required
def vaciar_carrito(request: HttpRequest) -> HttpResponse:
    """
    Vacía el carrito por completo.
    """
    request.session["carrito"] = {}
    request.session.modified = True
    messages.info(request, "Se vació el carrito.")
    return redirect("tienda_app:ver_carrito")


@login_required
@transaction.atomic
def checkout(request: HttpRequest) -> HttpResponse:
    """
    Procesa la compra generando un pedido en base a los productos del carrito.
    """
    carrito = _obtener_carrito(request)
    if not carrito:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect("tienda_app:home")

    if request.method == "POST":
        formulario = FormularioCheckout(request.POST)
        if formulario.is_valid():
            pedido: Order = formulario.save(commit=False)
            pedido.user = request.user
            pedido.status = OrderStatus.PENDING
            pedido.save()

            for pk, datos in carrito.items():
                producto = get_object_or_404(Product, pk=pk)
                if datos["cantidad"] > producto.stock:
                    messages.error(
                        request,
                        f"No hay stock suficiente de {producto.name}. Ajustá tu carrito.",
                    )
                    transaction.set_rollback(True)
                    return redirect("tienda_app:ver_carrito")
                producto.stock -= datos["cantidad"]
                producto.save()
                OrderItem.objects.create(
                    order=pedido,
                    product=producto,
                    quantity=datos["cantidad"],
                    price=producto.price,
                )

            try:
                preference = crear_preferencia_para_pedido(pedido, request)
                init_point = preference.get("init_point") or preference.get("sandbox_init_point")
                if not init_point:
                    raise MercadoPagoError("Mercado Pago no devolvió una URL válida para continuar con el pago.")
            except MercadoPagoError as exc:
                transaction.set_rollback(True)
                messages.error(
                    request,
                    f"No pudimos iniciar el pago con Mercado Pago. {exc}",
                )
                return redirect("tienda_app:ver_carrito")

            pedido.payment_provider = "mercadopago"
            pedido.payment_reference = preference.get("id", "")
            pedido.save(update_fields=["payment_provider", "payment_reference"])

            # Enviar notificación a Telegram
            try:
                enviar_notificacion_telegram(pedido)
            except Exception:
                # No fallar el checkout si falla la notificación
                pass

            request.session["carrito"] = {}
            request.session.modified = True
            messages.info(request, "Te redirigimos a Mercado Pago para completar el pago.")
            return redirect(init_point)
    else:
        formulario = FormularioCheckout()

    total = sum(Decimal(item["precio"]) * item["cantidad"] for item in carrito.values())
    return render(
        request,
        "tienda_app/checkout.html",
        {"formulario": formulario, "total": total},
    )


@login_required
def detalle_pedido(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Muestra el detalle de un pedido específico del usuario autenticado.
    """
    pedido = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, "tienda_app/detalle_pedido.html", {"pedido": pedido})


@login_required
def mis_pedidos(request: HttpRequest) -> HttpResponse:
    """
    Muestra todos los pedidos del usuario autenticado.
    """

    pedidos = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
    return render(request, "tienda_app/mis_pedidos.html", {"pedidos": pedidos})


@login_required
def mercadopago_resultado(request: HttpRequest) -> HttpResponse:
    """
    Procesa el retorno desde Mercado Pago y actualiza el estado del pedido según el resultado.
    """

    external_reference = request.GET.get("external_reference")
    if not external_reference:
        messages.error(request, "No se recibió la referencia del pedido.")
        return redirect("tienda_app:home")

    try:
        pedido_id = int(external_reference)
    except (TypeError, ValueError):
        messages.error(request, "Referencia de pedido inválida.")
        return redirect("tienda_app:home")

    pedido = get_object_or_404(Order, pk=pedido_id, user=request.user)
    payment_id = request.GET.get("payment_id")
    estado_reportado = request.GET.get("status") or request.GET.get("collection_status")

    try:
        pago = obtener_pago(payment_id)
    except MercadoPagoError:
        pago = None

    estado = (pago or {}).get("status") or estado_reportado

    if estado == "approved":
        pedido.status = OrderStatus.COMPLETED
        mensaje = "¡Pago aprobado! Tu pedido quedó confirmado."
        nivel = messages.SUCCESS
    elif estado in {"pending", "in_process"}:
        pedido.status = OrderStatus.PENDING
        mensaje = "El pago quedó pendiente. Te avisaremos cuando se acredite."
        nivel = messages.INFO
    else:
        pedido.status = OrderStatus.CANCELLED
        mensaje = "El pago fue cancelado o rechazado. Intentalo nuevamente."
        nivel = messages.WARNING

    pedido.save(update_fields=["status"])
    messages.add_message(request, nivel, mensaje)
    return redirect("tienda_app:detalle_pedido", pk=pedido.pk)


def registrar_usuario(request: HttpRequest) -> HttpResponse:
    """
    Permite crear un usuario de tipo cliente y acceder de inmediato.
    """
    if request.user.is_authenticated:
        return redirect("tienda_app:home")

    if request.method == "POST":
        formulario = FormularioRegistroCliente(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            login(request, usuario)
            messages.success(request, "Registro completado. ¡Bienvenido!")
            return redirect("tienda_app:home")
    else:
        formulario = FormularioRegistroCliente()

    return render(request, "tienda_app/registro.html", {"formulario": formulario})


def ingresar(request: HttpRequest) -> HttpResponse:
    """
    Permite ingresar al sitio tanto a clientes como al personal.
    """
    if request.user.is_authenticated:
        return redirect("tienda_app:home")

    formulario: AuthenticationForm = FormularioIngreso(request, data=request.POST or None)
    if request.method == "POST" and formulario.is_valid():
        usuario = formulario.get_user()
        login(request, usuario)
        messages.success(request, f"Hola {usuario.get_username()}, sesión iniciada.")
        return redirect(request.GET.get("next") or "tienda_app:home")

    return render(request, "tienda_app/ingreso.html", {"formulario": formulario})


