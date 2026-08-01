from django.contrib import admin
from . import models 
from .models import NewsletterSubscriber


admin.site.register(models.Profile)
admin.site.register(NewsletterSubscriber)
