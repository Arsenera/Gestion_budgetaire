# Generated by Django 5.0.2 on 2024-04-23 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Budget', '0014_alter_depense_budget_times'),
    ]

    operations = [
        migrations.AlterField(
            model_name='depense_budget',
            name='date',
            field=models.DateField(),
        ),
    ]