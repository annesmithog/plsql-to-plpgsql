CREATE OR REPLACE PROCEDURE
procedure2 (x VARCHAR2) IS
    msg1 VARCHAR2(10) := 'Hello';
BEGIN
    DBMS_OUTPUT.PUT_LINE(msg1 || ' ' || x);
EXCEPTION
WHEN DUP_VAL_ON_INDEX
THEN DBMS_OUTPUT.PUT_LINE('ERROR 1');
WHEN ZERO_DIVIDE
THEN DBMS_OUTPUT.PUT_LINE('ERROR 2');
END procedure2;
/

CALL procedure2('World');
