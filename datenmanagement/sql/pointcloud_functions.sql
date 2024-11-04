-- 1. Die Berechnungsfunktion
CREATE OR REPLACE FUNCTION fachdaten.generate_pointcloud_union(projekt_uuid uuid)
RETURNS geometry AS $$
    SELECT ST_Union(geometrie)
    FROM fachdaten.punktwolken
    WHERE punktwolken_projekte = $1;
$$ LANGUAGE SQL STABLE;

-- 2. Geometrie-Spalte zur punktwolken_projekte Tabelle hinzufügen
ALTER TABLE fachdaten.punktwolken_projekte
ADD COLUMN geometrie geometry(MultiPolygon, 25833);

-- 3. Die Trigger-Funktion
CREATE OR REPLACE FUNCTION fachdaten.update_projekt_geometry()
RETURNS TRIGGER AS $$
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
$$ LANGUAGE plpgsql;

-- 4. Den Trigger erstellen
CREATE TRIGGER update_projekt_geometry_trigger
AFTER INSERT OR UPDATE OR DELETE ON fachdaten.punktwolken
FOR EACH ROW
EXECUTE FUNCTION fachdaten.update_projekt_geometry();