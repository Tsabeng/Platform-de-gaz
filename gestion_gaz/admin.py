from django.contrib import admin

from .models import Depot,TypeGaz,Client

class DepotAdmin(admin.ModelAdmin):
    list_display=('nom','adresse','proprietaire')
admin.site.register(Depot,DepotAdmin)

class TypeGazAdmin(admin.ModelAdmin):
    list_display=('nom','depot','est_disponible')
admin.site.register(TypeGaz,TypeGazAdmin)

class ClientAdmin(admin.ModelAdmin):
    list_display=('utilisateur','adresse')
admin.site.register(Client,ClientAdmin)