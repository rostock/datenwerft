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
html_logo = '_static/logo.png'
html_show_copyright = False
html_show_search_summary = True
html_show_sourcelink = False
html_static_path = ['_static']
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
  'version_selector': False,
  'language_selector': False,
  'logo_only': True,
  'style_nav_header_background': '#0d6efd'
}
html_title = 'Datenwerft.HRO'
