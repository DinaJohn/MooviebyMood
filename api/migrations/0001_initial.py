# Generated by Django 4.2.6 on 2024-03-04 21:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Movie",
            fields=[
                ("movieId", models.IntegerField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255)),
                ("genres", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Link",
            fields=[
                (
                    "movieId",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="api.movie",
                    ),
                ),
                ("imdbId", models.CharField(max_length=255)),
                ("tmdbId", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("userId", models.IntegerField()),
                ("tag", models.CharField(max_length=255)),
                ("timestamp", models.DateTimeField()),
                (
                    "movieId",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.movie"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Rating",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("userId", models.IntegerField()),
                ("rating", models.FloatField()),
                ("timestamp", models.DateTimeField()),
                (
                    "movieId",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.movie"
                    ),
                ),
            ],
        ),
    ]
