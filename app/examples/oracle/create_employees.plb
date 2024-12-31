CREATE TABLE employees(
    empno CHAR(6) PRIMARY KEY NOT NULL,
    first_name VARCHAR2(20) NOT NULL,
    last_name VARCHAR2(20) NOT NULL,
    sex CHAR(1),
    height NUMBER(4, 0)
);