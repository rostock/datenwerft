from django_user_agents.utils import get_user_agent

from ..apps import StadtbereichskatalogConfig as appConfig
from ..utils import is_stadtbereichskatalog_user


def add_app_context_elements(context):
  """
  adds global app related elements to a context and returns it

  :param context: context
  :return: context with global app related elements added
  """
  context['app'] = {
    'verbose_name': getattr(appConfig, 'verbose_name', appConfig.name),
    'description': getattr(appConfig, 'description', ''),
  }
  return context


def add_permissions_context_elements(context, user):
  """
  adds permissions related elements to a context and returns it

  :param context: context
  :param user: user
  :return: context with permissions related elements added
  """
  permissions = {
    'is_stadtbereichskatalog_user': is_stadtbereichskatalog_user(user),
  }
  if user.is_superuser:
    permissions = {key: True for key in permissions}
  context.update(permissions)
  return context


def add_useragent_context_elements(context, request):
  """
  adds user agent related elements to a context and returns it

  :param context: context
  :param request: request
  :return: context with user agent related elements added
  """
  user_agent = get_user_agent(request)
  if user_agent.is_mobile or user_agent.is_tablet:
    context['is_mobile'] = True
  else:
    context['is_mobile'] = False
  return context
