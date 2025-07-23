from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import FormulaireInscription, FormulaireTypeGaz, FormulaireRechercheGaz, FormulaireMiseAJourStock
from .models import TypeGaz, Depot, Client
from django.db.models import Q

def accueil(request):
    depots_proches = []
    client_adresse = None

    if request.user.is_authenticated and hasattr(request.user, 'client'):
        client_adresse = request.user.client.adresse.lower()
        depots_proches = Depot.objects.filter(
            Q(adresse__icontains=client_adresse) |
            Q(adresse__icontains=client_adresse.split()[0])
        )[:3]

    return render(request, 'accueil.html', {
        'depots_proches': depots_proches,
        'client_adresse': client_adresse
    })

def inscription(request):
    if request.method == 'POST':
        formulaire = FormulaireInscription(request.POST, request.FILES)
        if formulaire.is_valid():
            utilisateur = formulaire.save(commit=False)
            role = request.POST.get('role')
            utilisateur.save()
            if role == 'client':
                Client.objects.create(
                    utilisateur=utilisateur,
                    adresse=formulaire.cleaned_data['adresse']
                )
            elif role == 'depot':
                Depot.objects.create(
                    proprietaire=utilisateur,
                    nom=formulaire.cleaned_data['nom_depot'],
                    adresse=formulaire.cleaned_data['adresse'],
                    telephone=formulaire.cleaned_data['telephone'],
                    whatsapp=formulaire.cleaned_data['whatsapp'],
                    image=formulaire.cleaned_data['image']
                )
            login(request, utilisateur)
            messages.success(request, "Inscription réussie !")
            return redirect('accueil')
    else:
        formulaire = FormulaireInscription()
    return render(request, 'inscription.html', {'formulaire': formulaire})

def check_depot_access(user):
    """Vérifie si l'utilisateur a un dépôt associé."""
    try:
        user.depot
        return True
    except AttributeError:
        return False

@login_required
def ajouter_type_gaz(request):
    if not check_depot_access(request.user):
        messages.error(request, "Seuls les propriétaires de dépôts peuvent ajouter des types de gaz.")
        return redirect('accueil')
    
    depot = request.user.depot
    if request.method == 'POST':
        form = FormulaireTypeGaz(request.POST)
        if form.is_valid():
            nom = form.cleaned_data['nom']
            quantite_stock = form.cleaned_data['quantite_stock']
            est_disponible = form.cleaned_data['est_disponible']
            
            existing_gaz = TypeGaz.objects.filter(nom=nom, depot=depot).first()
            if existing_gaz:
                messages.warning(request, f"Le type de gaz {nom} existe déjà. Veuillez mettre à jour le stock.")
                return redirect('modifier_stock', pk=existing_gaz.pk)
            else:
                type_gaz = form.save(commit=False)
                type_gaz.depot = depot
                type_gaz.save()
                messages.success(request, f"Le type de gaz {type_gaz.nom} a été ajouté avec succès !")
                return redirect('liste_types_gaz')
    else:
        form = FormulaireTypeGaz()
    return render(request, 'ajouter_type_gaz.html', {'form': form})

@login_required
def liste_types_gaz(request):
    if not check_depot_access(request.user):
        messages.error(request, "Seuls les propriétaires de dépôts peuvent voir la liste des types de gaz.")
        return redirect('accueil')
    types_gaz = TypeGaz.objects.filter(depot=request.user.depot)
    return render(request, 'liste_types_gaz.html', {'types_gaz': types_gaz})

@login_required
def supprimer_type_gaz(request, pk):
    if not check_depot_access(request.user):
        messages.error(request, "Seuls les propriétaires de dépôts peuvent supprimer des types de gaz.")
        return redirect('accueil')
    type_gaz = get_object_or_404(TypeGaz, pk=pk, depot=request.user.depot)
    if request.method == 'POST':
        type_gaz.delete()
        messages.success(request, "Type de gaz supprimé avec succès !")
        return redirect('liste_types_gaz')
    return render(request, 'confirmer_suppression.html', {'object': type_gaz})

@login_required
def modifier_stock(request, pk):
    if not check_depot_access(request.user):
        messages.error(request, "Seuls les propriétaires de dépôts peuvent modifier le stock.")
        return redirect('accueil')
    type_gaz = get_object_or_404(TypeGaz, pk=pk, depot=request.user.depot)
    if request.method == 'POST':
        form = FormulaireMiseAJourStock(request.POST)
        if form.is_valid():
            quantite = form.cleaned_data['quantite']
            nouvelle_quantite = type_gaz.quantite_stock + quantite
            if nouvelle_quantite < 0:
                form.add_error('quantite', 'La quantité en stock ne peut pas être négative.')
                return render(request, 'modifier_stock.html', {'form': form, 'type_gaz': type_gaz})
            type_gaz.quantite_stock = nouvelle_quantite
            type_gaz.est_disponible = form.cleaned_data['est_disponible']
            type_gaz.save()
            messages.success(request, "Stock mis à jour avec succès !")
            return redirect('liste_types_gaz')
    else:
        form = FormulaireMiseAJourStock(initial={'est_disponible': type_gaz.est_disponible})
    return render(request, 'modifier_stock.html', {'form': form, 'type_gaz': type_gaz})

def recherche_gaz(request):
    formulaire = FormulaireRechercheGaz(request.GET or None)
    resultats = []

    if formulaire.is_valid():
        nom_gaz = formulaire.cleaned_data['nom_gaz']
        adresse = formulaire.cleaned_data['adresse']
        resultats = TypeGaz.objects.filter(
            nom__icontains=nom_gaz,
            est_disponible=True,
            quantite_stock__gt=0
        )
        if adresse:
            resultats = resultats.filter(depot__adresse__icontains=adresse)
        
        if request.user.is_authenticated and hasattr(request.user, 'client'):
            client_adresse = request.user.client.adresse.lower()
            resultats_proches = resultats.filter(
                Q(depot__adresse__icontains=client_adresse) |
                Q(depot__adresse__icontains=client_adresse.split()[0])
            )
            resultats_autres = resultats.exclude(
                Q(depot__adresse__icontains=client_adresse) |
                Q(depot__adresse__icontains=client_adresse.split()[0])
            )
            resultats = list(resultats_proches) + list(resultats_autres)

    return render(request, 'recherche_gaz.html', {
        'formulaire': formulaire,
        'resultats': resultats
    })

def vitrine_depot(request, pk):
    depot = get_object_or_404(Depot, pk=pk)
    types_gaz = TypeGaz.objects.filter(depot=depot, est_disponible=True, quantite_stock__gt=0)
    return render(request, 'vitrine_depot.html', {
        'depot': depot,
        'types_gaz': types_gaz
    })

@login_required
def profil_depot(request):
    if not check_depot_access(request.user):
        messages.error(request, "Seuls les propriétaires de dépôts peuvent accéder à cette page.")
        return redirect('accueil')
    depot = request.user.depot
    if request.method == 'POST':
        form = FormulaireInscription(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            depot.nom = form.cleaned_data['nom_depot']
            depot.adresse = form.cleaned_data['adresse']
            depot.telephone = form.cleaned_data['telephone']
            depot.whatsapp = form.cleaned_data['whatsapp']
            if form.cleaned_data['image']:
                depot.image = form.cleaned_data['image']
            depot.save()
            messages.success(request, "Profil du dépôt mis à jour avec succès !")
            return redirect('profil_depot')
    else:
        form = FormulaireInscription(
            instance=request.user,
            initial={
                'nom_depot': depot.nom,
                'adresse': depot.adresse,
                'telephone': depot.telephone,
                'whatsapp': depot.whatsapp,
            }
        )
    return render(request, 'profil_depot.html', {'form': form, 'depot': depot})




from .forms import FormulaireProfilDepot
from django.contrib import messages

@login_required
def profil_depot(request):
    try:
        depot = request.user.depot
    except Depot.DoesNotExist:
        depot = None

    if request.method == 'POST':
        form = FormulaireProfilDepot(request.POST, request.FILES, instance=depot)
        if form.is_valid():
            if depot is None:
                depot = form.save(commit=False)
                depot.proprietaire = request.user
            else:
                # Mettre à jour uniquement les champs fournis
                for field in form.cleaned_data:
                    if form.cleaned_data[field] is not None and form.cleaned_data[field] != '':
                        setattr(depot, field, form.cleaned_data[field])
            depot.save()
            messages.success(request, "Profil du dépôt mis à jour avec succès.")
            return redirect('profil_depot')
        else:
            messages.error(request, "Erreur lors de la mise à jour du profil. Vérifiez les champs.")
    else:
        form = FormulaireProfilDepot(instance=depot)

    return render(request, 'profil_depot.html', {'form': form, 'depot': depot})