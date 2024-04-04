--
-- PostgreSQL database dump
--

-- Dumped from database version 15.6
-- Dumped by pg_dump version 15.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', 'public', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: basisdaten; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA basisdaten;


--
-- Name: codelisten; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA codelisten;


--
-- Name: fachdaten; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA fachdaten;


--
-- Name: fachdaten_adressbezug; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA fachdaten_adressbezug;


--
-- Name: fachdaten_gemeindeteilbezug; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA fachdaten_gemeindeteilbezug;


--
-- Name: fachdaten_strassenbezug; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA fachdaten_strassenbezug;


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: deaktiviert(); Type: FUNCTION; Schema: fachdaten; Owner: -
--

CREATE FUNCTION fachdaten.deaktiviert() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
   IF NEW.aktiv != OLD.aktiv THEN
     IF NEW.aktiv IS FALSE THEN
       NEW.deaktiviert = now()::date;
     ELSE
       NEW.deaktiviert = NULL;
     END IF;
   END IF;
   RETURN NEW;
END;
$$;


--
-- Name: foto(); Type: FUNCTION; Schema: fachdaten; Owner: -
--

CREATE FUNCTION fachdaten.foto() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
   IF NEW.foto = '' THEN
      NEW.foto := NULL; 
   END IF;
   RETURN NEW;
END;
$$;


--
-- Name: id_abfallbehaelter(); Type: FUNCTION; Schema: fachdaten; Owner: -
--

CREATE FUNCTION fachdaten.id_abfallbehaelter() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN
   NEW.id := lpad(floor(random() * 100000000)::text, 8, '0');
   RETURN NEW;
END;
$$;


--
-- Name: id_containerstellplaetze(); Type: FUNCTION; Schema: fachdaten; Owner: -
--

CREATE FUNCTION fachdaten.id_containerstellplaetze() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN
   NEW.id := lpad(floor(random() * 100)::text, 2, '0') || '-' || lpad(floor(random() * 100)::text, 2, '0');
   RETURN NEW;
END;
$$;


--
-- Name: id_denkmalbereiche(); Type: FUNCTION; Schema: fachdaten; Owner: -
--

CREATE FUNCTION fachdaten.id_denkmalbereiche() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    _id integer;
BEGIN
   EXECUTE 'SELECT CASE WHEN max(id) IS NULL THEN 0 ELSE max(id) END FROM fachdaten.denkmalbereiche_hro' INTO _id;
   NEW.id := _id + 1;
   RETURN NEW;
END;
$$;


--
-- Name: id_haltestellen(); Type: FUNCTION; Schema: fachdaten; Owner: -
--

CREATE FUNCTION fachdaten.id_haltestellen() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    _id integer;
BEGIN
   EXECUTE 'SELECT CASE WHEN max(id) IS NULL THEN 0 ELSE max(id) END FROM fachdaten.haltestellenkataster_haltestellen_hro' INTO _id;
   NEW.id := _id + 1;
   RETURN NEW;
END;
$$;


--
-- Name: id_hundetoiletten(); Type: FUNCTION; Schema: fachdaten; Owner: -
--

CREATE FUNCTION fachdaten.id_hundetoiletten() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN
   NEW.id := lpad(floor(random() * 100000000)::text, 8, '0');
   RETURN NEW;
END;
$$;


--
-- Name: laenge(); Type: FUNCTION; Schema: fachdaten; Owner: -
--

CREATE FUNCTION fachdaten.laenge() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
   IF (TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND NOT ST_Equals(NEW.geometrie ,OLD.geometrie))) AND ST_GeometryType(NEW.geometrie) ~ 'LineString' THEN
  NEW.laenge := ST_Length(NEW.geometrie);
   END IF;
   RETURN NEW;
END;
$$;


--
-- Name: laenge_in_hro(); Type: FUNCTION; Schema: fachdaten; Owner: -
--

CREATE FUNCTION fachdaten.laenge_in_hro() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
   IF (TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND NOT ST_Equals(NEW.geometrie ,OLD.geometrie))) AND ST_GeometryType(NEW.geometrie) ~ 'LineString' THEN
   NEW.laenge_in_hro := floor(random() * 32767);
    END IF;
   RETURN NEW;
END;
$$;


--
-- Name: id_baudenkmale(); Type: FUNCTION; Schema: fachdaten_adressbezug; Owner: -
--

CREATE FUNCTION fachdaten_adressbezug.id_baudenkmale() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    _id integer;
BEGIN
   EXECUTE 'SELECT CASE WHEN max(id) IS NULL THEN 0 ELSE max(id) END FROM fachdaten_adressbezug.baudenkmale_hro' INTO _id;
   NEW.id := _id + 1;
   RETURN NEW;
END;
$$;


--
-- Name: gemeindeteil(); Type: FUNCTION; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE FUNCTION fachdaten_strassenbezug.gemeindeteil() RETURNS trigger
    LANGUAGE plpgsql
    AS $_$

DECLARE
    _gemeindeteil uuid;
BEGIN
   IF (TG_OP = 'INSERT' OR (TG_OP = 'UPDATE' AND NOT ST_Equals(NEW.geometrie ,OLD.geometrie))) AND ST_GeometryType(NEW.geometrie) ~ 'LineString' THEN
   EXECUTE 'SELECT gt.uuid FROM basisdaten.gemeindeteile_datenwerft_hro gt ORDER BY (st_length(st_intersection(gt.geometrie, $1.geometrie))) DESC LIMIT 1' USING NEW INTO _gemeindeteil;
  NEW.gemeindeteil := _gemeindeteil;
   END IF;
   RETURN NEW;
END;
$_$;


--
-- Name: id(); Type: FUNCTION; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE FUNCTION fachdaten_strassenbezug.id() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN
   NEW.id := lpad(floor(random() * 1000000000)::text, 10, '0') || '-' || lpad(floor(random() * 1000)::text, 3, '0');
   RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: adressenliste_datenwerft; Type: TABLE; Schema: basisdaten; Owner: -
--

CREATE TABLE basisdaten.adressenliste_datenwerft (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    adresse character varying(255) NOT NULL,
    gemeinde character varying(255),
    gemeindeteil character varying(255),
    strasse character varying(255),
    hausnummer character varying(4),
    postleitzahl character(5),
    adresse_lang character varying(255)
);


--
-- Name: gemeindeteile_datenwerft_hro; Type: TABLE; Schema: basisdaten; Owner: -
--

CREATE TABLE basisdaten.gemeindeteile_datenwerft_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    gemeindeteil character varying(255) NOT NULL,
    geometrie public.geometry(MultiPolygon,25833) NOT NULL
);


--
-- Name: inoffizielle_strassenliste_datenwerft_hro; Type: TABLE; Schema: basisdaten; Owner: -
--

CREATE TABLE basisdaten.inoffizielle_strassenliste_datenwerft_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    strasse character varying(255) NOT NULL
);


--
-- Name: strassenliste_datenwerft; Type: TABLE; Schema: basisdaten; Owner: -
--

CREATE TABLE basisdaten.strassenliste_datenwerft (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    strasse character varying(255) NOT NULL,
    gemeinde character varying(255),
    gemeindeteil character varying(255),
    strasse_lang character varying(255)
);


--
-- Name: altersklassen_kadaverfunde; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.altersklassen_kadaverfunde (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ordinalzahl smallint NOT NULL,
    bezeichnung character varying(255) NOT NULL
);


--
-- Name: anbieter_carsharing; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.anbieter_carsharing (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    anbieter character varying(255) NOT NULL
);


--
-- Name: angebote_mobilpunkte; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.angebote_mobilpunkte (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    angebot character varying(255) NOT NULL
);


--
-- Name: angelberechtigungen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.angelberechtigungen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    angelberechtigung character varying(255) NOT NULL
);


--
-- Name: ansprechpartner_baustellen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.ansprechpartner_baustellen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    vorname character varying(255),
    nachname character varying(255),
    email character varying(255) NOT NULL
);


--
-- Name: arten_adressunsicherheiten; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_adressunsicherheiten (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_durchlaesse; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_durchlaesse (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_erdwaermesonden; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_erdwaermesonden (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_fahrradabstellanlagen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_fahrradabstellanlagen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_fairtrade; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_fairtrade (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_fallwildsuchen_kontrollen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_fallwildsuchen_kontrollen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_feldsportanlagen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_feldsportanlagen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_feuerwachen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_feuerwachen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_fliessgewaesser; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_fliessgewaesser (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_hundetoiletten; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_hundetoiletten (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_ingenieurbauwerke; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_ingenieurbauwerke (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_meldedienst_flaechenhaft; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_meldedienst_flaechenhaft (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_meldedienst_punkthaft; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_meldedienst_punkthaft (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_parkmoeglichkeiten; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_parkmoeglichkeiten (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_pflegeeinrichtungen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_pflegeeinrichtungen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_poller; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_poller (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_reisebusparkplaetze_terminals; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_reisebusparkplaetze_terminals (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_toiletten; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_toiletten (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_uvp_vorpruefungen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_uvp_vorpruefungen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_wege; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_wege (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: auftraggeber_baustellen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.auftraggeber_baustellen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    auftraggeber character varying(255) NOT NULL
);


--
-- Name: ausfuehrungen_haltestellenkataster; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.ausfuehrungen_haltestellenkataster (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ausfuehrung character varying(255) NOT NULL
);


--
-- Name: ausfuehrungen_ingenieurbauwerke; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.ausfuehrungen_ingenieurbauwerke (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ausfuehrung character varying(255) NOT NULL
);


--
-- Name: befestigungsarten_aufstellflaeche_bus_haltestellenkataster; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.befestigungsarten_aufstellflaeche_bus_haltestellenkataster (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    befestigungsart character varying(255) NOT NULL
);


--
-- Name: befestigungsarten_warteflaeche_haltestellenkataster; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.befestigungsarten_warteflaeche_haltestellenkataster (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    befestigungsart character varying(255) NOT NULL
);


--
-- Name: betriebsarten; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.betriebsarten (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    betriebsart character varying(255) NOT NULL
);


--
-- Name: betriebszeiten; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.betriebszeiten (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    betriebszeit character varying(255) NOT NULL
);


--
-- Name: bevollmaechtigte_bezirksschornsteinfeger; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.bevollmaechtigte_bezirksschornsteinfeger (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    auswaertig boolean NOT NULL,
    bezirk character(6) NOT NULL,
    bestellungszeitraum_beginn date,
    bestellungszeitraum_ende date,
    vorname character varying(255) NOT NULL,
    nachname character varying(255) NOT NULL,
    anschrift_strasse character varying(255) NOT NULL,
    anschrift_hausnummer character varying(4) NOT NULL,
    anschrift_postleitzahl character(5) NOT NULL,
    anschrift_ort character varying(255) NOT NULL,
    telefon_festnetz character varying(255),
    telefon_mobil character varying(255),
    email character varying(255),
    farbe character(7)
);


--
-- Name: bewirtschafter_betreiber_traeger_eigentuemer; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.bewirtschafter_betreiber_traeger_eigentuemer (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: dfi_typen_haltestellenkataster; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.dfi_typen_haltestellenkataster (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    dfi_typ character varying(255) NOT NULL
);


--
-- Name: e_anschluesse_parkscheinautomaten; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.e_anschluesse_parkscheinautomaten (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    e_anschluss character varying(255) NOT NULL
);


--
-- Name: ergebnisse_uvp_vorpruefungen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.ergebnisse_uvp_vorpruefungen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ergebnis character varying(255) NOT NULL
);


--
-- Name: fahrbahnwinterdienst_strassenreinigungssatzung_hro; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.fahrbahnwinterdienst_strassenreinigungssatzung_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    code character(1) NOT NULL
);


--
-- Name: fahrgastunterstandstypen_haltestellenkataster; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.fahrgastunterstandstypen_haltestellenkataster (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    fahrgastunterstandstyp character varying(255) NOT NULL
);


--
-- Name: fahrplanvitrinentypen_haltestellenkataster; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.fahrplanvitrinentypen_haltestellenkataster (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    fahrplanvitrinentyp character varying(255) NOT NULL
);


--
-- Name: fotomotive_haltestellenkataster; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.fotomotive_haltestellenkataster (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    fotomotiv character varying(255) NOT NULL
);


--
-- Name: fundamenttypen_rsag; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.fundamenttypen_rsag (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    typ character varying(255),
    erlaeuterung character varying(255)
);


--
-- Name: gebaeudearten_meldedienst_punkthaft; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.gebaeudearten_meldedienst_punkthaft (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL
);


--
-- Name: gebaeudebauweisen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.gebaeudebauweisen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    code smallint,
    bezeichnung character varying(255) NOT NULL
);


--
-- Name: gebaeudefunktionen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.gebaeudefunktionen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    code smallint,
    bezeichnung character varying(255) NOT NULL
);


--
-- Name: genehmigungsbehoerden_uvp_vorhaben; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.genehmigungsbehoerden_uvp_vorhaben (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    genehmigungsbehoerde character varying(255) NOT NULL
);


--
-- Name: geschlechter_kadaverfunde; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.geschlechter_kadaverfunde (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ordinalzahl smallint NOT NULL,
    bezeichnung character varying(255) NOT NULL
);


--
-- Name: haefen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.haefen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    abkuerzung character varying(5) NOT NULL,
    code smallint
);


--
-- Name: hersteller_poller; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.hersteller_poller (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL
);


--
-- Name: kabeltypen_lichtwellenleiterinfrastruktur; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.kabeltypen_lichtwellenleiterinfrastruktur (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    kabeltyp character varying(255) NOT NULL
);


--
-- Name: kategorien_strassen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.kategorien_strassen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    code smallint NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    erlaeuterung character varying(255) NOT NULL
);


--
-- Name: ladekarten_ladestationen_elektrofahrzeuge; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.ladekarten_ladestationen_elektrofahrzeuge (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ladekarte character varying(255) NOT NULL
);


--
-- Name: linien; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.linien (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    linie character varying(4) NOT NULL
);


--
-- Name: mastkennzeichen_rsag; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.mastkennzeichen_rsag (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    kennzeichen character varying(255),
    erlaeuterung character varying(255)
);


--
-- Name: masttypen_haltestellenkataster; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.masttypen_haltestellenkataster (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    masttyp character varying(255) NOT NULL
);


--
-- Name: masttypen_rsag; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.masttypen_rsag (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    typ character varying(255) NOT NULL,
    erlaeuterung character varying(255)
);


--
-- Name: materialien_denksteine; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.materialien_denksteine (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    material character varying(255) NOT NULL
);


--
-- Name: materialien_durchlaesse; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.materialien_durchlaesse (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    material character varying(255) NOT NULL
);


--
-- Name: objektarten_lichtwellenleiterinfrastruktur; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.objektarten_lichtwellenleiterinfrastruktur (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    objektart character varying(255) NOT NULL
);


--
-- Name: ordnungen_fliessgewaesser; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.ordnungen_fliessgewaesser (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ordnung smallint NOT NULL
);


--
-- Name: personentitel; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.personentitel (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL
);


--
-- Name: quartiere; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.quartiere (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    code character(3) NOT NULL
);


--
-- Name: raeumbreiten_strassenreinigungssatzung_hro; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.raeumbreiten_strassenreinigungssatzung_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    raeumbreite numeric(4,2) NOT NULL
);


--
-- Name: rechtsgrundlagen_uvp_vorhaben; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.rechtsgrundlagen_uvp_vorhaben (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    rechtsgrundlage character varying(255) NOT NULL
);


--
-- Name: reinigungsklassen_strassenreinigungssatzung_hro; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.reinigungsklassen_strassenreinigungssatzung_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    code smallint NOT NULL,
    reinigungshaeufigkeit_pro_jahr smallint NOT NULL
);


--
-- Name: reinigungsrhythmen_strassenreinigungssatzung_hro; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.reinigungsrhythmen_strassenreinigungssatzung_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ordinalzahl smallint NOT NULL,
    reinigungsrhythmus character varying(255) NOT NULL,
    reinigungshaeufigkeit_pro_jahr smallint
);


--
-- Name: schaeden_haltestellenkataster; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.schaeden_haltestellenkataster (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    schaden character varying(255) NOT NULL
);


--
-- Name: schlagwoerter_bildungstraeger; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.schlagwoerter_bildungstraeger (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    schlagwort character varying(255) NOT NULL
);


--
-- Name: schlagwoerter_vereine; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.schlagwoerter_vereine (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    schlagwort character varying(255) NOT NULL
);


--
-- Name: schliessungen_poller; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.schliessungen_poller (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    schliessung character varying(255) NOT NULL
);


--
-- Name: sitzbanktypen_haltestellenkataster; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.sitzbanktypen_haltestellenkataster (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    sitzbanktyp character varying(255) NOT NULL
);


--
-- Name: sparten_baustellen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.sparten_baustellen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    sparte character varying(255) NOT NULL
);


--
-- Name: sportarten; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.sportarten (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL
);


--
-- Name: status_baudenkmale_denkmalbereiche; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.status_baudenkmale_denkmalbereiche (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    status character varying(255) NOT NULL,
    CONSTRAINT status_check CHECK ((((status)::text !~ '^ '::text) AND ((status)::text !~ ' $'::text) AND ((status)::text !~ '´'::text) AND ((status)::text !~ '`'::text) AND ((status)::text !~ '  '::text) AND ((status)::text !~ '"'::text) AND ((status)::text !~ ''''::text)))
);


--
-- Name: status_baustellen_fotodokumentation_fotos; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.status_baustellen_fotodokumentation_fotos (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    status character varying(255) NOT NULL
);


--
-- Name: status_baustellen_geplant; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.status_baustellen_geplant (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    status character varying(255) NOT NULL
);


--
-- Name: status_poller; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.status_poller (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    status character varying(255) NOT NULL
);


--
-- Name: tierseuchen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.tierseuchen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL
);


--
-- Name: typen_abfallbehaelter; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.typen_abfallbehaelter (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    typ character varying(255) NOT NULL
);


--
-- Name: typen_erdwaermesonden; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.typen_erdwaermesonden (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    typ character varying(255) NOT NULL
);


--
-- Name: typen_feuerwehrzufahrten_schilder; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.typen_feuerwehrzufahrten_schilder (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    typ character varying(255) NOT NULL
);


--
-- Name: typen_haltestellen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.typen_haltestellen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    typ character varying(255) NOT NULL
);


--
-- Name: typen_kleinklaeranlagen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.typen_kleinklaeranlagen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    typ character varying(255) NOT NULL
);


--
-- Name: typen_poller; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.typen_poller (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    typ character varying(255) NOT NULL
);


--
-- Name: typen_uvp_vorhaben; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.typen_uvp_vorhaben (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    typ character varying(255) NOT NULL
);


--
-- Name: verbuende_ladestationen_elektrofahrzeuge; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.verbuende_ladestationen_elektrofahrzeuge (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    verbund character varying(255) NOT NULL
);


--
-- Name: verkehrliche_lagen_baustellen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.verkehrliche_lagen_baustellen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    verkehrliche_lage character varying(255) NOT NULL
);


--
-- Name: verkehrsmittelklassen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.verkehrsmittelklassen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    verkehrsmittelklasse character varying(255) NOT NULL
);


--
-- Name: vorgangsarten_uvp_vorhaben; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.vorgangsarten_uvp_vorhaben (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    vorgangsart character varying(255) NOT NULL
);


--
-- Name: wegebreiten_strassenreinigungssatzung_hro; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.wegebreiten_strassenreinigungssatzung_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    wegebreite numeric(4,2) NOT NULL
);


--
-- Name: wegereinigungsklassen_strassenreinigungssatzung_hro; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.wegereinigungsklassen_strassenreinigungssatzung_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    code smallint NOT NULL,
    reinigungshaeufigkeit_pro_jahr smallint NOT NULL
);


--
-- Name: wegereinigungsrhythmen_strassenreinigungssatzung_hro; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.wegereinigungsrhythmen_strassenreinigungssatzung_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ordinalzahl smallint NOT NULL,
    reinigungsrhythmus character varying(255) NOT NULL,
    reinigungshaeufigkeit_pro_jahr smallint
);


--
-- Name: wegetypen_strassenreinigungssatzung_hro; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.wegetypen_strassenreinigungssatzung_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    wegetyp character varying(255) NOT NULL
);


--
-- Name: zeiteinheiten; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.zeiteinheiten (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    zeiteinheit character varying(255) NOT NULL,
    erlaeuterung character varying(255) NOT NULL
);


--
-- Name: zh_typen_haltestellenkataster; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.zh_typen_haltestellenkataster (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    zh_typ character varying(255) NOT NULL
);


--
-- Name: zonen_parkscheinautomaten; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.zonen_parkscheinautomaten (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    zone character(1) NOT NULL
);


--
-- Name: zustaende_kadaverfunde; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.zustaende_kadaverfunde (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ordinalzahl smallint NOT NULL,
    zustand character varying(255) NOT NULL
);


--
-- Name: zustaende_schutzzaeune_tierseuchen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.zustaende_schutzzaeune_tierseuchen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ordinalzahl smallint NOT NULL,
    zustand character varying(255) NOT NULL
);


--
-- Name: zustandsbewertungen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.zustandsbewertungen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    zustandsbewertung smallint NOT NULL
);


--
-- Name: abfallbehaelter_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.abfallbehaelter_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    id character(8) NOT NULL,
    typ uuid,
    aufstellungsjahr smallint,
    eigentuemer uuid NOT NULL,
    bewirtschafter uuid NOT NULL,
    pflegeobjekt character varying(255) NOT NULL,
    inventarnummer character(8),
    anschaffungswert numeric(6,2),
    haltestelle boolean,
    sommer_mo smallint,
    sommer_di smallint,
    sommer_mi smallint,
    sommer_do smallint,
    sommer_fr smallint,
    sommer_sa smallint,
    sommer_so smallint,
    winter_mo smallint,
    winter_di smallint,
    winter_mi smallint,
    winter_do smallint,
    winter_fr smallint,
    winter_sa smallint,
    winter_so smallint,
    bemerkungen character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: adressunsicherheiten_fotos_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.adressunsicherheiten_fotos_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adressunsicherheit uuid NOT NULL,
    aufnahmedatum date NOT NULL,
    dateiname_original character varying(255) NOT NULL,
    foto character varying(255) NOT NULL
);


--
-- Name: angelverbotsbereiche_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.angelverbotsbereiche_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    bezeichnung character varying(255),
    beschreibung character varying(1000),
    geometrie public.geometry(LineString,25833) NOT NULL
);


--
-- Name: baustellen_fotodokumentation_fotos_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.baustellen_fotodokumentation_fotos_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    baustellen_fotodokumentation_baustelle uuid NOT NULL,
    status uuid NOT NULL,
    aufnahmedatum date NOT NULL,
    dateiname_original character varying(255) NOT NULL,
    foto character varying(255) NOT NULL
);


--
-- Name: baustellen_geplant_dokumente; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.baustellen_geplant_dokumente (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    baustelle_geplant uuid NOT NULL,
    dokument character varying(255) NOT NULL,
    bezeichnung character varying(255) NOT NULL
);


--
-- Name: baustellen_geplant_links; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.baustellen_geplant_links (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    baustelle_geplant uuid NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    link character varying(255) NOT NULL
);


--
-- Name: bemas_altdaten_journalereignisse; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.bemas_altdaten_journalereignisse (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    id integer NOT NULL,
    bearbeitet boolean,
    target_created_at timestamp with time zone NOT NULL,
    target_search_content character varying(255),
    target_description text NOT NULL,
    target_complaint_id integer NOT NULL,
    target_type_of_event character varying(255) NOT NULL
);


--
-- Name: containerstellplaetze_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.containerstellplaetze_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    id character(5) NOT NULL,
    privat boolean NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    bewirtschafter_grundundboden uuid,
    bewirtschafter_glas uuid,
    anzahl_glas smallint,
    anzahl_glas_unterflur smallint,
    bewirtschafter_papier uuid,
    anzahl_papier smallint,
    anzahl_papier_unterflur smallint,
    bewirtschafter_altkleider uuid,
    anzahl_altkleider smallint,
    inbetriebnahmejahr smallint,
    inventarnummer character(8),
    inventarnummer_grundundboden character(8),
    inventarnummer_zaun character(8),
    anschaffungswert numeric(7,2),
    oeffentliche_widmung boolean,
    bga boolean,
    bga_zaun boolean,
    bga_grundundboden boolean,
    art_eigentumserwerb character varying(255),
    art_eigentumserwerb_zaun character varying(255),
    vertraege character varying(255),
    winterdienst_a boolean,
    winterdienst_b boolean,
    winterdienst_c boolean,
    flaeche numeric(5,2),
    bemerkungen character varying(255),
    foto character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: COLUMN containerstellplaetze_hro.flaeche; Type: COMMENT; Schema: fachdaten; Owner: -
--

COMMENT ON COLUMN fachdaten.containerstellplaetze_hro.flaeche IS 'Einheit: m²';


--
-- Name: denkmalbereiche_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.denkmalbereiche_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    bezeichnung character varying(255),
    beschreibung character varying(255) NOT NULL,
    geometrie public.geometry(MultiPolygon,25833) NOT NULL,
    id integer NOT NULL,
    status uuid NOT NULL,
    unterschutzstellungen date[],
    hinweise character varying(500),
    aenderungen character varying(500),
    veroeffentlichungen date[],
    denkmalnummern character varying(255)[]
);


--
-- Name: durchlaesse_durchlaesse_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.durchlaesse_durchlaesse_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    art uuid,
    aktenzeichen character varying(255) NOT NULL,
    material uuid,
    baujahr smallint,
    nennweite smallint,
    laenge numeric(5,2),
    nebenanlagen character varying(255),
    zubehoer character varying(255),
    zustand_durchlass uuid,
    zustand_nebenanlagen uuid,
    zustand_zubehoer uuid,
    kontrolle date,
    bemerkungen character varying(255),
    bearbeiter character varying(255) NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL,
    zustaendigkeit character varying(255) NOT NULL
);


--
-- Name: durchlaesse_fotos_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.durchlaesse_fotos_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    durchlaesse_durchlass uuid NOT NULL,
    dateiname_original character varying(255) NOT NULL,
    foto character varying(255) NOT NULL,
    aufnahmedatum date,
    bemerkungen character varying(255)
);


--
-- Name: erdwaermesonden_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.erdwaermesonden_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    d3 character varying(16),
    aktenzeichen character varying(18) NOT NULL,
    art uuid NOT NULL,
    typ uuid,
    awsv_anlage boolean,
    anzahl_sonden smallint,
    sondenfeldgroesse smallint,
    endteufe numeric(5,2),
    hinweis character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: fahrradabstellanlagen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.fahrradabstellanlagen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    art uuid NOT NULL,
    stellplaetze smallint,
    gebuehren boolean NOT NULL,
    ueberdacht boolean NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL,
    ebike_lademoeglichkeiten boolean
);


--
-- Name: fallwildsuchen_kontrollgebiete_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.fallwildsuchen_kontrollgebiete_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    tierseuche uuid NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    geometrie public.geometry(Polygon,25833) NOT NULL
);


--
-- Name: fallwildsuchen_nachweise_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.fallwildsuchen_nachweise_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    kontrollgebiet uuid NOT NULL,
    art_kontrolle uuid NOT NULL,
    startzeitpunkt timestamp with time zone NOT NULL,
    endzeitpunkt timestamp with time zone NOT NULL,
    geometrie public.geometry(MultiLineString,25833) NOT NULL
);


--
-- Name: feldsportanlagen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.feldsportanlagen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    art uuid NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    traeger uuid NOT NULL,
    foto character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: fliessgewaesser_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.fliessgewaesser_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    nummer character varying(255) NOT NULL,
    art uuid NOT NULL,
    ordnung uuid,
    bezeichnung character varying(255),
    nennweite smallint,
    laenge integer NOT NULL,
    laenge_in_hro integer,
    geometrie public.geometry(LineString,25833) NOT NULL
);


--
-- Name: geh_und_radwegereinigung_flaechen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.geh_und_radwegereinigung_flaechen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    geh_und_radwegereinigung uuid NOT NULL,
    geometrie public.geometry(MultiPolygon,25833) NOT NULL
);


--
-- Name: geraetespielanlagen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.geraetespielanlagen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    bezeichnung character varying(255) NOT NULL,
    traeger uuid NOT NULL,
    beschreibung character varying(255),
    foto character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: haltestellenkataster_fotos_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.haltestellenkataster_fotos_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    haltestellenkataster_haltestelle uuid NOT NULL,
    motiv uuid NOT NULL,
    aufnahmedatum date NOT NULL,
    dateiname_original character varying(255) NOT NULL,
    foto character varying(255) NOT NULL
);


--
-- Name: haltestellenkataster_haltestellen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.haltestellenkataster_haltestellen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    id integer NOT NULL,
    hst_bezeichnung character varying(255) NOT NULL,
    hst_hafas_id character(8),
    hst_bus_bahnsteigbezeichnung character varying(255),
    hst_richtung character varying(255),
    hst_kategorie character varying(255),
    hst_linien character varying(4)[],
    hst_rsag boolean,
    hst_rebus boolean,
    hst_nur_ausstieg boolean,
    hst_nur_einstieg boolean,
    hst_verkehrsmittelklassen character varying(255)[] NOT NULL,
    bau_typ uuid,
    bau_wartebereich_laenge numeric(5,2),
    bau_wartebereich_breite numeric(5,2),
    bau_befestigungsart_aufstellflaeche_bus uuid,
    bau_zustand_aufstellflaeche_bus uuid,
    bau_befestigungsart_warteflaeche uuid,
    bau_zustand_warteflaeche uuid,
    bf_einstieg boolean,
    bf_zu_abgaenge boolean,
    bf_bewegungsraum boolean,
    tl_auffindestreifen boolean,
    tl_auffindestreifen_ausfuehrung uuid,
    tl_auffindestreifen_breite smallint,
    tl_einstiegsfeld boolean,
    tl_einstiegsfeld_ausfuehrung uuid,
    tl_einstiegsfeld_breite smallint,
    tl_leitstreifen boolean,
    tl_leitstreifen_ausfuehrung uuid,
    tl_leitstreifen_laenge smallint,
    tl_aufmerksamkeitsfeld boolean,
    tl_bahnsteigkante_visuell boolean,
    tl_bahnsteigkante_taktil boolean,
    as_zh_typ uuid,
    as_h_mast boolean,
    as_h_masttyp uuid,
    as_papierkorb boolean,
    as_fahrgastunterstand boolean,
    as_fahrgastunterstandstyp uuid,
    as_sitzbank_mit_armlehne boolean,
    as_sitzbank_ohne_armlehne boolean,
    as_sitzbanktyp uuid,
    as_gelaender boolean,
    as_fahrplanvitrine boolean,
    as_fahrplanvitrinentyp uuid,
    as_tarifinformation boolean,
    as_liniennetzplan boolean,
    as_fahrplan boolean,
    as_fahrausweisautomat boolean,
    as_lautsprecher boolean,
    as_dfi boolean,
    as_dfi_typ uuid,
    as_anfragetaster boolean,
    as_blindenschrift boolean,
    as_beleuchtung boolean,
    as_hinweis_warnblinklicht_ein boolean,
    bfe_seniorenheim boolean,
    bfe_pflegeeinrichtung boolean,
    bfe_fussgaengerueberweg boolean,
    bfe_medizinische_versorgungseinrichtung boolean,
    bfe_querungshilfe boolean,
    bfe_park_and_ride boolean,
    bfe_fahrradabstellmoeglichkeit boolean,
    bearbeiter character varying(255),
    bemerkungen character varying(500),
    geometrie public.geometry(Point,25833) NOT NULL,
    hst_abfahrten smallint,
    hst_fahrgastzahl_einstieg smallint,
    hst_fahrgastzahl_ausstieg smallint
);


--
-- Name: hundetoiletten_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.hundetoiletten_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    id character(8) NOT NULL,
    art uuid,
    aufstellungsjahr smallint,
    bewirtschafter uuid NOT NULL,
    pflegeobjekt character varying(255) NOT NULL,
    inventarnummer character(8),
    anschaffungswert numeric(6,2),
    bemerkungen character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: hydranten_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.hydranten_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    bezeichnung character varying(255) NOT NULL,
    eigentuemer uuid NOT NULL,
    bewirtschafter uuid NOT NULL,
    feuerloeschgeeignet boolean NOT NULL,
    betriebszeit uuid NOT NULL,
    entnahme character varying(255),
    hauptwasserzaehler character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: kadaverfunde_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.kadaverfunde_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    tierseuche uuid NOT NULL,
    zeitpunkt timestamp with time zone NOT NULL,
    geschlecht uuid NOT NULL,
    altersklasse uuid NOT NULL,
    gewicht smallint,
    zustand uuid NOT NULL,
    art_auffinden uuid NOT NULL,
    witterung character varying(255),
    bemerkungen character varying(500),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: kunst_im_oeffentlichen_raum_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.kunst_im_oeffentlichen_raum_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    bezeichnung character varying(255) NOT NULL,
    ausfuehrung character varying(255),
    schoepfer character varying(255),
    entstehungsjahr smallint,
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: lichtwellenleiterinfrastruktur_abschnitte_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.lichtwellenleiterinfrastruktur_abschnitte_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    bezeichnung character varying(255) NOT NULL
);


--
-- Name: lichtwellenleiterinfrastruktur_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.lichtwellenleiterinfrastruktur_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    objektart uuid NOT NULL,
    geometrie public.geometry(MultiLineString,25833) NOT NULL,
    kabeltyp uuid,
    abschnitt uuid
);


--
-- Name: meldedienst_flaechenhaft_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.meldedienst_flaechenhaft_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    art uuid NOT NULL,
    bearbeiter character varying(255) NOT NULL,
    bemerkungen character varying(255),
    datum date NOT NULL,
    geometrie public.geometry(Polygon,25833) NOT NULL
);


--
-- Name: mobilpunkte_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.mobilpunkte_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    bezeichnung character varying(255) NOT NULL,
    angebote character varying(255)[] NOT NULL,
    website character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: parkscheinautomaten_parkscheinautomaten_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.parkscheinautomaten_parkscheinautomaten_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    parkscheinautomaten_tarif uuid NOT NULL,
    nummer smallint NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    zone uuid NOT NULL,
    handyparkzone integer NOT NULL,
    bewohnerparkgebiet character(2),
    geraetenummer character(8) NOT NULL,
    inbetriebnahme date,
    e_anschluss uuid NOT NULL,
    stellplaetze_pkw smallint,
    stellplaetze_bus smallint,
    haendlerkartennummer bigint,
    laufzeit_geldkarte date,
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: parkscheinautomaten_tarife_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.parkscheinautomaten_tarife_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    bezeichnung character varying(255) NOT NULL,
    zeiten character varying(255) NOT NULL,
    normaltarif_parkdauer_min smallint NOT NULL,
    normaltarif_parkdauer_min_einheit uuid NOT NULL,
    normaltarif_parkdauer_max smallint NOT NULL,
    normaltarif_parkdauer_max_einheit uuid NOT NULL,
    normaltarif_gebuehren_max numeric(4,2),
    normaltarif_gebuehren_pro_stunde numeric(3,2),
    normaltarif_gebuehrenschritte character varying(255),
    veranstaltungstarif_parkdauer_min smallint,
    veranstaltungstarif_parkdauer_min_einheit uuid,
    veranstaltungstarif_parkdauer_max smallint,
    veranstaltungstarif_parkdauer_max_einheit uuid,
    veranstaltungstarif_gebuehren_max numeric(4,2),
    veranstaltungstarif_gebuehren_pro_stunde numeric(3,2),
    veranstaltungstarif_gebuehrenschritte character varying(255),
    zugelassene_muenzen character varying(255) NOT NULL
);


--
-- Name: poller_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.poller_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    art uuid NOT NULL,
    nummer character varying(3),
    bezeichnung character varying(255) NOT NULL,
    status uuid NOT NULL,
    zeiten character varying(255),
    hersteller uuid,
    typ uuid,
    anzahl smallint NOT NULL,
    schliessungen character varying(255)[],
    bemerkungen character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: reisebusparkplaetze_terminals_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.reisebusparkplaetze_terminals_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    art uuid NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    stellplaetze smallint NOT NULL,
    gebuehren boolean NOT NULL,
    einschraenkungen character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: rsag_gleise_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.rsag_gleise_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    quelle character(255),
    geometrie public.geometry(LineString,25833) NOT NULL
);


--
-- Name: rsag_leitungen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.rsag_leitungen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    geometrie public.geometry(LineString,25833) NOT NULL
);


--
-- Name: rsag_masten_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.rsag_masten_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    mastnummer character varying(255),
    moment_am_fundament numeric(5,2),
    spitzenzug_errechnet numeric(4,2),
    spitzenzug_gewaehlt numeric(4,2),
    gesamtlaenge numeric(4,2),
    einsatztiefe numeric(4,2),
    so_bis_fundament numeric(4,2),
    boeschung numeric(4,2),
    freie_laenge numeric(4,2),
    masttyp uuid NOT NULL,
    nennmass_ueber_so smallint,
    mastgewicht integer,
    fundamenttyp uuid,
    fundamentlaenge numeric(4,2),
    fundamentdurchmesser character varying(255),
    nicht_tragfaehiger_boden numeric(4,2),
    mastkennzeichen_1 uuid,
    mastkennzeichen_2 uuid,
    mastkennzeichen_3 uuid,
    mastkennzeichen_4 uuid,
    quelle character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL,
    dgm_hoehe numeric(5,2)
);


--
-- Name: rsag_quertraeger_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.rsag_quertraeger_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    mast uuid NOT NULL,
    quelle character varying(255),
    geometrie public.geometry(LineString,25833) NOT NULL
);


--
-- Name: rsag_spanndraehte_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.rsag_spanndraehte_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    mast uuid,
    quelle character varying(255),
    geometrie public.geometry(LineString,25833) NOT NULL
);


--
-- Name: schiffsliegeplaetze_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.schiffsliegeplaetze_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    hafen uuid NOT NULL,
    liegeplatznummer character varying(255) NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    geometrie public.geometry(Polygon,25833) NOT NULL,
    liegeplatzlaenge numeric(5,2),
    zulaessiger_tiefgang numeric(4,2),
    zulaessige_schiffslaenge numeric(5,2),
    kaihoehe numeric(3,2),
    pollerzug character varying(255),
    poller_von character varying(255),
    poller_bis character varying(255)
);


--
-- Name: schutzzaeune_tierseuchen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.schutzzaeune_tierseuchen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    tierseuche uuid NOT NULL,
    zustand uuid NOT NULL,
    geometrie public.geometry(MultiLineString,25833) NOT NULL,
    laenge integer NOT NULL
);


--
-- Name: COLUMN schutzzaeune_tierseuchen_hro.laenge; Type: COMMENT; Schema: fachdaten; Owner: -
--

COMMENT ON COLUMN fachdaten.schutzzaeune_tierseuchen_hro.laenge IS 'Einheit: m';


--
-- Name: strassen_historie_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.strassen_historie_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    strasse uuid NOT NULL,
    datum character varying(255),
    beschluss character varying(255),
    veroeffentlichung character varying(255),
    historie character varying(255)
);


--
-- Name: strassen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.strassen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    kategorie uuid NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    schluessel character(5) NOT NULL,
    geometrie public.geometry(MultiLineString,25833) NOT NULL
);


--
-- Name: strassen_namensanalye_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.strassen_namensanalye_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    strasse uuid NOT NULL,
    person_weiblich boolean,
    person_maennlich boolean,
    beruf boolean,
    literatur boolean,
    historisch boolean,
    flora_fauna boolean,
    orte_landschaften boolean,
    gesellschaft boolean,
    lagehinweis boolean,
    religion boolean,
    niederdeutsch boolean,
    erlaeuterungen_intern text,
    erlaeuterungen_richter text,
    wikipedia character varying(255)
);


--
-- Name: strassenreinigung_flaechen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.strassenreinigung_flaechen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    strassenreinigung uuid NOT NULL,
    geometrie public.geometry(MultiPolygon,25833) NOT NULL
);


--
-- Name: thalasso_kurwege_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.thalasso_kurwege_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    bezeichnung character varying(255) NOT NULL,
    geometrie public.geometry(LineString,25833) NOT NULL,
    barrierefrei boolean NOT NULL,
    streckenbeschreibung character varying(255),
    farbe character(7) NOT NULL,
    beschriftung character varying(255),
    laenge integer NOT NULL
);


--
-- Name: toiletten_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.toiletten_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    art uuid NOT NULL,
    bewirtschafter uuid,
    behindertengerecht boolean NOT NULL,
    duschmoeglichkeit boolean,
    wickelmoeglichkeit boolean,
    zeiten character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: trinkwassernotbrunnen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.trinkwassernotbrunnen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    nummer character(12) NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    eigentuemer uuid,
    betreiber uuid NOT NULL,
    betriebsbereit boolean NOT NULL,
    bohrtiefe numeric(4,2) NOT NULL,
    ausbautiefe numeric(4,2) NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: uvp_vorhaben_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.uvp_vorhaben_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    bezeichnung character varying(255) NOT NULL,
    vorgangsart uuid NOT NULL,
    genehmigungsbehoerde uuid NOT NULL,
    datum_posteingang_genehmigungsbehoerde date NOT NULL,
    registriernummer_bauamt character(8),
    aktenzeichen character varying(255),
    rechtsgrundlage uuid NOT NULL,
    typ uuid NOT NULL,
    geometrie public.geometry(Polygon,25833) NOT NULL
);


--
-- Name: uvp_vorpruefungen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.uvp_vorpruefungen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    uvp_vorhaben uuid NOT NULL,
    art uuid NOT NULL,
    datum_posteingang date NOT NULL,
    datum date NOT NULL,
    ergebnis uuid NOT NULL,
    datum_bekanntmachung date,
    datum_veroeffentlichung date,
    pruefprotokoll character varying(255)
);


--
-- Name: adressunsicherheiten_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.adressunsicherheiten_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid,
    art uuid NOT NULL,
    beschreibung character varying(255) NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: aufteilungsplaene_wohnungseigentumsgesetz_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.aufteilungsplaene_wohnungseigentumsgesetz_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    adresse uuid,
    aktenzeichen character varying(255),
    datum_abgeschlossenheitserklaerung date,
    bearbeiter character varying(255) NOT NULL,
    bemerkungen character varying(255),
    datum date NOT NULL,
    pdf character varying(255) NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL,
    deaktiviert date
);


--
-- Name: baudenkmale_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.baudenkmale_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid,
    beschreibung character varying(255) NOT NULL,
    geometrie public.geometry(MultiPolygon,25833),
    id integer NOT NULL,
    status uuid NOT NULL,
    vorherige_beschreibung character varying(255),
    hinweise character varying(500),
    aenderungen character varying(500),
    unterschutzstellungen date[],
    veroeffentlichungen date[],
    denkmalnummern character varying(255)[],
    lage character varying(255),
    gartendenkmal boolean NOT NULL
);


--
-- Name: behinderteneinrichtungen_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.behinderteneinrichtungen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    adresse uuid,
    bezeichnung character varying(255) NOT NULL,
    traeger uuid NOT NULL,
    plaetze smallint,
    telefon_festnetz character varying(255),
    telefon_mobil character varying(255),
    email character varying(255),
    website character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL,
    deaktiviert date
);


--
-- Name: bemas_altdaten_beschwerden; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.bemas_altdaten_beschwerden (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid,
    id integer NOT NULL,
    bearbeitet boolean,
    reason_date_of_receipt boolean NOT NULL,
    reason_immission_point boolean NOT NULL,
    reason_originator_id boolean NOT NULL,
    reason_type_of_immission boolean NOT NULL,
    source_beschwerdefuehrer_strasse character varying(255),
    source_beschwerdefuehrer_plz character varying(255),
    source_beschwerdefuehrer_ort character varying(255),
    source_immissionsart character varying(255),
    target_search_content character varying(255),
    target_date_of_receipt date,
    target_status_updated_at timestamp with time zone,
    target_description character varying(255) NOT NULL,
    target_storage_location character varying(255),
    target_originator_id integer NOT NULL,
    target_status character varying(255) NOT NULL,
    target_type_of_immission character varying(255),
    target_complainers_organizations integer[],
    target_complainers_persons integer[],
    geometrie public.geometry(Point,25833)
);


--
-- Name: bemas_altdaten_verursacher; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.bemas_altdaten_verursacher (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid,
    id integer NOT NULL,
    bearbeitet boolean,
    reason_sector boolean NOT NULL,
    reason_emission_point boolean NOT NULL,
    source_verursacher_strasse character varying(255),
    source_verursacher_plz character varying(255),
    source_verursacher_ort character varying(255),
    source_betreiber_name character varying(255),
    source_betreiber_strasse character varying(255),
    source_betreiber_plz character varying(255),
    source_betreiber_ort character varying(255),
    target_search_content character varying(255),
    target_description character varying(255) NOT NULL,
    target_operator_organization_id integer,
    target_operator_person_id integer,
    target_sector character varying(255),
    geometrie public.geometry(Point,25833)
);


--
-- Name: beschluesse_bau_planungsausschuss_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.beschluesse_bau_planungsausschuss_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    adresse uuid,
    beschlussjahr smallint NOT NULL,
    vorhabenbezeichnung character varying(255) NOT NULL,
    bearbeiter character varying(255) NOT NULL,
    pdf character varying(255) NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL,
    deaktiviert date
);


--
-- Name: bildungstraeger_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.bildungstraeger_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    adresse uuid,
    bezeichnung character varying(255) NOT NULL,
    betreiber character varying(255) NOT NULL,
    schlagwoerter character varying(255)[] NOT NULL,
    barrierefrei boolean,
    zeiten character varying(255),
    telefon_festnetz character varying(255),
    telefon_mobil character varying(255),
    email character varying(255),
    website character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL,
    deaktiviert date
);


--
-- Name: carsharing_stationen_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.carsharing_stationen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid,
    bezeichnung character varying(255) NOT NULL,
    anbieter uuid NOT NULL,
    anzahl_fahrzeuge smallint,
    bemerkungen character varying(500),
    telefon_festnetz character varying(255),
    telefon_mobil character varying(255),
    email character varying(255),
    website character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: denksteine_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.denksteine_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid,
    nummer character varying(255) NOT NULL,
    titel uuid,
    vorname character varying(255) NOT NULL,
    nachname character varying(255) NOT NULL,
    geburtsjahr smallint NOT NULL,
    sterbejahr smallint,
    text_auf_dem_stein character varying(255) NOT NULL,
    ehemalige_adresse character varying(255),
    material uuid NOT NULL,
    erstes_verlegejahr smallint NOT NULL,
    website character varying(255) NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: fairtrade_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.fairtrade_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    adresse uuid,
    art uuid NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    betreiber character varying(255),
    barrierefrei boolean,
    zeiten character varying(255),
    telefon_festnetz character varying(255),
    telefon_mobil character varying(255),
    email character varying(255),
    website character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL,
    deaktiviert date
);


--
-- Name: feuerwachen_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.feuerwachen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    adresse uuid,
    art uuid NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    telefon_festnetz character varying(255),
    telefon_mobil character varying(255),
    email character varying(255),
    website character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL,
    deaktiviert date
);


--
-- Name: gutachterfotos_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.gutachterfotos_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid,
    bearbeiter character varying(255),
    bemerkungen character varying(255),
    datum date NOT NULL,
    aufnahmedatum date NOT NULL,
    foto character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: hospize_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.hospize_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    adresse uuid,
    bezeichnung character varying(255) NOT NULL,
    traeger uuid NOT NULL,
    plaetze smallint,
    telefon_festnetz character varying(255),
    telefon_mobil character varying(255),
    email character varying(255),
    website character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL,
    deaktiviert date
);


--
-- Name: kehrbezirke_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.kehrbezirke_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid NOT NULL,
    bevollmaechtigter_bezirksschornsteinfeger uuid,
    vergabedatum date
);


--
-- Name: kinder_jugendbetreuung_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.kinder_jugendbetreuung_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    adresse uuid,
    bezeichnung character varying(255) NOT NULL,
    traeger uuid NOT NULL,
    telefon_festnetz character varying(255),
    telefon_mobil character varying(255),
    email character varying(255),
    website character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL,
    deaktiviert date
);


--
-- Name: kindertagespflegeeinrichtungen_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.kindertagespflegeeinrichtungen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    adresse uuid,
    vorname character varying(255) NOT NULL,
    nachname character varying(255) NOT NULL,
    plaetze smallint,
    zeiten character varying(255),
    telefon_festnetz character varying(255),
    telefon_mobil character varying(255),
    email character varying(255),
    website character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL,
    deaktiviert date
);


--
-- Name: kleinklaeranlagen_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.kleinklaeranlagen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    adresse uuid,
    d3 character varying(16) NOT NULL,
    we_datum date NOT NULL,
    we_aktenzeichen character varying(255),
    we_befristung date,
    typ uuid NOT NULL,
    einleitstelle character varying(255) NOT NULL,
    gewaesser_berichtspflichtig boolean NOT NULL,
    umfang_einleitung numeric(3,2),
    einwohnerwert numeric(3,1),
    zulassung character varying(11),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: ladestationen_elektrofahrzeuge_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.ladestationen_elektrofahrzeuge_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid,
    geplant boolean NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    betreiber uuid,
    verbund uuid,
    betriebsart uuid NOT NULL,
    anzahl_ladepunkte smallint,
    arten_ladepunkte character varying(255),
    ladekarten character varying(255)[],
    kosten character varying(255),
    zeiten character varying(255),
    website character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: meldedienst_punkthaft_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.meldedienst_punkthaft_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid,
    art uuid NOT NULL,
    bearbeiter character varying(255) NOT NULL,
    bemerkungen character varying(255),
    datum date NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL,
    gebaeudeart uuid,
    flaeche numeric(6,2)
);


--
-- Name: parkmoeglichkeiten_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.parkmoeglichkeiten_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid,
    art uuid NOT NULL,
    standort character varying(255) NOT NULL,
    betreiber uuid,
    stellplaetze_pkw smallint,
    stellplaetze_wohnmobil smallint,
    stellplaetze_bus smallint,
    gebuehren_halbe_stunde numeric(3,2),
    gebuehren_eine_stunde numeric(3,2),
    gebuehren_zwei_stunden numeric(3,2),
    gebuehren_ganztags numeric(3,2),
    bemerkungen character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: pflegeeinrichtungen_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.pflegeeinrichtungen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    adresse uuid,
    art uuid NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    betreiber character varying(255) NOT NULL,
    plaetze smallint,
    telefon_festnetz character varying(255),
    telefon_mobil character varying(255),
    email character varying(255),
    website character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL,
    deaktiviert date
);


--
-- Name: rettungswachen_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.rettungswachen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    adresse uuid,
    bezeichnung character varying(255) NOT NULL,
    traeger uuid NOT NULL,
    telefon_festnetz character varying(255),
    telefon_mobil character varying(255),
    email character varying(255),
    website character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL,
    deaktiviert date
);


--
-- Name: sporthallen_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.sporthallen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    adresse uuid,
    bezeichnung character varying(255) NOT NULL,
    traeger uuid NOT NULL,
    sportart uuid NOT NULL,
    barrierefrei boolean,
    zeiten character varying(255),
    telefon_festnetz character varying(255),
    telefon_mobil character varying(255),
    email character varying(255),
    website character varying(255),
    deaktiviert date,
    geometrie public.geometry(Point,25833) NOT NULL,
    foto character varying(255)
);


--
-- Name: stadtteil_begegnungszentren_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.stadtteil_begegnungszentren_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid,
    bezeichnung character varying(255) NOT NULL,
    traeger uuid NOT NULL,
    barrierefrei boolean,
    zeiten character varying(255),
    telefon_festnetz character varying(255),
    telefon_mobil character varying(255),
    email character varying(255),
    website character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: standortqualitaeten_geschaeftslagen_sanierungsgebiet_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.standortqualitaeten_geschaeftslagen_sanierungsgebiet_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid,
    bewertungsjahr smallint NOT NULL,
    quartier uuid NOT NULL,
    kundschaftskontakte_anfangswert numeric(4,2) NOT NULL,
    kundschaftskontakte_endwert numeric(4,2) NOT NULL,
    verkehrsanbindung_anfangswert numeric(4,2) NOT NULL,
    verkehrsanbindung_endwert numeric(4,2) NOT NULL,
    ausstattung_anfangswert numeric(4,2) NOT NULL,
    ausstattung_endwert numeric(4,2) NOT NULL,
    beeintraechtigung_anfangswert numeric(4,2) NOT NULL,
    beeintraechtigung_endwert numeric(4,2) NOT NULL,
    standortnutzung_anfangswert numeric(4,2) NOT NULL,
    standortnutzung_endwert numeric(4,2) NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: standortqualitaeten_wohnlagen_sanierungsgebiet_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.standortqualitaeten_wohnlagen_sanierungsgebiet_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid,
    bewertungsjahr smallint NOT NULL,
    quartier uuid NOT NULL,
    gesellschaftslage_anfangswert numeric(4,2) NOT NULL,
    gesellschaftslage_endwert numeric(4,2) NOT NULL,
    verkehrsanbindung_anfangswert numeric(4,2) NOT NULL,
    verkehrsanbindung_endwert numeric(4,2) NOT NULL,
    ausstattung_anfangswert numeric(4,2) NOT NULL,
    ausstattung_endwert numeric(4,2) NOT NULL,
    beeintraechtigung_anfangswert numeric(4,2) NOT NULL,
    beeintraechtigung_endwert numeric(4,2) NOT NULL,
    standortnutzung_anfangswert numeric(4,2) NOT NULL,
    standortnutzung_endwert numeric(4,2) NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: vereine_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.vereine_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    adresse uuid,
    bezeichnung character varying(255) NOT NULL,
    vereinsregister_id smallint,
    vereinsregister_datum date,
    schlagwoerter character varying(255)[] NOT NULL,
    telefon_festnetz character varying(255),
    telefon_mobil character varying(255),
    email character varying(255),
    website character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL,
    deaktiviert date
);


--
-- Name: verkaufstellen_angelberechtigungen_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.verkaufstellen_angelberechtigungen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid,
    bezeichnung character varying(255) NOT NULL,
    berechtigungen character varying(255)[],
    barrierefrei boolean,
    zeiten character varying(255),
    telefon_festnetz character varying(255),
    telefon_mobil character varying(255),
    email character varying(255),
    website character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: reinigungsreviere_hro; Type: TABLE; Schema: fachdaten_gemeindeteilbezug; Owner: -
--

CREATE TABLE fachdaten_gemeindeteilbezug.reinigungsreviere_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    gemeindeteil uuid,
    deaktiviert date,
    nummer smallint,
    bezeichnung character varying(255),
    geometrie public.geometry(MultiPolygon,25833) NOT NULL
);


--
-- Name: baustellen_fotodokumentation_baustellen_hro; Type: TABLE; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TABLE fachdaten_strassenbezug.baustellen_fotodokumentation_baustellen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    strasse uuid,
    deaktiviert date,
    bezeichnung character varying(255) NOT NULL,
    verkehrliche_lagen character varying(255)[] NOT NULL,
    sparten character varying(255)[] NOT NULL,
    auftraggeber uuid NOT NULL,
    ansprechpartner character varying(255) NOT NULL,
    bemerkungen character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: baustellen_geplant; Type: TABLE; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TABLE fachdaten_strassenbezug.baustellen_geplant (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    strasse uuid,
    projektbezeichnung character varying(255),
    bezeichnung character varying(255) NOT NULL,
    kurzbeschreibung text,
    lagebeschreibung character varying(255),
    verkehrliche_lagen character varying(255)[] NOT NULL,
    sparten character varying(255)[] NOT NULL,
    beginn date NOT NULL,
    ende date NOT NULL,
    auftraggeber uuid NOT NULL,
    ansprechpartner character varying(255) NOT NULL,
    status uuid NOT NULL,
    konflikt boolean,
    konflikt_tolerieren boolean,
    geometrie public.geometry(MultiPolygon,25833) NOT NULL,
    deaktiviert date
);


--
-- Name: geh_und_radwegereinigung_hro; Type: TABLE; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TABLE fachdaten_strassenbezug.geh_und_radwegereinigung_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    strasse uuid,
    deaktiviert date,
    nummer character varying(255),
    beschreibung character varying(255),
    geometrie public.geometry(MultiLineString,25833) NOT NULL,
    laenge numeric(6,2) NOT NULL,
    inoffizielle_strasse uuid,
    reinigungsklasse uuid,
    wegeart uuid NOT NULL,
    wegetyp uuid,
    reinigungsflaeche numeric(7,2),
    breite uuid,
    id character(14) NOT NULL,
    winterdienst boolean,
    raeumbreite uuid,
    reinigungsrhythmus uuid,
    winterdienstflaeche numeric(7,2),
    gemeindeteil uuid NOT NULL
);


--
-- Name: hausnummern_hro; Type: TABLE; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TABLE fachdaten_strassenbezug.hausnummern_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    strasse uuid NOT NULL,
    deaktiviert date,
    hausnummer smallint NOT NULL,
    hausnummer_zusatz character(1),
    postleitzahl character(5) NOT NULL,
    vergabe_datum date NOT NULL,
    antragsnummer character(6),
    gebaeude_bauweise uuid,
    gebaeude_funktion uuid,
    loeschung_details character varying(255),
    vorherige_adresse character varying(255),
    vorherige_antragsnummer character(6),
    bearbeiter character varying(255) NOT NULL,
    bemerkungen character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL,
    hinweise_gebaeude character varying(255)
);


--
-- Name: ingenieurbauwerke_hro; Type: TABLE; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TABLE fachdaten_strassenbezug.ingenieurbauwerke_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    strasse uuid,
    deaktiviert date,
    nummer character varying(255) NOT NULL,
    nummer_asb character varying(255),
    art uuid NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    baujahr character varying(255),
    ausfuehrung uuid,
    oben character varying(255),
    unten character varying(255),
    flaeche numeric(6,2),
    laenge numeric(5,2),
    breite character varying(255),
    hoehe character varying(255),
    lichte_weite numeric(4,2),
    lichte_hoehe character varying(255),
    durchfahrtshoehe numeric(4,2),
    nennweite character varying(255),
    schwerlast boolean NOT NULL,
    foto character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: strassenreinigung_hro; Type: TABLE; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TABLE fachdaten_strassenbezug.strassenreinigung_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    strasse uuid,
    deaktiviert date,
    reinigungsklasse uuid,
    fahrbahnwinterdienst uuid,
    geometrie public.geometry(MultiLineString,25833) NOT NULL,
    laenge numeric(6,2) NOT NULL,
    inoffizielle_strasse uuid,
    id character(14) NOT NULL,
    beschreibung character varying(255),
    ausserhalb boolean DEFAULT false NOT NULL,
    reinigungsrhythmus uuid,
    gemeindeteil uuid NOT NULL
);


--
-- Name: adressenliste_datenwerft adressenliste_datenwerft_pk; Type: CONSTRAINT; Schema: basisdaten; Owner: -
--

ALTER TABLE ONLY basisdaten.adressenliste_datenwerft
    ADD CONSTRAINT adressenliste_datenwerft_pk PRIMARY KEY (uuid);


--
-- Name: gemeindeteile_datenwerft_hro gemeindeteilte_datenwerft_pk; Type: CONSTRAINT; Schema: basisdaten; Owner: -
--

ALTER TABLE ONLY basisdaten.gemeindeteile_datenwerft_hro
    ADD CONSTRAINT gemeindeteilte_datenwerft_pk PRIMARY KEY (uuid);


--
-- Name: inoffizielle_strassenliste_datenwerft_hro inoffizielle_strassenliste_datenwerft_hro_pk; Type: CONSTRAINT; Schema: basisdaten; Owner: -
--

ALTER TABLE ONLY basisdaten.inoffizielle_strassenliste_datenwerft_hro
    ADD CONSTRAINT inoffizielle_strassenliste_datenwerft_hro_pk PRIMARY KEY (uuid);


--
-- Name: strassenliste_datenwerft strassenliste_datenwerft_pk; Type: CONSTRAINT; Schema: basisdaten; Owner: -
--

ALTER TABLE ONLY basisdaten.strassenliste_datenwerft
    ADD CONSTRAINT strassenliste_datenwerft_pk PRIMARY KEY (uuid);


--
-- Name: altersklassen_kadaverfunde altersklassen_kadaverfunde_bezeichnung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.altersklassen_kadaverfunde
    ADD CONSTRAINT altersklassen_kadaverfunde_bezeichnung_unique UNIQUE (bezeichnung);


--
-- Name: altersklassen_kadaverfunde altersklassen_kadaverfunde_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.altersklassen_kadaverfunde
    ADD CONSTRAINT altersklassen_kadaverfunde_pk PRIMARY KEY (uuid);


--
-- Name: anbieter_carsharing anbieter_carsharing_anbieter_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.anbieter_carsharing
    ADD CONSTRAINT anbieter_carsharing_anbieter_unique UNIQUE (anbieter);


--
-- Name: anbieter_carsharing anbieter_carsharing_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.anbieter_carsharing
    ADD CONSTRAINT anbieter_carsharing_pk PRIMARY KEY (uuid);


--
-- Name: angebote_mobilpunkte angebote_mobilpunkte_angebot_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.angebote_mobilpunkte
    ADD CONSTRAINT angebote_mobilpunkte_angebot_unique UNIQUE (angebot);


--
-- Name: angebote_mobilpunkte angebote_mobilpunkte_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.angebote_mobilpunkte
    ADD CONSTRAINT angebote_mobilpunkte_pk PRIMARY KEY (uuid);


--
-- Name: angelberechtigungen angelberechtigungen_angelberechtigung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.angelberechtigungen
    ADD CONSTRAINT angelberechtigungen_angelberechtigung_unique UNIQUE (angelberechtigung);


--
-- Name: angelberechtigungen angelberechtigungen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.angelberechtigungen
    ADD CONSTRAINT angelberechtigungen_pk PRIMARY KEY (uuid);


--
-- Name: ansprechpartner_baustellen ansprechpartner_baustellen_email_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ansprechpartner_baustellen
    ADD CONSTRAINT ansprechpartner_baustellen_email_unique UNIQUE (email);


--
-- Name: ansprechpartner_baustellen ansprechpartner_baustellen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ansprechpartner_baustellen
    ADD CONSTRAINT ansprechpartner_baustellen_pk PRIMARY KEY (uuid);


--
-- Name: arten_adressunsicherheiten arten_adressunsicherheiten_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_adressunsicherheiten
    ADD CONSTRAINT arten_adressunsicherheiten_art_unique UNIQUE (art);


--
-- Name: arten_adressunsicherheiten arten_adressunsicherheiten_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_adressunsicherheiten
    ADD CONSTRAINT arten_adressunsicherheiten_pk PRIMARY KEY (uuid);


--
-- Name: arten_durchlaesse arten_durchlaesse_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_durchlaesse
    ADD CONSTRAINT arten_durchlaesse_art_unique UNIQUE (art);


--
-- Name: arten_durchlaesse arten_durchlaesse_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_durchlaesse
    ADD CONSTRAINT arten_durchlaesse_pk PRIMARY KEY (uuid);


--
-- Name: arten_erdwaermesonden arten_erdwaermesonden_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_erdwaermesonden
    ADD CONSTRAINT arten_erdwaermesonden_art_unique UNIQUE (art);


--
-- Name: arten_erdwaermesonden arten_erdwaermesonden_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_erdwaermesonden
    ADD CONSTRAINT arten_erdwaermesonden_pk PRIMARY KEY (uuid);


--
-- Name: arten_fahrradabstellanlagen arten_fahrradabstellanlagen_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_fahrradabstellanlagen
    ADD CONSTRAINT arten_fahrradabstellanlagen_art_unique UNIQUE (art);


--
-- Name: arten_fahrradabstellanlagen arten_fahrradabstellanlagen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_fahrradabstellanlagen
    ADD CONSTRAINT arten_fahrradabstellanlagen_pk PRIMARY KEY (uuid);


--
-- Name: arten_fairtrade arten_fairtrade_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_fairtrade
    ADD CONSTRAINT arten_fairtrade_art_unique UNIQUE (art);


--
-- Name: arten_fairtrade arten_fairtrade_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_fairtrade
    ADD CONSTRAINT arten_fairtrade_pk PRIMARY KEY (uuid);


--
-- Name: arten_fallwildsuchen_kontrollen arten_fallwildsuchen_kontrollen_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_fallwildsuchen_kontrollen
    ADD CONSTRAINT arten_fallwildsuchen_kontrollen_art_unique UNIQUE (art);


--
-- Name: arten_fallwildsuchen_kontrollen arten_fallwildsuchen_kontrollen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_fallwildsuchen_kontrollen
    ADD CONSTRAINT arten_fallwildsuchen_kontrollen_pk PRIMARY KEY (uuid);


--
-- Name: arten_feldsportanlagen arten_feldsportanlagen_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_feldsportanlagen
    ADD CONSTRAINT arten_feldsportanlagen_art_unique UNIQUE (art);


--
-- Name: arten_feldsportanlagen arten_feldsportanlagen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_feldsportanlagen
    ADD CONSTRAINT arten_feldsportanlagen_pk PRIMARY KEY (uuid);


--
-- Name: arten_feuerwachen arten_feuerwachen_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_feuerwachen
    ADD CONSTRAINT arten_feuerwachen_art_unique UNIQUE (art);


--
-- Name: arten_feuerwachen arten_feuerwachen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_feuerwachen
    ADD CONSTRAINT arten_feuerwachen_pk PRIMARY KEY (uuid);


--
-- Name: arten_fliessgewaesser arten_fliessgewaesser_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_fliessgewaesser
    ADD CONSTRAINT arten_fliessgewaesser_art_unique UNIQUE (art);


--
-- Name: arten_fliessgewaesser arten_fliessgewaesser_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_fliessgewaesser
    ADD CONSTRAINT arten_fliessgewaesser_pk PRIMARY KEY (uuid);


--
-- Name: arten_hundetoiletten arten_hundetoiletten_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_hundetoiletten
    ADD CONSTRAINT arten_hundetoiletten_art_unique UNIQUE (art);


--
-- Name: arten_hundetoiletten arten_hundetoiletten_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_hundetoiletten
    ADD CONSTRAINT arten_hundetoiletten_pk PRIMARY KEY (uuid);


--
-- Name: arten_ingenieurbauwerke arten_ingenieurbauwerke_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_ingenieurbauwerke
    ADD CONSTRAINT arten_ingenieurbauwerke_art_unique UNIQUE (art);


--
-- Name: arten_ingenieurbauwerke arten_ingenieurbauwerke_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_ingenieurbauwerke
    ADD CONSTRAINT arten_ingenieurbauwerke_pk PRIMARY KEY (uuid);


--
-- Name: arten_meldedienst_flaechenhaft arten_meldedienst_flaechenhaft_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_meldedienst_flaechenhaft
    ADD CONSTRAINT arten_meldedienst_flaechenhaft_art_unique UNIQUE (art);


--
-- Name: arten_meldedienst_flaechenhaft arten_meldedienst_flaechenhaft_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_meldedienst_flaechenhaft
    ADD CONSTRAINT arten_meldedienst_flaechenhaft_pk PRIMARY KEY (uuid);


--
-- Name: arten_meldedienst_punkthaft arten_meldedienst_punkthaft_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_meldedienst_punkthaft
    ADD CONSTRAINT arten_meldedienst_punkthaft_art_unique UNIQUE (art);


--
-- Name: arten_meldedienst_punkthaft arten_meldedienst_punkthaft_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_meldedienst_punkthaft
    ADD CONSTRAINT arten_meldedienst_punkthaft_pk PRIMARY KEY (uuid);


--
-- Name: arten_parkmoeglichkeiten arten_parkmoeglichkeiten_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_parkmoeglichkeiten
    ADD CONSTRAINT arten_parkmoeglichkeiten_art_unique UNIQUE (art);


--
-- Name: arten_parkmoeglichkeiten arten_parkmoeglichkeiten_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_parkmoeglichkeiten
    ADD CONSTRAINT arten_parkmoeglichkeiten_pk PRIMARY KEY (uuid);


--
-- Name: arten_pflegeeinrichtungen arten_pflegeeinrichtungen_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_pflegeeinrichtungen
    ADD CONSTRAINT arten_pflegeeinrichtungen_art_unique UNIQUE (art);


--
-- Name: arten_pflegeeinrichtungen arten_pflegeeinrichtungen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_pflegeeinrichtungen
    ADD CONSTRAINT arten_pflegeeinrichtungen_pk PRIMARY KEY (uuid);


--
-- Name: arten_poller arten_poller_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_poller
    ADD CONSTRAINT arten_poller_art_unique UNIQUE (art);


--
-- Name: arten_poller arten_poller_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_poller
    ADD CONSTRAINT arten_poller_pk PRIMARY KEY (uuid);


--
-- Name: arten_reisebusparkplaetze_terminals arten_reisebusparkplaetze_terminals_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_reisebusparkplaetze_terminals
    ADD CONSTRAINT arten_reisebusparkplaetze_terminals_art_unique UNIQUE (art);


--
-- Name: arten_reisebusparkplaetze_terminals arten_reisebusparkplaetze_terminals_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_reisebusparkplaetze_terminals
    ADD CONSTRAINT arten_reisebusparkplaetze_terminals_pk PRIMARY KEY (uuid);


--
-- Name: arten_toiletten arten_toiletten_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_toiletten
    ADD CONSTRAINT arten_toiletten_art_unique UNIQUE (art);


--
-- Name: arten_toiletten arten_toiletten_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_toiletten
    ADD CONSTRAINT arten_toiletten_pk PRIMARY KEY (uuid);


--
-- Name: arten_uvp_vorpruefungen arten_uvp_vorpruefungen_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_uvp_vorpruefungen
    ADD CONSTRAINT arten_uvp_vorpruefungen_art_unique UNIQUE (art);


--
-- Name: arten_uvp_vorpruefungen arten_uvp_vorpruefungen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_uvp_vorpruefungen
    ADD CONSTRAINT arten_uvp_vorpruefungen_pk PRIMARY KEY (uuid);


--
-- Name: arten_wege arten_wege_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_wege
    ADD CONSTRAINT arten_wege_art_unique UNIQUE (art);


--
-- Name: arten_wege arten_wege_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_wege
    ADD CONSTRAINT arten_wege_pk PRIMARY KEY (uuid);


--
-- Name: auftraggeber_baustellen auftraggeber_baustellen_auftraggeber_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.auftraggeber_baustellen
    ADD CONSTRAINT auftraggeber_baustellen_auftraggeber_unique UNIQUE (auftraggeber);


--
-- Name: auftraggeber_baustellen auftraggeber_baustellen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.auftraggeber_baustellen
    ADD CONSTRAINT auftraggeber_baustellen_pk PRIMARY KEY (uuid);


--
-- Name: ausfuehrungen_haltestellenkataster ausfuehrungen_haltestellenkataster_ausfuehrung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ausfuehrungen_haltestellenkataster
    ADD CONSTRAINT ausfuehrungen_haltestellenkataster_ausfuehrung_unique UNIQUE (ausfuehrung);


--
-- Name: ausfuehrungen_haltestellenkataster ausfuehrungen_haltestellenkataster_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ausfuehrungen_haltestellenkataster
    ADD CONSTRAINT ausfuehrungen_haltestellenkataster_pk PRIMARY KEY (uuid);


--
-- Name: ausfuehrungen_ingenieurbauwerke ausfuehrungen_ingenieurbauwerke_ausfuehrung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ausfuehrungen_ingenieurbauwerke
    ADD CONSTRAINT ausfuehrungen_ingenieurbauwerke_ausfuehrung_unique UNIQUE (ausfuehrung);


--
-- Name: ausfuehrungen_ingenieurbauwerke ausfuehrungen_ingenieurbauwerke_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ausfuehrungen_ingenieurbauwerke
    ADD CONSTRAINT ausfuehrungen_ingenieurbauwerke_pk PRIMARY KEY (uuid);


--
-- Name: befestigungsarten_aufstellflaeche_bus_haltestellenkataster befestigungsarten_aufstellflaeche_bus_haltestellenkataster_befe; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.befestigungsarten_aufstellflaeche_bus_haltestellenkataster
    ADD CONSTRAINT befestigungsarten_aufstellflaeche_bus_haltestellenkataster_befe UNIQUE (befestigungsart);


--
-- Name: befestigungsarten_aufstellflaeche_bus_haltestellenkataster befestigungsarten_aufstellflaeche_bus_haltestellenkataster_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.befestigungsarten_aufstellflaeche_bus_haltestellenkataster
    ADD CONSTRAINT befestigungsarten_aufstellflaeche_bus_haltestellenkataster_pk PRIMARY KEY (uuid);


--
-- Name: befestigungsarten_warteflaeche_haltestellenkataster befestigungsarten_warteflaeche_haltestellenkataster_befestigung; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.befestigungsarten_warteflaeche_haltestellenkataster
    ADD CONSTRAINT befestigungsarten_warteflaeche_haltestellenkataster_befestigung UNIQUE (befestigungsart);


--
-- Name: befestigungsarten_warteflaeche_haltestellenkataster befestigungsarten_warteflaeche_haltestellenkataster_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.befestigungsarten_warteflaeche_haltestellenkataster
    ADD CONSTRAINT befestigungsarten_warteflaeche_haltestellenkataster_pk PRIMARY KEY (uuid);


--
-- Name: betriebsarten betriebsarten_betriebsart_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.betriebsarten
    ADD CONSTRAINT betriebsarten_betriebsart_unique UNIQUE (betriebsart);


--
-- Name: betriebsarten betriebsarten_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.betriebsarten
    ADD CONSTRAINT betriebsarten_pk PRIMARY KEY (uuid);


--
-- Name: betriebszeiten betriebszeiten_betriebszeit_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.betriebszeiten
    ADD CONSTRAINT betriebszeiten_betriebszeit_unique UNIQUE (betriebszeit);


--
-- Name: betriebszeiten betriebszeiten_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.betriebszeiten
    ADD CONSTRAINT betriebszeiten_pk PRIMARY KEY (uuid);


--
-- Name: bevollmaechtigte_bezirksschornsteinfeger bevollmaechtigte_bezirksschornsteinfeger_bezirk_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.bevollmaechtigte_bezirksschornsteinfeger
    ADD CONSTRAINT bevollmaechtigte_bezirksschornsteinfeger_bezirk_unique UNIQUE (bezirk);


--
-- Name: bevollmaechtigte_bezirksschornsteinfeger bevollmaechtigte_bezirksschornsteinfeger_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.bevollmaechtigte_bezirksschornsteinfeger
    ADD CONSTRAINT bevollmaechtigte_bezirksschornsteinfeger_pk PRIMARY KEY (uuid);


--
-- Name: bewirtschafter_betreiber_traeger_eigentuemer bewirtschafter_betreiber_traeger_eigentuemer_bezeichnung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.bewirtschafter_betreiber_traeger_eigentuemer
    ADD CONSTRAINT bewirtschafter_betreiber_traeger_eigentuemer_bezeichnung_unique UNIQUE (bezeichnung);


--
-- Name: bewirtschafter_betreiber_traeger_eigentuemer bewirtschafter_betreiber_traeger_eigentuemer_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.bewirtschafter_betreiber_traeger_eigentuemer
    ADD CONSTRAINT bewirtschafter_betreiber_traeger_eigentuemer_pk PRIMARY KEY (uuid);


--
-- Name: dfi_typen_haltestellenkataster dfi_typen_haltestellenkataster_dfi_typ_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.dfi_typen_haltestellenkataster
    ADD CONSTRAINT dfi_typen_haltestellenkataster_dfi_typ_unique UNIQUE (dfi_typ);


--
-- Name: dfi_typen_haltestellenkataster dfi_typen_haltestellenkataster_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.dfi_typen_haltestellenkataster
    ADD CONSTRAINT dfi_typen_haltestellenkataster_pk PRIMARY KEY (uuid);


--
-- Name: e_anschluesse_parkscheinautomaten e_anschluesse_parkscheinautomaten_e_anschluss_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.e_anschluesse_parkscheinautomaten
    ADD CONSTRAINT e_anschluesse_parkscheinautomaten_e_anschluss_unique UNIQUE (e_anschluss);


--
-- Name: e_anschluesse_parkscheinautomaten e_anschluesse_parkscheinautomaten_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.e_anschluesse_parkscheinautomaten
    ADD CONSTRAINT e_anschluesse_parkscheinautomaten_pk PRIMARY KEY (uuid);


--
-- Name: ergebnisse_uvp_vorpruefungen ergebnisse_uvp_vorpruefungen_ergebnis_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ergebnisse_uvp_vorpruefungen
    ADD CONSTRAINT ergebnisse_uvp_vorpruefungen_ergebnis_unique UNIQUE (ergebnis);


--
-- Name: ergebnisse_uvp_vorpruefungen ergebnisse_uvp_vorpruefungen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ergebnisse_uvp_vorpruefungen
    ADD CONSTRAINT ergebnisse_uvp_vorpruefungen_pk PRIMARY KEY (uuid);


--
-- Name: fahrbahnwinterdienst_strassenreinigungssatzung_hro fahrbahnwinterdienst_strassenreinigungssatzung_hro_code_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.fahrbahnwinterdienst_strassenreinigungssatzung_hro
    ADD CONSTRAINT fahrbahnwinterdienst_strassenreinigungssatzung_hro_code_unique UNIQUE (code);


--
-- Name: fahrbahnwinterdienst_strassenreinigungssatzung_hro fahrbahnwinterdienst_strassenreinigungssatzung_hro_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.fahrbahnwinterdienst_strassenreinigungssatzung_hro
    ADD CONSTRAINT fahrbahnwinterdienst_strassenreinigungssatzung_hro_pk PRIMARY KEY (uuid);


--
-- Name: fahrgastunterstandstypen_haltestellenkataster fahrgastunterstandstypen_haltestellenkataster_fahrgastunterstan; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.fahrgastunterstandstypen_haltestellenkataster
    ADD CONSTRAINT fahrgastunterstandstypen_haltestellenkataster_fahrgastunterstan UNIQUE (fahrgastunterstandstyp);


--
-- Name: fahrgastunterstandstypen_haltestellenkataster fahrgastunterstandstypen_haltestellenkataster_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.fahrgastunterstandstypen_haltestellenkataster
    ADD CONSTRAINT fahrgastunterstandstypen_haltestellenkataster_pk PRIMARY KEY (uuid);


--
-- Name: fahrplanvitrinentypen_haltestellenkataster fahrplanvitrinentypen_haltestellenkataster_fahrplanvitrinentyp_; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.fahrplanvitrinentypen_haltestellenkataster
    ADD CONSTRAINT fahrplanvitrinentypen_haltestellenkataster_fahrplanvitrinentyp_ UNIQUE (fahrplanvitrinentyp);


--
-- Name: fahrplanvitrinentypen_haltestellenkataster fahrplanvitrinentypen_haltestellenkataster_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.fahrplanvitrinentypen_haltestellenkataster
    ADD CONSTRAINT fahrplanvitrinentypen_haltestellenkataster_pk PRIMARY KEY (uuid);


--
-- Name: fotomotive_haltestellenkataster fotomotive_haltestellenkataster_fotomotiv_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.fotomotive_haltestellenkataster
    ADD CONSTRAINT fotomotive_haltestellenkataster_fotomotiv_unique UNIQUE (fotomotiv);


--
-- Name: fotomotive_haltestellenkataster fotomotive_haltestellenkataster_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.fotomotive_haltestellenkataster
    ADD CONSTRAINT fotomotive_haltestellenkataster_pk PRIMARY KEY (uuid);


--
-- Name: fundamenttypen_rsag fundamenttypen_rsag_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.fundamenttypen_rsag
    ADD CONSTRAINT fundamenttypen_rsag_pk PRIMARY KEY (uuid);


--
-- Name: fundamenttypen_rsag fundamenttypen_rsag_typ_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.fundamenttypen_rsag
    ADD CONSTRAINT fundamenttypen_rsag_typ_unique UNIQUE (typ);


--
-- Name: gebaeudearten_meldedienst_punkthaft gebaeudearten_meldedienst_punkthaft_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.gebaeudearten_meldedienst_punkthaft
    ADD CONSTRAINT gebaeudearten_meldedienst_punkthaft_pk PRIMARY KEY (uuid);


--
-- Name: gebaeudebauweisen gebaeudebauweisen_code_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.gebaeudebauweisen
    ADD CONSTRAINT gebaeudebauweisen_code_unique UNIQUE (code);


--
-- Name: gebaeudebauweisen gebaeudebauweisen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.gebaeudebauweisen
    ADD CONSTRAINT gebaeudebauweisen_pk PRIMARY KEY (uuid);


--
-- Name: gebaeudefunktionen gebaeudefunktionen_code_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.gebaeudefunktionen
    ADD CONSTRAINT gebaeudefunktionen_code_unique UNIQUE (code);


--
-- Name: gebaeudefunktionen gebaeudefunktionen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.gebaeudefunktionen
    ADD CONSTRAINT gebaeudefunktionen_pk PRIMARY KEY (uuid);


--
-- Name: genehmigungsbehoerden_uvp_vorhaben genehmigungsbehoerden_uvp_vorhaben_genehmigungsbehoerde_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.genehmigungsbehoerden_uvp_vorhaben
    ADD CONSTRAINT genehmigungsbehoerden_uvp_vorhaben_genehmigungsbehoerde_unique UNIQUE (genehmigungsbehoerde);


--
-- Name: genehmigungsbehoerden_uvp_vorhaben genehmigungsbehoerden_uvp_vorhaben_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.genehmigungsbehoerden_uvp_vorhaben
    ADD CONSTRAINT genehmigungsbehoerden_uvp_vorhaben_pk PRIMARY KEY (uuid);


--
-- Name: geschlechter_kadaverfunde geschlechter_kadaverfunde_bezeichnung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.geschlechter_kadaverfunde
    ADD CONSTRAINT geschlechter_kadaverfunde_bezeichnung_unique UNIQUE (bezeichnung);


--
-- Name: geschlechter_kadaverfunde geschlechter_kadaverfunde_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.geschlechter_kadaverfunde
    ADD CONSTRAINT geschlechter_kadaverfunde_pk PRIMARY KEY (uuid);


--
-- Name: haefen haefen_abkuerzung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.haefen
    ADD CONSTRAINT haefen_abkuerzung_unique UNIQUE (abkuerzung);


--
-- Name: haefen haefen_code_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.haefen
    ADD CONSTRAINT haefen_code_unique UNIQUE (code);


--
-- Name: haefen haefen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.haefen
    ADD CONSTRAINT haefen_pk PRIMARY KEY (uuid);


--
-- Name: hersteller_poller hersteller_poller_bezeichnung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.hersteller_poller
    ADD CONSTRAINT hersteller_poller_bezeichnung_unique UNIQUE (bezeichnung);


--
-- Name: hersteller_poller hersteller_poller_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.hersteller_poller
    ADD CONSTRAINT hersteller_poller_pk PRIMARY KEY (uuid);


--
-- Name: kabeltypen_lichtwellenleiterinfrastruktur kabeltypen_lichtwellenleiterinfrastruktur_kabeltyp_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.kabeltypen_lichtwellenleiterinfrastruktur
    ADD CONSTRAINT kabeltypen_lichtwellenleiterinfrastruktur_kabeltyp_unique UNIQUE (kabeltyp);


--
-- Name: kabeltypen_lichtwellenleiterinfrastruktur kabeltypen_lichtwellenleiterinfrastruktur_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.kabeltypen_lichtwellenleiterinfrastruktur
    ADD CONSTRAINT kabeltypen_lichtwellenleiterinfrastruktur_pk PRIMARY KEY (uuid);


--
-- Name: kategorien_strassen kategorien_strassen_code_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.kategorien_strassen
    ADD CONSTRAINT kategorien_strassen_code_unique UNIQUE (code);


--
-- Name: kategorien_strassen kategorien_strassen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.kategorien_strassen
    ADD CONSTRAINT kategorien_strassen_pk PRIMARY KEY (uuid);


--
-- Name: ladekarten_ladestationen_elektrofahrzeuge ladekarten_ladestationen_elektrofahrzeuge_ladekarte_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ladekarten_ladestationen_elektrofahrzeuge
    ADD CONSTRAINT ladekarten_ladestationen_elektrofahrzeuge_ladekarte_unique UNIQUE (ladekarte);


--
-- Name: ladekarten_ladestationen_elektrofahrzeuge ladekarten_ladestationen_elektrofahrzeuge_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ladekarten_ladestationen_elektrofahrzeuge
    ADD CONSTRAINT ladekarten_ladestationen_elektrofahrzeuge_pk PRIMARY KEY (uuid);


--
-- Name: linien linien_linie_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.linien
    ADD CONSTRAINT linien_linie_unique UNIQUE (linie);


--
-- Name: linien linien_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.linien
    ADD CONSTRAINT linien_pk PRIMARY KEY (uuid);


--
-- Name: mastkennzeichen_rsag mastkennzeichen_rsag_kennzeichen_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.mastkennzeichen_rsag
    ADD CONSTRAINT mastkennzeichen_rsag_kennzeichen_unique UNIQUE (kennzeichen);


--
-- Name: mastkennzeichen_rsag mastkennzeichen_rsag_pkey; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.mastkennzeichen_rsag
    ADD CONSTRAINT mastkennzeichen_rsag_pkey PRIMARY KEY (uuid);


--
-- Name: masttypen_haltestellenkataster masttypen_haltestellenkataster_masttyp_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.masttypen_haltestellenkataster
    ADD CONSTRAINT masttypen_haltestellenkataster_masttyp_unique UNIQUE (masttyp);


--
-- Name: masttypen_haltestellenkataster masttypen_haltestellenkataster_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.masttypen_haltestellenkataster
    ADD CONSTRAINT masttypen_haltestellenkataster_pk PRIMARY KEY (uuid);


--
-- Name: masttypen_rsag masttypen_rsag_pkey; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.masttypen_rsag
    ADD CONSTRAINT masttypen_rsag_pkey PRIMARY KEY (uuid);


--
-- Name: masttypen_rsag masttypen_rsag_typ_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.masttypen_rsag
    ADD CONSTRAINT masttypen_rsag_typ_unique UNIQUE (typ);


--
-- Name: materialien_denksteine materialien_denksteine_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.materialien_denksteine
    ADD CONSTRAINT materialien_denksteine_pk PRIMARY KEY (uuid);


--
-- Name: materialien_denksteine materialien_denksteine_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.materialien_denksteine
    ADD CONSTRAINT materialien_denksteine_unique UNIQUE (material);


--
-- Name: materialien_durchlaesse materialien_durchlaesse_material_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.materialien_durchlaesse
    ADD CONSTRAINT materialien_durchlaesse_material_unique UNIQUE (material);


--
-- Name: materialien_durchlaesse materialien_durchlaesse_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.materialien_durchlaesse
    ADD CONSTRAINT materialien_durchlaesse_pk PRIMARY KEY (uuid);


--
-- Name: objektarten_lichtwellenleiterinfrastruktur objektarten_lichtwellenleiterinfrastruktur_objektart_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.objektarten_lichtwellenleiterinfrastruktur
    ADD CONSTRAINT objektarten_lichtwellenleiterinfrastruktur_objektart_unique UNIQUE (objektart);


--
-- Name: objektarten_lichtwellenleiterinfrastruktur objektarten_lichtwellenleiterinfrastruktur_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.objektarten_lichtwellenleiterinfrastruktur
    ADD CONSTRAINT objektarten_lichtwellenleiterinfrastruktur_pk PRIMARY KEY (uuid);


--
-- Name: ordnungen_fliessgewaesser ordnungen_fliessgewaesser_ordnung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ordnungen_fliessgewaesser
    ADD CONSTRAINT ordnungen_fliessgewaesser_ordnung_unique UNIQUE (ordnung);


--
-- Name: ordnungen_fliessgewaesser ordnungen_fliessgewaesser_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ordnungen_fliessgewaesser
    ADD CONSTRAINT ordnungen_fliessgewaesser_pk PRIMARY KEY (uuid);


--
-- Name: personentitel personentitel_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.personentitel
    ADD CONSTRAINT personentitel_pk PRIMARY KEY (uuid);


--
-- Name: personentitel personentitel_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.personentitel
    ADD CONSTRAINT personentitel_unique UNIQUE (bezeichnung);


--
-- Name: quartiere quartiere_code_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.quartiere
    ADD CONSTRAINT quartiere_code_unique UNIQUE (code);


--
-- Name: quartiere quartiere_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.quartiere
    ADD CONSTRAINT quartiere_pk PRIMARY KEY (uuid);


--
-- Name: raeumbreiten_strassenreinigungssatzung_hro raeumbreiten_strassenreinigungssatzung_hro_code_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.raeumbreiten_strassenreinigungssatzung_hro
    ADD CONSTRAINT raeumbreiten_strassenreinigungssatzung_hro_code_unique UNIQUE (raeumbreite);


--
-- Name: raeumbreiten_strassenreinigungssatzung_hro raeumbreiten_strassenreinigungssatzung_hro_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.raeumbreiten_strassenreinigungssatzung_hro
    ADD CONSTRAINT raeumbreiten_strassenreinigungssatzung_hro_pk PRIMARY KEY (uuid);


--
-- Name: rechtsgrundlagen_uvp_vorhaben rechtsgrundlagen_uvp_vorhaben_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.rechtsgrundlagen_uvp_vorhaben
    ADD CONSTRAINT rechtsgrundlagen_uvp_vorhaben_pk PRIMARY KEY (uuid);


--
-- Name: rechtsgrundlagen_uvp_vorhaben rechtsgrundlagen_uvp_vorhaben_rechtsgrundlage_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.rechtsgrundlagen_uvp_vorhaben
    ADD CONSTRAINT rechtsgrundlagen_uvp_vorhaben_rechtsgrundlage_unique UNIQUE (rechtsgrundlage);


--
-- Name: reinigungsklassen_strassenreinigungssatzung_hro reinigungsklassen_strassenreinigungssatzung_hro_code_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.reinigungsklassen_strassenreinigungssatzung_hro
    ADD CONSTRAINT reinigungsklassen_strassenreinigungssatzung_hro_code_unique UNIQUE (code);


--
-- Name: reinigungsklassen_strassenreinigungssatzung_hro reinigungsklassen_strassenreinigungssatzung_hro_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.reinigungsklassen_strassenreinigungssatzung_hro
    ADD CONSTRAINT reinigungsklassen_strassenreinigungssatzung_hro_pk PRIMARY KEY (uuid);


--
-- Name: reinigungsrhythmen_strassenreinigungssatzung_hro reinigungsrhythmen_strassenreinigungssatzung_hro_ordinalzahl_un; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.reinigungsrhythmen_strassenreinigungssatzung_hro
    ADD CONSTRAINT reinigungsrhythmen_strassenreinigungssatzung_hro_ordinalzahl_un UNIQUE (ordinalzahl);


--
-- Name: reinigungsrhythmen_strassenreinigungssatzung_hro reinigungsrhythmen_strassenreinigungssatzung_hro_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.reinigungsrhythmen_strassenreinigungssatzung_hro
    ADD CONSTRAINT reinigungsrhythmen_strassenreinigungssatzung_hro_pk PRIMARY KEY (uuid);


--
-- Name: schaeden_haltestellenkataster schaeden_haltestellenkataster_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.schaeden_haltestellenkataster
    ADD CONSTRAINT schaeden_haltestellenkataster_pk PRIMARY KEY (uuid);


--
-- Name: schaeden_haltestellenkataster schaeden_haltestellenkataster_schaden_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.schaeden_haltestellenkataster
    ADD CONSTRAINT schaeden_haltestellenkataster_schaden_unique UNIQUE (schaden);


--
-- Name: schlagwoerter_bildungstraeger schlagwoerter_bildungstraeger_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.schlagwoerter_bildungstraeger
    ADD CONSTRAINT schlagwoerter_bildungstraeger_pk PRIMARY KEY (uuid);


--
-- Name: schlagwoerter_bildungstraeger schlagwoerter_bildungstraeger_schlagwort_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.schlagwoerter_bildungstraeger
    ADD CONSTRAINT schlagwoerter_bildungstraeger_schlagwort_unique UNIQUE (schlagwort);


--
-- Name: schlagwoerter_vereine schlagwoerter_vereine_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.schlagwoerter_vereine
    ADD CONSTRAINT schlagwoerter_vereine_pk PRIMARY KEY (uuid);


--
-- Name: schlagwoerter_vereine schlagwoerter_vereine_schlagwort_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.schlagwoerter_vereine
    ADD CONSTRAINT schlagwoerter_vereine_schlagwort_unique UNIQUE (schlagwort);


--
-- Name: schliessungen_poller schliessungen_poller_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.schliessungen_poller
    ADD CONSTRAINT schliessungen_poller_pk PRIMARY KEY (uuid);


--
-- Name: schliessungen_poller schliessungen_poller_schliessungen_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.schliessungen_poller
    ADD CONSTRAINT schliessungen_poller_schliessungen_unique UNIQUE (schliessung);


--
-- Name: sitzbanktypen_haltestellenkataster sitzbanktypen_haltestellenkataster_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.sitzbanktypen_haltestellenkataster
    ADD CONSTRAINT sitzbanktypen_haltestellenkataster_pk PRIMARY KEY (uuid);


--
-- Name: sitzbanktypen_haltestellenkataster sitzbanktypen_haltestellenkataster_sitzbanktyp_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.sitzbanktypen_haltestellenkataster
    ADD CONSTRAINT sitzbanktypen_haltestellenkataster_sitzbanktyp_unique UNIQUE (sitzbanktyp);


--
-- Name: sparten_baustellen sparten_baustellen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.sparten_baustellen
    ADD CONSTRAINT sparten_baustellen_pk PRIMARY KEY (uuid);


--
-- Name: sparten_baustellen sparten_baustellen_sparte_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.sparten_baustellen
    ADD CONSTRAINT sparten_baustellen_sparte_unique UNIQUE (sparte);


--
-- Name: sportarten sportarten_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.sportarten
    ADD CONSTRAINT sportarten_pk PRIMARY KEY (uuid);


--
-- Name: sportarten sportarten_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.sportarten
    ADD CONSTRAINT sportarten_unique UNIQUE (bezeichnung);


--
-- Name: status_baudenkmale_denkmalbereiche status_baudenkmale_denkmalbereiche_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.status_baudenkmale_denkmalbereiche
    ADD CONSTRAINT status_baudenkmale_denkmalbereiche_pk PRIMARY KEY (uuid);


--
-- Name: status_baudenkmale_denkmalbereiche status_baudenkmale_denkmalbereiche_status_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.status_baudenkmale_denkmalbereiche
    ADD CONSTRAINT status_baudenkmale_denkmalbereiche_status_unique UNIQUE (status);


--
-- Name: status_baustellen_fotodokumentation_fotos status_baustellen_fotodokumentation_fotos_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.status_baustellen_fotodokumentation_fotos
    ADD CONSTRAINT status_baustellen_fotodokumentation_fotos_pk PRIMARY KEY (uuid);


--
-- Name: status_baustellen_fotodokumentation_fotos status_baustellen_fotodokumentation_fotos_status_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.status_baustellen_fotodokumentation_fotos
    ADD CONSTRAINT status_baustellen_fotodokumentation_fotos_status_unique UNIQUE (status);


--
-- Name: status_baustellen_geplant status_baustellen_geplant_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.status_baustellen_geplant
    ADD CONSTRAINT status_baustellen_geplant_pk PRIMARY KEY (uuid);


--
-- Name: status_baustellen_geplant status_baustellen_geplant_status_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.status_baustellen_geplant
    ADD CONSTRAINT status_baustellen_geplant_status_unique UNIQUE (status);


--
-- Name: status_poller status_poller_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.status_poller
    ADD CONSTRAINT status_poller_pk PRIMARY KEY (uuid);


--
-- Name: status_poller status_poller_status_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.status_poller
    ADD CONSTRAINT status_poller_status_unique UNIQUE (status);


--
-- Name: tierseuchen tierseuchen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.tierseuchen
    ADD CONSTRAINT tierseuchen_pk PRIMARY KEY (uuid);


--
-- Name: tierseuchen tierseuchen_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.tierseuchen
    ADD CONSTRAINT tierseuchen_unique UNIQUE (bezeichnung);


--
-- Name: typen_abfallbehaelter typen_abfallbehaelter_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_abfallbehaelter
    ADD CONSTRAINT typen_abfallbehaelter_pk PRIMARY KEY (uuid);


--
-- Name: typen_abfallbehaelter typen_abfallbehaelter_typ_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_abfallbehaelter
    ADD CONSTRAINT typen_abfallbehaelter_typ_unique UNIQUE (typ);


--
-- Name: typen_erdwaermesonden typen_erdwaermesonden_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_erdwaermesonden
    ADD CONSTRAINT typen_erdwaermesonden_pk PRIMARY KEY (uuid);


--
-- Name: typen_erdwaermesonden typen_erdwaermesonden_typ_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_erdwaermesonden
    ADD CONSTRAINT typen_erdwaermesonden_typ_unique UNIQUE (typ);


--
-- Name: typen_feuerwehrzufahrten_schilder typen_feuerwehrzufahrten_schilder_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_feuerwehrzufahrten_schilder
    ADD CONSTRAINT typen_feuerwehrzufahrten_schilder_pk PRIMARY KEY (uuid);


--
-- Name: typen_feuerwehrzufahrten_schilder typen_feuerwehrzufahrten_schilder_typ_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_feuerwehrzufahrten_schilder
    ADD CONSTRAINT typen_feuerwehrzufahrten_schilder_typ_unique UNIQUE (typ);


--
-- Name: typen_haltestellen typen_haltestellen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_haltestellen
    ADD CONSTRAINT typen_haltestellen_pk PRIMARY KEY (uuid);


--
-- Name: typen_haltestellen typen_haltestellen_typ_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_haltestellen
    ADD CONSTRAINT typen_haltestellen_typ_unique UNIQUE (typ);


--
-- Name: typen_kleinklaeranlagen typen_kleinklaeranlagen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_kleinklaeranlagen
    ADD CONSTRAINT typen_kleinklaeranlagen_pk PRIMARY KEY (uuid);


--
-- Name: typen_kleinklaeranlagen typen_kleinklaeranlagen_typ_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_kleinklaeranlagen
    ADD CONSTRAINT typen_kleinklaeranlagen_typ_unique UNIQUE (typ);


--
-- Name: typen_poller typen_poller_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_poller
    ADD CONSTRAINT typen_poller_pk PRIMARY KEY (uuid);


--
-- Name: typen_poller typen_poller_typ_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_poller
    ADD CONSTRAINT typen_poller_typ_unique UNIQUE (typ);


--
-- Name: typen_uvp_vorhaben typen_uvp_vorhaben_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_uvp_vorhaben
    ADD CONSTRAINT typen_uvp_vorhaben_pk PRIMARY KEY (uuid);


--
-- Name: typen_uvp_vorhaben typen_uvp_vorhaben_typ_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_uvp_vorhaben
    ADD CONSTRAINT typen_uvp_vorhaben_typ_unique UNIQUE (typ);


--
-- Name: verbuende_ladestationen_elektrofahrzeuge verbuende_ladestationen_elektrofahrzeuge_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.verbuende_ladestationen_elektrofahrzeuge
    ADD CONSTRAINT verbuende_ladestationen_elektrofahrzeuge_pk PRIMARY KEY (uuid);


--
-- Name: verbuende_ladestationen_elektrofahrzeuge verbuende_ladestationen_elektrofahrzeuge_verbund_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.verbuende_ladestationen_elektrofahrzeuge
    ADD CONSTRAINT verbuende_ladestationen_elektrofahrzeuge_verbund_unique UNIQUE (verbund);


--
-- Name: verkehrliche_lagen_baustellen verkehrliche_lagen_baustellen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.verkehrliche_lagen_baustellen
    ADD CONSTRAINT verkehrliche_lagen_baustellen_pk PRIMARY KEY (uuid);


--
-- Name: verkehrliche_lagen_baustellen verkehrliche_lagen_baustellen_verkehrliche_lage_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.verkehrliche_lagen_baustellen
    ADD CONSTRAINT verkehrliche_lagen_baustellen_verkehrliche_lage_unique UNIQUE (verkehrliche_lage);


--
-- Name: verkehrsmittelklassen verkehrsmittelklassen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.verkehrsmittelklassen
    ADD CONSTRAINT verkehrsmittelklassen_pk PRIMARY KEY (uuid);


--
-- Name: verkehrsmittelklassen verkehrsmittelklassen_verkehrsmittelklasse_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.verkehrsmittelklassen
    ADD CONSTRAINT verkehrsmittelklassen_verkehrsmittelklasse_unique UNIQUE (verkehrsmittelklasse);


--
-- Name: vorgangsarten_uvp_vorhaben vorgangsarten_uvp_vorhaben_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.vorgangsarten_uvp_vorhaben
    ADD CONSTRAINT vorgangsarten_uvp_vorhaben_pk PRIMARY KEY (uuid);


--
-- Name: vorgangsarten_uvp_vorhaben vorgangsarten_uvp_vorhaben_vorgangsart_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.vorgangsarten_uvp_vorhaben
    ADD CONSTRAINT vorgangsarten_uvp_vorhaben_vorgangsart_unique UNIQUE (vorgangsart);


--
-- Name: wegebreiten_strassenreinigungssatzung_hro wegebreiten_strassenreinigungssatzung_hro_code_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.wegebreiten_strassenreinigungssatzung_hro
    ADD CONSTRAINT wegebreiten_strassenreinigungssatzung_hro_code_unique UNIQUE (wegebreite);


--
-- Name: wegebreiten_strassenreinigungssatzung_hro wegebreiten_strassenreinigungssatzung_hro_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.wegebreiten_strassenreinigungssatzung_hro
    ADD CONSTRAINT wegebreiten_strassenreinigungssatzung_hro_pk PRIMARY KEY (uuid);


--
-- Name: wegereinigungsklassen_strassenreinigungssatzung_hro wegereinigungsklassen_strassenreinigungssatzung_hro_code_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.wegereinigungsklassen_strassenreinigungssatzung_hro
    ADD CONSTRAINT wegereinigungsklassen_strassenreinigungssatzung_hro_code_unique UNIQUE (code);


--
-- Name: wegereinigungsklassen_strassenreinigungssatzung_hro wegereinigungsklassen_strassenreinigungssatzung_hro_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.wegereinigungsklassen_strassenreinigungssatzung_hro
    ADD CONSTRAINT wegereinigungsklassen_strassenreinigungssatzung_hro_pk PRIMARY KEY (uuid);


--
-- Name: wegereinigungsrhythmen_strassenreinigungssatzung_hro wegereinigungsrhythmen_strassenreinigungssatzung_hro_ordinalzah; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.wegereinigungsrhythmen_strassenreinigungssatzung_hro
    ADD CONSTRAINT wegereinigungsrhythmen_strassenreinigungssatzung_hro_ordinalzah UNIQUE (ordinalzahl);


--
-- Name: wegereinigungsrhythmen_strassenreinigungssatzung_hro wegereinigungsrhythmen_strassenreinigungssatzung_hro_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.wegereinigungsrhythmen_strassenreinigungssatzung_hro
    ADD CONSTRAINT wegereinigungsrhythmen_strassenreinigungssatzung_hro_pk PRIMARY KEY (uuid);


--
-- Name: wegetypen_strassenreinigungssatzung_hro wegetypen_strassenreinigungssatzung_hro_code_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.wegetypen_strassenreinigungssatzung_hro
    ADD CONSTRAINT wegetypen_strassenreinigungssatzung_hro_code_unique UNIQUE (wegetyp);


--
-- Name: wegetypen_strassenreinigungssatzung_hro wegetypen_strassenreinigungssatzung_hro_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.wegetypen_strassenreinigungssatzung_hro
    ADD CONSTRAINT wegetypen_strassenreinigungssatzung_hro_pk PRIMARY KEY (uuid);


--
-- Name: zeiteinheiten zeiteinheiten_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.zeiteinheiten
    ADD CONSTRAINT zeiteinheiten_pk PRIMARY KEY (uuid);


--
-- Name: zeiteinheiten zeiteinheiten_zeiteinheit_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.zeiteinheiten
    ADD CONSTRAINT zeiteinheiten_zeiteinheit_unique UNIQUE (zeiteinheit);


--
-- Name: zh_typen_haltestellenkataster zh_typen_haltestellenkataster_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.zh_typen_haltestellenkataster
    ADD CONSTRAINT zh_typen_haltestellenkataster_pk PRIMARY KEY (uuid);


--
-- Name: zh_typen_haltestellenkataster zh_typen_haltestellenkataster_zh_typ_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.zh_typen_haltestellenkataster
    ADD CONSTRAINT zh_typen_haltestellenkataster_zh_typ_unique UNIQUE (zh_typ);


--
-- Name: zonen_parkscheinautomaten zonen_parkscheinautomaten_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.zonen_parkscheinautomaten
    ADD CONSTRAINT zonen_parkscheinautomaten_pk PRIMARY KEY (uuid);


--
-- Name: zonen_parkscheinautomaten zonen_parkscheinautomaten_zone_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.zonen_parkscheinautomaten
    ADD CONSTRAINT zonen_parkscheinautomaten_zone_unique UNIQUE (zone);


--
-- Name: zustaende_kadaverfunde zustaende_kadaverfunde_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.zustaende_kadaverfunde
    ADD CONSTRAINT zustaende_kadaverfunde_pk PRIMARY KEY (uuid);


--
-- Name: zustaende_kadaverfunde zustaende_kadaverfunde_zustand_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.zustaende_kadaverfunde
    ADD CONSTRAINT zustaende_kadaverfunde_zustand_unique UNIQUE (zustand);


--
-- Name: zustaende_schutzzaeune_tierseuchen zustaende_schutzzaeune_tierseuchen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.zustaende_schutzzaeune_tierseuchen
    ADD CONSTRAINT zustaende_schutzzaeune_tierseuchen_pk PRIMARY KEY (uuid);


--
-- Name: zustaende_schutzzaeune_tierseuchen zustaende_schutzzaeune_tierseuchen_zustand_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.zustaende_schutzzaeune_tierseuchen
    ADD CONSTRAINT zustaende_schutzzaeune_tierseuchen_zustand_unique UNIQUE (zustand);


--
-- Name: zustandsbewertungen zustandsbewertungen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.zustandsbewertungen
    ADD CONSTRAINT zustandsbewertungen_pk PRIMARY KEY (uuid);


--
-- Name: zustandsbewertungen zustandsbewertungen_zustandsbewertung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.zustandsbewertungen
    ADD CONSTRAINT zustandsbewertungen_zustandsbewertung_unique UNIQUE (zustandsbewertung);


--
-- Name: abfallbehaelter_hro abfallbehaelter_hro_id_unique; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.abfallbehaelter_hro
    ADD CONSTRAINT abfallbehaelter_hro_id_unique UNIQUE (id);


--
-- Name: abfallbehaelter_hro abfallbehaelter_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.abfallbehaelter_hro
    ADD CONSTRAINT abfallbehaelter_hro_pk PRIMARY KEY (uuid);


--
-- Name: adressunsicherheiten_fotos_hro adressunsicherheiten_fotos_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.adressunsicherheiten_fotos_hro
    ADD CONSTRAINT adressunsicherheiten_fotos_hro_pk PRIMARY KEY (uuid);


--
-- Name: angelverbotsbereiche_hro angelverbotsbereiche_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.angelverbotsbereiche_hro
    ADD CONSTRAINT angelverbotsbereiche_hro_pk PRIMARY KEY (uuid);


--
-- Name: baustellen_fotodokumentation_fotos_hro baustellen_fotodokumentation_fotos_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.baustellen_fotodokumentation_fotos_hro
    ADD CONSTRAINT baustellen_fotodokumentation_fotos_hro_pk PRIMARY KEY (uuid);


--
-- Name: baustellen_geplant_dokumente baustellen_geplant_dokumente_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.baustellen_geplant_dokumente
    ADD CONSTRAINT baustellen_geplant_dokumente_pk PRIMARY KEY (uuid);


--
-- Name: baustellen_geplant_links baustellen_geplant_links_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.baustellen_geplant_links
    ADD CONSTRAINT baustellen_geplant_links_pk PRIMARY KEY (uuid);


--
-- Name: bemas_altdaten_journalereignisse bemas_altdaten_journalereignisse_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.bemas_altdaten_journalereignisse
    ADD CONSTRAINT bemas_altdaten_journalereignisse_pk PRIMARY KEY (uuid);


--
-- Name: containerstellplaetze_hro containerstellplaetze_hro_id_unique; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.containerstellplaetze_hro
    ADD CONSTRAINT containerstellplaetze_hro_id_unique UNIQUE (id);


--
-- Name: containerstellplaetze_hro containerstellplaetze_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.containerstellplaetze_hro
    ADD CONSTRAINT containerstellplaetze_hro_pk PRIMARY KEY (uuid);


--
-- Name: denkmalbereiche_hro denkmalbereiche_hro_id_unique; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.denkmalbereiche_hro
    ADD CONSTRAINT denkmalbereiche_hro_id_unique UNIQUE (id);


--
-- Name: denkmalbereiche_hro denkmalbereiche_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.denkmalbereiche_hro
    ADD CONSTRAINT denkmalbereiche_hro_pk PRIMARY KEY (uuid);


--
-- Name: durchlaesse_durchlaesse_hro durchlaesse_durchlaesse_hro_aktenzeichen_unique; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.durchlaesse_durchlaesse_hro
    ADD CONSTRAINT durchlaesse_durchlaesse_hro_aktenzeichen_unique UNIQUE (aktenzeichen);


--
-- Name: durchlaesse_durchlaesse_hro durchlaesse_durchlaesse_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.durchlaesse_durchlaesse_hro
    ADD CONSTRAINT durchlaesse_durchlaesse_hro_pk PRIMARY KEY (uuid);


--
-- Name: durchlaesse_fotos_hro durchlaesse_fotos_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.durchlaesse_fotos_hro
    ADD CONSTRAINT durchlaesse_fotos_hro_pk PRIMARY KEY (uuid);


--
-- Name: erdwaermesonden_hro erdwaermesonden_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.erdwaermesonden_hro
    ADD CONSTRAINT erdwaermesonden_hro_pk PRIMARY KEY (uuid);


--
-- Name: fahrradabstellanlagen_hro fahrradabstellanlagen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.fahrradabstellanlagen_hro
    ADD CONSTRAINT fahrradabstellanlagen_hro_pk PRIMARY KEY (uuid);


--
-- Name: fallwildsuchen_kontrollgebiete_hro fallwildsuchen_kontrollgebiete_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.fallwildsuchen_kontrollgebiete_hro
    ADD CONSTRAINT fallwildsuchen_kontrollgebiete_hro_pk PRIMARY KEY (uuid);


--
-- Name: fallwildsuchen_nachweise_hro fallwildsuchen_nachweise_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.fallwildsuchen_nachweise_hro
    ADD CONSTRAINT fallwildsuchen_nachweise_hro_pk PRIMARY KEY (uuid);


--
-- Name: feldsportanlagen_hro feldsportanlagen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.feldsportanlagen_hro
    ADD CONSTRAINT feldsportanlagen_hro_pk PRIMARY KEY (uuid);


--
-- Name: fliessgewaesser_hro fliessgewaesser_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.fliessgewaesser_hro
    ADD CONSTRAINT fliessgewaesser_hro_pk PRIMARY KEY (uuid);


--
-- Name: geh_und_radwegereinigung_flaechen_hro geh_und_radwegereinigung_flaechen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.geh_und_radwegereinigung_flaechen_hro
    ADD CONSTRAINT geh_und_radwegereinigung_flaechen_hro_pk PRIMARY KEY (uuid);


--
-- Name: geraetespielanlagen_hro geraetespielanlagen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.geraetespielanlagen_hro
    ADD CONSTRAINT geraetespielanlagen_hro_pk PRIMARY KEY (uuid);


--
-- Name: haltestellenkataster_fotos_hro haltestellenkataster_fotos_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_fotos_hro
    ADD CONSTRAINT haltestellenkataster_fotos_hro_pk PRIMARY KEY (uuid);


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_haltestelle_unique; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_haltestelle_unique UNIQUE (hst_hafas_id, hst_bus_bahnsteigbezeichnung);


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_id_unique; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_id_unique UNIQUE (id);


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_pk PRIMARY KEY (uuid);


--
-- Name: hundetoiletten_hro hundetoiletten_hro_id_unique; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.hundetoiletten_hro
    ADD CONSTRAINT hundetoiletten_hro_id_unique UNIQUE (id);


--
-- Name: hundetoiletten_hro hundetoiletten_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.hundetoiletten_hro
    ADD CONSTRAINT hundetoiletten_hro_pk PRIMARY KEY (uuid);


--
-- Name: hydranten_hro hydranten_hro_bezeichnung_unique; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.hydranten_hro
    ADD CONSTRAINT hydranten_hro_bezeichnung_unique UNIQUE (bezeichnung);


--
-- Name: hydranten_hro hydranten_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.hydranten_hro
    ADD CONSTRAINT hydranten_hro_pk PRIMARY KEY (uuid);


--
-- Name: kadaverfunde_hro kadaverfunde_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.kadaverfunde_hro
    ADD CONSTRAINT kadaverfunde_hro_pk PRIMARY KEY (uuid);


--
-- Name: kunst_im_oeffentlichen_raum_hro kunst_im_oeffentlichen_raum_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.kunst_im_oeffentlichen_raum_hro
    ADD CONSTRAINT kunst_im_oeffentlichen_raum_hro_pk PRIMARY KEY (uuid);


--
-- Name: lichtwellenleiterinfrastruktur_abschnitte_hro lichtwellenleiterinfrastruktur_abschnitte_hro_bezeichnung_uniqu; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.lichtwellenleiterinfrastruktur_abschnitte_hro
    ADD CONSTRAINT lichtwellenleiterinfrastruktur_abschnitte_hro_bezeichnung_uniqu UNIQUE (id_fachsystem);


--
-- Name: lichtwellenleiterinfrastruktur_abschnitte_hro lichtwellenleiterinfrastruktur_abschnitte_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.lichtwellenleiterinfrastruktur_abschnitte_hro
    ADD CONSTRAINT lichtwellenleiterinfrastruktur_abschnitte_hro_pk PRIMARY KEY (uuid);


--
-- Name: lichtwellenleiterinfrastruktur_hro lichtwellenleiterinfrastruktur_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.lichtwellenleiterinfrastruktur_hro
    ADD CONSTRAINT lichtwellenleiterinfrastruktur_hro_pk PRIMARY KEY (uuid);


--
-- Name: meldedienst_flaechenhaft_hro meldedienst_flaechenhaft_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.meldedienst_flaechenhaft_hro
    ADD CONSTRAINT meldedienst_flaechenhaft_hro_pk PRIMARY KEY (uuid);


--
-- Name: mobilpunkte_hro mobilpunkte_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.mobilpunkte_hro
    ADD CONSTRAINT mobilpunkte_hro_pk PRIMARY KEY (uuid);


--
-- Name: parkscheinautomaten_parkscheinautomaten_hro parkscheinautomaten_parkscheinautomaten_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.parkscheinautomaten_parkscheinautomaten_hro
    ADD CONSTRAINT parkscheinautomaten_parkscheinautomaten_hro_pk PRIMARY KEY (uuid);


--
-- Name: parkscheinautomaten_tarife_hro parkscheinautomaten_tarife_hro_bezeichnung_unique; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.parkscheinautomaten_tarife_hro
    ADD CONSTRAINT parkscheinautomaten_tarife_hro_bezeichnung_unique UNIQUE (bezeichnung);


--
-- Name: parkscheinautomaten_tarife_hro parkscheinautomaten_tarife_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.parkscheinautomaten_tarife_hro
    ADD CONSTRAINT parkscheinautomaten_tarife_hro_pk PRIMARY KEY (uuid);


--
-- Name: poller_hro poller_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.poller_hro
    ADD CONSTRAINT poller_hro_pk PRIMARY KEY (uuid);


--
-- Name: reisebusparkplaetze_terminals_hro reisebusparkplaetze_terminals_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.reisebusparkplaetze_terminals_hro
    ADD CONSTRAINT reisebusparkplaetze_terminals_hro_pk PRIMARY KEY (uuid);


--
-- Name: rsag_gleise_hro rsag_gleise_hro_pkey; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.rsag_gleise_hro
    ADD CONSTRAINT rsag_gleise_hro_pkey PRIMARY KEY (uuid);


--
-- Name: rsag_leitungen_hro rsag_leitungen_hro_pkey; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.rsag_leitungen_hro
    ADD CONSTRAINT rsag_leitungen_hro_pkey PRIMARY KEY (uuid);


--
-- Name: rsag_masten_hro rsag_masten_hro_pkey; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.rsag_masten_hro
    ADD CONSTRAINT rsag_masten_hro_pkey PRIMARY KEY (uuid);


--
-- Name: rsag_quertraeger_hro rsag_quertraeger_hro_pkey; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.rsag_quertraeger_hro
    ADD CONSTRAINT rsag_quertraeger_hro_pkey PRIMARY KEY (uuid);


--
-- Name: rsag_spanndraehte_hro rsag_spanndraehte_hro_pkey; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.rsag_spanndraehte_hro
    ADD CONSTRAINT rsag_spanndraehte_hro_pkey PRIMARY KEY (uuid);


--
-- Name: schiffsliegeplaetze_hro schiffsliegeplaetze_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.schiffsliegeplaetze_hro
    ADD CONSTRAINT schiffsliegeplaetze_hro_pk PRIMARY KEY (uuid);


--
-- Name: schutzzaeune_tierseuchen_hro schutzzaeune_tierseuchen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.schutzzaeune_tierseuchen_hro
    ADD CONSTRAINT schutzzaeune_tierseuchen_hro_pk PRIMARY KEY (uuid);


--
-- Name: strassen_historie_hro strassen_historie_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.strassen_historie_hro
    ADD CONSTRAINT strassen_historie_hro_pk PRIMARY KEY (uuid);


--
-- Name: strassen_hro strassen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.strassen_hro
    ADD CONSTRAINT strassen_hro_pk PRIMARY KEY (uuid);


--
-- Name: strassen_hro strassen_hro_schluessel_unique; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.strassen_hro
    ADD CONSTRAINT strassen_hro_schluessel_unique UNIQUE (schluessel);


--
-- Name: strassen_namensanalye_hro strassen_namensanalye_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.strassen_namensanalye_hro
    ADD CONSTRAINT strassen_namensanalye_hro_pk PRIMARY KEY (uuid);


--
-- Name: strassenreinigung_flaechen_hro strassenreinigung_flaechen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.strassenreinigung_flaechen_hro
    ADD CONSTRAINT strassenreinigung_flaechen_hro_pk PRIMARY KEY (uuid);


--
-- Name: thalasso_kurwege_hro thalasso_kurwege_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.thalasso_kurwege_hro
    ADD CONSTRAINT thalasso_kurwege_hro_pk PRIMARY KEY (uuid);


--
-- Name: toiletten_hro toiletten_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.toiletten_hro
    ADD CONSTRAINT toiletten_hro_pk PRIMARY KEY (uuid);


--
-- Name: trinkwassernotbrunnen_hro trinkwassernotbrunnen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.trinkwassernotbrunnen_hro
    ADD CONSTRAINT trinkwassernotbrunnen_hro_pk PRIMARY KEY (uuid);


--
-- Name: uvp_vorhaben_hro uvp_vorhaben_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.uvp_vorhaben_hro
    ADD CONSTRAINT uvp_vorhaben_hro_pk PRIMARY KEY (uuid);


--
-- Name: uvp_vorpruefungen_hro uvp_vorpruefungen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.uvp_vorpruefungen_hro
    ADD CONSTRAINT uvp_vorpruefungen_hro_pk PRIMARY KEY (uuid);


--
-- Name: adressunsicherheiten_hro adressunsicherheiten_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.adressunsicherheiten_hro
    ADD CONSTRAINT adressunsicherheiten_hro_pk PRIMARY KEY (uuid);


--
-- Name: aufteilungsplaene_wohnungseigentumsgesetz_hro aufteilungsplaene_wohnungseigentumsgesetz_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.aufteilungsplaene_wohnungseigentumsgesetz_hro
    ADD CONSTRAINT aufteilungsplaene_wohnungseigentumsgesetz_hro_pk PRIMARY KEY (uuid);


--
-- Name: baudenkmale_hro baudenkmale_hro_id_unique; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.baudenkmale_hro
    ADD CONSTRAINT baudenkmale_hro_id_unique UNIQUE (id);


--
-- Name: baudenkmale_hro baudenkmale_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.baudenkmale_hro
    ADD CONSTRAINT baudenkmale_hro_pk PRIMARY KEY (uuid);


--
-- Name: behinderteneinrichtungen_hro behinderteneinrichtungen_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.behinderteneinrichtungen_hro
    ADD CONSTRAINT behinderteneinrichtungen_hro_pk PRIMARY KEY (uuid);


--
-- Name: bemas_altdaten_beschwerden bemas_altdaten_beschwerden_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.bemas_altdaten_beschwerden
    ADD CONSTRAINT bemas_altdaten_beschwerden_pk PRIMARY KEY (uuid);


--
-- Name: bemas_altdaten_verursacher bemas_altdaten_verursacher_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.bemas_altdaten_verursacher
    ADD CONSTRAINT bemas_altdaten_verursacher_pk PRIMARY KEY (uuid);


--
-- Name: beschluesse_bau_planungsausschuss_hro beschluesse_bau_planungsausschuss_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.beschluesse_bau_planungsausschuss_hro
    ADD CONSTRAINT beschluesse_bau_planungsausschuss_hro_pk PRIMARY KEY (uuid);


--
-- Name: bildungstraeger_hro bildungstraeger_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.bildungstraeger_hro
    ADD CONSTRAINT bildungstraeger_hro_pk PRIMARY KEY (uuid);


--
-- Name: carsharing_stationen_hro carsharing_stationen_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.carsharing_stationen_hro
    ADD CONSTRAINT carsharing_stationen_hro_pk PRIMARY KEY (uuid);


--
-- Name: denksteine_hro denksteine_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.denksteine_hro
    ADD CONSTRAINT denksteine_hro_pk PRIMARY KEY (uuid);


--
-- Name: fairtrade_hro fairtrade_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.fairtrade_hro
    ADD CONSTRAINT fairtrade_hro_pk PRIMARY KEY (uuid);


--
-- Name: feuerwachen_hro feuerwachen_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.feuerwachen_hro
    ADD CONSTRAINT feuerwachen_hro_pk PRIMARY KEY (uuid);


--
-- Name: gutachterfotos_hro gutachterfotos_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.gutachterfotos_hro
    ADD CONSTRAINT gutachterfotos_hro_pk PRIMARY KEY (uuid);


--
-- Name: hospize_hro hospize_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.hospize_hro
    ADD CONSTRAINT hospize_hro_pk PRIMARY KEY (uuid);


--
-- Name: kehrbezirke_hro kehrbezirke_hro_adresse_unique; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.kehrbezirke_hro
    ADD CONSTRAINT kehrbezirke_hro_adresse_unique UNIQUE (adresse);


--
-- Name: kehrbezirke_hro kehrbezirke_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.kehrbezirke_hro
    ADD CONSTRAINT kehrbezirke_hro_pk PRIMARY KEY (uuid);


--
-- Name: kinder_jugendbetreuung_hro kinder_jugendbetreuung_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.kinder_jugendbetreuung_hro
    ADD CONSTRAINT kinder_jugendbetreuung_hro_pk PRIMARY KEY (uuid);


--
-- Name: kindertagespflegeeinrichtungen_hro kindertagespflegeeinrichtungen_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.kindertagespflegeeinrichtungen_hro
    ADD CONSTRAINT kindertagespflegeeinrichtungen_hro_pk PRIMARY KEY (uuid);


--
-- Name: kleinklaeranlagen_hro kleinklaeranlagen_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.kleinklaeranlagen_hro
    ADD CONSTRAINT kleinklaeranlagen_hro_pk PRIMARY KEY (uuid);


--
-- Name: ladestationen_elektrofahrzeuge_hro ladestationen_elektrofahrzeuge_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.ladestationen_elektrofahrzeuge_hro
    ADD CONSTRAINT ladestationen_elektrofahrzeuge_hro_pk PRIMARY KEY (uuid);


--
-- Name: meldedienst_punkthaft_hro meldedienst_punkthaft_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.meldedienst_punkthaft_hro
    ADD CONSTRAINT meldedienst_punkthaft_hro_pk PRIMARY KEY (uuid);


--
-- Name: parkmoeglichkeiten_hro parkmoeglichkeiten_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.parkmoeglichkeiten_hro
    ADD CONSTRAINT parkmoeglichkeiten_hro_pk PRIMARY KEY (uuid);


--
-- Name: pflegeeinrichtungen_hro pflegeeinrichtungen_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.pflegeeinrichtungen_hro
    ADD CONSTRAINT pflegeeinrichtungen_hro_pk PRIMARY KEY (uuid);


--
-- Name: rettungswachen_hro rettungswachen_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.rettungswachen_hro
    ADD CONSTRAINT rettungswachen_hro_pk PRIMARY KEY (uuid);


--
-- Name: sporthallen_hro sporthallen_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.sporthallen_hro
    ADD CONSTRAINT sporthallen_hro_pk PRIMARY KEY (uuid);


--
-- Name: stadtteil_begegnungszentren_hro stadtteil_begegnungszentren_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.stadtteil_begegnungszentren_hro
    ADD CONSTRAINT stadtteil_begegnungszentren_hro_pk PRIMARY KEY (uuid);


--
-- Name: standortqualitaeten_geschaeftslagen_sanierungsgebiet_hro standortqualitaeten_geschaeftslagen_sanierungsgebiet_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.standortqualitaeten_geschaeftslagen_sanierungsgebiet_hro
    ADD CONSTRAINT standortqualitaeten_geschaeftslagen_sanierungsgebiet_hro_pk PRIMARY KEY (uuid);


--
-- Name: standortqualitaeten_wohnlagen_sanierungsgebiet_hro standortqualitaeten_wohnlagen_sanierungsgebiet_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.standortqualitaeten_wohnlagen_sanierungsgebiet_hro
    ADD CONSTRAINT standortqualitaeten_wohnlagen_sanierungsgebiet_hro_pk PRIMARY KEY (uuid);


--
-- Name: vereine_hro vereine_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.vereine_hro
    ADD CONSTRAINT vereine_hro_pk PRIMARY KEY (uuid);


--
-- Name: verkaufstellen_angelberechtigungen_hro verkaufstellen_angelberechtigungen_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.verkaufstellen_angelberechtigungen_hro
    ADD CONSTRAINT verkaufstellen_angelberechtigungen_hro_pk PRIMARY KEY (uuid);


--
-- Name: reinigungsreviere_hro reinigungsreviere_hro_nummer_unique; Type: CONSTRAINT; Schema: fachdaten_gemeindeteilbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_gemeindeteilbezug.reinigungsreviere_hro
    ADD CONSTRAINT reinigungsreviere_hro_nummer_unique UNIQUE (nummer);


--
-- Name: reinigungsreviere_hro reinigungsreviere_hro_pk; Type: CONSTRAINT; Schema: fachdaten_gemeindeteilbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_gemeindeteilbezug.reinigungsreviere_hro
    ADD CONSTRAINT reinigungsreviere_hro_pk PRIMARY KEY (uuid);


--
-- Name: baustellen_fotodokumentation_baustellen_hro baustellen_fotodokumentation_baustellen_hro_pk; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.baustellen_fotodokumentation_baustellen_hro
    ADD CONSTRAINT baustellen_fotodokumentation_baustellen_hro_pk PRIMARY KEY (uuid);


--
-- Name: baustellen_geplant baustellen_geplant_pk; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.baustellen_geplant
    ADD CONSTRAINT baustellen_geplant_pk PRIMARY KEY (uuid);


--
-- Name: geh_und_radwegereinigung_hro geh_und_radwegereinigung_hro_pk; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.geh_und_radwegereinigung_hro
    ADD CONSTRAINT geh_und_radwegereinigung_hro_pk PRIMARY KEY (uuid);


--
-- Name: hausnummern_hro hausnummern_hro_hausnummer_unique; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.hausnummern_hro
    ADD CONSTRAINT hausnummern_hro_hausnummer_unique UNIQUE (strasse, hausnummer, hausnummer_zusatz);


--
-- Name: hausnummern_hro hausnummern_hro_pk; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.hausnummern_hro
    ADD CONSTRAINT hausnummern_hro_pk PRIMARY KEY (uuid);


--
-- Name: ingenieurbauwerke_hro ingenieurbauwerke_hro_pk; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.ingenieurbauwerke_hro
    ADD CONSTRAINT ingenieurbauwerke_hro_pk PRIMARY KEY (uuid);


--
-- Name: strassenreinigung_hro strassenreinigung_hro_pk; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.strassenreinigung_hro
    ADD CONSTRAINT strassenreinigung_hro_pk PRIMARY KEY (uuid);


--
-- Name: feldsportanlagen_hro tr_before_insert_10_foto; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_10_foto BEFORE INSERT ON fachdaten.feldsportanlagen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: geraetespielanlagen_hro tr_before_insert_10_foto; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_10_foto BEFORE INSERT ON fachdaten.geraetespielanlagen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: containerstellplaetze_hro tr_before_insert_10_id; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_10_id BEFORE INSERT ON fachdaten.containerstellplaetze_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.id_containerstellplaetze();


--
-- Name: fliessgewaesser_hro tr_before_insert_10_laenge; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_10_laenge BEFORE INSERT ON fachdaten.fliessgewaesser_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.laenge();


--
-- Name: schutzzaeune_tierseuchen_hro tr_before_insert_10_laenge; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_10_laenge BEFORE INSERT ON fachdaten.schutzzaeune_tierseuchen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.laenge();


--
-- Name: thalasso_kurwege_hro tr_before_insert_10_laenge; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_10_laenge BEFORE INSERT ON fachdaten.thalasso_kurwege_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.laenge();


--
-- Name: containerstellplaetze_hro tr_before_insert_20_foto; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_20_foto BEFORE INSERT ON fachdaten.containerstellplaetze_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: fliessgewaesser_hro tr_before_insert_20_laenge_in_hro; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_20_laenge_in_hro BEFORE INSERT ON fachdaten.fliessgewaesser_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.laenge_in_hro();


--
-- Name: abfallbehaelter_hro tr_before_insert_id; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_id BEFORE INSERT ON fachdaten.abfallbehaelter_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.id_abfallbehaelter();


--
-- Name: denkmalbereiche_hro tr_before_insert_id; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_id BEFORE INSERT ON fachdaten.denkmalbereiche_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.id_denkmalbereiche();


--
-- Name: haltestellenkataster_haltestellen_hro tr_before_insert_id; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_id BEFORE INSERT ON fachdaten.haltestellenkataster_haltestellen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.id_haltestellen();


--
-- Name: hundetoiletten_hro tr_before_insert_id; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_id BEFORE INSERT ON fachdaten.hundetoiletten_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.id_hundetoiletten();


--
-- Name: containerstellplaetze_hro tr_before_update_10_foto; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_update_10_foto BEFORE UPDATE OF foto ON fachdaten.containerstellplaetze_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: feldsportanlagen_hro tr_before_update_10_foto; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_update_10_foto BEFORE UPDATE OF foto ON fachdaten.feldsportanlagen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: geraetespielanlagen_hro tr_before_update_10_foto; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_update_10_foto BEFORE UPDATE OF foto ON fachdaten.geraetespielanlagen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: fliessgewaesser_hro tr_before_update_10_laenge; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_update_10_laenge BEFORE UPDATE OF geometrie ON fachdaten.fliessgewaesser_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.laenge();


--
-- Name: schutzzaeune_tierseuchen_hro tr_before_update_10_laenge; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_update_10_laenge BEFORE UPDATE OF geometrie ON fachdaten.schutzzaeune_tierseuchen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.laenge();


--
-- Name: thalasso_kurwege_hro tr_before_update_10_laenge; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_update_10_laenge BEFORE UPDATE OF geometrie ON fachdaten.thalasso_kurwege_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.laenge();


--
-- Name: fliessgewaesser_hro tr_before_update_20_laenge_in_hro; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_update_20_laenge_in_hro BEFORE UPDATE OF geometrie ON fachdaten.fliessgewaesser_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.laenge_in_hro();


--
-- Name: abfallbehaelter_hro tr_before_update_98_deaktiviert; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_update_98_deaktiviert BEFORE UPDATE OF aktiv ON fachdaten.abfallbehaelter_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.deaktiviert();


--
-- Name: containerstellplaetze_hro tr_before_update_98_deaktiviert; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_update_98_deaktiviert BEFORE UPDATE OF aktiv ON fachdaten.containerstellplaetze_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.deaktiviert();


--
-- Name: sporthallen_hro tr_before_insert_10_foto; Type: TRIGGER; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_10_foto BEFORE INSERT ON fachdaten_adressbezug.sporthallen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: baudenkmale_hro tr_before_insert_id; Type: TRIGGER; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_id BEFORE INSERT ON fachdaten_adressbezug.baudenkmale_hro FOR EACH ROW EXECUTE FUNCTION fachdaten_adressbezug.id_baudenkmale();


--
-- Name: sporthallen_hro tr_before_update_10_foto; Type: TRIGGER; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TRIGGER tr_before_update_10_foto BEFORE UPDATE OF foto ON fachdaten_adressbezug.sporthallen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: geh_und_radwegereinigung_hro tr_before_insert_10_laenge; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_10_laenge BEFORE INSERT ON fachdaten_strassenbezug.geh_und_radwegereinigung_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.laenge();


--
-- Name: strassenreinigung_hro tr_before_insert_10_laenge; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_10_laenge BEFORE INSERT ON fachdaten_strassenbezug.strassenreinigung_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.laenge();


--
-- Name: geh_und_radwegereinigung_hro tr_before_insert_20_gemeindeteil; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_20_gemeindeteil BEFORE INSERT ON fachdaten_strassenbezug.geh_und_radwegereinigung_hro FOR EACH ROW EXECUTE FUNCTION fachdaten_strassenbezug.gemeindeteil();


--
-- Name: strassenreinigung_hro tr_before_insert_20_gemeindeteil; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_20_gemeindeteil BEFORE INSERT ON fachdaten_strassenbezug.strassenreinigung_hro FOR EACH ROW EXECUTE FUNCTION fachdaten_strassenbezug.gemeindeteil();


--
-- Name: geh_und_radwegereinigung_hro tr_before_insert_id; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_id BEFORE INSERT ON fachdaten_strassenbezug.geh_und_radwegereinigung_hro FOR EACH ROW EXECUTE FUNCTION fachdaten_strassenbezug.id();


--
-- Name: strassenreinigung_hro tr_before_insert_id; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_id BEFORE INSERT ON fachdaten_strassenbezug.strassenreinigung_hro FOR EACH ROW EXECUTE FUNCTION fachdaten_strassenbezug.id();


--
-- Name: geh_und_radwegereinigung_hro tr_before_update_10_laenge; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_update_10_laenge BEFORE UPDATE OF geometrie ON fachdaten_strassenbezug.geh_und_radwegereinigung_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.laenge();


--
-- Name: strassenreinigung_hro tr_before_update_10_laenge; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_update_10_laenge BEFORE UPDATE OF geometrie ON fachdaten_strassenbezug.strassenreinigung_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.laenge();


--
-- Name: geh_und_radwegereinigung_hro tr_before_update_20_gemeindeteil; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_update_20_gemeindeteil BEFORE UPDATE OF geometrie ON fachdaten_strassenbezug.geh_und_radwegereinigung_hro FOR EACH ROW EXECUTE FUNCTION fachdaten_strassenbezug.gemeindeteil();


--
-- Name: strassenreinigung_hro tr_before_update_20_gemeindeteil; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_update_20_gemeindeteil BEFORE UPDATE OF geometrie ON fachdaten_strassenbezug.strassenreinigung_hro FOR EACH ROW EXECUTE FUNCTION fachdaten_strassenbezug.gemeindeteil();


--
-- Name: abfallbehaelter_hro abfallbehaelter_hro_bewirtschafter_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.abfallbehaelter_hro
    ADD CONSTRAINT abfallbehaelter_hro_bewirtschafter_fk FOREIGN KEY (bewirtschafter) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: abfallbehaelter_hro abfallbehaelter_hro_eigentuemer_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.abfallbehaelter_hro
    ADD CONSTRAINT abfallbehaelter_hro_eigentuemer_fk FOREIGN KEY (eigentuemer) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: abfallbehaelter_hro abfallbehaelter_hro_typen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.abfallbehaelter_hro
    ADD CONSTRAINT abfallbehaelter_hro_typen_fk FOREIGN KEY (typ) REFERENCES codelisten.typen_abfallbehaelter(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: adressunsicherheiten_fotos_hro adressunsicherheiten_fotos_hro_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.adressunsicherheiten_fotos_hro
    ADD CONSTRAINT adressunsicherheiten_fotos_hro_fk FOREIGN KEY (adressunsicherheit) REFERENCES fachdaten_adressbezug.adressunsicherheiten_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: baustellen_fotodokumentation_fotos_hro baustellen_fotodokumentation_fotos_hro_baustellen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.baustellen_fotodokumentation_fotos_hro
    ADD CONSTRAINT baustellen_fotodokumentation_fotos_hro_baustellen_fk FOREIGN KEY (baustellen_fotodokumentation_baustelle) REFERENCES fachdaten_strassenbezug.baustellen_fotodokumentation_baustellen_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: baustellen_fotodokumentation_fotos_hro baustellen_fotodokumentation_fotos_hro_status_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.baustellen_fotodokumentation_fotos_hro
    ADD CONSTRAINT baustellen_fotodokumentation_fotos_hro_status_fk FOREIGN KEY (status) REFERENCES codelisten.status_baustellen_fotodokumentation_fotos(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: baustellen_geplant_dokumente baustellen_geplant_dokumente_baustellen_geplant_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.baustellen_geplant_dokumente
    ADD CONSTRAINT baustellen_geplant_dokumente_baustellen_geplant_fk FOREIGN KEY (baustelle_geplant) REFERENCES fachdaten_strassenbezug.baustellen_geplant(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: baustellen_geplant_links baustellen_geplant_links_baustellen_geplant_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.baustellen_geplant_links
    ADD CONSTRAINT baustellen_geplant_links_baustellen_geplant_fk FOREIGN KEY (baustelle_geplant) REFERENCES fachdaten_strassenbezug.baustellen_geplant(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: containerstellplaetze_hro containerstellplaetze_hro_bewirtschafter_altkleider_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.containerstellplaetze_hro
    ADD CONSTRAINT containerstellplaetze_hro_bewirtschafter_altkleider_fk FOREIGN KEY (bewirtschafter_altkleider) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: containerstellplaetze_hro containerstellplaetze_hro_bewirtschafter_glas_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.containerstellplaetze_hro
    ADD CONSTRAINT containerstellplaetze_hro_bewirtschafter_glas_fk FOREIGN KEY (bewirtschafter_glas) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: containerstellplaetze_hro containerstellplaetze_hro_bewirtschafter_grundundboden_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.containerstellplaetze_hro
    ADD CONSTRAINT containerstellplaetze_hro_bewirtschafter_grundundboden_fk FOREIGN KEY (bewirtschafter_grundundboden) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: containerstellplaetze_hro containerstellplaetze_hro_bewirtschafter_papier_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.containerstellplaetze_hro
    ADD CONSTRAINT containerstellplaetze_hro_bewirtschafter_papier_fk FOREIGN KEY (bewirtschafter_papier) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: denkmalbereiche_hro denkmalbereiche_hro_status_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.denkmalbereiche_hro
    ADD CONSTRAINT denkmalbereiche_hro_status_fk FOREIGN KEY (status) REFERENCES codelisten.status_baudenkmale_denkmalbereiche(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: durchlaesse_durchlaesse_hro durchlaesse_durchlaesse_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.durchlaesse_durchlaesse_hro
    ADD CONSTRAINT durchlaesse_durchlaesse_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_durchlaesse(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: durchlaesse_durchlaesse_hro durchlaesse_durchlaesse_hro_materialien_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.durchlaesse_durchlaesse_hro
    ADD CONSTRAINT durchlaesse_durchlaesse_hro_materialien_fk FOREIGN KEY (material) REFERENCES codelisten.materialien_durchlaesse(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: durchlaesse_durchlaesse_hro durchlaesse_durchlaesse_hro_zustaende_durchlaesse_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.durchlaesse_durchlaesse_hro
    ADD CONSTRAINT durchlaesse_durchlaesse_hro_zustaende_durchlaesse_fk FOREIGN KEY (zustand_durchlass) REFERENCES codelisten.zustandsbewertungen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: durchlaesse_durchlaesse_hro durchlaesse_durchlaesse_hro_zustaende_nebenanlagen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.durchlaesse_durchlaesse_hro
    ADD CONSTRAINT durchlaesse_durchlaesse_hro_zustaende_nebenanlagen_fk FOREIGN KEY (zustand_nebenanlagen) REFERENCES codelisten.zustandsbewertungen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: durchlaesse_durchlaesse_hro durchlaesse_durchlaesse_hro_zustaende_zubehoer_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.durchlaesse_durchlaesse_hro
    ADD CONSTRAINT durchlaesse_durchlaesse_hro_zustaende_zubehoer_fk FOREIGN KEY (zustand_zubehoer) REFERENCES codelisten.zustandsbewertungen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: durchlaesse_fotos_hro durchlaesse_fotos_hro_durchlaesse_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.durchlaesse_fotos_hro
    ADD CONSTRAINT durchlaesse_fotos_hro_durchlaesse_fk FOREIGN KEY (durchlaesse_durchlass) REFERENCES fachdaten.durchlaesse_durchlaesse_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: erdwaermesonden_hro erdwaermesonden_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.erdwaermesonden_hro
    ADD CONSTRAINT erdwaermesonden_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_erdwaermesonden(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: erdwaermesonden_hro erdwaermesonden_hro_typen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.erdwaermesonden_hro
    ADD CONSTRAINT erdwaermesonden_hro_typen_fk FOREIGN KEY (typ) REFERENCES codelisten.typen_erdwaermesonden(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: fahrradabstellanlagen_hro fahrradabstellanlagen_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.fahrradabstellanlagen_hro
    ADD CONSTRAINT fahrradabstellanlagen_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_fahrradabstellanlagen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: fallwildsuchen_kontrollgebiete_hro fallwildsuchen_kontrollgebiete_hro_tierseuchen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.fallwildsuchen_kontrollgebiete_hro
    ADD CONSTRAINT fallwildsuchen_kontrollgebiete_hro_tierseuchen_fk FOREIGN KEY (tierseuche) REFERENCES codelisten.tierseuchen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: fallwildsuchen_nachweise_hro fallwildsuchen_nachweise_hro_arten_kontrolle_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.fallwildsuchen_nachweise_hro
    ADD CONSTRAINT fallwildsuchen_nachweise_hro_arten_kontrolle_fk FOREIGN KEY (art_kontrolle) REFERENCES codelisten.arten_fallwildsuchen_kontrollen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: fallwildsuchen_nachweise_hro fallwildsuchen_nachweise_hro_kontrollgebiete_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.fallwildsuchen_nachweise_hro
    ADD CONSTRAINT fallwildsuchen_nachweise_hro_kontrollgebiete_fk FOREIGN KEY (kontrollgebiet) REFERENCES fachdaten.fallwildsuchen_kontrollgebiete_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: feldsportanlagen_hro feldsportanlagen_hro_traeger_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.feldsportanlagen_hro
    ADD CONSTRAINT feldsportanlagen_hro_traeger_fk FOREIGN KEY (traeger) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: fliessgewaesser_hro fliessgewaesser_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.fliessgewaesser_hro
    ADD CONSTRAINT fliessgewaesser_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_fliessgewaesser(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: fliessgewaesser_hro fliessgewaesser_hro_ordnungen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.fliessgewaesser_hro
    ADD CONSTRAINT fliessgewaesser_hro_ordnungen_fk FOREIGN KEY (ordnung) REFERENCES codelisten.ordnungen_fliessgewaesser(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: geraetespielanlagen_hro geraetespielanlagen_hro_traeger_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.geraetespielanlagen_hro
    ADD CONSTRAINT geraetespielanlagen_hro_traeger_fk FOREIGN KEY (traeger) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: haltestellenkataster_fotos_hro haltestellenkataster_fotos_hro_haltestellen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_fotos_hro
    ADD CONSTRAINT haltestellenkataster_fotos_hro_haltestellen_fk FOREIGN KEY (haltestellenkataster_haltestelle) REFERENCES fachdaten.haltestellenkataster_haltestellen_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: haltestellenkataster_fotos_hro haltestellenkataster_fotos_hro_motive_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_fotos_hro
    ADD CONSTRAINT haltestellenkataster_fotos_hro_motive_fk FOREIGN KEY (motiv) REFERENCES codelisten.fotomotive_haltestellenkataster(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_as_dfi_typen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_as_dfi_typen_fk FOREIGN KEY (as_dfi_typ) REFERENCES codelisten.dfi_typen_haltestellenkataster(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_as_fahrgastunterstandstyp; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_as_fahrgastunterstandstyp FOREIGN KEY (as_fahrgastunterstandstyp) REFERENCES codelisten.fahrgastunterstandstypen_haltestellenkataster(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_as_fahrplanvitrinentypen_; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_as_fahrplanvitrinentypen_ FOREIGN KEY (as_fahrplanvitrinentyp) REFERENCES codelisten.fahrplanvitrinentypen_haltestellenkataster(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_as_h_masttypen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_as_h_masttypen_fk FOREIGN KEY (as_h_masttyp) REFERENCES codelisten.masttypen_haltestellenkataster(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_as_sitzbanktypen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_as_sitzbanktypen_fk FOREIGN KEY (as_sitzbanktyp) REFERENCES codelisten.sitzbanktypen_haltestellenkataster(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_as_zh_typen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_as_zh_typen_fk FOREIGN KEY (as_zh_typ) REFERENCES codelisten.zh_typen_haltestellenkataster(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_bau_befestigungsarten_auf; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_bau_befestigungsarten_auf FOREIGN KEY (bau_befestigungsart_aufstellflaeche_bus) REFERENCES codelisten.befestigungsarten_aufstellflaeche_bus_haltestellenkataster(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_bau_befestigungsarten_war; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_bau_befestigungsarten_war FOREIGN KEY (bau_befestigungsart_warteflaeche) REFERENCES codelisten.befestigungsarten_warteflaeche_haltestellenkataster(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_bau_typen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_bau_typen_fk FOREIGN KEY (bau_typ) REFERENCES codelisten.typen_haltestellen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_bau_zustaende_aufstellfla; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_bau_zustaende_aufstellfla FOREIGN KEY (bau_zustand_aufstellflaeche_bus) REFERENCES codelisten.schaeden_haltestellenkataster(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_bau_zustaende_warteflaech; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_bau_zustaende_warteflaech FOREIGN KEY (bau_zustand_warteflaeche) REFERENCES codelisten.schaeden_haltestellenkataster(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_tl_auffindestreifen_ausfu; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_tl_auffindestreifen_ausfu FOREIGN KEY (tl_auffindestreifen_ausfuehrung) REFERENCES codelisten.ausfuehrungen_haltestellenkataster(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_tl_einstiegsfelder_ausfue; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_tl_einstiegsfelder_ausfue FOREIGN KEY (tl_einstiegsfeld_ausfuehrung) REFERENCES codelisten.ausfuehrungen_haltestellenkataster(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: haltestellenkataster_haltestellen_hro haltestellenkataster_haltestellen_hro_tl_leitstreifen_ausfuehru; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.haltestellenkataster_haltestellen_hro
    ADD CONSTRAINT haltestellenkataster_haltestellen_hro_tl_leitstreifen_ausfuehru FOREIGN KEY (tl_leitstreifen_ausfuehrung) REFERENCES codelisten.ausfuehrungen_haltestellenkataster(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: hundetoiletten_hro hundetoiletten_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.hundetoiletten_hro
    ADD CONSTRAINT hundetoiletten_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_hundetoiletten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: hundetoiletten_hro hundetoiletten_hro_bewirtschafter_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.hundetoiletten_hro
    ADD CONSTRAINT hundetoiletten_hro_bewirtschafter_fk FOREIGN KEY (bewirtschafter) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: hydranten_hro hydranten_hro_betriebszeiten_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.hydranten_hro
    ADD CONSTRAINT hydranten_hro_betriebszeiten_fk FOREIGN KEY (betriebszeit) REFERENCES codelisten.betriebszeiten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: hydranten_hro hydranten_hro_bewirtschafter_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.hydranten_hro
    ADD CONSTRAINT hydranten_hro_bewirtschafter_fk FOREIGN KEY (bewirtschafter) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: hydranten_hro hydranten_hro_eigentuemer_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.hydranten_hro
    ADD CONSTRAINT hydranten_hro_eigentuemer_fk FOREIGN KEY (eigentuemer) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: kadaverfunde_hro kadaverfunde_hro_altersklassen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.kadaverfunde_hro
    ADD CONSTRAINT kadaverfunde_hro_altersklassen_fk FOREIGN KEY (altersklasse) REFERENCES codelisten.altersklassen_kadaverfunde(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: kadaverfunde_hro kadaverfunde_hro_arten_auffinden_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.kadaverfunde_hro
    ADD CONSTRAINT kadaverfunde_hro_arten_auffinden_fk FOREIGN KEY (art_auffinden) REFERENCES codelisten.arten_fallwildsuchen_kontrollen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: kadaverfunde_hro kadaverfunde_hro_geschlechter_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.kadaverfunde_hro
    ADD CONSTRAINT kadaverfunde_hro_geschlechter_fk FOREIGN KEY (geschlecht) REFERENCES codelisten.geschlechter_kadaverfunde(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: kadaverfunde_hro kadaverfunde_hro_tierseuchen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.kadaverfunde_hro
    ADD CONSTRAINT kadaverfunde_hro_tierseuchen_fk FOREIGN KEY (tierseuche) REFERENCES codelisten.tierseuchen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: kadaverfunde_hro kadaverfunde_hro_zustaende_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.kadaverfunde_hro
    ADD CONSTRAINT kadaverfunde_hro_zustaende_fk FOREIGN KEY (zustand) REFERENCES codelisten.zustaende_kadaverfunde(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: lichtwellenleiterinfrastruktur_hro lichtwellenleiterinfrastruktur_hro_kabeltypen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.lichtwellenleiterinfrastruktur_hro
    ADD CONSTRAINT lichtwellenleiterinfrastruktur_hro_kabeltypen_fk FOREIGN KEY (kabeltyp) REFERENCES codelisten.kabeltypen_lichtwellenleiterinfrastruktur(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: lichtwellenleiterinfrastruktur_hro lichtwellenleiterinfrastruktur_hro_objektarten_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.lichtwellenleiterinfrastruktur_hro
    ADD CONSTRAINT lichtwellenleiterinfrastruktur_hro_objektarten_fk FOREIGN KEY (objektart) REFERENCES codelisten.objektarten_lichtwellenleiterinfrastruktur(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: meldedienst_flaechenhaft_hro meldedienst_flaechenhaft_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.meldedienst_flaechenhaft_hro
    ADD CONSTRAINT meldedienst_flaechenhaft_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_meldedienst_flaechenhaft(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: parkscheinautomaten_parkscheinautomaten_hro parkscheinautomaten_parkscheinautomaten_hro_e_anschluesse_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.parkscheinautomaten_parkscheinautomaten_hro
    ADD CONSTRAINT parkscheinautomaten_parkscheinautomaten_hro_e_anschluesse_fk FOREIGN KEY (e_anschluss) REFERENCES codelisten.e_anschluesse_parkscheinautomaten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: parkscheinautomaten_parkscheinautomaten_hro parkscheinautomaten_parkscheinautomaten_hro_tarife_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.parkscheinautomaten_parkscheinautomaten_hro
    ADD CONSTRAINT parkscheinautomaten_parkscheinautomaten_hro_tarife_fk FOREIGN KEY (parkscheinautomaten_tarif) REFERENCES fachdaten.parkscheinautomaten_tarife_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: parkscheinautomaten_parkscheinautomaten_hro parkscheinautomaten_parkscheinautomaten_hro_zonen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.parkscheinautomaten_parkscheinautomaten_hro
    ADD CONSTRAINT parkscheinautomaten_parkscheinautomaten_hro_zonen_fk FOREIGN KEY (zone) REFERENCES codelisten.zonen_parkscheinautomaten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: parkscheinautomaten_tarife_hro parkscheinautomaten_tarife_hro_normaltarif_parkdauer_max_einhei; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.parkscheinautomaten_tarife_hro
    ADD CONSTRAINT parkscheinautomaten_tarife_hro_normaltarif_parkdauer_max_einhei FOREIGN KEY (normaltarif_parkdauer_max_einheit) REFERENCES codelisten.zeiteinheiten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: parkscheinautomaten_tarife_hro parkscheinautomaten_tarife_hro_normaltarif_parkdauer_min_einhei; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.parkscheinautomaten_tarife_hro
    ADD CONSTRAINT parkscheinautomaten_tarife_hro_normaltarif_parkdauer_min_einhei FOREIGN KEY (normaltarif_parkdauer_min_einheit) REFERENCES codelisten.zeiteinheiten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: parkscheinautomaten_tarife_hro parkscheinautomaten_tarife_hro_veranstaltungstarif_parkdauer_ma; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.parkscheinautomaten_tarife_hro
    ADD CONSTRAINT parkscheinautomaten_tarife_hro_veranstaltungstarif_parkdauer_ma FOREIGN KEY (veranstaltungstarif_parkdauer_max_einheit) REFERENCES codelisten.zeiteinheiten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: parkscheinautomaten_tarife_hro parkscheinautomaten_tarife_hro_veranstaltungstarif_parkdauer_mi; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.parkscheinautomaten_tarife_hro
    ADD CONSTRAINT parkscheinautomaten_tarife_hro_veranstaltungstarif_parkdauer_mi FOREIGN KEY (veranstaltungstarif_parkdauer_min_einheit) REFERENCES codelisten.zeiteinheiten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: poller_hro poller_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.poller_hro
    ADD CONSTRAINT poller_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_poller(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: poller_hro poller_hro_hersteller_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.poller_hro
    ADD CONSTRAINT poller_hro_hersteller_fk FOREIGN KEY (hersteller) REFERENCES codelisten.hersteller_poller(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: poller_hro poller_hro_status_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.poller_hro
    ADD CONSTRAINT poller_hro_status_fk FOREIGN KEY (status) REFERENCES codelisten.status_poller(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: poller_hro poller_hro_typen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.poller_hro
    ADD CONSTRAINT poller_hro_typen_fk FOREIGN KEY (typ) REFERENCES codelisten.typen_poller(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: reisebusparkplaetze_terminals_hro reisebusparkplaetze_terminals_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.reisebusparkplaetze_terminals_hro
    ADD CONSTRAINT reisebusparkplaetze_terminals_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_reisebusparkplaetze_terminals(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: rsag_masten_hro rsag_masten_hro_fundamenttypen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.rsag_masten_hro
    ADD CONSTRAINT rsag_masten_hro_fundamenttypen_fk FOREIGN KEY (fundamenttyp) REFERENCES codelisten.fundamenttypen_rsag(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: rsag_masten_hro rsag_masten_hro_mastkennzeichen_1_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.rsag_masten_hro
    ADD CONSTRAINT rsag_masten_hro_mastkennzeichen_1_fk FOREIGN KEY (mastkennzeichen_1) REFERENCES codelisten.mastkennzeichen_rsag(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: rsag_masten_hro rsag_masten_hro_mastkennzeichen_2_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.rsag_masten_hro
    ADD CONSTRAINT rsag_masten_hro_mastkennzeichen_2_fk FOREIGN KEY (mastkennzeichen_2) REFERENCES codelisten.mastkennzeichen_rsag(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: rsag_masten_hro rsag_masten_hro_mastkennzeichen_3_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.rsag_masten_hro
    ADD CONSTRAINT rsag_masten_hro_mastkennzeichen_3_fk FOREIGN KEY (mastkennzeichen_3) REFERENCES codelisten.mastkennzeichen_rsag(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: rsag_masten_hro rsag_masten_hro_masttypen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.rsag_masten_hro
    ADD CONSTRAINT rsag_masten_hro_masttypen_fk FOREIGN KEY (masttyp) REFERENCES codelisten.masttypen_rsag(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: rsag_masten_hro rsag_msten_hro_mastkennzeichen_4_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.rsag_masten_hro
    ADD CONSTRAINT rsag_msten_hro_mastkennzeichen_4_fk FOREIGN KEY (mastkennzeichen_4) REFERENCES codelisten.mastkennzeichen_rsag(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: rsag_quertraeger_hro rsag_quertraeger_hro_masten_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.rsag_quertraeger_hro
    ADD CONSTRAINT rsag_quertraeger_hro_masten_fk FOREIGN KEY (mast) REFERENCES fachdaten.rsag_masten_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: rsag_spanndraehte_hro rsag_spanndraehte_hro_mast_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.rsag_spanndraehte_hro
    ADD CONSTRAINT rsag_spanndraehte_hro_mast_fk FOREIGN KEY (mast) REFERENCES fachdaten.rsag_masten_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: schiffsliegeplaetze_hro schiffsliegeplaetze_hro_haefen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.schiffsliegeplaetze_hro
    ADD CONSTRAINT schiffsliegeplaetze_hro_haefen_fk FOREIGN KEY (hafen) REFERENCES codelisten.haefen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: schutzzaeune_tierseuchen_hro schutzzaeune_tierseuchen_hro_tierseuchen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.schutzzaeune_tierseuchen_hro
    ADD CONSTRAINT schutzzaeune_tierseuchen_hro_tierseuchen_fk FOREIGN KEY (tierseuche) REFERENCES codelisten.tierseuchen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: schutzzaeune_tierseuchen_hro schutzzaeune_tierseuchen_hro_zustaende_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.schutzzaeune_tierseuchen_hro
    ADD CONSTRAINT schutzzaeune_tierseuchen_hro_zustaende_fk FOREIGN KEY (zustand) REFERENCES codelisten.zustaende_schutzzaeune_tierseuchen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: strassen_historie_hro strassen_historie_hro_strassen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.strassen_historie_hro
    ADD CONSTRAINT strassen_historie_hro_strassen_fk FOREIGN KEY (strasse) REFERENCES fachdaten.strassen_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: strassen_hro strassen_hro_kategorien_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.strassen_hro
    ADD CONSTRAINT strassen_hro_kategorien_fk FOREIGN KEY (kategorie) REFERENCES codelisten.kategorien_strassen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: strassen_namensanalye_hro strassen_namensanalye_hro_strassen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.strassen_namensanalye_hro
    ADD CONSTRAINT strassen_namensanalye_hro_strassen_fk FOREIGN KEY (strasse) REFERENCES fachdaten.strassen_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: toiletten_hro toiletten_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.toiletten_hro
    ADD CONSTRAINT toiletten_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_toiletten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: toiletten_hro toiletten_hro_bewirtschafter_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.toiletten_hro
    ADD CONSTRAINT toiletten_hro_bewirtschafter_fk FOREIGN KEY (bewirtschafter) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: trinkwassernotbrunnen_hro trinkwassernotbrunnen_hro_betreiber_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.trinkwassernotbrunnen_hro
    ADD CONSTRAINT trinkwassernotbrunnen_hro_betreiber_fk FOREIGN KEY (betreiber) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: trinkwassernotbrunnen_hro trinkwassernotbrunnen_hro_eigentuemer_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.trinkwassernotbrunnen_hro
    ADD CONSTRAINT trinkwassernotbrunnen_hro_eigentuemer_fk FOREIGN KEY (eigentuemer) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: uvp_vorhaben_hro uvp_vorhaben_hro_genehmigungsbehoerden_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.uvp_vorhaben_hro
    ADD CONSTRAINT uvp_vorhaben_hro_genehmigungsbehoerden_fk FOREIGN KEY (genehmigungsbehoerde) REFERENCES codelisten.genehmigungsbehoerden_uvp_vorhaben(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: uvp_vorhaben_hro uvp_vorhaben_hro_rechtsgrundlagen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.uvp_vorhaben_hro
    ADD CONSTRAINT uvp_vorhaben_hro_rechtsgrundlagen_fk FOREIGN KEY (rechtsgrundlage) REFERENCES codelisten.rechtsgrundlagen_uvp_vorhaben(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: uvp_vorhaben_hro uvp_vorhaben_hro_typen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.uvp_vorhaben_hro
    ADD CONSTRAINT uvp_vorhaben_hro_typen_fk FOREIGN KEY (typ) REFERENCES codelisten.typen_uvp_vorhaben(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: uvp_vorhaben_hro uvp_vorhaben_hro_vorgangsarten_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.uvp_vorhaben_hro
    ADD CONSTRAINT uvp_vorhaben_hro_vorgangsarten_fk FOREIGN KEY (vorgangsart) REFERENCES codelisten.vorgangsarten_uvp_vorhaben(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: uvp_vorpruefungen_hro uvp_vorpruefungen_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.uvp_vorpruefungen_hro
    ADD CONSTRAINT uvp_vorpruefungen_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_uvp_vorpruefungen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: uvp_vorpruefungen_hro uvp_vorpruefungen_hro_ergebnisse_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.uvp_vorpruefungen_hro
    ADD CONSTRAINT uvp_vorpruefungen_hro_ergebnisse_fk FOREIGN KEY (ergebnis) REFERENCES codelisten.ergebnisse_uvp_vorpruefungen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: uvp_vorpruefungen_hro uvp_vorpruefungen_hro_uvp_vorhaben_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.uvp_vorpruefungen_hro
    ADD CONSTRAINT uvp_vorpruefungen_hro_uvp_vorhaben_fk FOREIGN KEY (uvp_vorhaben) REFERENCES fachdaten.uvp_vorhaben_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: adressunsicherheiten_hro adressunsicherheiten_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.adressunsicherheiten_hro
    ADD CONSTRAINT adressunsicherheiten_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_adressunsicherheiten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: baudenkmale_hro baudenkmale_hro_status_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.baudenkmale_hro
    ADD CONSTRAINT baudenkmale_hro_status_fk FOREIGN KEY (status) REFERENCES codelisten.status_baudenkmale_denkmalbereiche(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: behinderteneinrichtungen_hro behinderteneinrichtungen_hro_traeger_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.behinderteneinrichtungen_hro
    ADD CONSTRAINT behinderteneinrichtungen_hro_traeger_fk FOREIGN KEY (traeger) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: carsharing_stationen_hro carsharing_stationen_hro_anbieter_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.carsharing_stationen_hro
    ADD CONSTRAINT carsharing_stationen_hro_anbieter_fk FOREIGN KEY (anbieter) REFERENCES codelisten.anbieter_carsharing(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: denksteine_hro denksteine_hro_materialien_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.denksteine_hro
    ADD CONSTRAINT denksteine_hro_materialien_fk FOREIGN KEY (material) REFERENCES codelisten.materialien_denksteine(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: denksteine_hro denksteine_hro_titel_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.denksteine_hro
    ADD CONSTRAINT denksteine_hro_titel_fk FOREIGN KEY (titel) REFERENCES codelisten.personentitel(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: fairtrade_hro fairtrade_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.fairtrade_hro
    ADD CONSTRAINT fairtrade_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_fairtrade(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: feuerwachen_hro feuerwachen_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.feuerwachen_hro
    ADD CONSTRAINT feuerwachen_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_feuerwachen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: hospize_hro hospize_hro_traeger_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.hospize_hro
    ADD CONSTRAINT hospize_hro_traeger_fk FOREIGN KEY (traeger) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: kehrbezirke_hro kehrbezirke_hro_bevollmaechtigte_bezirksschornsteinfeger_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.kehrbezirke_hro
    ADD CONSTRAINT kehrbezirke_hro_bevollmaechtigte_bezirksschornsteinfeger_fk FOREIGN KEY (bevollmaechtigter_bezirksschornsteinfeger) REFERENCES codelisten.bevollmaechtigte_bezirksschornsteinfeger(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: kinder_jugendbetreuung_hro kinder_jugendbetreuung_hro_traeger_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.kinder_jugendbetreuung_hro
    ADD CONSTRAINT kinder_jugendbetreuung_hro_traeger_fk FOREIGN KEY (traeger) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: kleinklaeranlagen_hro kleinklaeranlagen_hro_typen_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.kleinklaeranlagen_hro
    ADD CONSTRAINT kleinklaeranlagen_hro_typen_fk FOREIGN KEY (typ) REFERENCES codelisten.typen_kleinklaeranlagen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: ladestationen_elektrofahrzeuge_hro ladestationen_elektrofahrzeuge_hro_betreiber_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.ladestationen_elektrofahrzeuge_hro
    ADD CONSTRAINT ladestationen_elektrofahrzeuge_hro_betreiber_fk FOREIGN KEY (betreiber) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: ladestationen_elektrofahrzeuge_hro ladestationen_elektrofahrzeuge_hro_betriebsarten_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.ladestationen_elektrofahrzeuge_hro
    ADD CONSTRAINT ladestationen_elektrofahrzeuge_hro_betriebsarten_fk FOREIGN KEY (betriebsart) REFERENCES codelisten.betriebsarten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: ladestationen_elektrofahrzeuge_hro ladestationen_elektrofahrzeuge_hro_verbuende_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.ladestationen_elektrofahrzeuge_hro
    ADD CONSTRAINT ladestationen_elektrofahrzeuge_hro_verbuende_fk FOREIGN KEY (verbund) REFERENCES codelisten.verbuende_ladestationen_elektrofahrzeuge(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: meldedienst_punkthaft_hro meldedienst_punkthaft_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.meldedienst_punkthaft_hro
    ADD CONSTRAINT meldedienst_punkthaft_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_meldedienst_punkthaft(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: meldedienst_punkthaft_hro meldedienst_punkthaft_hro_gebaeudearten_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.meldedienst_punkthaft_hro
    ADD CONSTRAINT meldedienst_punkthaft_hro_gebaeudearten_fk FOREIGN KEY (gebaeudeart) REFERENCES codelisten.gebaeudearten_meldedienst_punkthaft(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: parkmoeglichkeiten_hro parkmoeglichkeiten_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.parkmoeglichkeiten_hro
    ADD CONSTRAINT parkmoeglichkeiten_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_parkmoeglichkeiten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: parkmoeglichkeiten_hro parkmoeglichkeiten_hro_betreiber_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.parkmoeglichkeiten_hro
    ADD CONSTRAINT parkmoeglichkeiten_hro_betreiber_fk FOREIGN KEY (betreiber) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: pflegeeinrichtungen_hro pflegeeinrichtungen_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.pflegeeinrichtungen_hro
    ADD CONSTRAINT pflegeeinrichtungen_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_pflegeeinrichtungen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: rettungswachen_hro rettungswachen_hro_traeger_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.rettungswachen_hro
    ADD CONSTRAINT rettungswachen_hro_traeger_fk FOREIGN KEY (traeger) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: sporthallen_hro sporthallen_hro_sportarten_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.sporthallen_hro
    ADD CONSTRAINT sporthallen_hro_sportarten_fk FOREIGN KEY (sportart) REFERENCES codelisten.sportarten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: sporthallen_hro sporthallen_hro_traeger_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.sporthallen_hro
    ADD CONSTRAINT sporthallen_hro_traeger_fk FOREIGN KEY (traeger) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: stadtteil_begegnungszentren_hro stadtteil_begegnungszentren_hro_traeger_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.stadtteil_begegnungszentren_hro
    ADD CONSTRAINT stadtteil_begegnungszentren_hro_traeger_fk FOREIGN KEY (traeger) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: standortqualitaeten_geschaeftslagen_sanierungsgebiet_hro standortqualitaeten_geschaeftslagen_sanierungsgebiet_hro_quarti; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.standortqualitaeten_geschaeftslagen_sanierungsgebiet_hro
    ADD CONSTRAINT standortqualitaeten_geschaeftslagen_sanierungsgebiet_hro_quarti FOREIGN KEY (quartier) REFERENCES codelisten.quartiere(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: standortqualitaeten_wohnlagen_sanierungsgebiet_hro standortqualitaeten_wohnlagen_sanierungsgebiet_hro_quartiere_fk; Type: FK CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.standortqualitaeten_wohnlagen_sanierungsgebiet_hro
    ADD CONSTRAINT standortqualitaeten_wohnlagen_sanierungsgebiet_hro_quartiere_fk FOREIGN KEY (quartier) REFERENCES codelisten.quartiere(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: baustellen_fotodokumentation_baustellen_hro baustellen_fotodokumentation_baustellen_hro_auftraggeber_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.baustellen_fotodokumentation_baustellen_hro
    ADD CONSTRAINT baustellen_fotodokumentation_baustellen_hro_auftraggeber_fk FOREIGN KEY (auftraggeber) REFERENCES codelisten.auftraggeber_baustellen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: baustellen_geplant baustellen_geplant_auftraggeber_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.baustellen_geplant
    ADD CONSTRAINT baustellen_geplant_auftraggeber_fk FOREIGN KEY (auftraggeber) REFERENCES codelisten.auftraggeber_baustellen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: baustellen_geplant baustellen_geplant_status_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.baustellen_geplant
    ADD CONSTRAINT baustellen_geplant_status_fk FOREIGN KEY (status) REFERENCES codelisten.status_baustellen_geplant(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: geh_und_radwegereinigung_hro geh_und_radwegereinigung_hro_breiten_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.geh_und_radwegereinigung_hro
    ADD CONSTRAINT geh_und_radwegereinigung_hro_breiten_fk FOREIGN KEY (breite) REFERENCES codelisten.wegebreiten_strassenreinigungssatzung_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: geh_und_radwegereinigung_hro geh_und_radwegereinigung_hro_inoffizielle_strassen_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.geh_und_radwegereinigung_hro
    ADD CONSTRAINT geh_und_radwegereinigung_hro_inoffizielle_strassen_fk FOREIGN KEY (inoffizielle_strasse) REFERENCES basisdaten.inoffizielle_strassenliste_datenwerft_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: geh_und_radwegereinigung_hro geh_und_radwegereinigung_hro_raeumbreiten_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.geh_und_radwegereinigung_hro
    ADD CONSTRAINT geh_und_radwegereinigung_hro_raeumbreiten_fk FOREIGN KEY (raeumbreite) REFERENCES codelisten.raeumbreiten_strassenreinigungssatzung_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: geh_und_radwegereinigung_hro geh_und_radwegereinigung_hro_reinigungsklassen_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.geh_und_radwegereinigung_hro
    ADD CONSTRAINT geh_und_radwegereinigung_hro_reinigungsklassen_fk FOREIGN KEY (reinigungsklasse) REFERENCES codelisten.wegereinigungsklassen_strassenreinigungssatzung_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: geh_und_radwegereinigung_hro geh_und_radwegereinigung_hro_reinigungsrhythmen_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.geh_und_radwegereinigung_hro
    ADD CONSTRAINT geh_und_radwegereinigung_hro_reinigungsrhythmen_fk FOREIGN KEY (reinigungsrhythmus) REFERENCES codelisten.wegereinigungsrhythmen_strassenreinigungssatzung_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: geh_und_radwegereinigung_hro geh_und_radwegereinigung_hro_wegearten_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.geh_und_radwegereinigung_hro
    ADD CONSTRAINT geh_und_radwegereinigung_hro_wegearten_fk FOREIGN KEY (wegeart) REFERENCES codelisten.arten_wege(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: geh_und_radwegereinigung_hro geh_und_radwegereinigung_hro_wegetypen_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.geh_und_radwegereinigung_hro
    ADD CONSTRAINT geh_und_radwegereinigung_hro_wegetypen_fk FOREIGN KEY (wegetyp) REFERENCES codelisten.wegetypen_strassenreinigungssatzung_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: hausnummern_hro hausnummern_hro_gebaeude_bauweisen_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.hausnummern_hro
    ADD CONSTRAINT hausnummern_hro_gebaeude_bauweisen_fk FOREIGN KEY (gebaeude_bauweise) REFERENCES codelisten.gebaeudebauweisen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: hausnummern_hro hausnummern_hro_gebaeude_funktionen_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.hausnummern_hro
    ADD CONSTRAINT hausnummern_hro_gebaeude_funktionen_fk FOREIGN KEY (gebaeude_funktion) REFERENCES codelisten.gebaeudefunktionen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: ingenieurbauwerke_hro ingenieurbauwerke_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.ingenieurbauwerke_hro
    ADD CONSTRAINT ingenieurbauwerke_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_ingenieurbauwerke(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: ingenieurbauwerke_hro ingenieurbauwerke_hro_ausfuehrungen_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.ingenieurbauwerke_hro
    ADD CONSTRAINT ingenieurbauwerke_hro_ausfuehrungen_fk FOREIGN KEY (ausfuehrung) REFERENCES codelisten.ausfuehrungen_ingenieurbauwerke(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: strassenreinigung_hro strassenreinigung_hro_fahrbahnwinterdienst_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.strassenreinigung_hro
    ADD CONSTRAINT strassenreinigung_hro_fahrbahnwinterdienst_fk FOREIGN KEY (fahrbahnwinterdienst) REFERENCES codelisten.fahrbahnwinterdienst_strassenreinigungssatzung_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: strassenreinigung_hro strassenreinigung_hro_inoffizielle_strassen_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.strassenreinigung_hro
    ADD CONSTRAINT strassenreinigung_hro_inoffizielle_strassen_fk FOREIGN KEY (inoffizielle_strasse) REFERENCES basisdaten.inoffizielle_strassenliste_datenwerft_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: strassenreinigung_hro strassenreinigung_hro_reinigungsklassen_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.strassenreinigung_hro
    ADD CONSTRAINT strassenreinigung_hro_reinigungsklassen_fk FOREIGN KEY (reinigungsklasse) REFERENCES codelisten.reinigungsklassen_strassenreinigungssatzung_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: strassenreinigung_hro strassenreinigung_hro_reinigungsrhythmen_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.strassenreinigung_hro
    ADD CONSTRAINT strassenreinigung_hro_reinigungsrhythmen_fk FOREIGN KEY (reinigungsrhythmus) REFERENCES codelisten.reinigungsrhythmen_strassenreinigungssatzung_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

