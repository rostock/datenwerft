#
# validators
#

arrondierungsflaechen_registriernummer_regex = r'^[0-9]+(\.)?([0-9]+)?$'
arrondierungsflaechen_registriernummer_message = (
  'Die <strong><em>Registriernummer</em>'
  '</strong> muss eines der folgenden Formate '
  'aufweisen (Beispiele): '
  '10244, 484.42 oder 2456.1'
)
bevollmaechtigte_bezirksschornsteinfeger_bezirk_regex = r'^[A-Z]{3}-[0-9]{2}$'
bevollmaechtigte_bezirksschornsteinfeger_bezirk_message = (
  'Der <strong><em>Bezirk</em></strong> '
  'muss aus drei Großbuchstaben, einem '
  'Bindestrich und zwei Ziffern bestehen.'
)
brunnen_d3_regex = r'^[0-9]{2,3}\.[0-9]#[0-9]{2}-[0-9]{3}\/[0-9]{3}$'
brunnen_d3_message = (
  'Die <strong><em>d.3</em></strong>-Nummer muss eines der folgenden '
  'Formate aufweisen (Beispiele): 552.6#04-004/008 (für einen Vorgang) '
  'oder 55.2#02-002/009 (für einen Vorgang).'
)
denksteine_nummer_regex = r'^[0-9]+[a-z]*$'
denksteine_nummer_message = (
  'Die <strong><em>Nummer</em></strong> muss mit '
  'einer Ziffer beginnen und mit einer Ziffer '
  'oder einem Kleinbuchstaben enden.'
)
durchlaesse_aktenzeichen_regex = r'^[A-Z-]{2,}\.[0-9]{1,2}-[0-9]{1,2}(-[0-9]{1,2})?$'
durchlaesse_aktenzeichen_message = (
  'Das <strong><em>Aktenzeichen'
  '</em></strong> muss aus '
  'mindestens zwei '
  'Großbuchstaben und/oder '
  'Bindestrichen, gefolgt von '
  'genau einem Punkt, einer '
  'oder zwei Ziffern, '
  'gefolgt von genau einem '
  'Bindestrich, und abermals '
  'einer oder zwei Ziffern '
  'bestehen. Darauf können '
  'optional nochmals genau ein '
  'Bindestrich sowie '
  'abermals eine oder zwei '
  'Ziffern folgen.'
)
erdwaermesonden_aktenzeichen_regex = (
  r'^B\/EW\/[0-9]{2}\/[0-9]{4}$|'
  r'^WST\/[0-9]{2}\/[0-9]{4}$|'
  r'^73\.40\.[0-9]{2}\.[0-9]{2}-[0-9]*$|'
  r'^73\.40\.[0-9]{2}\.[0-9]{2}-[0-9]*-Ä$'
)
erdwaermesonden_aktenzeichen_message = (
  'Das <strong><em>Aktenzeichen</em></strong> muss '
  'eines der folgenden Formate aufweisen (Beispiele): '
  'B/EW/02/2005, WST/20/2015, 73.40.01.05-2001 oder '
  '73.40.01.05-2102-Ä'
)
erdwaermesonden_d3_regex = r'^[0-9]{3}\.[0-9]#[0-9]{2}-[0-9]{3}\/[0-9]{3}$'
erdwaermesonden_d3_message = (
  'Die <strong><em>d.3</em></strong>-Nummer muss folgendes '
  'Format aufweisen (Beispiel): 552.6#04-004/008 (für einen Vorgang).'
)
fahrbahnwinterdienst_code_regex = r'^[A-C]$'
fahrbahnwinterdienst_code_message = (
  'Der <strong><em>Code</em></strong> muss entweder <em>A,</em> <em>B</em> oder <em>C</em> lauten.'
)
gemeinbedarfsflaechen_registriernummer_regex = r'^[0-9]+(\.)?([0-9]+)?$'
gemeinbedarfsflaechen_registriernummer_message = (
  'Die <strong><em>Registriernummer</em>'
  '</strong> muss eines der folgenden Formate '
  'aufweisen (Beispiele): '
  '10244, 484.42 oder 2456.1'
)
haefen_abkuerzung_regex = r'^[A-Z-]{3,5}$'
haefen_abkuerzung_message = (
  'Die <strong><em>Abkürzung</em></strong> muss '
  'aus drei, vier oder fünf Großbuchstaben '
  'und/oder Bindestrichen bestehen.'
)
hausnummern_antragsnummer_regex = r'^[0-9]{2}H[0-9]{3}$'
hausnummern_antragsnummer_message = (
  'Die <strong><em>Antragsnummer</em></strong> '
  'muss aus genau zwei Ziffern, gefolgt vom '
  'Großbuchstaben H, und abermals genau drei '
  'Ziffern bestehen.'
)
haltestellenkataster_hafas_id_regex = r'^[0-9]{8}$'
haltestellenkataster_hafas_id_message = (
  'Die <strong><em>HAFAS-ID</em></strong> muss aus genau acht Ziffern bestehen.'
)
hydranten_bezeichnung_regex = r'^HSA .*$'
hydranten_bezeichnung_message = (
  'Die <strong><em>Bezeichnung</em></strong> '
  'muss mit der Großbuchstabenfolge '
  '<em>HSA</em> beginnen, gefolgt von genau '
  'einem Leerzeichen. Die übrigen Zeichen '
  'können beliebig gewählt werden.'
)
ingenieurbauwerke_baujahr_regex = (
  r'^[0-9]{4}$|'
  r'^[0-9]{4}\/[0-9]{4}$'
)
ingenieurbauwerke_baujahr_message = (
  'Das <strong><em>Baujahr</em></strong> muss '
  'eines der folgenden Formate aufweisen (Beispiele): '
  '2002 oder 1980/1999'
)
ingenieurbauwerke_nummer_asb_regex = (
  r'^[0-9]{4}\:$|'
  r'^[0-9]{4}\:[0-9]{3}$|'
  r'^[0-9]{4}\:[0-9]{3} [0-9]$|'
  r'^[0-9]{4}\:[0-9]{3} [A-Z]$|'
  r'^[0-9]{4}\:[0-9]{3} [A-Z][0-9]$'
)
ingenieurbauwerke_nummer_asb_message = (
  'Die <strong><em>ASB-Nummer</em></strong> muss '
  'eines der folgenden Formate aufweisen (Beispiele): '
  '1838:, 1838:661, 1838:802 1, 1838:862 A oder 1838:520 A2'
)
kleinklaeranlagen_zulassung_regex = r'^Z-55\.[0-9]{1,2}-[0-9]{1,3}$'
kleinklaeranlagen_zulassung_message = (
  'Die <strong><em>Zulassung</em></strong> muss folgendes Format aufweisen (Beispiel): Z-55.32-608'
)
linien_linie_regex = r'^[A-Z0-9]+[A-Z0-9]*$'
linien_linie_message = (
  'Die <strong><em>Linie</em></strong> muss mit einer '
  'Ziffer oder einem Großbuchstaben beginnen, der bzw. '
  'dem optional weitere Ziffern und/oder Großbuchstaben folgen können.'
)
mobilfunkantennen_stob_regex = r'^[0-9]{6,8}$'
mobilfunkantennen_stob_message = (
  'Die <strong><em>Standortbescheinigungsnummer</em></strong> '
  'muss aus sechs bis acht Ziffern bestehen.'
)
parkscheinautomaten_bewohnerparkgebiet_regex = r'^[A-Z][0-9]$'
parkscheinautomaten_bewohnerparkgebiet_message = (
  'Das <strong><em>Bewohnerparkgebiet</em>'
  '</strong> muss aus genau einem '
  'Großbuchstaben sowie genau einer Ziffer '
  'bestehen.'
)
parkscheinautomaten_geraetenummer_regex = r'^[0-9]{2}_[0-9]{5}$'
parkscheinautomaten_geraetenummer_message = (
  'Die <strong><em>Gerätenummer</em></strong> '
  'muss aus genau zwei Ziffern, gefolgt von genau '
  'einem Unterstrich, und abermals genau fünf '
  'Ziffern bestehen.'
)
parkscheinautomaten_zone_regex = r'^[A-Z]$'
parkscheinautomaten_zone_message = (
  'Die <strong><em>Zone</em></strong> muss aus genau einem Großbuchstaben bestehen.'
)
quartiere_code_regex = r'^[0-9]{3}$'
quartiere_code_message = 'Der <strong><em>Code</em></strong> muss aus genau drei Ziffern bestehen.'
strassen_schluessel_regex = r'^[0-9]{5}$'
strassen_schluessel_message = (
  'Der <strong><em>Schlüssel</em></strong> muss aus genau fünf Ziffern bestehen.'
)
trinkwassernotbrunnen_nummer_regex = r'^13003000-[0-9]{3}$'
trinkwassernotbrunnen_nummer_message = (
  'Die <strong><em>Nummer</em></strong> muss aus '
  '<em>13003000-,</em> gefolgt von genau drei '
  'Ziffern, bestehen.'
)
uvp_registriernummer_bauamt_regex = r'^[0-9]{5}-[0-9]{2}$'
uvp_registriernummer_bauamt_message = (
  'Die <strong><em>Registriernummer '
  'des Bauamtes</em></strong> muss '
  'aus genau fünf Ziffern, gefolgt '
  'von genau einem Bindestrich und '
  'genau zwei Ziffern bestehen.'
)
wikipedia_regex = r'^https:\/\/de.wikipedia.org\/wiki\/.*$'
wikipedia_message = (
  'Der <strong><em>Link auf Wikipedia</em></strong> muss folgendes '
  'Format aufweisen (Beispiel): https://de.wikipedia.org/wiki/Albert_Einstein'
)


#
# enums
#

ANERKENNUNGSGEBUEHREN_HERRSCHEND_GRUNDBUCHEINTRAG = (
  ('ja', 'ja'),
  ('nein', 'nein'),
  ('prüfen', 'prüfen'),
)
