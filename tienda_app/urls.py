from __future__ import annotations

from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "tienda_app"

urlpatterns = [
    path("", views.vista_inicio, name="home"),
    path("producto/<slug:slug>/", views.vista_detalle_producto, name="product_detail"),
    path("carrito/", views.ver_carrito, name="ver_carrito"),
    path("carrito/agregar/<slug:slug>/", views.agregar_al_carrito, name="agregar_al_carrito"),
    path("carrito/eliminar/<str:pk>/", views.eliminar_del_carrito, name="eliminar_del_carrito"),
    path("carrito/vaciar/", views.vaciar_carrito, name="vaciar_carrito"),
    path("checkout/", views.checkout, name="checkout"),
    path("pedido/<int:pk>/", views.detalle_pedido, name="detalle_pedido"),
    path("mis-pedidos/", views.mis_pedidos, name="mis_pedidos"),
    path("registro/", views.registrar_usuario, name="registro"),
    path("ingreso/", views.ingresar, name="ingreso"),
    path("salir/", LogoutView.as_view(next_page="tienda_app:home"), name="salir"),
    path(
        "pago/mercadopago/resultado/",
        views.mercadopago_resultado,
        name="mercadopago_resultado",
    ),
]

