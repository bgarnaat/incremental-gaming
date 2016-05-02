# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-02 21:02
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clicker_game', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game_Instance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.TextField()),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='clicker_game',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games_owned', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='game_instance',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='running_games', to='clicker_game.Clicker_Game'),
        ),
        migrations.AddField(
            model_name='game_instance',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games_playing', to=settings.AUTH_USER_MODEL),
        ),
    ]
