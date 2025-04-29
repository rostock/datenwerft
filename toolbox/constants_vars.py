from django.core.validators import RegexValidator

#
# validators
#

akut_regex = r'^(?!.*´).*$'
akut_message = (
  'Texte dürfen keine Akute (´) enthalten. Stattdessen muss '
  'der typographisch korrekte Apostroph (’) verwendet werden.'
)
anfuehrungszeichen_regex = r'^(?!.*\").*$'
anfuehrungszeichen_message = (
  'Texte dürfen keine doppelten '
  'Schreibmaschinensatz-Anführungszeichen (") '
  'enthalten. Stattdessen müssen die '
  'typographisch korrekten Anführungszeichen '
  '(„“) verwendet werden.'
)
aktenzeichen_anerkennungsgebuehren_regex = r'^2334NA[0-9]{6}$'
aktenzeichen_anerkennungsgebuehren_message = (
  'Das <strong><em>Aktenzeichen '
  'Anerkennungsgebühren</em></strong> muss folgendes Format aufweisen '
  '(Beispiel): 2334NA100038'
)
aktenzeichen_kommunalvermoegen_regex = r'^[0-9]{6}\/[0-9]{3}$'
aktenzeichen_kommunalvermoegen_message = (
  'Das <strong><em>Aktenzeichen Kommunalvermögen</em>'
  '</strong> muss folgendes Format aufweisen (Beispiel): '
  '009465/017'
)
ansprechpartner_regex = r'^(?!.*\(.*[A-Z]+.*\)).*'
ansprechpartner_message = (
  'Die E-Mail-Adresse der <strong><em>Ansprechpartnerin</em></strong> '
  'oder des <strong><em>Ansprechpartners</em></strong> '
  'darf keine Großbuchstaben enthalten.'
)
apostroph_regex = r'^(?!.*\').*$'
apostroph_message = (
  'Texte dürfen keine einfachen '
  "Schreibmaschinensatz-Anführungszeichen (') enthalten. "
  'Stattdessen muss der typographisch korrekte Apostroph'
  '(’) verwendet werden.'
)
bindestrich_leerzeichen_regex = r'^(?!.*- ).*$'
bindestrich_leerzeichen_message = 'Im Text darf nach einem Bindestrich kein Leerzeichen stehen.'
d3_regex = r'^[0-9]{3}\.[0-9]{1,5}(-[0-9]{3}(\/[0-9]{3})?)?$'
d3_message = (
  'Der <strong><em>d.3</em></strong>-Vorgang muss folgendes Format aufweisen '
  '(Beispiele): 512.431-003/002 oder 002.13 oder 114.521-025'
)
dateiname_regex = r'^[a-z-]*(\.?[a-z]*?)$'
dateiname_message = (
  'Es dürfen nur Kleinbuchstaben – exklusive ä, ö, ü sowie ß – und Bindestriche verwendet werden'
  'sowie optional am Ende eine durch Punkt abgetrennte Dateiendung.'
)
doppelleerzeichen_regex = r'^(?!.*  ).*$'
doppelleerzeichen_message = 'Texte dürfen keine doppelten Leerzeichen enthalten.'
email_message = (
  'E-Mail-Adressen müssen syntaktisch korrekt sein und daher folgendes Format '
  'aufweisen (Beispiele): abc@def.xyz oder 1cba_mno.asff@xy.a23c.zy'
)
gravis_regex = r'^(?!.*`).*$'
gravis_message = (
  'Texte dürfen keine Gravis (`) enthalten. Stattdessen '
  'muss der typographisch korrekte Apostroph (’) verwendet werden.'
)
hausnummer_regex = r'^[1-9][0-9]{0,2}[a-z]?$'
hausnummer_message = (
  'Die <strong><em>Hausnummer</em></strong> muss eine Zahl '
  'zwischen 1 und 999 sein, optional direkt gefolgt von einem Kleinbuchstaben.'
)
hausnummer_zusatz_regex = r'^[a-z]$'
hausnummer_zusatz_message = (
  'Der <strong><em>Hausnummernzusatz</em></strong> muss aus genau einem Kleinbuchstaben bestehen.'
)
inventarnummer_regex = r'^[0-9]{8}$'
inventarnummer_message = (
  'Die <strong><em>Inventarnummer</em></strong> muss aus genau acht Ziffern bestehen.'
)
kleinbuchstaben_bindestrich_regex = r'^[a-z-]*$'
kleinbuchstaben_bindestrich_message = (
  'Es dürfen nur Kleinbuchstaben – exklusive ä, ö, ü sowie ß – und Bindestriche verwendet werden.'
)
leerzeichen_bindestrich_regex = r'^(?!.* -).*$'
leerzeichen_bindestrich_message = 'Im Text darf vor einem Bindestrich kein Leerzeichen stehen.'
postleitzahl_regex = r'^[0-9]{5}$'
postleitzahl_message = (
  'Die <strong><em>Postleitzahl</em></strong> muss aus genau fünf Ziffern bestehen.'
)
rufnummer_regex = r'^\+(1 )?([0-9]{1,3}) [1-9][0-9]{1,5} [0-9]{1,13}$'
rufnummer_message = (
  'Die Schreibweise von Telefonnummern muss '
  'der Empfehlung E.123 der Internationalen Fernmeldeunion entsprechen '
  'und daher folgendes Format aufweisen (Beispiel): '
  '+49 381 3816256'
)
url_message = (
  'Die Adressen von Websites müssen syntaktisch korrekt sein '
  'und daher folgendes Format aufweisen (Beispiel): '
  'http[s]://abc-123.098_zyx.xyz-567/def/abc'
)
standard_validators = [
  RegexValidator(regex=akut_regex, message=akut_message),
  RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message),
  RegexValidator(regex=apostroph_regex, message=apostroph_message),
  RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message),
  RegexValidator(regex=gravis_regex, message=gravis_message),
]
ansprechpartner_validators = standard_validators[:]
ansprechpartner_validators.append(
  RegexValidator(regex=ansprechpartner_regex, message=ansprechpartner_message)
)
personennamen_validators = standard_validators[:]
personennamen_validators.extend(
  [
    RegexValidator(regex=bindestrich_leerzeichen_regex, message=bindestrich_leerzeichen_message),
    RegexValidator(regex=leerzeichen_bindestrich_regex, message=leerzeichen_bindestrich_message),
  ]
)
