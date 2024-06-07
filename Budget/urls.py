from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentification
    path('', connexion, name='connexion'),
    path('inscription', inscription, name='inscription'),
    path('code/', code, name='code'),
    path('deconnexion/', deconnexion, name='deconnexion'),
    path('page404', erreur404, name="page404"),

    
    # Admin
    path('adminparametre', adminparametre, name="adminparametre"),
    path('adminIndex', adminIndex, name="adminIndex"),
    path('modifieradmin', modifieradmin, name='modifieradmin'),
    path('modifiercode', modifiercode, name='modifiercode'),
    path('ajouterbudget', ajouterbudget, name='ajouterbudget'),
    path('modifer/<int:id>/', modiferbudget, name='modiferbudget'),
    path("supprimer_budget/<int:id>/", supprimer_budget, name="supprimer_budget"),
    path('adminutilisateur', adminutilisateur, name='adminutilisateur'),
    path('modifierutilisateur/<int:id>/', modifierutilisateur, name='modifierutilisateur'),    
    path('adminsuivi', adminsuivi, name='adminsuivi'),
    path('depenseinfo/<int:id>/', depenseinfo, name='depenseinfo'),
    path('modifierdepense/<int:id>/', modifierdepense, name='modifierdepense'),
    path("supprimer_depense/<int:id>/", supprimer_depense, name="supprimer_depense"),
    path('adminstatistique', adminstatistique, name='adminstatistique'),
    path('depenseinfoparmois', depenseinfoparmois, name='depenseinfoparmois'),
    path('admin404', admin404, name="admin404"),
    
    # Comptable
    path('comptableindex', comptableindex, name="comptableindex"),
    path('comptablesaisie', comptablesaisie, name="comptablesaisie"),
    path('comptablesuivi', comptablesuivi, name="comptablesuivi"),
    path('compta404', compta404, name="compta404"),

]

