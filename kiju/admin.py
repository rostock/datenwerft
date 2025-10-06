from django.contrib import admin

from .models.base import Host, Topic
from .models.main_models import Angebot, Ferienangebot

admin.site.register(Topic)
admin.site.register(Angebot)
admin.site.register(Ferienangebot)
admin.site.register(Host)
