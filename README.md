# Handson FastAPI
Handson FastAPI example

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
| Name                | Description                      |
| ------------------- | -------------------------------- |
| APP_MODE            | choose from production, development, testing |
| APP_HOST            | ip address                       |
| APP_PORT            | port number                      |
| DB_USER_NAME        | db user name                     |
| DB_USER_PASSWD      | db user password                 |
| DB_HOST             | db host                          |
| DB_DB_NAME          | db name                          |
| REDIS_HOST          | redis ip address                 |
| REDIS_PASSWD        | redis password                   |

### 3. db migrate
```sh
$ alembic upgrade head
```
migrate db tables
