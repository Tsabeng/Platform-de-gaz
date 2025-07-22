from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from gestion_gaz.models import Client, TypeGaz

class FormulaireInscription(UserCreationForm):
    adresse = forms.CharField(widget=forms.Textarea, label="Adresse")
    telephone = forms.CharField(max_length=20, required=False, label="Numéro de téléphone")
    whatsapp = forms.CharField(max_length=20, required=False, label="Numéro WhatsApp")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'adresse', 'telephone', 'whatsapp']

class FormulaireTypeGaz(forms.ModelForm):
    class Meta:
        model = TypeGaz
        fields = ['nom', 'est_disponible', 'quantite_stock']
        labels = {
            'nom': 'Nom du gaz',
            'est_disponible': 'Disponible',
            'quantite_stock': 'Quantité en stock',
        }

class FormulaireRechercheGaz(forms.Form):
    nom_gaz = forms.CharField(max_length=50, required=False, label="Nom du gaz")
    adresse = forms.CharField(widget=forms.Textarea, required=False, label="Adresse")

class FormulaireMiseAJourStock(forms.Form):
    quantite = forms.IntegerField(label="Quantité à ajouter ou réduire", help_text="Utilisez un nombre positif pour ajouter, négatif pour réduire")
    est_disponible = forms.BooleanField(label="Disponible", required=False)