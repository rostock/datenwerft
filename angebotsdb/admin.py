from django.contrib import admin

from .models.base import (
  InboxMessage,
  Law,
  OrgUnit,
  Provider,
  ReviewTask,
  Tag,
  TargetGroup,
  Topic,
  UserProfile,
)
from .models.services import ChildrenAndYouthService, ServiceImage

admin.site.register(Provider)
admin.site.register(Topic)
admin.site.register(Law)
admin.site.register(TargetGroup)
admin.site.register(ChildrenAndYouthService)
admin.site.register(Tag)
admin.site.register(OrgUnit)
admin.site.register(UserProfile)
admin.site.register(ReviewTask)
admin.site.register(InboxMessage)
admin.site.register(ServiceImage)
