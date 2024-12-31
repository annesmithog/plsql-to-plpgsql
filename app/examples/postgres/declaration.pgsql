CREATE OR REPLACE PROCEDURE
procedure1 (name VARCHAR) AS $$
DECLARE
    var1 TEXT;
    var2 BYTEA;
    var3 VARCHAR(100);
    var4 NUMERIC(10);
BEGIN
    var4 := 12345;
    RAISE NOTICE '%', 'Test';
END;
$$ LANGUAGE plpgsql;