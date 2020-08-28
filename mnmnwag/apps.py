from django.apps import AppConfig


class MnmnwagConfig(AppConfig):
    name = 'mnmnwag'
    verbose_name = 'mahna mahna .net 3.0'

    def ready(self):
        import mnmnwag.signals  # noqa F401
