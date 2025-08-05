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
$ . venv/Scripts/activate # windows git bash
```

```sh
$ pip install -r requirements.txt
```

### 2. set environment or create config.json
| Name             | Description                                  |
| ---------------- |----------------------------------------------|
| APP_MODE         | choose from production, development, testing |
| APP_HOST         | ip address ex) 0.0.0.0                       |
| APP_PORT         | port number ex) 8888                         |
| DB_USER_NAME     | db user name                                 |
| DB_USER_PASSWD   | db user password                             |
| DB_HOST          | db host ex) devmaker.kr                      |
| DB_NAME          | db name                                      |
| REDIS_HOST       | redis ip address default) localhost          |
| REDIS_PASSWD     | redis password default) None                 |

### 3. db migrate
```mysql
# mysql
create database Youtube
```

```sh
$ alembic upgrade head
```
create db and migrate tables

```mysql
INSERT INTO
    Channel (name, image, created_at, user_id)
values ('한빛미디어', 'https://gureuso.s3.ap-northeast-2.amazonaws.com/fastapi/hanbit_logo.webp', '2025-06-05 19:16:12', 1);

INSERT INTO
    Video (user_id, channel_id, title, thumbnail, content, created_at, tag)
values
    (1, 1, '파이썬으로 프로그래밍 시작하기', 'https://cdn-prod.hanbit.co.kr/thumbnails/C2662526625_cover.jpg',
     'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4', '2025-06-05 19:16:12', '파이썬'),
    (1, 1, '혼자 공부하는 파이썬', 'https://cdn-prod.hanbit.co.kr/thumbnails/C5104434431_cover.jpg',
     'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4', '2025-06-05 19:16:12', '파이썬'),
    (1, 1, '쿠버네티스로 시작하기', 'https://cdn-prod.hanbit.co.kr/thumbnails/C3865785505_cover.jpg',
     'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4', '2025-06-05 19:16:12', '인프라');

INSERT INTO
    Tag (video_id, name)
values
    (1, '파이썬'), (2, '파이썬'), (3, '인프라');

INSERT INTO
    Shorts (user_id, channel_id, title, thumbnail, content, created_at, tag)
values
    (1, 1, '혼자 만들면서 공부하는 파이썬', 'https://www.hanbit.co.kr/data/books/B5580711889_l.jpg',
     'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4', '2025-06-05 19:16:12', '파이썬'),
    (1, 1, '조코딩의 AI 비트코인 자동 매매 시스템 만들기', 'https://www.hanbit.co.kr/data/books/B5063161940_l.jpg',
     'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4', '2025-06-05 19:16:12', 'AI'),
    (1, 1, '소문난 명강의 김길성의 네트워크 딥다이브', 'https://www.hanbit.co.kr/data/books/B9674813480_l.jpg',
     'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4', '2025-06-05 19:16:12', '네트워크'),
    (1, 1, '요즘 교사를 위한 AI 수업 활용 가이드 with 2022 개정 교육과정', 'https://www.hanbit.co.kr/data/books/B5865274723_l.jpg',
     'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4', '2025-06-05 19:16:12', 'AI');
```
create table data
