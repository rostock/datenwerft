from bemas.utils import is_bemas_admin, is_bemas_user


def add_default_context_elements(context, user):
  """
  adds default elements to a context and returns it

  :param context: context
  :param user: user
  :return: context with default elements added
  """
  if user.is_superuser or is_bemas_user(user):
    context['is_bemas_user'], context['is_bemas_admin'] = True, True
  else:
    context['is_bemas_user'] = False
    context['is_bemas_admin'] = is_bemas_admin(user)
  return context
