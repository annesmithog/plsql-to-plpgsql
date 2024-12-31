CREATE OR REPLACE PROCEDURE run() AS $$
DECLARE
BEGIN
    INSERT INTO employees VALUES ('1', 'John', 'Smith', 'M', 170);
	INSERT INTO employees VALUES ('2', 'Tetsuto', 'Yamada', 'M', 182);
	INSERT INTO employees VALUES ('3', 'Anne', 'Smith', 'F', 174);
END;
$$ LANGUAGE plpgsql;

CALL run();
