--
-- PostgreSQL database dump
--

-- Dumped from database version 15.13
-- Dumped by pg_dump version 16.9

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
-- Name: generate_pointcloud_union(uuid); Type: FUNCTION; Schema: fachdaten; Owner: -
--

CREATE FUNCTION fachdaten.generate_pointcloud_union(projekt_uuid uuid) RETURNS public.geometry
    LANGUAGE sql STABLE
    AS $_$
    SELECT ST_Union(geometrie)
    FROM fachdaten.punktwolken
    WHERE punktwolken_projekte = $1;
$_$;


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
-- Name: update_projekt_geometry(); Type: FUNCTION; Schema: fachdaten; Owner: -
--

CREATE FUNCTION fachdaten.update_projekt_geometry() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Bei INSERT oder UPDATE
    IF TG_OP IN ('INSERT', 'UPDATE') THEN
        UPDATE fachdaten.punktwolken_projekte
        SET geometrie = fachdaten.generate_pointcloud_union(NEW.punktwolken_projekte)
        WHERE uuid = NEW.punktwolken_projekte;
    -- Bei DELETE
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE fachdaten.punktwolken_projekte
        SET geometrie = fachdaten.generate_pointcloud_union(OLD.punktwolken_projekte)
        WHERE uuid = OLD.punktwolken_projekte;
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
    hausnummer character varying(5),
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
-- Name: antragsteller_jagdkataster_skizzenebenen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.antragsteller_jagdkataster_skizzenebenen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL
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
-- Name: arten_brunnen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_brunnen (
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
-- Name: arten_fallwildsuchen_kontrollen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_fallwildsuchen_kontrollen (
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
-- Name: arten_naturdenkmale; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_naturdenkmale (
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
-- Name: arten_reisebusparkplaetze_terminals; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_reisebusparkplaetze_terminals (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art character varying(255) NOT NULL
);


--
-- Name: arten_sportanlagen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.arten_sportanlagen (
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
-- Name: auftraggeber_baugrunduntersuchungen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.auftraggeber_baugrunduntersuchungen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    auftraggeber character varying(255) NOT NULL
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
-- Name: ausfuehrungen_fahrradabstellanlagen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.ausfuehrungen_fahrradabstellanlagen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ausfuehrung character varying(255) NOT NULL
);


--
-- Name: ausfuehrungen_fahrradabstellanlagen_stellplaetze; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.ausfuehrungen_fahrradabstellanlagen_stellplaetze (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ausfuehrung character varying(255) NOT NULL
);


--
-- Name: ausfuehrungen_fahrradboxen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.ausfuehrungen_fahrradboxen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ausfuehrung character varying(255) NOT NULL
);


--
-- Name: ausfuehrungen_fahrradreparatursets; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.ausfuehrungen_fahrradreparatursets (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ausfuehrung character varying(255) NOT NULL
);


--
-- Name: ausfuehrungen_fahrradstaender; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.ausfuehrungen_fahrradstaender (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    ausfuehrung character varying(255) NOT NULL
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
-- Name: beleuchtungsarten; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.beleuchtungsarten (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL
);


--
-- Name: besonderheiten_freizeitsport; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.besonderheiten_freizeitsport (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    besonderheit character varying(255) NOT NULL
);


--
-- Name: besonderheiten_spielplaetze; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.besonderheiten_spielplaetze (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    besonderheit character varying(255) NOT NULL
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
-- Name: bodenarten_freizeitsport; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.bodenarten_freizeitsport (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bodenart character varying(255) NOT NULL
);


--
-- Name: bodenarten_spielplaetze; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.bodenarten_spielplaetze (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bodenart character varying(255) NOT NULL
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
-- Name: freizeitsportarten; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.freizeitsportarten (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL
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
-- Name: hersteller_fahrradabstellanlagen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.hersteller_fahrradabstellanlagen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL
);


--
-- Name: hersteller_versenkpoller; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.hersteller_versenkpoller (
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
-- Name: labore_baugrunduntersuchungen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.labore_baugrunduntersuchungen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    anschrift character varying(255),
    telefon character varying(255),
    email character varying(255)
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
-- Name: leerungszeiten; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.leerungszeiten (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    leerungshaeufigkeit_pro_jahr smallint
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
-- Name: spielgeraete; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.spielgeraete (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL
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
-- Name: status_jagdkataster_skizzenebenen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.status_jagdkataster_skizzenebenen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    status character varying(255) NOT NULL
);


--
-- Name: themen_jagdkataster_skizzenebenen; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.themen_jagdkataster_skizzenebenen (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL
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
    typ character varying(255) NOT NULL,
    model_3d character varying(255)
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
-- Name: typen_naturdenkmale; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.typen_naturdenkmale (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    art uuid NOT NULL,
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
-- Name: typen_versenkpoller; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.typen_versenkpoller (
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
-- Name: wartungsfirmen_versenkpoller; Type: TABLE; Schema: codelisten; Owner: -
--

CREATE TABLE codelisten.wartungsfirmen_versenkpoller (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    bezeichnung character varying(255) NOT NULL
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
-- Name: _naturdenkmale_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten._naturdenkmale_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    typ uuid NOT NULL,
    nummer smallint NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    rechtsvorschrift_festsetzung character varying(255),
    datum_rechtsvorschrift_festsetzung date,
    pdf character varying(255) NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL
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
    bemerkungen character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL,
    leerungszeiten_sommer uuid,
    leerungszeiten_winter uuid
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
-- Name: anerkennungsgebuehren_herrschend_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.anerkennungsgebuehren_herrschend_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    grundbucheintrag character varying(255) NOT NULL,
    aktenzeichen_anerkennungsgebuehren character(12),
    aktenzeichen_kommunalvermoegen character(10),
    vermoegenszuordnung_hro boolean,
    bemerkungen character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL
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
-- Name: arrondierungsflaechen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.arrondierungsflaechen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    registriernummer character varying(6) NOT NULL,
    jahr smallint NOT NULL,
    geometrie public.geometry(Polygon,25833) NOT NULL
);


--
-- Name: baugrunduntersuchungen_baugrundbohrungen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.baugrunduntersuchungen_baugrundbohrungen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    baugrunduntersuchung uuid NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL,
    nummer character varying(255) NOT NULL
);


--
-- Name: baugrunduntersuchungen_dokumente_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.baugrunduntersuchungen_dokumente_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    baugrunduntersuchung uuid NOT NULL,
    dateiname_original character varying(255) NOT NULL,
    pdf character varying(255) NOT NULL
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
    pdf character varying(255) NOT NULL,
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
-- Name: brunnen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.brunnen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    d3 character varying(16),
    aktenzeichen character varying(255),
    art uuid NOT NULL,
    datum_bescheid date,
    datum_befristung date,
    lagebeschreibung character varying(255) NOT NULL,
    realisierung_erfolgt boolean,
    in_betrieb boolean,
    endteufe numeric(3,1)[],
    entnahmemenge integer,
    geometrie public.geometry(Point,25833) NOT NULL
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
-- Name: feuerwehrzufahrten_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.feuerwehrzufahrten_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    registriernummer smallint,
    bauvorhaben_aktenzeichen_bauamt character varying(255)[],
    bauvorhaben_adressen character varying(255)[],
    erreichbare_objekte character varying(255)[],
    flaechen_feuerwehrzufahrt boolean,
    feuerwehraufstellflaechen_hubrettungsfahrzeug boolean,
    feuerwehrbewegungsflaechen boolean,
    amtlichmachung date,
    bemerkungen character varying(255)
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
-- Name: freizeitsport_fotos_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.freizeitsport_fotos_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    freizeitsport uuid NOT NULL,
    dateiname_original character varying(255) NOT NULL,
    foto character varying(255) NOT NULL,
    oeffentlich_sichtbar boolean NOT NULL,
    aufnahmedatum date,
    bemerkungen character varying(255)
);


--
-- Name: freizeitsport_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.freizeitsport_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    gruenpflegeobjekt uuid,
    staedtisch boolean NOT NULL,
    bezeichnung character varying(255),
    beschreibung character varying(255),
    sportarten character varying(255)[] NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL,
    freizeitsport character varying(255),
    bodenarten character varying(255)[],
    besonderheiten character varying(255)[]
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
-- Name: gemeinbedarfsflaechen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.gemeinbedarfsflaechen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    registriernummer character varying(6) NOT NULL,
    jahr smallint NOT NULL,
    geometrie public.geometry(Polygon,25833) NOT NULL
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
-- Name: gruenpflegeobjekte_datenwerft; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.gruenpflegeobjekte_datenwerft (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    id character(17) NOT NULL,
    art character varying(255) NOT NULL,
    gruenpflegebezirk character varying(255) NOT NULL,
    nummer character varying(7) NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    geometrie public.geometry(MultiPolygon,25833) NOT NULL,
    gruenpflegeobjekt character varying(255) NOT NULL
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
-- Name: jagdkataster_skizzenebenen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.jagdkataster_skizzenebenen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    thema uuid NOT NULL,
    status uuid NOT NULL,
    bemerkungen character varying(255),
    geometrie public.geometry(MultiLineString,25833) NOT NULL,
    antragsteller uuid NOT NULL
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
    erfasser character varying(255) NOT NULL,
    bemerkungen character varying(255),
    erfassungsdatum date NOT NULL,
    geometrie public.geometry(Polygon,25833) NOT NULL,
    bearbeitungsbeginn date,
    bearbeiter character varying(255)
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
    geometrie public.geometry(Point,25833) NOT NULL,
    foto character varying(255)
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
-- Name: punktwolken; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.punktwolken (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktiv boolean DEFAULT true NOT NULL,
    erstellt date DEFAULT now() NOT NULL,
    aktualisiert date DEFAULT now() NOT NULL,
    dateiname character varying(255) NOT NULL,
    punktwolke character varying(255) NOT NULL,
    aufnahme timestamp(0) with time zone,
    geometrie public.geometry(Polygon,25833),
    punktwolken_projekte uuid NOT NULL,
    vc_update timestamp(0) with time zone DEFAULT CURRENT_TIMESTAMP(0),
    vcp_object_key character varying(255),
    file_size bigint
);


--
-- Name: punktwolken_projekte; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.punktwolken_projekte (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktiv boolean DEFAULT true NOT NULL,
    erstellt date DEFAULT now() NOT NULL,
    aktualisiert date DEFAULT now(),
    bezeichnung character varying(255) NOT NULL,
    beschreibung character varying(255),
    projekt_update timestamp(0) with time zone DEFAULT now(),
    vcp_task_id character varying(255),
    vcp_dataset_bucket_id uuid,
    vcp_datasource_id character varying(255),
    geometrie public.geometry(MultiPolygon,25833)
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
-- Name: spielplaetze_fotos_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.spielplaetze_fotos_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    spielplatz uuid NOT NULL,
    dateiname_original character varying(255) NOT NULL,
    foto character varying(255) NOT NULL,
    oeffentlich_sichtbar boolean NOT NULL,
    aufnahmedatum date,
    bemerkungen character varying(255)
);


--
-- Name: spielplaetze_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.spielplaetze_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    gruenpflegeobjekt uuid,
    staedtisch boolean NOT NULL,
    bezeichnung character varying(255),
    beschreibung character varying(255),
    geometrie public.geometry(Point,25833) NOT NULL,
    spielplatz character varying(255),
    spielgeraete character varying(255)[],
    bodenarten character varying(255)[],
    besonderheiten character varying(255)[]
);


--
-- Name: sportanlagen_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.sportanlagen_hro (
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
-- Name: versenkpoller_hro; Type: TABLE; Schema: fachdaten; Owner: -
--

CREATE TABLE fachdaten.versenkpoller_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    nummer smallint,
    kurzbezeichnung character(3),
    lagebeschreibung character varying(255),
    statusinformation character varying(255),
    zusatzbeschilderung character varying(255),
    hersteller uuid,
    typ uuid,
    baujahr smallint,
    wartungsfirma uuid,
    foto character varying(255),
    geometrie public.geometry(Point,25833)
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
-- Name: feuerwehrzufahrten_schilder_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.feuerwehrzufahrten_schilder_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    adresse uuid,
    feuerwehrzufahrt uuid NOT NULL,
    typ uuid,
    hinweise_aufstellort character varying(255) NOT NULL,
    bemerkungen character varying(255),
    foto character varying(255),
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
-- Name: mobilfunkantennen_hro; Type: TABLE; Schema: fachdaten_adressbezug; Owner: -
--

CREATE TABLE fachdaten_adressbezug.mobilfunkantennen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    id_zielsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    deaktiviert date,
    adresse uuid,
    stob character varying(8) NOT NULL,
    erteilungsdatum date NOT NULL,
    techniken character varying(255)[],
    betreiber character varying(255)[],
    montagehoehe character varying(255),
    anzahl_gsm smallint,
    anzahl_umts smallint,
    anzahl_lte smallint,
    anzahl_sonstige smallint,
    geometrie public.geometry(Point,25833)
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
    geometrie public.geometry(Point,25833) NOT NULL,
    parkandride boolean
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
-- Name: abstellflaechen_e_tretroller_hro; Type: TABLE; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TABLE fachdaten_strassenbezug.abstellflaechen_e_tretroller_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    strasse uuid,
    id character(8) NOT NULL,
    lagebeschreibung character varying(255),
    erstmarkierung smallint NOT NULL,
    breite numeric(3,2) NOT NULL,
    laenge numeric(4,2) NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: baugrunduntersuchungen_hro; Type: TABLE; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TABLE fachdaten_strassenbezug.baugrunduntersuchungen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    strasse uuid,
    labor uuid NOT NULL,
    bezeichnung character varying(255) NOT NULL,
    datum date NOT NULL,
    auftraggeber uuid NOT NULL,
    historisch boolean NOT NULL
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
-- Name: fahrradabstellanlagen_hro; Type: TABLE; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TABLE fachdaten_strassenbezug.fahrradabstellanlagen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    strasse uuid,
    id character(8) NOT NULL,
    ausfuehrung uuid NOT NULL,
    lagebeschreibung character varying(255),
    ausfuehrung_stellplaetze uuid,
    anzahl_stellplaetze smallint,
    eigentuemer uuid NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL,
    baujahr smallint,
    hersteller uuid,
    foto character varying(255)
);


--
-- Name: fahrradboxen_hro; Type: TABLE; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TABLE fachdaten_strassenbezug.fahrradboxen_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    strasse uuid,
    id character(8) NOT NULL,
    ausfuehrung uuid NOT NULL,
    lagebeschreibung character varying(255),
    anzahl_stellplaetze smallint,
    eigentuemer uuid NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL,
    foto character varying(255)
);


--
-- Name: fahrradreparatursets_hro; Type: TABLE; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TABLE fachdaten_strassenbezug.fahrradreparatursets_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    strasse uuid,
    id character(8) NOT NULL,
    ausfuehrung uuid NOT NULL,
    lagebeschreibung character varying(255),
    baujahr smallint,
    eigentuemer uuid NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL
);


--
-- Name: fahrradstaender_hro; Type: TABLE; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TABLE fachdaten_strassenbezug.fahrradstaender_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    strasse uuid,
    id character(8) NOT NULL,
    ausfuehrung uuid NOT NULL,
    lagebeschreibung character varying(255),
    anzahl_stellplaetze smallint,
    anzahl_fahrradstaender smallint,
    eigentuemer uuid NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL,
    foto character varying(255)
);


--
-- Name: fussgaengerueberwege_hro; Type: TABLE; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TABLE fachdaten_strassenbezug.fussgaengerueberwege_hro (
    uuid uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    aktualisiert date DEFAULT (now())::date NOT NULL,
    erstellt date DEFAULT (now())::date NOT NULL,
    id_fachsystem character varying(255),
    aktiv boolean DEFAULT true NOT NULL,
    id_zielsystem character varying(255),
    deaktiviert date,
    strasse uuid,
    id character(8) NOT NULL,
    breite numeric(3,2) NOT NULL,
    laenge numeric(4,2) NOT NULL,
    barrierefrei boolean NOT NULL,
    beleuchtungsart uuid NOT NULL,
    geometrie public.geometry(Point,25833) NOT NULL,
    lagebeschreibung character varying(255),
    baujahr smallint,
    kreisverkehr boolean
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
-- Name: antragsteller_jagdkataster_skizzenebenen antragsteller_jagdkataster_skizzenebenen_bezeichnung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.antragsteller_jagdkataster_skizzenebenen
    ADD CONSTRAINT antragsteller_jagdkataster_skizzenebenen_bezeichnung_unique UNIQUE (bezeichnung);


--
-- Name: antragsteller_jagdkataster_skizzenebenen antragsteller_jagdkataster_skizzenebenen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.antragsteller_jagdkataster_skizzenebenen
    ADD CONSTRAINT antragsteller_jagdkataster_skizzenebenen_pk PRIMARY KEY (uuid);


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
-- Name: arten_brunnen arten_brunnen_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_brunnen
    ADD CONSTRAINT arten_brunnen_art_unique UNIQUE (art);


--
-- Name: arten_brunnen arten_brunnen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_brunnen
    ADD CONSTRAINT arten_brunnen_pk PRIMARY KEY (uuid);


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
-- Name: arten_naturdenkmale arten_naturdenkmale_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_naturdenkmale
    ADD CONSTRAINT arten_naturdenkmale_art_unique UNIQUE (art);


--
-- Name: arten_naturdenkmale arten_naturdenkmale_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_naturdenkmale
    ADD CONSTRAINT arten_naturdenkmale_pk PRIMARY KEY (uuid);


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
-- Name: arten_sportanlagen arten_sportanlagen_art_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_sportanlagen
    ADD CONSTRAINT arten_sportanlagen_art_unique UNIQUE (art);


--
-- Name: arten_sportanlagen arten_sportanlagen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.arten_sportanlagen
    ADD CONSTRAINT arten_sportanlagen_pk PRIMARY KEY (uuid);


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
-- Name: auftraggeber_baugrunduntersuchungen auftraggeber_baugrunduntersuchungen_auftraggeber_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.auftraggeber_baugrunduntersuchungen
    ADD CONSTRAINT auftraggeber_baugrunduntersuchungen_auftraggeber_unique UNIQUE (auftraggeber);


--
-- Name: auftraggeber_baugrunduntersuchungen auftraggeber_baugrunduntersuchungen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.auftraggeber_baugrunduntersuchungen
    ADD CONSTRAINT auftraggeber_baugrunduntersuchungen_pk PRIMARY KEY (uuid);


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
-- Name: ausfuehrungen_fahrradabstellanlagen ausfuehrungen_fahrradabstellanlagen_ausfuehrung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ausfuehrungen_fahrradabstellanlagen
    ADD CONSTRAINT ausfuehrungen_fahrradabstellanlagen_ausfuehrung_unique UNIQUE (ausfuehrung);


--
-- Name: ausfuehrungen_fahrradabstellanlagen ausfuehrungen_fahrradabstellanlagen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ausfuehrungen_fahrradabstellanlagen
    ADD CONSTRAINT ausfuehrungen_fahrradabstellanlagen_pk PRIMARY KEY (uuid);


--
-- Name: ausfuehrungen_fahrradabstellanlagen_stellplaetze ausfuehrungen_fahrradabstellanlagen_stellplaetze_ausfuehrung_un; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ausfuehrungen_fahrradabstellanlagen_stellplaetze
    ADD CONSTRAINT ausfuehrungen_fahrradabstellanlagen_stellplaetze_ausfuehrung_un UNIQUE (ausfuehrung);


--
-- Name: ausfuehrungen_fahrradabstellanlagen_stellplaetze ausfuehrungen_fahrradabstellanlagen_stellplaetze_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ausfuehrungen_fahrradabstellanlagen_stellplaetze
    ADD CONSTRAINT ausfuehrungen_fahrradabstellanlagen_stellplaetze_pk PRIMARY KEY (uuid);


--
-- Name: ausfuehrungen_fahrradboxen ausfuehrungen_fahrradboxen_ausfuehrung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ausfuehrungen_fahrradboxen
    ADD CONSTRAINT ausfuehrungen_fahrradboxen_ausfuehrung_unique UNIQUE (ausfuehrung);


--
-- Name: ausfuehrungen_fahrradboxen ausfuehrungen_fahrradboxen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ausfuehrungen_fahrradboxen
    ADD CONSTRAINT ausfuehrungen_fahrradboxen_pk PRIMARY KEY (uuid);


--
-- Name: ausfuehrungen_fahrradreparatursets ausfuehrungen_fahrradreparatursets_ausfuehrung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ausfuehrungen_fahrradreparatursets
    ADD CONSTRAINT ausfuehrungen_fahrradreparatursets_ausfuehrung_unique UNIQUE (ausfuehrung);


--
-- Name: ausfuehrungen_fahrradreparatursets ausfuehrungen_fahrradreparatursets_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ausfuehrungen_fahrradreparatursets
    ADD CONSTRAINT ausfuehrungen_fahrradreparatursets_pk PRIMARY KEY (uuid);


--
-- Name: ausfuehrungen_fahrradstaender ausfuehrungen_fahrradstaender_ausfuehrung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ausfuehrungen_fahrradstaender
    ADD CONSTRAINT ausfuehrungen_fahrradstaender_ausfuehrung_unique UNIQUE (ausfuehrung);


--
-- Name: ausfuehrungen_fahrradstaender ausfuehrungen_fahrradstaender_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.ausfuehrungen_fahrradstaender
    ADD CONSTRAINT ausfuehrungen_fahrradstaender_pk PRIMARY KEY (uuid);


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
-- Name: beleuchtungsarten beleuchtungsarten_bezeichnung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.beleuchtungsarten
    ADD CONSTRAINT beleuchtungsarten_bezeichnung_unique UNIQUE (bezeichnung);


--
-- Name: beleuchtungsarten beleuchtungsarten_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.beleuchtungsarten
    ADD CONSTRAINT beleuchtungsarten_pk PRIMARY KEY (uuid);


--
-- Name: besonderheiten_freizeitsport besonderheiten_freizeitsport_besonderheit_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.besonderheiten_freizeitsport
    ADD CONSTRAINT besonderheiten_freizeitsport_besonderheit_unique UNIQUE (besonderheit);


--
-- Name: besonderheiten_freizeitsport besonderheiten_freizeitsport_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.besonderheiten_freizeitsport
    ADD CONSTRAINT besonderheiten_freizeitsport_pk PRIMARY KEY (uuid);


--
-- Name: besonderheiten_spielplaetze besonderheiten_spielplaetze_besonderheit_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.besonderheiten_spielplaetze
    ADD CONSTRAINT besonderheiten_spielplaetze_besonderheit_unique UNIQUE (besonderheit);


--
-- Name: besonderheiten_spielplaetze besonderheiten_spielplaetze_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.besonderheiten_spielplaetze
    ADD CONSTRAINT besonderheiten_spielplaetze_pk PRIMARY KEY (uuid);


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
-- Name: bodenarten_freizeitsport bodenarten_freizeitsport_bodenart_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.bodenarten_freizeitsport
    ADD CONSTRAINT bodenarten_freizeitsport_bodenart_unique UNIQUE (bodenart);


--
-- Name: bodenarten_freizeitsport bodenarten_freizeitsport_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.bodenarten_freizeitsport
    ADD CONSTRAINT bodenarten_freizeitsport_pk PRIMARY KEY (uuid);


--
-- Name: bodenarten_spielplaetze bodenarten_spielplaetze_bodenart_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.bodenarten_spielplaetze
    ADD CONSTRAINT bodenarten_spielplaetze_bodenart_unique UNIQUE (bodenart);


--
-- Name: bodenarten_spielplaetze bodenarten_spielplaetze_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.bodenarten_spielplaetze
    ADD CONSTRAINT bodenarten_spielplaetze_pk PRIMARY KEY (uuid);


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
-- Name: freizeitsportarten freizeitsportarten_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.freizeitsportarten
    ADD CONSTRAINT freizeitsportarten_pk PRIMARY KEY (uuid);


--
-- Name: freizeitsportarten freizeitsportarten_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.freizeitsportarten
    ADD CONSTRAINT freizeitsportarten_unique UNIQUE (bezeichnung);


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
-- Name: hersteller_fahrradabstellanlagen hersteller_fahrradabstellanlagen_bezeichnung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.hersteller_fahrradabstellanlagen
    ADD CONSTRAINT hersteller_fahrradabstellanlagen_bezeichnung_unique UNIQUE (bezeichnung);


--
-- Name: hersteller_fahrradabstellanlagen hersteller_fahrradabstellanlagen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.hersteller_fahrradabstellanlagen
    ADD CONSTRAINT hersteller_fahrradabstellanlagen_pk PRIMARY KEY (uuid);


--
-- Name: hersteller_versenkpoller hersteller_versenkpoller_bezeichnung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.hersteller_versenkpoller
    ADD CONSTRAINT hersteller_versenkpoller_bezeichnung_unique UNIQUE (bezeichnung);


--
-- Name: hersteller_versenkpoller hersteller_versenkpoller_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.hersteller_versenkpoller
    ADD CONSTRAINT hersteller_versenkpoller_pk PRIMARY KEY (uuid);


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
-- Name: labore_baugrunduntersuchungen labore_baugrunduntersuchungen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.labore_baugrunduntersuchungen
    ADD CONSTRAINT labore_baugrunduntersuchungen_pk PRIMARY KEY (uuid);


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
-- Name: leerungszeiten leerungszeiten_bezeichnung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.leerungszeiten
    ADD CONSTRAINT leerungszeiten_bezeichnung_unique UNIQUE (bezeichnung);


--
-- Name: leerungszeiten leerungszeiten_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.leerungszeiten
    ADD CONSTRAINT leerungszeiten_pk PRIMARY KEY (uuid);


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
-- Name: spielgeraete spielgeraete_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.spielgeraete
    ADD CONSTRAINT spielgeraete_pk PRIMARY KEY (uuid);


--
-- Name: spielgeraete spielgeraete_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.spielgeraete
    ADD CONSTRAINT spielgeraete_unique UNIQUE (bezeichnung);


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
-- Name: status_jagdkataster_skizzenebenen status_jagdkataster_skizzenebenen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.status_jagdkataster_skizzenebenen
    ADD CONSTRAINT status_jagdkataster_skizzenebenen_pk PRIMARY KEY (uuid);


--
-- Name: status_jagdkataster_skizzenebenen status_jagdkataster_skizzenebenen_status_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.status_jagdkataster_skizzenebenen
    ADD CONSTRAINT status_jagdkataster_skizzenebenen_status_unique UNIQUE (status);


--
-- Name: themen_jagdkataster_skizzenebenen themen_jagdkataster_skizzenebenen_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.themen_jagdkataster_skizzenebenen
    ADD CONSTRAINT themen_jagdkataster_skizzenebenen_pk PRIMARY KEY (uuid);


--
-- Name: themen_jagdkataster_skizzenebenen themen_jagdkataster_skizzenebenen_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.themen_jagdkataster_skizzenebenen
    ADD CONSTRAINT themen_jagdkataster_skizzenebenen_unique UNIQUE (bezeichnung);


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
-- Name: typen_naturdenkmale typen_naturdenkmale_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_naturdenkmale
    ADD CONSTRAINT typen_naturdenkmale_pk PRIMARY KEY (uuid);


--
-- Name: typen_naturdenkmale typen_naturdenkmale_typ_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_naturdenkmale
    ADD CONSTRAINT typen_naturdenkmale_typ_unique UNIQUE (typ);


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
-- Name: typen_versenkpoller typen_versenkpoller_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_versenkpoller
    ADD CONSTRAINT typen_versenkpoller_pk PRIMARY KEY (uuid);


--
-- Name: typen_versenkpoller typen_versenkpoller_typ_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_versenkpoller
    ADD CONSTRAINT typen_versenkpoller_typ_unique UNIQUE (typ);


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
-- Name: wartungsfirmen_versenkpoller wartungsfirmen_versenkpoller_bezeichnung_unique; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.wartungsfirmen_versenkpoller
    ADD CONSTRAINT wartungsfirmen_versenkpoller_bezeichnung_unique UNIQUE (bezeichnung);


--
-- Name: wartungsfirmen_versenkpoller wartungsfirmen_versenkpoller_pk; Type: CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.wartungsfirmen_versenkpoller
    ADD CONSTRAINT wartungsfirmen_versenkpoller_pk PRIMARY KEY (uuid);


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
-- Name: _naturdenkmale_hro _naturdenkmale_hro_nummer_unique; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten._naturdenkmale_hro
    ADD CONSTRAINT _naturdenkmale_hro_nummer_unique UNIQUE (nummer);


--
-- Name: _naturdenkmale_hro _naturdenkmale_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten._naturdenkmale_hro
    ADD CONSTRAINT _naturdenkmale_hro_pk PRIMARY KEY (uuid);


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
-- Name: anerkennungsgebuehren_herrschend_hro anerkennungsgebuehren_herrschend_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.anerkennungsgebuehren_herrschend_hro
    ADD CONSTRAINT anerkennungsgebuehren_herrschend_hro_pk PRIMARY KEY (uuid);


--
-- Name: angelverbotsbereiche_hro angelverbotsbereiche_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.angelverbotsbereiche_hro
    ADD CONSTRAINT angelverbotsbereiche_hro_pk PRIMARY KEY (uuid);


--
-- Name: arrondierungsflaechen_hro arrondierungsflaechen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.arrondierungsflaechen_hro
    ADD CONSTRAINT arrondierungsflaechen_hro_pk PRIMARY KEY (uuid);


--
-- Name: baugrunduntersuchungen_baugrundbohrungen_hro baugrunduntersuchungen_baugrundbohrungen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.baugrunduntersuchungen_baugrundbohrungen_hro
    ADD CONSTRAINT baugrunduntersuchungen_baugrundbohrungen_hro_pk PRIMARY KEY (uuid);


--
-- Name: baugrunduntersuchungen_dokumente_hro baugrunduntersuchungen_dokumente_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.baugrunduntersuchungen_dokumente_hro
    ADD CONSTRAINT baugrunduntersuchungen_dokumente_hro_pk PRIMARY KEY (uuid);


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
-- Name: brunnen_hro brunnen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.brunnen_hro
    ADD CONSTRAINT brunnen_hro_pk PRIMARY KEY (uuid);


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
-- Name: feuerwehrzufahrten_hro feuerwehrzufahrten_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.feuerwehrzufahrten_hro
    ADD CONSTRAINT feuerwehrzufahrten_hro_pk PRIMARY KEY (uuid);


--
-- Name: fliessgewaesser_hro fliessgewaesser_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.fliessgewaesser_hro
    ADD CONSTRAINT fliessgewaesser_hro_pk PRIMARY KEY (uuid);


--
-- Name: freizeitsport_fotos_hro freizeitsport_fotos_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.freizeitsport_fotos_hro
    ADD CONSTRAINT freizeitsport_fotos_hro_pk PRIMARY KEY (uuid);


--
-- Name: freizeitsport_hro freizeitsport_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.freizeitsport_hro
    ADD CONSTRAINT freizeitsport_hro_pk PRIMARY KEY (uuid);


--
-- Name: geh_und_radwegereinigung_flaechen_hro geh_und_radwegereinigung_flaechen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.geh_und_radwegereinigung_flaechen_hro
    ADD CONSTRAINT geh_und_radwegereinigung_flaechen_hro_pk PRIMARY KEY (uuid);


--
-- Name: gemeinbedarfsflaechen_hro gemeinbedarfsflaechen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.gemeinbedarfsflaechen_hro
    ADD CONSTRAINT gemeinbedarfsflaechen_hro_pk PRIMARY KEY (uuid);


--
-- Name: geraetespielanlagen_hro geraetespielanlagen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.geraetespielanlagen_hro
    ADD CONSTRAINT geraetespielanlagen_hro_pk PRIMARY KEY (uuid);


--
-- Name: gruenpflegeobjekte_datenwerft gruenpflegeobjekte_datenwerft_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.gruenpflegeobjekte_datenwerft
    ADD CONSTRAINT gruenpflegeobjekte_datenwerft_pk PRIMARY KEY (uuid);


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
-- Name: jagdkataster_skizzenebenen_hro jagdkataster_skizzenebenen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.jagdkataster_skizzenebenen_hro
    ADD CONSTRAINT jagdkataster_skizzenebenen_hro_pk PRIMARY KEY (uuid);


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
-- Name: punktwolken punktwolken_pkey; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.punktwolken
    ADD CONSTRAINT punktwolken_pkey PRIMARY KEY (uuid);


--
-- Name: punktwolken_projekte punktwolken_projekte_pkey; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.punktwolken_projekte
    ADD CONSTRAINT punktwolken_projekte_pkey PRIMARY KEY (uuid);


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
-- Name: spielplaetze_fotos_hro spielplaetze_fotos_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.spielplaetze_fotos_hro
    ADD CONSTRAINT spielplaetze_fotos_hro_pk PRIMARY KEY (uuid);


--
-- Name: spielplaetze_hro spielplaetze_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.spielplaetze_hro
    ADD CONSTRAINT spielplaetze_hro_pk PRIMARY KEY (uuid);


--
-- Name: sportanlagen_hro sportanlagen_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.sportanlagen_hro
    ADD CONSTRAINT sportanlagen_hro_pk PRIMARY KEY (uuid);


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
-- Name: versenkpoller_hro versenkpoller_hro_pk; Type: CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.versenkpoller_hro
    ADD CONSTRAINT versenkpoller_hro_pk PRIMARY KEY (uuid);


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
-- Name: feuerwachen_hro feuerwachen_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.feuerwachen_hro
    ADD CONSTRAINT feuerwachen_hro_pk PRIMARY KEY (uuid);


--
-- Name: feuerwehrzufahrten_schilder_hro feuerwehrzufahrten_schilder_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.feuerwehrzufahrten_schilder_hro
    ADD CONSTRAINT feuerwehrzufahrten_schilder_hro_pk PRIMARY KEY (uuid);


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
-- Name: mobilfunkantennen_hro mobilfunkantennen_hro_pk; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.mobilfunkantennen_hro
    ADD CONSTRAINT mobilfunkantennen_hro_pk PRIMARY KEY (uuid);


--
-- Name: mobilfunkantennen_hro mobilfunkantennen_hro_stob_unique; Type: CONSTRAINT; Schema: fachdaten_adressbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_adressbezug.mobilfunkantennen_hro
    ADD CONSTRAINT mobilfunkantennen_hro_stob_unique UNIQUE (stob);


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
-- Name: reinigungsreviere_hro reinigungsreviere_hro_pk; Type: CONSTRAINT; Schema: fachdaten_gemeindeteilbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_gemeindeteilbezug.reinigungsreviere_hro
    ADD CONSTRAINT reinigungsreviere_hro_pk PRIMARY KEY (uuid);


--
-- Name: abstellflaechen_e_tretroller_hro abstellflaechen_e_tretroller_hro_id_unique; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.abstellflaechen_e_tretroller_hro
    ADD CONSTRAINT abstellflaechen_e_tretroller_hro_id_unique UNIQUE (id);


--
-- Name: abstellflaechen_e_tretroller_hro abstellflaechen_e_tretroller_hro_pk; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.abstellflaechen_e_tretroller_hro
    ADD CONSTRAINT abstellflaechen_e_tretroller_hro_pk PRIMARY KEY (uuid);


--
-- Name: baugrunduntersuchungen_hro baugrunduntersuchungen_hro_pk; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.baugrunduntersuchungen_hro
    ADD CONSTRAINT baugrunduntersuchungen_hro_pk PRIMARY KEY (uuid);


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
-- Name: fahrradabstellanlagen_hro fahrradabstellanlagen_hro_id_unique; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradabstellanlagen_hro
    ADD CONSTRAINT fahrradabstellanlagen_hro_id_unique UNIQUE (id);


--
-- Name: fahrradabstellanlagen_hro fahrradabstellanlagen_hro_pk; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradabstellanlagen_hro
    ADD CONSTRAINT fahrradabstellanlagen_hro_pk PRIMARY KEY (uuid);


--
-- Name: fahrradboxen_hro fahrradboxen_hro_id_unique; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradboxen_hro
    ADD CONSTRAINT fahrradboxen_hro_id_unique UNIQUE (id);


--
-- Name: fahrradboxen_hro fahrradboxen_hro_pk; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradboxen_hro
    ADD CONSTRAINT fahrradboxen_hro_pk PRIMARY KEY (uuid);


--
-- Name: fahrradreparatursets_hro fahrradreparatursets_hro_id_unique; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradreparatursets_hro
    ADD CONSTRAINT fahrradreparatursets_hro_id_unique UNIQUE (id);


--
-- Name: fahrradreparatursets_hro fahrradreparatursets_hro_pk; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradreparatursets_hro
    ADD CONSTRAINT fahrradreparatursets_hro_pk PRIMARY KEY (uuid);


--
-- Name: fahrradstaender_hro fahrradstaender_hro_id_unique; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradstaender_hro
    ADD CONSTRAINT fahrradstaender_hro_id_unique UNIQUE (id);


--
-- Name: fahrradstaender_hro fahrradstaender_hro_pk; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradstaender_hro
    ADD CONSTRAINT fahrradstaender_hro_pk PRIMARY KEY (uuid);


--
-- Name: fussgaengerueberwege_hro fussgaengerueberwege_hro_id_unique; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fussgaengerueberwege_hro
    ADD CONSTRAINT fussgaengerueberwege_hro_id_unique UNIQUE (id);


--
-- Name: fussgaengerueberwege_hro fussgaengerueberwege_hro_pk; Type: CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fussgaengerueberwege_hro
    ADD CONSTRAINT fussgaengerueberwege_hro_pk PRIMARY KEY (uuid);


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
-- Name: baugrunduntersuchungen_hro_auftraggeber_ix; Type: INDEX; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE INDEX baugrunduntersuchungen_hro_auftraggeber_ix ON fachdaten_strassenbezug.baugrunduntersuchungen_hro USING btree (auftraggeber);


--
-- Name: geraetespielanlagen_hro tr_before_insert_10_foto; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_10_foto BEFORE INSERT ON fachdaten.geraetespielanlagen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: parkscheinautomaten_parkscheinautomaten_hro tr_before_insert_10_foto; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_10_foto BEFORE INSERT ON fachdaten.parkscheinautomaten_parkscheinautomaten_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: sportanlagen_hro tr_before_insert_10_foto; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_10_foto BEFORE INSERT ON fachdaten.sportanlagen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: versenkpoller_hro tr_before_insert_10_foto; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_insert_10_foto BEFORE INSERT ON fachdaten.versenkpoller_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


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
-- Name: geraetespielanlagen_hro tr_before_update_10_foto; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_update_10_foto BEFORE UPDATE OF foto ON fachdaten.geraetespielanlagen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: parkscheinautomaten_parkscheinautomaten_hro tr_before_update_10_foto; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_update_10_foto BEFORE UPDATE OF foto ON fachdaten.parkscheinautomaten_parkscheinautomaten_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: sportanlagen_hro tr_before_update_10_foto; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_update_10_foto BEFORE UPDATE OF foto ON fachdaten.sportanlagen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: versenkpoller_hro tr_before_update_10_foto; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER tr_before_update_10_foto BEFORE UPDATE OF foto ON fachdaten.versenkpoller_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


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
-- Name: punktwolken update_projekt_geometry_trigger; Type: TRIGGER; Schema: fachdaten; Owner: -
--

CREATE TRIGGER update_projekt_geometry_trigger AFTER INSERT OR DELETE OR UPDATE ON fachdaten.punktwolken FOR EACH ROW EXECUTE FUNCTION fachdaten.update_projekt_geometry();


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
-- Name: fahrradabstellanlagen_hro tr_before_insert_10_foto; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_10_foto BEFORE INSERT ON fachdaten_strassenbezug.fahrradabstellanlagen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: fahrradboxen_hro tr_before_insert_10_foto; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_10_foto BEFORE INSERT ON fachdaten_strassenbezug.fahrradboxen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: fahrradstaender_hro tr_before_insert_10_foto; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_10_foto BEFORE INSERT ON fachdaten_strassenbezug.fahrradstaender_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


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
-- Name: abstellflaechen_e_tretroller_hro tr_before_insert_id; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_id BEFORE INSERT ON fachdaten_strassenbezug.abstellflaechen_e_tretroller_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.id_abfallbehaelter();


--
-- Name: fahrradabstellanlagen_hro tr_before_insert_id; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_id BEFORE INSERT ON fachdaten_strassenbezug.fahrradabstellanlagen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.id_abfallbehaelter();


--
-- Name: fahrradboxen_hro tr_before_insert_id; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_id BEFORE INSERT ON fachdaten_strassenbezug.fahrradboxen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.id_abfallbehaelter();


--
-- Name: fahrradreparatursets_hro tr_before_insert_id; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_id BEFORE INSERT ON fachdaten_strassenbezug.fahrradreparatursets_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.id_abfallbehaelter();


--
-- Name: fahrradstaender_hro tr_before_insert_id; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_id BEFORE INSERT ON fachdaten_strassenbezug.fahrradstaender_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.id_abfallbehaelter();


--
-- Name: fussgaengerueberwege_hro tr_before_insert_id; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_id BEFORE INSERT ON fachdaten_strassenbezug.fussgaengerueberwege_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.id_abfallbehaelter();


--
-- Name: geh_und_radwegereinigung_hro tr_before_insert_id; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_id BEFORE INSERT ON fachdaten_strassenbezug.geh_und_radwegereinigung_hro FOR EACH ROW EXECUTE FUNCTION fachdaten_strassenbezug.id();


--
-- Name: strassenreinigung_hro tr_before_insert_id; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_insert_id BEFORE INSERT ON fachdaten_strassenbezug.strassenreinigung_hro FOR EACH ROW EXECUTE FUNCTION fachdaten_strassenbezug.id();


--
-- Name: fahrradabstellanlagen_hro tr_before_update_10_foto; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_update_10_foto BEFORE UPDATE OF foto ON fachdaten_strassenbezug.fahrradabstellanlagen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: fahrradboxen_hro tr_before_update_10_foto; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_update_10_foto BEFORE UPDATE OF foto ON fachdaten_strassenbezug.fahrradboxen_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


--
-- Name: fahrradstaender_hro tr_before_update_10_foto; Type: TRIGGER; Schema: fachdaten_strassenbezug; Owner: -
--

CREATE TRIGGER tr_before_update_10_foto BEFORE UPDATE OF foto ON fachdaten_strassenbezug.fahrradstaender_hro FOR EACH ROW EXECUTE FUNCTION fachdaten.foto();


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
-- Name: typen_naturdenkmale typen_naturdenkmale_arten_fk; Type: FK CONSTRAINT; Schema: codelisten; Owner: -
--

ALTER TABLE ONLY codelisten.typen_naturdenkmale
    ADD CONSTRAINT typen_naturdenkmale_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_naturdenkmale(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: _naturdenkmale_hro _naturdenkmale_hro_typen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten._naturdenkmale_hro
    ADD CONSTRAINT _naturdenkmale_hro_typen_fk FOREIGN KEY (typ) REFERENCES codelisten.typen_naturdenkmale(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


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
-- Name: abfallbehaelter_hro abfallbehaelter_hro_leerungszeiten_sommer_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.abfallbehaelter_hro
    ADD CONSTRAINT abfallbehaelter_hro_leerungszeiten_sommer_fk FOREIGN KEY (leerungszeiten_sommer) REFERENCES codelisten.leerungszeiten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: abfallbehaelter_hro abfallbehaelter_hro_leerungszeiten_winter_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.abfallbehaelter_hro
    ADD CONSTRAINT abfallbehaelter_hro_leerungszeiten_winter_fk FOREIGN KEY (leerungszeiten_winter) REFERENCES codelisten.leerungszeiten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


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
-- Name: baugrunduntersuchungen_baugrundbohrungen_hro baugrunduntersuchungen_baugrundbohrungen_hro_baugrunduntersuchu; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.baugrunduntersuchungen_baugrundbohrungen_hro
    ADD CONSTRAINT baugrunduntersuchungen_baugrundbohrungen_hro_baugrunduntersuchu FOREIGN KEY (baugrunduntersuchung) REFERENCES fachdaten_strassenbezug.baugrunduntersuchungen_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: baugrunduntersuchungen_dokumente_hro baugrunduntersuchungen_dokumente_hro_baugrunduntersuchungen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.baugrunduntersuchungen_dokumente_hro
    ADD CONSTRAINT baugrunduntersuchungen_dokumente_hro_baugrunduntersuchungen_fk FOREIGN KEY (baugrunduntersuchung) REFERENCES fachdaten_strassenbezug.baugrunduntersuchungen_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


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
-- Name: brunnen_hro brunnen_hro_arten_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.brunnen_hro
    ADD CONSTRAINT brunnen_hro_arten_fk FOREIGN KEY (art) REFERENCES codelisten.arten_brunnen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


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
-- Name: freizeitsport_fotos_hro freizeitsport_fotos_hro_freizeitsport_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.freizeitsport_fotos_hro
    ADD CONSTRAINT freizeitsport_fotos_hro_freizeitsport_fk FOREIGN KEY (freizeitsport) REFERENCES fachdaten.freizeitsport_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: freizeitsport_hro freizeitsport_hro_gruenpflegeobjekte_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.freizeitsport_hro
    ADD CONSTRAINT freizeitsport_hro_gruenpflegeobjekte_fk FOREIGN KEY (gruenpflegeobjekt) REFERENCES fachdaten.gruenpflegeobjekte_datenwerft(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


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
-- Name: jagdkataster_skizzenebenen_hro jagdkataster_skizzenebenen_hro_antragsteller_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.jagdkataster_skizzenebenen_hro
    ADD CONSTRAINT jagdkataster_skizzenebenen_hro_antragsteller_fk FOREIGN KEY (antragsteller) REFERENCES codelisten.antragsteller_jagdkataster_skizzenebenen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: jagdkataster_skizzenebenen_hro jagdkataster_skizzenebenen_hro_status_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.jagdkataster_skizzenebenen_hro
    ADD CONSTRAINT jagdkataster_skizzenebenen_hro_status_fk FOREIGN KEY (status) REFERENCES codelisten.status_jagdkataster_skizzenebenen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: jagdkataster_skizzenebenen_hro jagdkataster_skizzenebenen_hro_themen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.jagdkataster_skizzenebenen_hro
    ADD CONSTRAINT jagdkataster_skizzenebenen_hro_themen_fk FOREIGN KEY (thema) REFERENCES codelisten.themen_jagdkataster_skizzenebenen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


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
-- Name: punktwolken punktwolken_punktwolken_projekte_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.punktwolken
    ADD CONSTRAINT punktwolken_punktwolken_projekte_fk FOREIGN KEY (punktwolken_projekte) REFERENCES fachdaten.punktwolken_projekte(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


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
-- Name: spielplaetze_fotos_hro spielplaetze_fotos_hro_spielplaetze_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.spielplaetze_fotos_hro
    ADD CONSTRAINT spielplaetze_fotos_hro_spielplaetze_fk FOREIGN KEY (spielplatz) REFERENCES fachdaten.spielplaetze_hro(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: spielplaetze_hro spielplaetze_hro_gruenpflegeobjekte_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.spielplaetze_hro
    ADD CONSTRAINT spielplaetze_hro_gruenpflegeobjekte_fk FOREIGN KEY (gruenpflegeobjekt) REFERENCES fachdaten.gruenpflegeobjekte_datenwerft(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: sportanlagen_hro sportanlagen_hro_traeger_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.sportanlagen_hro
    ADD CONSTRAINT sportanlagen_hro_traeger_fk FOREIGN KEY (traeger) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


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
-- Name: versenkpoller_hro versenkpoller_hro_hersteller_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.versenkpoller_hro
    ADD CONSTRAINT versenkpoller_hro_hersteller_fk FOREIGN KEY (hersteller) REFERENCES codelisten.hersteller_versenkpoller(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: versenkpoller_hro versenkpoller_hro_typen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.versenkpoller_hro
    ADD CONSTRAINT versenkpoller_hro_typen_fk FOREIGN KEY (typ) REFERENCES codelisten.typen_versenkpoller(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: versenkpoller_hro versenkpoller_hro_wartungsfirmen_fk; Type: FK CONSTRAINT; Schema: fachdaten; Owner: -
--

ALTER TABLE ONLY fachdaten.versenkpoller_hro
    ADD CONSTRAINT versenkpoller_hro_wartungsfirmen_fk FOREIGN KEY (wartungsfirma) REFERENCES codelisten.wartungsfirmen_versenkpoller(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


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
-- Name: baugrunduntersuchungen_hro baugrunduntersuchungen_hro_auftraggeber_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.baugrunduntersuchungen_hro
    ADD CONSTRAINT baugrunduntersuchungen_hro_auftraggeber_fk FOREIGN KEY (auftraggeber) REFERENCES codelisten.auftraggeber_baugrunduntersuchungen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: baugrunduntersuchungen_hro baugrunduntersuchungen_hro_labore_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.baugrunduntersuchungen_hro
    ADD CONSTRAINT baugrunduntersuchungen_hro_labore_fk FOREIGN KEY (labor) REFERENCES codelisten.labore_baugrunduntersuchungen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


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
-- Name: fahrradabstellanlagen_hro fahrradabstellanlagen_hro_ausfuehrungen_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradabstellanlagen_hro
    ADD CONSTRAINT fahrradabstellanlagen_hro_ausfuehrungen_fk FOREIGN KEY (ausfuehrung) REFERENCES codelisten.ausfuehrungen_fahrradabstellanlagen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: fahrradabstellanlagen_hro fahrradabstellanlagen_hro_ausfuehrungen_stellplaetze_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradabstellanlagen_hro
    ADD CONSTRAINT fahrradabstellanlagen_hro_ausfuehrungen_stellplaetze_fk FOREIGN KEY (ausfuehrung_stellplaetze) REFERENCES codelisten.ausfuehrungen_fahrradabstellanlagen_stellplaetze(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: fahrradabstellanlagen_hro fahrradabstellanlagen_hro_eigentuemer_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradabstellanlagen_hro
    ADD CONSTRAINT fahrradabstellanlagen_hro_eigentuemer_fk FOREIGN KEY (eigentuemer) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: fahrradabstellanlagen_hro fahrradabstellanlagen_hro_hersteller_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradabstellanlagen_hro
    ADD CONSTRAINT fahrradabstellanlagen_hro_hersteller_fk FOREIGN KEY (hersteller) REFERENCES codelisten.hersteller_fahrradabstellanlagen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: fahrradboxen_hro fahrradboxen_hro_ausfuehrungen_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradboxen_hro
    ADD CONSTRAINT fahrradboxen_hro_ausfuehrungen_fk FOREIGN KEY (ausfuehrung) REFERENCES codelisten.ausfuehrungen_fahrradboxen(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: fahrradboxen_hro fahrradboxen_hro_eigentuemer_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradboxen_hro
    ADD CONSTRAINT fahrradboxen_hro_eigentuemer_fk FOREIGN KEY (eigentuemer) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: fahrradreparatursets_hro fahrradreparatursets_hro_ausfuehrungen_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradreparatursets_hro
    ADD CONSTRAINT fahrradreparatursets_hro_ausfuehrungen_fk FOREIGN KEY (ausfuehrung) REFERENCES codelisten.ausfuehrungen_fahrradreparatursets(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: fahrradreparatursets_hro fahrradreparatursets_hro_eigentuemer_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradreparatursets_hro
    ADD CONSTRAINT fahrradreparatursets_hro_eigentuemer_fk FOREIGN KEY (eigentuemer) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: fahrradstaender_hro fahrradstaender_hro_ausfuehrungen_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradstaender_hro
    ADD CONSTRAINT fahrradstaender_hro_ausfuehrungen_fk FOREIGN KEY (ausfuehrung) REFERENCES codelisten.ausfuehrungen_fahrradstaender(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: fahrradstaender_hro fahrradstaender_hro_eigentuemer_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fahrradstaender_hro
    ADD CONSTRAINT fahrradstaender_hro_eigentuemer_fk FOREIGN KEY (eigentuemer) REFERENCES codelisten.bewirtschafter_betreiber_traeger_eigentuemer(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: fussgaengerueberwege_hro fussgaengerueberwege_hro_beleuchtungsarten_fk; Type: FK CONSTRAINT; Schema: fachdaten_strassenbezug; Owner: -
--

ALTER TABLE ONLY fachdaten_strassenbezug.fussgaengerueberwege_hro
    ADD CONSTRAINT fussgaengerueberwege_hro_beleuchtungsarten_fk FOREIGN KEY (beleuchtungsart) REFERENCES codelisten.beleuchtungsarten(uuid) MATCH FULL ON UPDATE CASCADE ON DELETE RESTRICT;


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

