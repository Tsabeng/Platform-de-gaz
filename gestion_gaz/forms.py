from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from gestion_gaz.models import Client, TypeGaz, Depot
from django.core.exceptions import ValidationError

class FormulaireInscription(UserCreationForm):
    adresse = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), label="Adresse")
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
    nom_gaz = forms.CharField(
        max_length=50,
        required=False,
        label="Nom du gaz",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex. SCTM, Camgaz, Totalgaz',
            'aria-label': 'Nom du gaz'
        })
    )
    adresse = forms.CharField(
        max_length=300,
        required=False,
        label="Adresse",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex. Douala, Yaoundé, Simbock',
            'aria-label': 'Adresse'
        })
    )
class FormulaireMiseAJourStock(forms.Form):
    quantite = forms.IntegerField(label="Quantité à ajouter ou réduire", help_text="Utilisez un nombre positif pour ajouter, négatif pour réduire")
    est_disponible = forms.BooleanField(label="Disponible", required=False)


class FormulaireProfilDepot(forms.ModelForm):
    class Meta:
        model = Depot
        fields = ['nom', 'adresse', 'telephone', 'whatsapp', 'image']
        labels = {
            'nom': 'Nom du dépôt',
            'adresse': 'Adresse du dépôt',
            'telephone': 'Numéro de téléphone',
            'whatsapp': 'Numéro WhatsApp',
            'image': 'Image du dépôt',
        }
        help_texts = {
            'nom': 'Entrez le nom de votre dépôt (facultatif).',
            'adresse': 'Entrez l’adresse complète de votre dépôt (facultatif).',
            'telephone': 'Entrez un numéro de téléphone (facultatif).',
            'whatsapp': 'Entrez un numéro WhatsApp avec le code pays, ex: +237123456789 (facultatif).',
            'image': 'Uploadez une image de votre dépôt (PNG/JPEG, max 5 Mo, facultatif).',
        }
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if not image.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                raise ValidationError("Seuls les formats PNG et JPEG sont acceptés.")
            if image.size > 5 * 1024 * 1024:  # 5 Mo max
                raise ValidationError("L'image ne doit pas dépasser 5 Mo.")
        return image

    def clean_whatsapp(self):
        whatsapp = self.cleaned_data.get('whatsapp')
        if whatsapp and not whatsapp.startswith('+'):
            raise ValidationError("Le numéro WhatsApp doit commencer par '+' suivi du code pays.")
        return whatsapp