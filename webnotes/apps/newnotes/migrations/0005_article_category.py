# Generated by Django 3.2.7 on 2021-10-28 16:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('newnotes', '0004_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='category',
            field=models.ForeignKey(default=7, on_delete=django.db.models.deletion.CASCADE, to='newnotes.category'),
            preserve_default=False,
        ),
    ]
