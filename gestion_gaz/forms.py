from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from gestion_gaz.models import Client, TypeGaz, Depot

class FormulaireInscription(UserCreationForm):
    adresse = forms.CharField(widget=forms.Textarea, label="Adresse")
    telephone = forms.CharField(max_length=20, required=False, label="Numéro de téléphone")
    whatsapp = forms.CharField(max_length=20, required=False, label="Numéro WhatsApp")
    nom_depot = forms.CharField(max_length=100, required=False, label="Nom du dépôt (pour les propriétaires)")
    image = forms.ImageField(required=False, label="Image du dépôt")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'adresse', 'telephone', 'whatsapp', 'nom_depot', 'image']

    def clean(self):
        cleaned_data = super().clean()
        role = self.data.get('role')
        nom_depot = cleaned_data.get('nom_depot')

        if role == 'depot' and not nom_depot:
            self.add_error('nom_depot', 'Le nom du dépôt est requis pour les propriétaires.')
        return cleaned_data

class FormulaireTypeGaz(forms.ModelForm):
    class Meta:
        model = TypeGaz
        fields = ['nom', 'est_disponible', 'quantite_stock']
        labels = {
            'nom': 'Nom du gaz',
            'est_disponible': 'Disponible',
            'quantite_stock': 'Quantité en stock',
        }

    def clean(self):
        cleaned_data = super().clean()
        nom = cleaned_data.get('nom')
        depot = self.instance.depot if self.instance.pk else None

        if depot and nom:
            existing_gaz = TypeGaz.objects.filter(nom=nom, depot=depot).exclude(pk=self.instance.pk)
            if existing_gaz.exists():
                self.add_error('nom', 'Ce type de gaz existe déjà dans ce dépôt. Veuillez mettre à jour le stock existant via la page de gestion du stock.')
        return cleaned_data

class FormulaireRechercheGaz(forms.Form):
    nom_gaz = forms.CharField(max_length=50, required=False, label="Nom du gaz")
    adresse = forms.CharField(widget=forms.Textarea, required=False, label="Adresse")

class FormulaireMiseAJourStock(forms.Form):
    quantite = forms.IntegerField(label="Quantité à ajouter ou réduire", help_text="Utilisez un nombre positif pour ajouter, négatif pour réduire")
    est_disponible = forms.BooleanField(label="Disponible", required=False)