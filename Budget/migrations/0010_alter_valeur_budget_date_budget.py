# Generated by Django 5.0.2 on 2024-04-23 08:00

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Budget', '0009_depense_budget_time_alter_depense_budget_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='valeur_budget',
            name='date_budget',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]