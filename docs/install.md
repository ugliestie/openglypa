# Установка бота

> [!IMPORTANT]
> Для работы бота необходимо, чтобы Privacy Mode был отключен в Bot Settings [@BotFather](https://t.me/BotFather), иначе он не будет отвечать на команды и обучаться!

### Установка

```sh
git clone https://github.com/ugliestie/openglypa.git

cd openglypa

pip install -r requirements.txt
```

### Настройка

> Переименуйте example.env в .env и заполните:

```sh
TOKEN="TOKEN"   # Токен бота
```

### Запуск

```sh
python main.py
```
