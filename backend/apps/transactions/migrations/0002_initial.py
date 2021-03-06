# Generated by Django 3.2.6 on 2022-05-18 17:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('transactions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='userwallet',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='transactions',
            name='user_from',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_from', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='transactions',
            name='user_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_to', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='transactiondetail',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='transactions.currency'),
        ),
        migrations.AddField(
            model_name='transactiondetail',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='transactions.transactions'),
        ),
    ]
