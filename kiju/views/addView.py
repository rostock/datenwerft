from django.views.generic import TemplateView

from .functions import add_permission_context_elements


class AddView(TemplateView):
  """
  View for the Add page of KiJu.
  """

  template_name = 'kiju/add.html'
  model = None

  def init(self, model, *args, **kwargs):
    self.model = model

  def dispatch(self, request, *args, **kwargs):
    """
    Dispatches the request to the appropriate method.
    """
    # if not is_authorized_user(request.user, self):
    #  return False
    # return super().dispatch(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    """
    returns a dictionary containing the context data for the index page.
    """
    context = super().get_context_data(**kwargs)
    context = add_permission_context_elements(context, self.request.user)
    # context['is_authorized_user'] = is_authorized_user(self.request.user, self)
    context['model'] = self.model
    context['model_name'] = self.model.__name__
    context['model_lower'] = self.model.__name__.lower()
    context['model_verbose_name'] = self.model._meta.verbose_name

    return context
