from django.urls import path

from . import views

app_name = 'metadatenmanagement'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]

api_urlpatterns = [
    # API URL-Patterns werden später hinzugefügt
]
