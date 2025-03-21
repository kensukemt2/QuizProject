# Generated by Django 5.1.6 on 2025-03-13 05:27

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz_api', '0002_quizattempt_questionresponse'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='quizattempt',
            index=models.Index(fields=['user', 'category'], name='quiz_api_qu_user_id_eed165_idx'),
        ),
        migrations.AddIndex(
            model_name='quizattempt',
            index=models.Index(fields=['category'], name='quiz_api_qu_categor_f2e13d_idx'),
        ),
        migrations.AddIndex(
            model_name='quizattempt',
            index=models.Index(fields=['percentage'], name='quiz_api_qu_percent_0ce6e3_idx'),
        ),
    ]
