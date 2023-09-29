import os
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
  def handle(self, *args, **options):

    verbose = False
    if options.get('verbosity') > 1:
      verbose = True

    rmroot = os.path.join(settings.BASE_DIR, 'toolbox', 'mkpdf')
    os.chdir(rmroot)
    fs = os.listdir()
    deld = 0
    skpd = 0
    for f in fs:
      if f[:4] == 'tmp_':
        os.remove(f)
        if verbose:
          print(f'del {f}')
        deld += 1
      else:
        if verbose:
          print(f'skip {f}')
        skpd += 1
    print(f'{deld} Datei(en) gelöscht, {skpd} Datei(en) übersprungen in {rmroot}')
