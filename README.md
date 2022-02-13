# ArtCommunity

---

### Описание

---

Проект предназначен для создания пользователями постов, содержаших тест и изображения. Посты можно отнести к различным группам.
Есть возможность писать комментарии к постам, а так же оформлять подписки на авторов. 

---

### Установка

---

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/ilyasurkov94/api_final_yatube.git
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source venv/Scripts/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

---

