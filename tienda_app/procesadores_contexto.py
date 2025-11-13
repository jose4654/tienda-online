from __future__ import annotations

from typing import Any, Dict


def carrito(request) -> Dict[str, Any]:
    """
    Expone en todas las plantillas los datos principales del carrito
    almacenado en la sesión.
    """
    carrito = request.session.get("carrito", {})
    cantidad_total = sum(item.get("cantidad", 0) for item in carrito.values())
    monto_total = sum(item.get("cantidad", 0) * item.get("precio", 0) for item in carrito.values())
    return {
        "carrito_cantidad_total": cantidad_total,
        "carrito_monto_total": monto_total,
    }

