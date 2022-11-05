from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User, Permission, Group
from django.contrib.auth.views import LoginView
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from guardian.models import UserObjectPermission, GroupObjectPermission
from rest_framework import viewsets

from accounts import serializers
from accounts.forms import ExternalAuthenticationForm
from .emails import send_login_code
from .models import UserAuthToken
from .utils import get_client_ip, ip_in_array


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = serializers.PermissionSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer


class ContentTypeViewSet(viewsets.ModelViewSet):
    queryset = ContentType.objects.all()
    serializer_class = serializers.ContentTypeSerializer
    # lookup_field = 'model'


class UserObjectPermissionViewSet(viewsets.ModelViewSet):
    queryset = UserObjectPermission.objects.all()
    serializer_class = serializers.UserObjectPermissionSerializer


class GroupObjectPermissionViewSet(viewsets.ModelViewSet):
    queryset = GroupObjectPermission.objects.all()
    serializer_class = serializers.GroupObjectPermissionSerializer


class PreLoginView(LoginView):
    """
    Login View
    users with internal ip address go through the normal login process.
    Users with external IP address have to go through a two-factor authentication process
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        user = form.get_user()
        user_ip = get_client_ip(self.request)
        if user_ip in settings.AUTH_LDAP_EXTENSION_INTERNAL_IP_ADDRESSES:
            # user is internal
            login(self.request, user)
            return HttpResponseRedirect(self.get_success_url())
        else:
            # user is external next step is to generate login tokens
            user_auth, create = UserAuthToken.objects.get_or_create(user=user)
            if not create:
                # refresh tokens
                user_auth.save()
            user_auth.refresh_from_db()
            self.request.session['_token'] = f'{user_auth.session_token}'
            send_login_code(user_auth.user)
            # url_token is only to show a dynamic url.
            # The crucial token is the session token
            return HttpResponseRedirect(reverse(
                'accounts:external_login',
                kwargs={'url_token': user_auth.url_token})
            )


class ExternalLoginView(LoginView):
    """
    second login View for external user
    """
    template_name = 'accounts/login_add_token.html'
    form_class = ExternalAuthenticationForm
    redirect_authenticated_user = True

    @method_decorator(sensitive_post_parameters('email_token'))
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        session_token = request.session.get('_token')
        url_token = kwargs.get('url_token')
        if not session_token or not url_token:
            # something wrong, restart login process
            return HttpResponseRedirect(reverse('account:login'))
        try:
            UserAuthToken.objects.get(session_token=session_token, url_token=url_token)
        except UserAuthToken.DoesNotExist:
            if session_token:
                request.session.pop('_token')
            raise Http404()
        else:
            user_ip = get_client_ip(self.request)
            if ip_in_array(user_ip, settings.AUTH_LDAP_EXTENSION_INTERNAL_IP_ADDRESSES):
                # user is internal
                # the token is not needed
                request.session.pop('_token')
                return HttpResponseRedirect(reverse('accounts:login'))
        return super().dispatch(request, *args, **kwargs)
