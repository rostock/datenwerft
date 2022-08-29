from django.conf import settings
from django.urls import reverse, NoReverseMatch
import django


def address_search_key(request):
    return {'address_search_key': settings.ADDRESS_SEARCH_KEY}


def datenmanagement_version(request):
    return {'datenmanagement_version': settings.DATENMANAGEMENT_VERSION}


def include_login_form(request):
    from django.contrib.auth.forms import AuthenticationForm
    form = AuthenticationForm()
    loginredirect = request.get_full_path()
    try:
        if request.get_full_path() == reverse('logout'):
            loginredirect = reverse('events:list')
    except NoReverseMatch:
        loginredirect = request.get_full_path()
    return {
        'login_form': form,
        'current_path': loginredirect
    }
