# Generated by Django 5.0.2 on 2024-03-20 05:07

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('id_url', models.URLField(blank=True, default='', null=True)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('source', models.URLField(blank=True, default='', null=True)),
                ('origin', models.URLField(blank=True, default='', null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('contentType', models.CharField(choices=[('text/markdown', 'Markdown'), ('text/plain', 'Plain Text'), ('image/png;base64', 'PNG Image'), ('image/jpeg;base64', 'JPEG Image')], max_length=50)),
                ('published', models.DateTimeField(default=django.utils.timezone.now)),
                ('visibility', models.CharField(choices=[('PUBLIC', 'Public'), ('FRIENDS', 'Friends'), ('UNLISTED', 'Unlisted')], max_length=10)),
                ('image', models.ImageField(blank=True, null=True, upload_to='posts/images/')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('id_url', models.URLField(blank=True, default='', null=True)),
                ('comment', models.TextField()),
                ('contentType', models.CharField(choices=[('text/markdown', 'Markdown'), ('text/plain', 'Plain Text')], max_length=50)),
                ('published', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='Posts.post')),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('published', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to=settings.AUTH_USER_MODEL)),
                ('comment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='Posts.comment')),
                ('post', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='Posts.post')),
            ],
            options={
                'unique_together': {('comment', 'author'), ('post', 'author')},
            },
        ),
    ]