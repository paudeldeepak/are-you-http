# Generated by Django 5.0.2 on 2024-04-01 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Accounts", "0006_tokenmapping"),
    ]

    operations = [
        migrations.AddField(
            model_name="author",
            name="auth_token_key",
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
