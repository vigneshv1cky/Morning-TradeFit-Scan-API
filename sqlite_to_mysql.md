
# Migrating from SQLite to MySQL

This guide explains how to convert your SQLite database to MySQL for your FastAPI project.

---

## 1) Install a MySQL driver

Pick **one**:

* Easy & pure-Python (no system libs):
  `pymysql`
* Faster but needs MySQL client libs on your machine:
  `mysqlclient`

Add to `requirements.txt` (choose one):

```
pymysql
# or
mysqlclient
```

Install:

```bash
pip install -r requirements.txt
```

---

## 2) Update your DB URL in `app/config.py`

**PyMySQL (recommended for easiest install):**

```python
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/yourdbname?charset=utf8mb4"
```

**mysqlclient:**

```python
SQLALCHEMY_DATABASE_URL = "mysql+mysqlclient://username:password@localhost:3306/yourdbname?charset=utf8mb4"
```

> Tip: Always include `charset=utf8mb4` so you support full Unicode (including emojis).

---

## 3) Update `app/database.py` to use the new URL

Make sure your SQLAlchemy engine is created with the MySQL URL and enable `pool_pre_ping`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,         # avoids stale connections
    future=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

If you’re using async SQLAlchemy, use `asyncmy`:

```
pip install sqlalchemy[asyncio] asyncmy
```

```python
DATABASE_URL = "mysql+asyncmy://username:password@localhost:3306/yourdbname?charset=utf8mb4"
```

---

## 4) Create the MySQL database (and user)

Using the MySQL client:

```bash
mysql -u root -p
```

```sql
CREATE DATABASE yourdbname CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER 'username'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON yourdbname.* TO 'username'@'%';
FLUSH PRIVILEGES;
```

> If `utf8mb4_0900_ai_ci` isn’t available (older MySQL/MariaDB), use `utf8mb4_general_ci`.

---

## 5) Migrate data from SQLite → MySQL

### Option A (one-command CLI): `sqlite3-to-mysql`

This is the easiest for most projects.

```bash
pip install sqlite3-to-mysql
sqlite3mysql \
  --sqlite-file /absolute/path/to/tradefit.db \
  --mysql-user username \
  --mysql-password password \
  --mysql-host localhost \
  --mysql-port 3306 \
  --mysql-database yourdbname \
  --with-rowid
```

Notes:

* Stop your app while migrating so writes don’t change mid-transfer.
* If you used SQLite booleans, they’ll become `TINYINT(1)` (normal for MySQL).
* If you hit key/constraint errors, migrate schema first with Alembic (next step), then migrate data table-by-table.

### Option B (scripted ETL)

If you have tricky types or want full control, write a small Python script that reads from SQLite and bulk-inserts into MySQL (SQLAlchemy ORM or `pandas.to_sql`). This is slower but very flexible.

---

## 6) Apply migrations (if using Alembic)

Update `alembic.ini` or your env to use the MySQL URL (same as step 2), then:

```bash
alembic upgrade head
```

**MySQL gotchas to check in migrations/models:**

* Use `String(length=...)` for indexed text columns (MySQL requires a length).
* `JSON` type needs MySQL 5.7+ / 8.0+ (ok on MySQL 8).
* `DateTime(timezone=True)` is stored as naive in MySQL; handle TZ in app.
* Large `Text`/`LONGTEXT` vs `VARCHAR`—pick appropriately.
* Ensure `__table_args__ = {"mysql_engine": "InnoDB"}` if you need InnoDB explicitly.

---

## 7) Update Docker Compose (if using Docker)

```yaml
services:
  db:
    image: mysql:8.4
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: yourdbname
      MYSQL_USER: username
      MYSQL_PASSWORD: password
    ports:
      - "3306:3306"
    command: >
      mysqld --character-set-server=utf8mb4 --collation-server=utf8mb4_0900_ai_ci
    volumes:
      - mysql_data:/var/lib/mysql
    your_psychologycheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "username", "-ppassword"]
      interval: 10s
      timeout: 5s
      retries: 10

volumes:
  mysql_data:
```

> If your host is Apple Silicon and you use `mysqlclient`, install MySQL client libs or switch to `pymysql`.

---

## 8) Point your app to MySQL & test

* Update `.env` / config with the MySQL URL.
* Restart your app (and containers).
* Run a quick sanity check (list tables, basic CRUD).

---

## Optional: exact `app/database.py` and Alembic tweaks

If you share your current `app/database.py` and `alembic.ini` (or models), I’ll give you the precise code diffs (sync or async), plus index length adjustments for MySQL.
