from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import FormulaireInscription, FormulaireTypeGaz, FormulaireRechercheGaz, FormulaireMiseAJourStock
from .models import TypeGaz, Depot, Client

def accueil(request):
    return render(request, 'accueil.html')

def inscription(request):
    if request.method == 'POST':
        formulaire = FormulaireInscription(request.POST)
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
                    nom=request.POST.get('nom_depot', utilisateur.username + ' Depot'),
                    adresse=formulaire.cleaned_data['adresse'],
                    telephone=formulaire.cleaned_data['telephone'],
                    whatsapp=formulaire.cleaned_data['whatsapp']
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
            
            # Vérifier si le type de gaz existe déjà dans le dépôt
            existing_gaz = TypeGaz.objects.filter(nom=nom, depot=depot).first()
            if existing_gaz:
                # Rediriger vers la mise à jour du stock
                messages.warning(request, f"Le type de gaz {nom} existe déjà. Veuillez mettre à jour le stock.")
                return redirect('modifier_stock', pk=existing_gaz.pk)
            else:
                # Créer un nouveau type de gaz
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
    return render(request, 'recherche_gaz.html', {'formulaire': formulaire, 'resultats': resultats})

def vitrine_depot(request, pk):
    depot = get_object_or_404(Depot, pk=pk)
    types_gaz = TypeGaz.objects.filter(depot=depot, est_disponible=True, quantite_stock__gt=0)
    return render(request, 'vitrine_depot.html', {'depot': depot, 'types_gaz': types_gaz})