from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import RegexValidator
from django.utils import timezone
from django.db import models
import locale

# Configuration de la localisation en français
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

class Utilisateurs(models.Model):
    pseudo = models.CharField(max_length=255)
    mdp = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    contact = models.CharField(max_length=10, default='0321234567', validators=[RegexValidator(r'^(032|033|034|038)\d{7}$', message='Veuillez entrer un numéro de téléphone valide.')])

class Code_valid_comptable(models.Model):
    code = models.CharField(max_length=255)
    
class Valeur_budget(models.Model):
    budget_initial = models.IntegerField(default=0)
    budget_balence = models.IntegerField(default=0)
    budget_solde = models.IntegerField(default=0)
    date_budget = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)

    def date_formattee(self):
        return self.date_budget.strftime("%d/%m/%Y")
    def heure_formattee(self):
        return self.time.strftime("%H:%M:%S")
    
class Depense_budget(models.Model):
    users_id = models.ForeignKey(Utilisateurs, on_delete=models.DO_NOTHING, default=1)
    rubrique = models.CharField(max_length=255)
    ligne = models.CharField(max_length=255)
    date = models.DateField(default=timezone.now)
    times = models.TimeField(default=timezone.now)
    montant = models.IntegerField(default=0)
    obs = models.TextField(default='')
    
    def date_formattee(self):
        return self.date.strftime("%d/%m/%Y")
    
    def heure_formattee(self):
        return self.times.strftime("%H:%M:%S")
    
    
    
    