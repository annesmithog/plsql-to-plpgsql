CREATE OR REPLACE PROCEDURE
procedure1 (name VARCHAR) AS $$
DECLARE
    msg1 VARCHAR(10) := 'Hello';
BEGIN
    RAISE NOTICE '%', CONCAT(msg1, ' ', name);
END;
$$ LANGUAGE plpgsql;

CALL procedure1('World');
