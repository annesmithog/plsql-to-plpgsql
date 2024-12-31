CREATE TABLE employees(
    empno CHAR(6) PRIMARY KEY NOT NULL,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    sex CHAR(1),
    height NUMERIC(4, 0)
);