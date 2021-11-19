from django.contrib import admin


class MnmnwagAdminSite(admin.AdminSite):
    enable_nav_sidebar = False
    index_title = 'HELLO SAILOR!'
    site_header = 'mahna mahna .net admin'
    site_title = 'mahnamahna.net admin'
