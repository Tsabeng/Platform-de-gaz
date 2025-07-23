from django.db import models
from django.contrib.auth.models import User

class Depot(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.TextField()
    proprietaire = models.OneToOneField(User, on_delete=models.CASCADE, related_name='depot')
    date_creation = models.DateTimeField(auto_now_add=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to='depots/images/', blank=True, null=True, help_text="Image du dépôt")

    def __str__(self):
        return self.nom

class Client(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE)
    adresse = models.TextField()

    def __str__(self):
        return f"Client: {self.utilisateur.username}"

class TypeGaz(models.Model):
    TYPE_GAZ_CHOICES = [
        ('TradexGaz', 'TradexGaz'),
        ('GPL', 'GPL'),
        ('SCTM', 'SCTM'),
        ('TotalEnergies', 'TotalEnergies'),
        ('Afriquia Gaz', 'Afriquia Gaz'),
        ('Camgaz', 'Camgaz'),
        ('GlocalGaz', 'GlocalGaz'),
        ('Gaz du Cameroun', 'Gaz du Cameroun (GDC)'),
        ('MRS Cameroon', 'MRS Cameroon'),
        ('BOCOM Petroleum', 'BOCOM Petroleum'),
    ]
    nom = models.CharField(max_length=50, choices=TYPE_GAZ_CHOICES)
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE, related_name='types_gaz')
    quantite_stock = models.PositiveIntegerField(default=0)
    est_disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nom} - {self.depot.nom}"