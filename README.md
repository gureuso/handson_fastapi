# Handson FastAPI
Handson FastAPI example

python >= 3.12

# Usage

### 1. install virtualenv
```sh
$ pip install virtualenv
$ virtualenv -p python3 venv
```

```sh
$ . venv/bin/activate # mac, linux
$ call venv\Scripts\activate # windows
```

```sh
$ pip install -r requirements.txt
```

### 2. set environment or create config.json
| Name                | Description                                  |
| ------------------- |----------------------------------------------|
| APP_MODE            | choose from production, development, testing |
| APP_HOST            | ip address ex) 0.0.0.0                       |
| APP_PORT            | port number                                  |
| DB_USER_NAME        | db user name                                 |
| DB_USER_PASSWD      | db user password                             |
| DB_HOST             | db host                                      |
| DB_DB_NAME          | db name                                      |
| REDIS_HOST          | redis ip address                             |
| REDIS_PASSWD        | redis password                               |

### 3. db migrate
```mysql
create database Youtube
```

```sh
$ alembic upgrade head
```
create db and migrate tables
