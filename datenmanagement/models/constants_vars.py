from django.core.validators import RegexValidator
from django.db.models import options

#
# Datenmodelloptionen bzw. Meta-Attribute für Datenmodelle
#

options.DEFAULT_NAMES += (
  'codelist',
  # optional;
  # Boolean;
  # Handelt es sich um eine Codeliste, die dann für normale Benutzer in der
  # Liste der verfügbaren Datenmodelle nicht auftaucht (True)?
  'complex',
  # optional;
  # Boolean;
  # Handelt es sich um ein komplexes Datenmodell (True)?
  'description',
  # Pflicht;
  # Text;
  # Beschreibung bzw. Langtitel des Datenmodells
  'catalog_link_fields',
  # optional;
  # Dictionary;
  # Namen der Felder (als Keys), die im Formular mit einem entsprechenden
  # Katalog verlinkt werden sollen, mit ihren Links (als Values)
  'choices_models_for_choices_fields',
  # optional;
  # Dictionary;
  # Namen der Felder (als Keys), denen Modelle (als Values) zugewiesen sind,
  # die zur Befüllung entsprechender Auswahllisten herangezogen werden sollen
  'list_fields',
  # Pflicht;
  # Dictionary;
  # Namen der Felder (als Keys), die in genau dieser Reihenfolge in der
  # Tabelle der Listenansicht als Spalten auftreten sollen, mit ihren Labels
  # (als Values)
  'list_fields_with_number',
  # optional;
  # Liste;
  # Liste mit den Namen der Felder aus list_fields, deren Werte von einem
  # numerischen Datentyp sind und die daher entsprechend behandelt werden
  # müssen, damit die Sortierung in der Tabelle
  # der Listenansicht funktioniert
  'list_fields_with_date',
  # optional;
  # Liste;
  # Liste mit den Namen der Felder aus list_fields, deren Werte vom Datentyp
  # Datum sind und die daher entsprechend behandelt werden müssen, damit die
  # Sortierung in der Tabelle der Listenansicht funktioniert
  'list_fields_with_datetime',
  # optional;
  # Liste;
  # Liste mit den Namen der Felder aus list_fields, deren Werte vom Datentyp
  # Datum mit Zeit sind und die daher entsprechend behandelt werden müssen,
  # damit die Sortierung in der Tabelle der Listenansicht funktioniert
  'list_fields_with_foreign_key',
  # optional;
  # Dictionary;
  # Namen der Felder (als Keys) aus list_fields, die für die Tabelle der
  # Listenansicht in Namen von Fremdschlüsselfeldern (als Values) umgewandelt
  # werden sollen, damit sie in der jeweils referenzierten Tabelle auch
  # gefunden und in der Tabelle der Listenansicht dargestellt werden
  'fields_with_foreign_key_to_linkify',
  # optional;
  # Liste;
  # Liste mit den Namen der Felder, deren Werte mit Fremdschlüssellinks
  # versehen werden sollen
  'associated_models',
  # optional;
  # Dictionary;
  # Sollen andere Modelle (als Keys), die mit Fremdschlüsselfeldern
  # (als Values) auf dieses Model verweisen, herangezogen werden, um
  # entsprechende Links auf der Bearbeitungsseite und in der Tabelle der
  # Listenansicht dieses Modelle bereitzustellen?
  'highlight_flag',
  # optional;
  # Text;
  # Name des Boolean-Feldes, dessen Wert als Flag zum Highlighten
  # entsprechender Zeilen herangezogen werden soll
  'readonly_fields',
  # optional;
  # Liste;
  # Namen der Felder, die in der Hinzufügen-/Änderungsansicht nur lesbar
  # erscheinen sollen
  'object_title',
  # optional;
  # Text;
  # Textbaustein für die Löschansicht (relevant nur bei Modellen mit
  # Fremdschlüssel)
  'foreign_key_label',
  # optional ; Text       ; Titel des Feldes mit dem Fremdschlüssel
  # (relevant nur bei Modellen mit Fremdschlüssel)
  'map_feature_tooltip_field',
  # optional;
  # Text;
  # Name des Feldes, dessen Werte in der Kartenansicht als Tooltip der
  # Kartenobjekte angezeigt werden sollen
  'map_feature_tooltip_fields',
  # optional;
  # Liste;
  # Namen der Felder, deren Werte in genau dieser Reihenfolge jeweils
  # getrennt durch ein Leerzeichen zusammengefügt werden sollen, damit das
  # Ergebnis in der Kartenansicht als Tooltip der Kartenobjekte angezeigt
  # werden kann
  'map_one_click_filters',
  # optional;
  # Boolean;
  # Soll(en) der/die Ein-Klick-Filter in der Kartenansicht greifen,
  # der/die im Template für dieses Datenmodell definiert ist/sind (True)?
  'map_rangefilter_fields',
  # optional;
  # Dictionary;
  # Namen der Felder (als Keys), die in genau dieser Reihenfolge in der
  # Kartenansicht als Intervallfilter auftreten sollen, mit ihren Titeln
  # (als Values) – Achtung: Verarbeitung immer paarweise!
  'map_deadlinefilter_fields',
  # optional;
  # Liste;
  # Namen von genau zwei Datumsfeldern, die in der Kartenansicht für einen
  # Stichtagsfilter herangezogen werden sollen – Achtung: Verarbeitung nur
  # als Paar!
  'map_filter_fields',
  # optional;
  # Dictionary;
  # Namen der Felder (als Keys), die in genau dieser Reihenfolge in der
  # Kartenansicht als Filter auftreten sollen, mit ihren Titeln (als Values)
  'map_filter_fields_as_list',
  # optional;
  # Liste;
  # Namen der Felder aus map_filter_fields, die als Listenfilter dargestellt werden sollen
  'map_filter_fields_as_checkbox',
  # optional;
  # Liste;
  # Namen der Felder aus map_filter_fields, die als Checkboxen-Set dargestellt werden sollen
  # (Achtung: Hierbei darf es sich nicht um jene Felder aus map_filter_fields handeln,
  # die ohnehin bereits Mehrfachauswahlfelder sind!)
  'map_filter_boolean_fields_as_checkbox',
  # optional;
  # Boolean;
  # Sollen Boolean-Felder, die in der Kartenansicht als Filter auftreten
  # sollen, als Checkboxen-Set dargestellt werden (True)?
  'map_filter_hide_initial',
  # optional;
  # Dictionary;
  # Name des Feldes (als Key), dessen bestimmter Wert (als Value) dazu führen
  # soll, Objekte initial nicht auf der Karte erscheinen, die in diesem Feld
  # genau diesen bestimmten Wert aufweisen
  'address_type',
  # optional;
  # Text;
  # Typ des Adressenbezugs: Adresse (Adresse), Straße (Straße) oder Gemeindeteil (Gemeindeteil)
  'address_mandatory',
  # optional;
  # Boolean;
  # Soll die Adresse, die Straße oder der Gemeindeteil (je nach Typ des Adressenbezugs)
  # eine Pflichtangabe sein (True)?
  'geometry_type',
  # optional;
  # Text;
  # Geometrietyp
  'thumbs',
  # optional;
  # Boolean;
  # Sollen Thumbnails aus den hochgeladenen Fotos erzeugt werden (True)?
  'multi_foto_field',
  # optional;
  # Boolean;
  # Sollen mehrere Fotos hochgeladen werden können (True)? Es werden dann
  # automatisch mehrere Datensätze erstellt, und zwar jeweils einer pro Foto.
  # Achtung: Es muss bei Verwendung dieser Option ein Pflichtfeld mit Namen
  # 'foto' existieren!
  'group_with_users_for_choice_field',
  # optional;
  # Text;
  # Name der Gruppe von Benutzern, die für das Feld
  # Ansprechpartner:in/Bearbeiter:in in einer entsprechenden Auswahlliste
  # genutzt werden sollen
  'additional_wms_layers',
  # optional;
  # Liste;
  # Eigenschaften zusätzlicher WMS-Layer, die für dieses Modell in den
  # jeweiligen Kartenansichten optional mit angeboten werden sollen
  'as_overlay',
  # optional;
  # Boolean;
  # Zusätzliche Overlay Layer
  'gpx_input',
  # optional;
  # Boolean;
  # Gibt an, ob ein GPX-Upload-Feld im Formular angezeigt werden soll.
  'postcode_assigner',
  # optional;
  # Text;
  # Name des Feldes, das im Formular mit einer Funktion zur
  # automatischen Zuweisung einer Postleitzahl ausgestattet werden soll.
  'heavy_load_limit'
  # optional;
  # Zahl;
  # Limit für einzelne Datenladeschritte in Kartenübersicht,
  # falls sehr große Datenmenge zu erwarten ist.

)

#
# Validatoren
#

# allgemein

akut_regex = r'^(?!.*´).*$'
akut_message = 'Der Text darf keine Akute (´) enthalten. Stattdessen muss ' \
               'der typographisch korrekte Apostroph (’) verwendet werden.'
anfuehrungszeichen_regex = r'^(?!.*\").*$'
anfuehrungszeichen_message = 'Der Text darf keine doppelten ' \
                             'Schreibmaschinensatz-Anführungszeichen (") ' \
                             'enthalten. Stattdessen müssen die ' \
                             'typographisch korrekten Anführungszeichen ' \
                             '(„“) verwendet werden.'
ansprechpartner_regex = r'^(?!.*\(.*[A-Z]+.*\)).*'
ansprechpartner_message = 'Die E-Mail-Adresse der <strong><em>Ansprechpartnerin</em></strong> ' \
                          'oder des <strong><em>Ansprechpartners</em></strong> ' \
                          'darf keine Großbuchstaben enthalten.'
apostroph_regex = r'^(?!.*\').*$'
apostroph_message = 'Der Text darf keine einfachen ' \
                    'Schreibmaschinensatz-Anführungszeichen (\') enthalten. ' \
                    'Stattdessen muss der typographisch korrekte Apostroph' \
                    '(’) verwendet werden.'
bindestrich_leerzeichen_regex = r'^(?!.*- ).*$'
bindestrich_leerzeichen_message = 'Im Text darf nach einen Bindestrich kein ' \
                                  'Leerzeichen stehen.'
doppelleerzeichen_regex = r'^(?!.*  ).*$'
doppelleerzeichen_message = 'Der Text darf keine doppelten Leerzeichen ' \
                            'und/oder Zeilenumbrüche enthalten.'
email_message = 'Die <strong><em>E-Mail-Adresse</em></strong> muss ' \
                'syntaktisch korrekt sein und daher folgendes Format ' \
                'aufweisen: abc-123.098_zyx@xyz-567.def.abc'
gravis_regex = r'^(?!.*`).*$'
gravis_message = 'Der Text darf keine Gravis (`) enthalten. Stattdessen ' \
                 'muss der typographisch korrekte Apostroph (’) ' \
                 'verwendet werden.'
hausnummer_zusatz_regex = r'^[a-z]$'
hausnummer_zusatz_message = 'Der <strong><em>Hausnummernzusatz</em>' \
                            '</strong>muss aus genau einem ' \
                            'Kleinbuchstaben bestehen.'
inventarnummer_regex = r'^[0-9]{8}$'
inventarnummer_message = 'Die <strong><em>Inventarnummer</em></strong> muss ' \
                         'aus genau acht Ziffern bestehen.'
leerzeichen_bindestrich_regex = r'^(?!.* -).*$'
leerzeichen_bindestrich_message = 'Im Text darf vor einem Bindestrich kein ' \
                                  'Leerzeichen stehen.'
postleitzahl_regex = r'^[0-9]{5}$'
postleitzahl_message = 'Die <strong><em>Postleitzahl</em></strong> ' \
                       'muss aus genau fünf Ziffern bestehen.'
rufnummer_regex = r'^\+(1 )?([0-9]{1,3}) [1-9][0-9]{1,5} [0-9]{1,13}$'
rufnummer_message = 'Die Schreibweise von ' \
                    '<strong><em>Rufnummern</em></strong> muss der ' \
                    'Empfehlung E.123 der Internationalen Fernmeldeunion ' \
                    'entsprechen und daher folgendes Format aufweisen: ' \
                    '+49 381 3816256'
url_message = 'Die Adresse der <strong><em>Website</em></strong> muss ' \
              'syntaktisch korrekt sein und daher folgendes Format ' \
              'aufweisen: http[s]://abc-123.098_zyx.xyz-567/def/abc'
standard_validators = [
  RegexValidator(regex=akut_regex, message=akut_message),
  RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message),
  RegexValidator(regex=apostroph_regex, message=apostroph_message),
  RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message),
  RegexValidator(regex=gravis_regex, message=gravis_message)
]
ansprechpartner_validators = standard_validators
ansprechpartner_validators.append(
  RegexValidator(regex=ansprechpartner_regex, message=ansprechpartner_message)
)
personennamen_validators = standard_validators
personennamen_validators.extend([
  RegexValidator(regex=bindestrich_leerzeichen_regex, message=bindestrich_leerzeichen_message),
  RegexValidator(regex=leerzeichen_bindestrich_regex, message=leerzeichen_bindestrich_message)
])

# speziell

denk_nummer_regex = r'^[0-9]+[a-z]*$'
denk_nummer_message = 'Die <strong><em>Nummer</em></strong> muss mit ' \
                      'einer Ziffer beginnen und mit einer Ziffer ' \
                      'oder einem Kleinbuchstaben enden.'
dl_aktenzeichen_regex = r'^[A-Z-]{2,}\.[0-9]{1,2}-[0-9]{1,2}(-[0-9]{1,2})?$'
dl_aktenzeichen_message = 'Das <strong><em>Aktenzeichen' \
                          '</em></strong> muss aus ' \
                          'mindestens zwei ' \
                          'Großbuchstaben und/oder ' \
                          'Bindestrichen, gefolgt von ' \
                          'genau einem Punkt, einer ' \
                          'oder zwei Ziffern, ' \
                          'gefolgt von genau einem ' \
                          'Bindestrich, und abermals ' \
                          'einer oder zwei Ziffern ' \
                          'bestehen. Darauf können ' \
                          'optional nochmals genau ein ' \
                          'Bindestrich sowie ' \
                          'abermals eine oder zwei ' \
                          'Ziffern folgen.'
fw_sr_code_regex = r'^[A-C]$'
fw_sr_code_message = 'Der <strong><em>Code</em></strong> muss entweder ' \
                     '<em>A,</em> <em>B</em> oder <em>C</em> lauten.'
haef_abkuerzung_regex = r'^[A-Z-]{3,5}$'
haef_abkuerzung_message = 'Die <strong><em>Abkürzung</em></strong> muss ' \
                          'aus drei, vier oder fünf Großbuchstaben ' \
                          'und/oder Bindestrichen bestehen.'
hnr_antragsnummer_regex = r'^[0-9]{2}H[0-9]{3}$'
hnr_antragsnummer_message = 'Die <strong><em>Antragsnummer</em></strong> ' \
                            'muss aus genau zwei Ziffern, gefolgt vom ' \
                            'Großbuchstaben H, und abermals genau drei ' \
                            'Ziffern bestehen.'
hst_hst_hafas_id_regex = r'^[0-9]{8}$'
hst_hst_hafas_id_message = 'Die <strong><em>HAFAS-ID</em></strong> muss aus ' \
                           'genau acht Ziffern bestehen.'
hyd_bezeichnung_regex = r'^HSA .*$'
hyd_bezeichnung_message = 'Die <strong><em>Bezeichnung</em></strong> ' \
                          'muss mit der Großbuchstabenfolge ' \
                          '<em>HSA</em> beginnen, gefolgt von genau ' \
                          'einem Leerzeichen. Die übrigen Zeichen ' \
                          'können beliebig gewählt werden.'
lin_linie_regex = r'^[A-Z0-9]+[A-Z0-9]*$'
lin_linie_message = 'Die <strong><em>Linie</em></strong> muss mit einer ' \
                    'Ziffer oder einem Großbuchstaben beginnen, der bzw. ' \
                    'dem optional weitere Ziffern und/oder ' \
                    'Großbuchstaben folgen können.'
mit_personalnummer_regex = r'^[0-9]{6}$'
mit_personalnummer_message = 'Die <strong><em>Personalnummer</em></strong> muss aus ' \
                           'genau sechs Ziffern bestehen.'
psa_bewohnerparkgebiet_regex = r'^[A-Z][0-9]$'
psa_bewohnerparkgebiet_message = 'Das <strong><em>Bewohnerparkgebiet</em>' \
                                 '</strong> muss aus genau einem ' \
                                 'Großbuchstaben sowie genau einer Ziffer ' \
                                 'bestehen.'
psa_geraetenummer_regex = r'^[0-9]{2}_[0-9]{5}$'
psa_geraetenummer_message = 'Die <strong><em>Gerätenummer</em></strong> ' \
                            'muss aus genau zwei Ziffern, gefolgt von genau ' \
                            'einem Unterstrich, und abermals genau fünf ' \
                            'Ziffern bestehen.'
poll_nummer_regex = r'^[A-Z][0-9]{0,2}$'
poll_nummer_message = 'Die <strong><em>Nummer</em></strong> muss aus ' \
                      'genau einem Großbuchstaben bestehen, der um eine ' \
                      'oder zwei Ziffer(n) ergänzt werden kann.'
quar_code_regex = r'^[0-9]{3}$'
quar_code_message = 'Der <strong><em>Code</em></strong> muss aus genau drei Ziffern bestehen.'
twnb_nummer_regex = r'^13003000-[0-9]{3}$'
twnb_nummer_message = 'Die <strong><em>Nummer</em></strong> muss aus ' \
                      '<em>13003000-,</em> gefolgt von genau drei ' \
                      'Ziffern, bestehen.'
uvp_vh_registriernummer_bauamt_regex = r'^[0-9]{5}-[0-9]{2}$'
uvp_vh_registriernummer_bauamt_message = 'Die <strong><em>Registriernummer ' \
                                         'des Bauamtes</em></strong> muss ' \
                                         'aus genau fünf Ziffern, gefolgt ' \
                                         'von genau einem Bindestrich und ' \
                                         'genau zwei Ziffern bestehen.'
zon_psa_zone_regex = r'^[A-Z]$'
zon_psa_zone_message = 'Die <strong><em>Zone</em></strong> ' \
                       'muss aus genau einem Großbuchstaben bestehen.'
