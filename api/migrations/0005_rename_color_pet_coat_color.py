# Generated by Django 4.0.6 on 2022-08-01 22:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_rename_animal_breed_species_rename_type_pet_species'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pet',
            old_name='color',
            new_name='coat_color',
        ),
    ]
