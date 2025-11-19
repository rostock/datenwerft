from django.contrib import admin

from .models.base import Host, Law, Provider, TargetGroup, Topic
from .models.services import HolidayService, PreventionService

admin.site.register(Provider)
admin.site.register(Topic)
admin.site.register(Law)
admin.site.register(TargetGroup)
admin.site.register(Host)
admin.site.register(HolidayService)
admin.site.register(PreventionService)
