CREATE OR REPLACE PROCEDURE
procedure2 (x VARCHAR) AS $$
DECLARE
    msg1 VARCHAR(10) := 'Hello';
BEGIN
    RAISE NOTICE '%', CONCAT(msg1, ' ', x);
EXCEPTION
WHEN UNIQUE_VIOLATION
THEN RAISE NOTICE '%', 'ERROR 1';
WHEN DIVISION_BY_ZERO
THEN RAISE NOTICE '%', 'ERROR 2';
END;
$$ LANGUAGE plpgsql;

CALL procedure2('World');
