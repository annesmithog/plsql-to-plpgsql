[開発者向けREADME](README-dev.md)

plsql-to-plpgsql
---

Oracle PL/SQL を PostgreSQL PL/pgSQLに変換するツールです。

## 前提条件

システムに以下がインストールされていること。

- Python (3.7以上推奨)
- pip

## インストール

1. リポジトリのクローン

```sh
git clone https://github.com/annesmithog/plsql-to-plpgsql.git
cd plsql-to-plpgsql
```

2. 仮想環境の設定

```sh
python -m venv venv
```

3. アクティベート

```sh
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

4. 依存関係のインストール

```sh
pip install -r requirements.txt
```

5. 実行・アクセス

```sh
flask run
# http://127.0.0.1:5000 にアクセス
```

## 基本

### 基本構造 / Basic Structure

- `CREATE PROCEDURE` 
  - `IS` => `AS $$`
  - `END procedure_name;` => `END;`
  - `/` => `$$ LANGUAGE plpgsql;`

### 宣言 / Declaration

- `CLOB` => `TEXT`
- `BLOB` => `BYTEA`
- `VARCHAR2` => `VARCHAR`
- `NUMBER` => `NUMERIC`
- `CURSOR` 
  - `CURSOR cursor_name IS` => `cursor_name CURSOR FOR`
  - `CURSOR cursor_name(param) IS` => `CURSOR cursor_name(param) FOR`

### 実行 / Execution

- `FROM dual` => ``
- `systimestamp` => `current_timestamp`
- `WHERE rownum < 10` => `LIMIT 9`
- `WHERE a.col = b.col1 (+)` => `LEFT OUTER JOIN table2 b on a.col1 = b.col1`
- `DECODE(col1, 100, 'A', 'B')` => `CASE col1 WHEN 100 THEN 'A' ELSE 'B' END`
- `EXCEPTION WHEN DUP_VAL_ON_INDEX` => `EXCEPTION WHEN UNIQUE_VIOLATION`
- `EXCEPTION WHEN ZERO_DIVIDE` => `EXCEPTION WHEN DIVISION_BY_ZERO`
- `DBMS_OUTPUT.PUT_LINE('output_text');` => `RAISE NOTICE '%', 'output_text';`
