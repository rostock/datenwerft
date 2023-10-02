# project information

project = 'Datenwerft.HRO'
author = 'Hanse- und Universitätsstadt Rostock'


# general configuration

extensions = [
  'sphinx.ext.autodoc'
]
root_doc = 'index'


# options for internationalization

language = 'de'


# options for HTML output

htmlhelp_basename = 'datenwerft'
html_show_copyright = False
html_show_search_summary = True
html_show_sourcelink = False
html_static_path = ['_static']
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
  'display_version': False
}
html_title = 'Datenwerft.HRO'
