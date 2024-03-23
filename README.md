## Инструкция по запуску сервиса
1. Нужно установить зависимости проекта, это можно сделать через команду<br\>:
```bash
pip3 install -r requirements.txt
``
2. Запустить сам сервис (сервис запустится на 5000 порту):
```bash
python3 main.py
```
# Примеры обращений к сервису
Чтобы создать фильм нужно сделать POST запрос, сделать этом можно через команду curl<br\>:
```bash
curl -X POST -i -H 'Content-Type: application/json' -d '{"movie": {"id": 1,"title": "Example movie","year": 2018,"director": {"id": 1, "fio": "Gleb Gerlakh"},"length": "02:30:00","rating": 8}}' http://127.0.0.1:5000/api/movies
```
<br\>Ответ будет следующего формата
```json
{
    "id": 1,
    "title": "Example movie",
    "year": 2018,
    "director": {
        "id": 1,
        "fio": "Gleb Gerlakh"
    },
    "length": "02:30:00",
    "rating": 8
}
```
Посмотреть созданный фильм можно через следующую команду curl:
```bash
curl -i http://127.0.0.1:5000/api/movie/1 
```
Ответ будет в следующем формате:
```json
{"director":{"fio":"Gleb Gerlakh","id":1},"id":1,"length":"02:30:00","rating":8,"title":"Example movie","year":2018}
```
Также можно посмотреть созданный фильм через curl:
```bash
curl -i http://127.0.0.1:5000/api/director/1
```
Ответ будет в следующем формате:
```json
{"fio":"Gleb Gerlakh","id":1}
```