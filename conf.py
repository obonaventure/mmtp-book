# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/stable/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'Modern Multipath Transport Protocols'
copyright = '2022, Olivier Bonaventure'
author = 'Olivier Bonaventure'

# The short X.Y version
version = '0.0'
# The full version, including alpha/beta/rc tags
release = '2022'


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinxcontrib.tikz',
    'sphinxcontrib.bibtex',
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinxcontrib.spelling',
    'sphinx.ext.githubpages',
    'matplotlib.sphinxext.plot_directive',
    
   

]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store','._*rst','venv/*']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# spelling
spelling_lang='en_US'
tokenizer_lang='en_US'
spelling_show_suggestions=True
# Private dictionnary
spelling_word_list_filename=['wordlist.dict']

spelling_exclude_patterns=['biblio.rst']

# bibtex

bibtex_bibfiles = ['bib/rfc.bib',
                   'bib/quic.bib',
                   'bib/papers.bib',
                   'mptcp-bib/bibs/2007.bib',
                   'mptcp-bib/bibs/2008.bib',
                   'mptcp-bib/bibs/2009.bib',
                   'mptcp-bib/bibs/2010.bib',
                   'mptcp-bib/bibs/2011.bib',
                   'mptcp-bib/bibs/2012.bib',
                   'mptcp-bib/bibs/2013.bib',
                   'mptcp-bib/bibs/2014.bib',
                   'mptcp-bib/bibs/2015.bib',
                   'mptcp-bib/bibs/2016.bib',
                   'mptcp-bib/bibs/2017.bib',
                   'mptcp-bib/bibs/2018.bib',
                   'mptcp-bib/bibs/2019.bib',
                   'mptcp-bib/bibs/2020.bib',
                   'mptcp-bib/bibs/2021.bib',
                   'mptcp-bib/bibs/2022.bib',
                       ]

bibtex_default_style = 'unsrt'


numfig=True


# Matplotlib

plot_include_source=False
plot_html_show_source_link=False
plot_html_show_formats=False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

html_theme_options = {
    #'analytics_id': 'G-XXXXXXXXXX',  #  Provided by Google in your dashboard
    #'analytics_anonymize_ip': False,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': 'white',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

html_context = {
  'display_github': True,
  'github_user': 'obonaventure',
  'github_repo': 'mmtp-book',
  'github_version': 'main',
}

#github_url = '

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'MMTP'


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'MMTP.tex', 'Modern Multipath Transport Protocols', 
     'Olivier Bonaventure', 'manual'),
]

latex_elements = {
'preamble': '''
\\usepackage{tikz}
\\usepackage{xcolor}
\\usepackage{bytefield}
\\usepackage{pgfplots}
\pgfplotsset{compat=1.16}
\\usetikzlibrary{arrows,arrows.meta,positioning, matrix,backgrounds,shapes,shapes.symbols,shadows,calc,automata,math}
'''
}

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# latex_additional_files

latex_additional_files= [ 'bytefield.sty' ]

# If false, no module index is generated.
#latex_use_modindex = True

tikz_libraries="arrows,arrows.meta,positioning, matrix,backgrounds,shapes,shapes.symbols,shadows,calc,automata,math,automata,background,shapes" #positioning,matrix,arrows,arrows.meta,shapes,automata,math,shapes,backgrounds"

tikz_proc_suite='pdf2svg' #'ImageMagick'

tikz_latex_preamble='''
%preamble
\\usepackage{tikz}
\\usepackage{pgfplots}
\\usepackage{pgfkeys}
\\usepackage[normalem]{ulem}
\\usepackage{bytefield}
%\pgfplotsset{compat=1.16}
\\tikzset{router/.style = {rectangle, draw, text centered, minimum height=2em
}, }
\\tikzset{host/.style = {circle, draw, text centered, minimum height=2em}, }
'''

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'mmtcp', 'Modern Multipath Transport Protocols',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'MultipathTCPamoreresilienttransport', 'Multipath TCP : a more resilient transport Documentation',
     author, 'MultipathTCPamoreresilienttransport', 'One line description of project.',
     'Miscellaneous'),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']


# -- Extension configuration -------------------------------------------------

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
