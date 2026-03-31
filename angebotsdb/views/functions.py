from ..utils import is_angebotsdb_admin, is_angebotsdb_user


def add_permission_context_elements(context, user):
  """
  adds default elements to a context and returns it

  :param context: context
  :param user: user
  :return: context with default elements added
  """
  context['is_angebotsdb_user'], context['is_angebotsdb_admin'] = False, False
  if user.is_superuser:
    context['is_angebotsdb_user'], context['is_angebotsdb_admin'] = True, True
  elif is_angebotsdb_user(user) or is_angebotsdb_admin(user):
    context['is_angebotsdb_user'] = True
    if is_angebotsdb_admin(user):
      context['is_angebotsdb_admin'] = True
  return context
