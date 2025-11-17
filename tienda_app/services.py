from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import mercadopago
import requests
from django.conf import settings
from django.urls import reverse

from .models import Order

logger = logging.getLogger(__name__)


class MercadoPagoError(Exception):
    """Errores de integración con Mercado Pago."""


def _get_sdk() -> mercadopago.SDK:
    access_token = getattr(settings, "MERCADOPAGO_ACCESS_TOKEN", "")
    if not access_token:
        raise MercadoPagoError("No hay un Access Token configurado para Mercado Pago.")
    return mercadopago.SDK(access_token)


def _build_callback_url(request) -> str:
    explicit = getattr(settings, "MERCADOPAGO_SUCCESS_URL", "") or ""
    if explicit:
        return explicit
    return request.build_absolute_uri(reverse("tienda_app:mercadopago_resultado"))


def crear_preferencia_para_pedido(pedido: Order, request) -> Dict[str, Any]:
    """
    Genera una preferencia de pago para un pedido y devuelve la respuesta cruda del SDK.
    """

    items = []
    for item in pedido.items.select_related("product"):
        items.append(
            {
                "id": str(item.pk),
                "title": item.product.name,
                "quantity": int(item.quantity),
                "currency_id": getattr(settings, "MERCADOPAGO_CURRENCY_ID", "ARS"),
                "unit_price": float(item.price),
            }
        )

    callback_url = _build_callback_url(request)
    parsed = urlparse(callback_url)
    back_urls = {
        "success": callback_url,
        "pending": callback_url,
        "failure": callback_url,
    }
    use_auto_return = parsed.scheme == "https"
    if not use_auto_return:
        logger.warning(
            "Mercado Pago auto_return deshabilitado porque la URL de retorno no es HTTPS (%s)",
            callback_url,
        )

    sdk = _get_sdk()
    preference_data: Dict[str, Any] = {
        "items": items,
        "external_reference": str(pedido.pk),
        "payer": {
            "name": request.user.first_name,
            "surname": request.user.last_name,
            "email": request.user.email or "comprador@example.com",
        },
        "back_urls": back_urls,
        "metadata": {"order_id": pedido.pk},
    }
    if use_auto_return:
        preference_data["auto_return"] = "approved"
    notification_url = getattr(settings, "MERCADOPAGO_NOTIFICATION_URL", "")
    if notification_url:
        preference_data["notification_url"] = notification_url
    response = sdk.preference().create(preference_data)
    if response.get("status") not in (200, 201):
        details = response.get("response") or {}
        raise MercadoPagoError(
            f"Mercado Pago devolvió un estado inesperado al crear la preferencia: {details}"
        )
    return response["response"]


def obtener_pago(payment_id: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Recupera los detalles de un pago usando el ID entregado por Mercado Pago.
    """

    if not payment_id:
        return None

    sdk = _get_sdk()
    response = sdk.payment().get(payment_id)
    if response.get("status") != 200:
        raise MercadoPagoError("No se pudo consultar el pago en Mercado Pago.")
    return response["response"]


def enviar_notificacion_telegram(pedido: Order) -> bool:
    """
    Envía una notificación a Telegram con los datos del pedido y comprador.
    Retorna True si se envió exitosamente, False en caso contrario.
    """
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    chat_id = getattr(settings, "TELEGRAM_CHAT_ID", "")

    if not token or not chat_id:
        logger.warning("Telegram no configurado: falta token o chat_id")
        return False

    try:
        # Obtener datos del usuario y perfil
        usuario = pedido.user
        perfil = getattr(usuario, "profile", None)

        # Construir mensaje
        mensaje = f"🛒 *NUEVO PEDIDO* 🛒\n\n"
        mensaje += f"📦 *Pedido #{pedido.pk}*\n"
        mensaje += f"📅 Fecha: {pedido.created_at.strftime('%d/%m/%Y %H:%M')}\n"
        mensaje += f"📊 Estado: {pedido.get_status_display()}\n\n"

        mensaje += f"👤 *DATOS DEL COMPRADOR*\n"
        mensaje += f"Nombre: {usuario.get_full_name() or usuario.get_username()}\n"
        mensaje += f"Usuario: {usuario.get_username()}\n"
        mensaje += f"Email: {usuario.email or 'No proporcionado'}\n"
        if perfil:
            if perfil.phone:
                mensaje += f"Teléfono: {perfil.phone}\n"
            if perfil.address:
                mensaje += f"Dirección: {perfil.address}\n"
            if perfil.city:
                mensaje += f"Ciudad: {perfil.city}\n"
        if pedido.shipping_address:
            mensaje += f"Dirección de envío: {pedido.shipping_address}\n"
        mensaje += "\n"

        mensaje += f"🛍️ *PRODUCTOS*\n"
        total = pedido.total_amount
        for item in pedido.items.select_related("product"):
            subtotal = item.subtotal
            mensaje += f"• {item.product.name}\n"
            mensaje += f"  Cantidad: {item.quantity} x ${item.price:.2f} = ${subtotal:.2f}\n"
        mensaje += f"\n💰 *TOTAL: ${total:.2f}*\n"

        if pedido.payment_provider:
            mensaje += f"\n💳 Método de pago: {pedido.payment_provider.upper()}\n"
        if pedido.payment_reference:
            mensaje += f"🔗 Referencia: {pedido.payment_reference}\n"
        if pedido.observations:
            mensaje += f"\n📝 Observaciones: {pedido.observations}\n"

        # Enviar mensaje a Telegram
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": mensaje,
            "parse_mode": "Markdown",
        }

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Notificación de Telegram enviada para pedido #{pedido.pk}")
        return True

    except requests.RequestException as e:
        logger.error(f"Error al enviar notificación a Telegram: {e}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Error inesperado al notificar a Telegram: {e}", exc_info=True)
        return False

