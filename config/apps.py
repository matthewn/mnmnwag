from django.contrib.admin.apps import AdminConfig


class MnmnwagAdminConfig(AdminConfig):
    default_site = 'config.admin.MnmnwagAdminSite'
