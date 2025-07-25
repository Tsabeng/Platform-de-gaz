# Generated by Django 3.1.1 on 2025-07-23 13:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Depot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('adresse', models.TextField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('telephone', models.CharField(blank=True, max_length=20, null=True)),
                ('whatsapp', models.CharField(blank=True, max_length=20, null=True)),
                ('image', models.ImageField(blank=True, help_text='Image du dépôt', null=True, upload_to='depots/images/')),
                ('proprietaire', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='depot', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TypeGaz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('quantite_stock', models.PositiveIntegerField(default=0)),
                ('est_disponible', models.BooleanField(default=True)),
                ('depot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='types_gaz', to='gestion_gaz.depot')),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adresse', models.TextField()),
                ('utilisateur', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
