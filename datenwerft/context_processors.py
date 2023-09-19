from django.urls import NoReverseMatch, reverse


def include_login_form(request):
  """
  returns login form based on passed request

  :param request: request
  :return: login form based on passed request
  """
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
