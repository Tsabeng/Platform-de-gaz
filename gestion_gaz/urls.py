from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('inscription/', views.inscription, name='inscription'),
    path('ajouter-type-gaz/', views.ajouter_type_gaz, name='ajouter_type_gaz'),
    path('types-gaz/', views.liste_types_gaz, name='liste_types_gaz'),
    path('recherche-gaz/', views.recherche_gaz, name='recherche_gaz'),
    path('supprimer-type-gaz/<int:pk>/', views.supprimer_type_gaz, name='supprimer_type_gaz'),
    path('depot/<int:pk>/', views.vitrine_depot, name='vitrine_depot'),
    path('modifier-stock/<int:pk>/', views.modifier_stock, name='modifier_stock'),
    path('profil-depot/', views.profil_depot, name='profil_depot'),
    path('contact/', views.contact, name='contact'),

]