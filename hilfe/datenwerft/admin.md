# Allgemein → Administration

## Benutzer:in hinzufügen

### mit LDAP

1.  ggf. sicherstellen, dass Benutzer:in in LDAP Mitglied in jener Gruppe 
    ist, die in der Einstellungsdirektive `AUTH_LDAP_REQUIRE_GROUP` eingetragen ist
    (hinfällig, falls Einstellungsdirektive `AUTH_LDAP_REQUIRE_GROUP` leer ist)
2.  Benutzer:in einmalig in *Datenwerft.HRO* an- und wieder abmelden
    lassen, sodass *Django* automatisch ein neues Benutzerobjekt anlegt
3.  als Administrator:in in *Datenwerft.HRO* anmelden
4.  in Administrationsbereich wechseln
5.  unter *Authentifizierung und Autorisierung* → *Benutzer* die/den
    Benutzer:in anklicken
6.  unter *Berechtigungen* Gruppenzugehörigkeit(en) entsprechend setzen
7.  ggf. *Mitarbeiter-Status* unter *Berechtigungen* aktivieren

### ohne LDAP

1.  als Administrator:in in *Datenwerft.HRO* anmelden
2.  in Administrationsbereich wechseln
3.  unter *Authentifizierung und Autorisierung* → *Benutzer* eine:n neue:n
    Benutzer:in anlegen
4.  unter *Authentifizierung und Autorisierung* → *Benutzer* die/den gerade
    neu angelegte:n Benutzer:in anklicken
5.  unter *Berechtigungen* Gruppenzugehörigkeit(en) entsprechend setzen
6.  ggf. *Mitarbeiter-Status* unter *Berechtigungen* aktivieren

## Berechtigungen an Datenmodell vergeben

1.  als Administrator:in in *Datenwerft.HRO* anmelden
2.  in Administrationsbereich wechseln
3.  nach *Authentifizierung und Autorisierung* → *Gruppen* navigieren
4.  entweder neue Gruppe erstellen mit entsprechendem Namen, zum
    Beispiel `datenmanagement_schulen_add`, oder vorhandene Gruppe
    auswählen, zum Beispiel `datenmanagement_schulen_full`
5.  neuer oder vorhandener Gruppe die entsprechende(n) Berechtigung(en)
    zuweisen aus dem Pool verfügbarer Berechtigungen, zum Beispiel
    `datenmanagement | Schulen | Can add Schule`
6.  neuer oder vorhandener Gruppe gewünschte Benutzer:innen zuordnen

