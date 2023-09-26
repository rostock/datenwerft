from django.db.models import Q
from re import match, search, sub


def optimize_datatable_filter(search_element, search_column, qs_params_inner):
  """
  optimizes datatables queryset filter based on passed parameters

  :param search_element: search element
  :param search_column: search column
  :param qs_params_inner: queryset parameters
  :return: optimized datatables queryset filter based on passed parameters
  """
  case_a = search('^[0-9]{2}\\.[0-9]{2}\\.[0-9]{4}$', search_element)
  case_b = search('^[0-9]{2}\\.[0-9]{4}$', search_element)
  case_c = search('^[0-9]{2}\\.[0-9]{2}$', search_element)
  if case_a or case_b or case_c:
    search_element_splitted = search_element.split('.')
    kwargs = {
        '{0}__{1}'.format(search_column, 'icontains'): (search_element_splitted[
            2] + '-' if case_a else '') +
        search_element_splitted[1] + '-' +
        search_element_splitted[0]
    }
  elif search_element == 'ja':
    kwargs = {
        '{0}__{1}'.format(search_column, 'icontains'): 'true'
    }
  elif search_element == 'nein' or search_element == 'nei':
    kwargs = {
        '{0}__{1}'.format(search_column, 'icontains'): 'false'
    }
  elif match(r"^[0-9]+,[0-9]+$", search_element):
    kwargs = {
        '{0}__{1}'.format(search_column, 'icontains'): sub(',', '.', search_element)
    }
  else:
    kwargs = {
        '{0}__{1}'.format(search_column, 'icontains'): search_element
    }
  q = Q(**kwargs)
  return qs_params_inner | q if qs_params_inner else q
