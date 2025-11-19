from django.views.generic import TemplateView


class AddView(TemplateView):
  """
  View for the Add page of KiJu.
  """

  template_name = 'kiju/add.html'
  model = None

  def init(self, model, *args, **kwargs):
    self.model = model

  def get_context_data(self, **kwargs):
    """
    returns a dictionary containing the context data for the index page.
    """
    context = super().get_context_data(**kwargs)
    context['model'] = self.model
    context['model_name'] = self.model.__name__
    context['model_lower'] = self.model.__name__.lower()
    context['model_verbose_name'] = self.model._meta.verbose_name
    return context
