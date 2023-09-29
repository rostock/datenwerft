import jinja2
import json
import subprocess
from datetime import datetime
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from functools import cmp_to_key
from itertools import chain
from os.path import join as joinpath
from uuid import uuid1

from datenmanagement.models.models_simple import Baudenkmale, Denkmalbereiche
from .models import SuitableFor


def compare_adresses(denkmal1, denkmal2):
  l1 = denkmal1['position'].split(' ')
  l2 = denkmal2['position'].split(' ')
  nr1 = ''
  nr2 = ''

  for wort1, wort2 in zip(l1, l2):
    if wort1[0].isdigit():
      # Wir sind bei den Hausnummern angelangt.
      i = 0
      j = 0
      while i < len(wort1) and wort1[i].isdigit():
        nr1 += (wort1[i])
        i += 1
      while j < len(wort2) and wort2[j].isdigit():
        nr2 += (wort2[j])
        j += 1
      return int(nr1) - int(nr2)
    elif wort1 < wort2:
      return -1
    elif wort1 > wort2:
      return 1
  return 0


def preparecontext(request):
  params = json.loads(request.body)
  suitable = SuitableFor.objects.get(pk=params['templateid'])
  params['suitable'] = suitable
  if params.get('onlyactive') is None:
    params['onlyactive'] = True
  if suitable.usedkeys is None:
    params["usedkeys"] = []
  else:
    params["usedkeys"] = suitable.usedkeys
  if suitable.sortby is None:
    params['sortby'] = []
  else:
    params['sortby'] = suitable.sortby
  return params


def render(
    data,
    templatefiledescriptor,
    outfilename="tmp_",
    pdfdir="toolbox/mkpdf/"):
  data["jetzt"] = datetime.now().strftime("%d.%m.%Y")
  uid = uuid1()
  outfilename += str(uid)
  tpl = jinja2.Template(
    templatefiledescriptor.read().decode("utf-8"),
    block_start_string=settings.PDF_JINJASTRINGS["block_start"],
    block_end_string=settings.PDF_JINJASTRINGS["block_end"],
    variable_start_string=settings.PDF_JINJASTRINGS["variable_start"],
    variable_end_string=settings.PDF_JINJASTRINGS["variable_end"],
    comment_start_string=r"\JCMNT",
    comment_end_string="}"
  )
  f = open(joinpath(settings.BASE_DIR, pdfdir, outfilename+".latex"), "w")
  f.write(tpl.render(data))
  f.close()
  log = open(f"toolbox/mkpdf/tmp_{uid}_texlog.txt", "w")
  subprocess.run(
      ["latexmk", outfilename+".latex", "-interaction=batchmode"],
      cwd=joinpath(settings.BASE_DIR, pdfdir),
      stdout=log,
      stdin=subprocess.DEVNULL,
      check=False)
  log.close()

  try:
    f = open(joinpath(settings.BASE_DIR, pdfdir, outfilename+".pdf"), "rb")
    success = True
    return success, f
  except FileNotFoundError:
    success = False
    print(" versuche texlog.txt zurückzugeben")
    f = open(joinpath(settings.BASE_DIR, pdfdir, f"tmp_{uid}.log"), "r", encoding='latin-1')
    ret = f.read()
  return success, ret


def prep4latex(string):
  for esc in settings.PDF_REPLACES:
    string = string.replace(esc[0], esc[1])
  return string


def fetchdata(datenthema, pks, onlyactive=True, order=None, usedkeys=None, **kwargs):
  if order is None:
    order = []
  print(datenthema)
  dt = ContentType.objects.get(app_label="datenmanagement", model=datenthema.lower())
  print(dt)
  thema = dt.model_class()

  display_names = dict()
  for field in thema._meta.fields:
    display_names[field.name] = field.verbose_name
    display_names[field.name+"_id"] = field.verbose_name

  if usedkeys is None or usedkeys == []:
    usedkeys = [field.name for field in thema._meta.fields]
  else:
    usedkeys = [key[0] for key in usedkeys]

  if len(pks) > 0:
    if onlyactive:
      records = thema.objects.filter(pk__in=pks, aktiv=True).order_by(*order)
    else:
      records = thema.objects.filter(pk__in=pks).order_by(*order)
  else:
    if onlyactive:
      records = thema.objects.filter(aktiv=True).order_by(*order)
    else:
      records = thema.objects.all().order_by(*order)

  escapedrecords = list()
  for record in records:
    escapedrecord = dict()
    for key in usedkeys:
      escapedrecord[key] = prep4latex(str(getattr(record, key)))
    escapedrecords.append(escapedrecord)
  return escapedrecords, display_names


def chkforwmd(record):
  if "Warnemünde" in record.beschreibung:
    return True
  elif "Wmd" in record.beschreibung:
    return True
  elif "Wmd" in record.bezeichnung:
    return True
  elif "Warnemünde" in record.bezeichnung:
    return True
  else:
    return False


def cleanqueryrecord(datum):
  ret = dict()
  ret['lage'] = prep4latex(str(datum.bezeichnung))
  ret['beschreibung'] = prep4latex(str(datum.beschreibung))
  ret['landschaftsdenkmal'] = True
  if chkforwmd(datum):
    ret['adresse'] = "(Wmd)"
  return ret


def baudenkmalefull(pks=None, onlyactive=True):

  if pks is None:
    pks = []
  if onlyactive:
    brds = Denkmalbereiche.objects.filter(aktiv=True).order_by('bezeichnung')
    if len(pks) > 0:
      bdms = Baudenkmale.objects.filter(pk__in=pks, aktiv=True).order_by('adresse')
    else:
      bdms = Baudenkmale.objects.filter(aktiv=True).order_by('adresse')
  else:
    brds = Denkmalbereiche.objects.all()('bezeichnung')
    if len(pks) > 0:
      bdms = Baudenkmale.objects.filter(pk__in=pks).order_by('adresse')
    else:
      bdms = Baudenkmale.objects.all().order_by('adresse')

  data = [{
    'name': "Baudenkmale",
    'orte': [{
      'name': "Rostock",
      'byletter': dict()
    }, {
      'name': "Warnemünde",
      'byletter': dict()
    }]}, {
    'name': "Denkmalbereiche",
    'orte': [{
      'name': "Rostock",
      'byletter': dict()
    }, {
      'name': "Warnemünde",
      'byletter': dict()
    }]}
  ]

  for bdm in bdms:
    rec = dict()

    adr = str(bdm.adresse)
    if bdm.lage is not None:
      rec['position'] = prep4latex(bdm.lage)
    else:
      rec['position'] = prep4latex(adr[:len(adr)-5])
    if adr[len(adr)-5:] == "(Wmd)":
      rec['wmd'] = True
    else:
      rec['wmd'] = False
    rec['beschreibung'] = prep4latex(str(bdm.beschreibung))
    if bdm.landschaftsdenkmal:
      rec['beschreibung'] += '*'

    if rec['wmd']:
      insert_or_append(data[0]['orte'][1]['byletter'], rec['position'][0].upper(), rec)
    else:
      insert_or_append(data[0]['orte'][0]['byletter'], rec['position'][0].upper(), rec)

  for brd in brds:
    rec = dict()
    rec['position'] = prep4latex(brd.bezeichnung)
    rec['beschreibung'] = prep4latex(brd.beschreibung)
    rec['wmd'] = chkforwmd(brd)

    if rec['wmd']:
      insert_or_append(data[1]['orte'][1]['byletter'], rec['position'][0].upper(), rec)
    else:
      insert_or_append(data[1]['orte'][0]['byletter'], rec['position'][0].upper(), rec)

  for kat in data:
    for ort in kat['orte']:
      for anfang in ort['byletter']:
        ort['byletter'][anfang].sort(key=cmp_to_key(compare_adresses))

#  print("orte Typ: ", type(orte))
#  for ortindex in range(len(orte)):
#    for eintragsklassenindex in range(len(orte[ortindex]['eintragsklassen'])):
#      for key in orte[ortindex][eintragsklassenindex]['byletter'].keys():
#        orte[ortindex][eintragsklassenindex]['byletter'][key].sort(key=cmp_to_key(compare_adresses))
#        print("Typ:", type(orte[ortindex][eintragsklassenindex]['byletter'][key]))

  return {'kategorien': data}


def sortforbaudenkmale(data, brdauch=False):

  baud_rost_byl = {}
  baud_wamue_byl = {}
  bere_rost_byl = {}
  bere_wamue_byl = {}
  for rec in data:
    rec.pop('geometrie')
    print(rec)

  if brdauch:
    brds = Denkmalbereiche.objects.all()
    preppedbrds = [cleanqueryrecord(rec) for rec in brds]
    data = chain(data, preppedbrds)

  for item in data:
    if item.get('lage') is None:
      if item.get('adresse') is None:
        raise KeyError(f"{item} ({type(item)} hat weder Adresse noch lage!")
      position = item['adresse'][:len(item.adresse.adresse)-5]
    else:
      position = item['lage']
    print(f"{item['uuid']}: {position}")
    bschrbng = item['beschreibung']
    key = position[0].upper()
    val = {'adresse': position, 'beschreibung': bschrbng}
    if item.get('adresse') is not None and item['adresse'][len(item['adresse'])-5:] == "(Wmd)":
      if item['landschaftsdenkmal']:
        insert_or_append(bere_wamue_byl, key, val)
      else:
        insert_or_append(baud_wamue_byl, key, val)
    else:
      if item['landschaftsdenkmal']:
        insert_or_append(bere_rost_byl, key, val)
      else:
        insert_or_append(baud_rost_byl, key, val)

  baud_rost = {"name": "Baudenkmale", "byletter": baud_rost_byl}
  bere_rost = {"name": "Denkmalbereiche", "byletter": bere_rost_byl}
  baud_wamue = {"name": "Baudenkmale", "byletter": baud_wamue_byl}
  bere_wamue = {"name": "Denkmalbereiche", "byletter": bere_wamue_byl}
  rostock = {"name": "Rostock", "eintragsklassen": [baud_rost, bere_rost]}
  warnemuende = {"name": "Warnemünde", "eintragsklassen": [baud_wamue, bere_wamue]}
  orte = [rostock, warnemuende]

  return {"orte": orte}


def insert_or_append(dic, key, vals):
  if dic.get(key) is None:
    dic[key] = [vals]
  else:
    # insort(dic[key], vals, key=cmp_to_key(compare_adresses))
    dic[key].append(vals)
    # dic[key].sort(key=cmp_to_key(compare_adresses))
