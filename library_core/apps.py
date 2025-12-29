from django.apps import AppConfig

class LibraryCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library_core'

    def ready(self):
        import library_core.signals
