from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from django.urls import reverse
from django.db.models import Sum
from datetime import datetime
import pytz
import secrets
import string

# Authentification
def connexion(request):
    request.session.flush()
    
    if request.method == "POST":
        pseudo = request.POST.get("pseudo")
        mdp = request.POST.get("mdp")
        
        # Utilisation de Django ORM pour récupérer l'utilisateur correspondant
        try:
            us = Utilisateurs.objects.get(pseudo=pseudo, mdp=mdp)
        except Utilisateurs.DoesNotExist:
            return render(request, 'Authentification/connexion.html', {'error_message': "Nom ou mot de passe incorrect.", 'pseudo':pseudo})
        
        role = us.role  # Récupérer le rôle de l'utilisateur à partir du modèle Utilisateur
        
        # Création de la session pour l'utilisateur connecté
        
        if role == 'Admin':
            request.session['admin_id'] = us.id
            return redirect('adminIndex')
        elif role == 'Comptable':
            request.session['comptable_id'] = us.id
            return redirect('comptableindex')
    
    return render(request, 'Authentification/connexion.html')

def inscription(request):
    if not request.session.get('access'):
        # Rediriger vers une autre vue ou afficher un message d'erreur
        return redirect('code')  # Rediriger vers la vue de saisie du code
    
    if request.method == "POST":     
        pseudo = request.POST.get('pseudo')
        mdp = request.POST.get('mdp')
        mdp2 = request.POST.get('mdp2')
        contact = request.POST.get('contact')
        
        # Vérification que les mots de passe correspondent
        if mdp != mdp2 or str(mdp).isspace():
            return render(request, 'Authentification/inscription.html', {'error_message': "Les mots de passe ne correspondent pas.", 'pseudo':pseudo, 'contact':contact})
        
        if (str(pseudo).isidentifier() == False):
            return render(request, 'Authentification/inscription.html', {'error_message': "On ne peut pas avoir un pseudo invalid", 'pseudo':pseudo, 'contact':contact}) 
        # Vérification si le pseudo est déjà utilisé
        
        # # Vérification si le pseudo contient des caractères spéciaux
        # if any(not c.isalnum() for c in pseudo):
        #     return render(request, 'Authentification/verification.html', {'error_message': "Le pseudo ne peut pas contenir de caractères spéciaux.", 'code_v':code_v, 'pseudo':pseudo, 'contact':contact})
        
        if Utilisateurs.objects.filter(pseudo=pseudo).exists():
            return render(request, 'Authentification/inscription.html', {'error_message': "Ce nom est déjà utilisé."})
        
        # Pas d'erreur
        utilisateurs = Utilisateurs(pseudo=pseudo, mdp=mdp, contact=contact, role='Comptable')
        utilisateurs.save()
        
        # Création de la session pour l'utilisateur nouvellement inscrit
        request.session['comptable_id'] = utilisateurs.id
        
        return redirect('comptableindex')
    
    return render(request, 'Authentification/inscription.html')

def generer_random_code(length=10):
    characters = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def code(request):
    if request.method == "POST":
        code_v = Code_valid_comptable.objects.get(pk=1)
        verife = request.POST.get('verife')
        
        # Vérification que les mots de passe correspondent
        if verife != code_v.code:
            return render(request, 'Authentification/code.html', {'message': "Le code de verification est incorrect"})
        else:
            # Création de la session
            request.session['access'] = True
            
            # Changement code
            code_v = Code_valid_comptable.objects.get(pk=1)
            # Générer un code aléatoire
            code_v.code = generer_random_code()
            code_v.save()
            
            return redirect('inscription')
    return render(request, 'Authentification/code.html')

def deconnexion(request):
    # Supprimer toutes les données de session
    request.session.flush()
    # Rediriger l'utilisateur vers la page de connexion ou toute autre page appropriée
    return redirect('connexion')

# Administrateur
def adminparametre(request):
    try:   
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            # Faites page d'erreur au comptable
            return redirect("compta404")
    
        else:
            # Obtenir l'année prochaine
            next_year = datetime.now().year + 1
            
            # Obtenir l'année en cours
            current_year = datetime.now().year

            # Filtrer les instances de Valeur_budget de l'année en cours
            budgets_this_year = Valeur_budget.objects.filter(date_budget__year=current_year)

            # Si vous voulez récupérer les montants des budgets, vous pouvez par exemple additionner les valeurs:
            total_initial_budget = sum(budget.budget_initial for budget in budgets_this_year)
            
            depenser = total_initial_budget * 2
            economiser = total_initial_budget * 1
            limiter = total_initial_budget / 1.2
            
            depenser = f"{depenser:.2f}"
            economiser = f"{economiser:.2f}"
            limiter = f"{limiter:.2f}"
            
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
            
            solde = total_montant - total_depense
        
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        return redirect("page404")
    return render(request, 'Administrateur/adminparametre.html', {'current_year':current_year, 'depenser':depenser, 'economiser':economiser, 'limiter':limiter, 'budget': budget, 'total_montant': total_montant, 'total_depense': total_depense, 'next_year':next_year, 'solde':solde} )

def adminIndex(request):
    try:   
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            # Faites page d'erreur au comptable
            return redirect("compta404")
    
        else:
            utilisateur = Utilisateurs.objects.get(id=1)
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
            
            solde = total_montant - total_depense
            
            code_valid = Code_valid_comptable.objects.all()
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        return redirect("page404")
    return render(request, 'Administrateur/adminindex.html', {'users':users, 'solde':solde, 'budget': budget, 'total_montant': total_montant, 'total_depense': total_depense, 'code_valid': code_valid, 'utilisateur':utilisateur} )

def modifieradmin(request):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else: 
            admin_info = Utilisateurs.objects.get(pk=1) 
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
                
            solde = total_montant - total_depense
            
            if request.method == "POST":
                pseudo = request.POST.get('pseudo')
                mdp = request.POST.get('mdp')
                mdp1 = request.POST.get('mdp1')
                contact = request.POST.get('contact')
                
                 # Vérification que les mots de passe correspondent
                if mdp != mdp1 or str(mdp).isspace():
                    return render(request, 'Administrateur/modifieradmin.html', {'total_montant': total_montant, 'total_depense': total_depense, 'solde':solde, 'admin_info':admin_info , 'pseudo':pseudo, 'mdp':mdp, 'contact':contact, 'error_message':'le mot de passe est invalid'})
                
                if (str(pseudo).isidentifier() == False):
                    return render(request, 'Administrateur/modifieradmin.html', {'total_montant': total_montant, 'total_depense': total_depense, 'solde':solde, 'admin_info':admin_info , 'pseudo':pseudo, 'mdp':mdp, 'contact':contact, 'error_message':'le pseudo est invalid'})
                
                admin_modifier = Utilisateurs.objects.get(pk=1)
                admin_modifier.pseudo = pseudo
                admin_modifier.mdp = mdp
                admin_modifier.contact = contact
                
                admin_modifier.save()
                return redirect('adminIndex')
            
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, page erreur
        return redirect("page404")
    return render(request, 'Administrateur/modifieradmin.html', {'total_montant': total_montant, 'total_depense': total_depense, 'solde':solde, 'admin_info':admin_info })

def modifiercode(request):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")

        else: 
            if request.method == "POST":     
                verifec = request.POST.get('verifec')
                code_modifier = Code_valid_comptable.objects.get(pk=1)
                code_modifier.code = verifec
                code_modifier.save()
                return redirect('adminIndex')
            code_modifie = Code_valid_comptable.objects.get(pk=1)
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
                
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/modifiercode.html', {'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde, 'code_modifie':code_modifie})

def ajouterbudget(request):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else:
            if request.method == "POST":
                budget_initial = request.POST.get('budget_initial')
                
                # Obtenir le fuseau horaire de Madagascar
                fuseau_horaire_madagascar = pytz.timezone('Indian/Antananarivo')
        
                # Obtenir la date et l'heure actuelles dans le fuseau horaire de Madagascar
                date_budget = datetime.now(fuseau_horaire_madagascar)
                
                # Obtenir l'heure actuelle dans le fuseau horaire de Madagascar
                time_budget = date_budget.time()
                
                # Vérifier si le budget initial est supérieur à zéro
                if float(budget_initial) <= 0:
                    messages.add_message(request, messages.SUCCESS, "le budget initial doit etre superieur à zéro")
                    # Si le budget initial est inférieur ou égal à zéro, afficher un message d'erreur ou prendre une action appropriée
                    return redirect('ajouterbudget')
                else:
                    insert = Valeur_budget(budget_initial=budget_initial, date_budget=date_budget, time=time_budget)
                    insert.save()       
                    return redirect('adminIndex')
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
                
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        return redirect("page404")
    return render(request, 'Administrateur/ajouterbudget.html', {'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde})

def modiferbudget(request, id):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else:
            budget_modifier = Valeur_budget.objects.get(pk=id)
            if request.method == "POST":  
                budget_initial = request.POST.get('budget_initial')
                
                 # Vérifier si le budget initial est supérieur à zéro
                if float(budget_initial) <= 0:
                    messages.add_message(request, messages.SUCCESS, "le budget initial doit etre superieur à zéro")
                    # Si le budget initial est inférieur ou égal à zéro, afficher un message d'erreur ou prendre une action appropriée
                    return redirect(reverse('modiferbudget', args=[id]))
                # elif float(budget_initial) < budget_modifier.budget_initial:
                #     messages.add_message(request, messages.SUCCESS, "Le nouveau budget initial ne peut pas être inférieur à l'ancien")
                #     return redirect(reverse('modifebudget', args=[id]))
                else:
                    budget_modifier.budget_initial = budget_initial
                    budget_modifier.save()
                    return redirect('adminIndex')
                
            budget1 = Valeur_budget.objects.get(pk=id)
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']   
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
                
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        return redirect("page404")
    return render(request, 'Administrateur/modiferbudget.html', {'budget':budget, 'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde, 'budget1':budget1})

# Supprimer budget
def supprimer_budget(request, id):
    if 'comptable_id' in request.session:
        # Accéder à la valeur de la clé 'comptable_id'
        comptable_id = request.session['comptable_id']
        return redirect("page404")
    # Faites ce que vous devez faire avec comptable_id
    else:
        if request.method == 'POST':
            budget = Valeur_budget.objects.get(pk=id)
            budget.delete()
        
    return redirect('adminIndex')

def adminutilisateur(request):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else:        
            utilisateurs = Utilisateurs.objects.exclude(id=1).all()
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
            
            solde = total_montant - total_depense
            
            # Ajouter une pagination à utilisateurs
            paginator = Paginator(utilisateurs, 10)  # 2 éléments par page
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        return redirect("page404")
    return render(request, 'Administrateur/adminutilisateur.html', {'page_obj': page_obj,'utilisateurs':utilisateurs, 'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde})

def modifierutilisateur(request, id):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else: 
            if request.method == "POST":     
                pseudo = request.POST.get('pseudo')
                contact = request.POST.get('contact')
                mdp = request.POST.get('mdp')
                
                if str(pseudo).isspace():
                    messages.error(request, "Le pseudo est invalid.")
                    return redirect(reverse('modifierutilisateur', args=[id]))
                if any(not c.isalnum() for c in pseudo):
                    messages.error(request, "Le pseudo ne doit contenir que des caractères alphanumériques.")
                    return redirect(reverse('modifierutilisateur', args=[id]))
                user_modifier = Utilisateurs.objects.get(pk=id)
                user_modifier.pseudo = pseudo
                user_modifier.contact = contact
                user_modifier.mdp = mdp
                user_modifier.save()
                return redirect('adminutilisateur')
            utilisateur = Utilisateurs.objects.get(pk=id)
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
                
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/modifierutilisateur.html', {'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde, 'utilisateur':utilisateur})

def adminsuivi(request):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else:        
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all().order_by('-id')
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
            
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
    # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/adminsuivi.html', {'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde, 'depense':depense})

def depenseinfo(request, id):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else:     
            depense1 = Depense_budget.objects.get(pk=id)    
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all().order_by('-id')
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
            
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/depenseinfo.html', {'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde, 'depense':depense, 'depense1':depense1})

def modifierdepense(request, id):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else: 
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            depense1 = Depense_budget.objects.get(pk=id)
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            solde = total_montant - total_depense
            
            if request.method == "POST":     
                rubrique = request.POST.get('rubrique')
                ligne = request.POST.get('ligne')
                montant = request.POST.get('montant')
                
                # Vérifier si le budget initial est supérieur à zéro
                if float(montant) <= 0:
                    # Si le budget initial est inférieur ou égal à zéro, afficher un message d'erreur ou prendre une action appropriée
                    return HttpResponseForbidden("Le montant ne peut pas inferieur a egal 0")

                # Vérifier si total_depense est nul
                if total_montant is None:
                    total_montant = 0
                if total_depense is None:
                    total_depense = 0
                    
                # Calculer le nouveau solde après l'insertion de la dépense
                nouveau_solde = solde - int(montant)
                        
                # Vérifier si le nouveau solde est négatif
                if nouveau_solde >= 0:
                    # Créer et enregistrer l'objet de dépense uniquement si le solde n'est pas négatif
                    dep_modifier = Depense_budget.objects.get(pk=id)
                    dep_modifier.rubrique = rubrique
                    dep_modifier.ligne = ligne
                    dep_modifier.montant = montant
                    dep_modifier.save()
                    return redirect('adminsuivi')
                else:
                    # Si le solde devient négatif après l'insertion de la dépense, renvoyer une réponse HTTP 403 (Forbidden)
                    return render(request, "Administrateur/modifierdepense.html", {'error_message': "votre budget est atteint, vous ne pouvez pas inserer.", 'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde, 'depense1':depense1})
   
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/modifierdepense.html', {'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde, 'depense1':depense1})

def supprimer_depense(request, id):
    if 'comptable_id' in request.session:
        # Accéder à la valeur de la clé 'comptable_id'
        comptable_id = request.session['comptable_id']
        return redirect("page404")
    # Faites ce que vous devez faire avec comptable_id
    else:
        if request.method == 'POST':
            Depense = Depense_budget.objects.get(pk=id)
            Depense.delete()    
        return redirect('adminsuivi')
    
def adminstatistique(request):
    try:   
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else:
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
            
            solde = total_montant - total_depense
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            selected_year = request.GET.get('selected_year')
            if selected_year:
                selected_year = int(selected_year)
            else:
                # Si aucune année n'est sélectionnée, utilisez l'année actuelle
                selected_year = timezone.now().year

            # Récupération de tous les objets Valeur_budget
            budget_initial = Valeur_budget.objects.filter(date_budget__year=selected_year).aggregate(Sum('budget_initial'))['budget_initial__sum'] or 0
            totalDepense = depense.filter(date__year=selected_year).aggregate(total=models.Sum('montant'))['total']
            # Liste des mois en français
            mois_fr = {
                1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
                5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
                9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
            }

            # Initialisation du dictionnaire pour stocker les totaux par mois
            depenses_par_mois = {mois: 0 for mois in mois_fr.values()}

            # Récupération des dépenses pour chaque mois et l'année sélectionnée
            for mois_num in range(1, 13):
                # Filtrage des dépenses pour le mois en cours et l'année sélectionnée
                depenses_mois = Depense_budget.objects.filter(date__year=selected_year, date__month=mois_num)
                # Calcul du total des dépenses pour le mois en cours
                
                total_mois = depenses_mois.aggregate(total=Sum('montant'))['total'] or 0
                # Stockage du total dans le dictionnaire
                depenses_par_mois[mois_fr[mois_num]] = total_mois
            
            # Calcul du pourcentage des dépenses par rapport au budget initial
            depenses_en_pourcentage = {}
            stat = {}
          
            for mois, total in depenses_par_mois.items():
                if budget_initial != 0:
                    pourcentage = (total / budget_initial) * 100
                else:
                    pourcentage = 0
                
                
                
                depenses_en_pourcentage[mois] = {"total": total, "pourcentage": "{:.2f}".format(pourcentage)}
                stat[mois] = pourcentage
               
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    
    return render(request, 'Administrateur/adminstatistique.html', {'stat':stat, 'totalDepense':totalDepense, 'total_montant':total_montant, 'total_depense':total_depense,'solde':solde, 'depenses_en_pourcentage': depenses_en_pourcentage, 'selected_year': selected_year, 'budget_initial': budget_initial, 'depenses_mois': depenses_mois})

def depenseinfoparmois(request):
    try:
        if 'comptable_id' in request.session:
            # Accéder à la valeur de la clé 'comptable_id'
            comptable_id = request.session['comptable_id']
            return redirect("compta404")
        # Faites ce que vous devez faire avec comptable_id
        else:   
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            user_id = request.session.get('admin_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
            
            solde = total_montant - total_depense
                 
            mois_annee = request.GET.get('mois')
            mois, selected_year = mois_annee.split("-")

            # Dictionnaire pour mapper le nom du mois à son numéro
            mois_dict = {
                "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
                "juillet": 7, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12
            }

            # Convertir le nom du mois en minuscules et obtenir son numéro
            mois_int = mois_dict.get(mois.lower())

            # Récupérer les dépenses pour le mois et l'année spécifiés
            depenses = Depense_budget.objects.filter(date__month=mois_int, date__year=selected_year)

    except Utilisateurs.DoesNotExist:
    # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Administrateur/depenseinfoparmois.html', {'total_montant':total_montant, 'total_depense':total_depense, 'solde':solde,'mois':mois, 'depenses':depenses, 'selected_year':selected_year})

def admin404(request):
    try:    
        pass
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        return redirect("page404")
    return render(request, 'Administrateur/404.html')

# Comptable
def comptableindex(request):
    try:
        if 'admin_id' in request.session:
            # Accéder à la valeur de la clé 'admin_id_id'
            admin_id = request.session['admin_id']
            return redirect("admin404")
        # Faites ce que vous devez faire avec comptable_id
        else:
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']     
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            # Session
            user_id = request.session.get('comptable_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
                
            solde = total_montant - total_depense  
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Comptable/comptableindex.html', {'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde})

def comptablesaisie(request):
    try:
        if 'admin_id' in request.session:
            # Accéder à la valeur de la clé 'admin_id_id'
            admin_id = request.session['admin_id']
            return redirect("admin404")
        # Faites ce que vous devez faire avec comptable_id
        else:        
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all()
            
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
            
            affichedepense = Depense_budget.objects.all().order_by('-id')
            
            solde = total_montant - total_depense
            # Session
            user_id = request.session.get('comptable_id')
            users = Utilisateurs.objects.get(id=user_id)
            
            if request.method == "POST":     
                rubrique = request.POST.get('rubrique')
                ligne = request.POST.get('ligne')
                montant = request.POST.get('montant')
                obs = request.POST.get('obs')
                
                # Vérifier si le budget initial est supérieur à zéro
                if float(montant) <= 0:
                    messages.add_message(request, messages.SUCCESS, "le montant ne doit pas inférieur ou égal à zéro")
                    # Si le budget initial est inférieur ou égal à zéro, afficher un message d'erreur ou prendre une action appropriée
                    return redirect("comptablesaisie")
                else:
                    # Obtenir le fuseau horaire de Madagascar
                    fuseau_horaire_madagascar = pytz.timezone('Indian/Antananarivo')
            
                    # Obtenir la date et l'heure actuelles dans le fuseau horaire de Madagascar
                    date = datetime.now(fuseau_horaire_madagascar)
            
                    # Obtenir l'heure actuelle dans le fuseau horaire de Madagascar
                    times = date.time()
                    
                    # Calculer le nouveau solde après l'insertion de la dépense
                    nouveau_solde = solde - int(montant)
                    
                    # Vérifier si le nouveau solde est négatif
                    if nouveau_solde >= 0:
                        # Créer et enregistrer l'objet de dépense uniquement si le solde n'est pas négatif
                        depense = Depense_budget(rubrique=rubrique, ligne=ligne, date=date, times=times, montant=montant, obs=obs, users_id=users)
                        depense.save()
                        return redirect('comptablesaisie')
                    else:
                        # Si le solde devient négatif après l'insertion de la dépense, renvoyer une réponse HTTP 403 (Forbidden)
                        return render(request, "Comptable/comptablesaisie.html", {'error_message': "votre budget est atteint, vous ne pouvez pas inserer.", 'total_montant': total_montant, 'affichedepense': affichedepense, 'total_depense': total_depense , 'solde':solde})
   
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Comptable/comptablesaisie.html', {'total_montant': total_montant, 'affichedepense': affichedepense, 'total_depense': total_depense , 'solde':solde})

def comptablesuivi(request):
    try:
        if 'admin_id' in request.session:
            # Accéder à la valeur de la clé 'admin_id_id'
            admin_id = request.session['admin_id']
            return redirect("admin404")
        # Faites ce que vous devez faire avec comptable_id
        else:        
            budget = Valeur_budget.objects.all()  
            depense = Depense_budget.objects.all().order_by('-id')
            total_montant = budget.aggregate(total=models.Sum('budget_initial'))['total']
            total_depense = depense.aggregate(total=models.Sum('montant'))['total']
            
            # Session
            user_id = request.session.get('comptable_id')
            users = Utilisateurs.objects.get(id=user_id)
                
            # Vérifier si total_depense est nul
            if total_montant is None:
                total_montant = 0
            if total_depense is None:
                total_depense = 0
            
            solde = total_montant - total_depense
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Comptable/comptablesuivi.html', {'total_montant': total_montant, 'total_depense': total_depense , 'solde':solde , 'depense':depense})

def compta404(request):
    try:
        pass
    except Utilisateurs.DoesNotExist:
        # Si l'utilisateur n'existe pas, vous pouvez prendre une action appropriée
        # Par exemple, afficher un message d'erreur ou rediriger vers une autre page
        return redirect("page404")
    return render(request, 'Comptable/404.html')

def erreur404(request):
    return render(request, '404.html')