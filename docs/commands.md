# Справка по комнадам Openglypa

В данной статье будет показаны различные примеры использования команд бота, а компактную справку в чате всегда можно получить с помощью `h j h`

## Генерация текстового контента

Все текстовые команды опираются на цепь Маркова и принцип работы данной цепи был подсмотрен у проекта [Witless](https://github.com/jieggii/witless), спасибо его разработчикам! :3

+ `h j g` - бот генерирует текст любой длины с любым началом
+ `h j g <начало>` - генерация текста с заданным началом
<div align="center">
  <img width="198" height="80" alt="image" src="https://github.com/user-attachments/assets/8335ca4c-6547-4b2e-b3d9-e5db175a5cc4" />
</div>

+ `h j g <число>` - генерация фиксированной длины
+ `h j g l` - генерация длинного текста
+ `h j p` - генерация опроса или викторины

## Генерация медиаконтента

+ `h j t` - генерация сообщения в стиле [телеграм-канала Топор 1+](https://t.me/topor1plus)
<div align="center">
<img width="508" height="475" alt="image" src="https://github.com/user-attachments/assets/fa83c4a2-f46f-46bd-927e-dc3702d72bf5" />
</div>

+ `h j d` - генерация демотиватора из случайного изображения, сохранённого в чате
<div align="center">
<img width="508" alt="image" src="https://github.com/user-attachments/assets/35b1f284-ffe0-4569-8cb9-69001888ca45" />
</div>

+ `h j m` - генерация случайного мема (посмотреть все шаблоны можно в [/utils/resources/templates](https://github.com/ugliestie/openglypa/tree/main/utils/resources/templates))

<div align="center">
<img width="508"alt="image" src="https://github.com/user-attachments/assets/4eb5b0a3-0839-4986-b3e7-93b4071a6936" />
</div>

## Настройки бота

Бот также отправляет сообщения самостоятельно, без команд, и это поведение также можно изменить!

+ `h j s` - открыть настройки

<div align="center">
  <img width="297" height="98" alt="image" src="https://github.com/user-attachments/assets/7444931d-4285-4974-85c9-1049e7347ae6" />
  Первоначальный экран настроек</br>  </br> 
  <img width="297" height="181" alt="image" src="https://github.com/user-attachments/assets/ea56c6df-a661-4499-8d8c-e3fad7044744" />
  Настройки генерации</br> </br> 

  <img width="487" height="155" alt="image" src="https://github.com/user-attachments/assets/dbf34e65-ab11-4218-b040-2a863a2571ae" />
  Настройка лени бота, автоматическая работа бота настроена так что бот в 95% ленится писать сам, если кто-то написал в чате. Это можно изменить, отправив число от 0 до 100.</br> </br> 

  <img width="482" height="234" alt="image" src="https://github.com/user-attachments/assets/f7ffc1c8-cb7c-426a-b021-b1f046c02f85" />
  В "Типы контента" можно выбрать можно какие команды бота можно использовать в чате, а в "Автоматический вызов" - какой контент он будет генерировать самостоятельно </br> </br> 
</div>

+ `h j del` в ответ на сообщение - удалить из базы данных бота изображение/стикер
