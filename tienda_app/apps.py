from django.apps import AppConfig


class TiendaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tienda_app'
    verbose_name = "Tienda"

    def ready(self):
        from . import signals  # noqa: F401