from django.contrib import admin

from .models.base import Host, Law, Provider, Tag, TargetGroup, Topic
from .models.services import PreventionService

admin.site.register(Provider)
admin.site.register(Topic)
admin.site.register(Law)
admin.site.register(TargetGroup)
admin.site.register(Host)
admin.site.register(PreventionService)
admin.site.register(Tag)
