# Generated by Django 5.0.2 on 2024-03-20 18:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0002_initial'),
        ('Posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inbox_feed',
            name='comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox_feeds', to='Posts.comment'),
        ),
        migrations.AddField(
            model_name='inbox_feed',
            name='like',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inbox_feeds', to='Posts.like'),
        ),
    ]
