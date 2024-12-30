CREATE OR REPLACE PROCEDURE
procedure1 (name VARCHAR2) IS
    var1 CLOB;
    var2 BLOB;
    var3 VARCHAR2(100);
    var4 NUMBER(10);
BEGIN
    var4 := 12345;
    DBMS_OUTPUT.PUT_LINE('Test');
END procedure1;
/