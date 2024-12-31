CREATE OR REPLACE PROCEDURE
procedure1 (name VARCHAR2) IS
    msg1 VARCHAR2(10) := 'Hello';
BEGIN
    DBMS_OUTPUT.PUT_LINE(msg1 || ' ' || name);
END procedure1;
/

CALL procedure1('World');
