import os
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

TOKEN = os.getenv("VK_TOKEN")
ADMIN_ID = 312757194  # твой VK ID

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

users = {}  # здесь храним состояние пользователей

# Главное меню
def main_menu_keyboard():
    kb = VkKeyboard(one_time=False)
    kb.add_button("Частые вопросы", VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("Заказ", VkKeyboardColor.POSITIVE)
    kb.add_button("О нас", VkKeyboardColor.SECONDARY) 
    return kb.get_keyboard()

# Сообщение при неправильном вводе
def wrong_input(user_id, keyboard=None):
    vk.messages.send(
        user_id=user_id,
        message="❗Пожалуйста, используйте кнопки или введите корректные данные.",
        random_id=0,
        keyboard=keyboard
    )

# Клавиатура выбора размера
def size_keyboard():
    kb = VkKeyboard(one_time=True)
    sizes = [str(x) for x in range(35, 46)]
    for i, s in enumerate(sizes):
        kb.add_button(s, VkKeyboardColor.PRIMARY)
        if (i + 1) % 5 == 0:
            kb.add_line()
    return kb.get_keyboard()

# Основной цикл бота
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id = event.user_id
        text = event.text.strip()

        if user_id not in users:
            # Новый пользователь – показываем главное меню
            users[user_id] = {"step": 0}
            vk.messages.send(
                user_id=user_id,
                message="👋 Привет! Выбери действие:",
                random_id=0,
                keyboard=main_menu_keyboard()
            )
            continue

        step = users[user_id]["step"]

        # Главная кнопка меню
        if step == 0:
            if text == "Частые вопросы":
                vk.messages.send(
                    user_id=user_id,
                    message=(
                        "📦 Доставка 9-15 дней\n"
                        "💰 Товар оплачивается сразу\n"
                        "🚚 Доставка оплачивается отдельно (800 руб/кг)\n"
                        "💵 Наша комиссия - 15%\n"
                    ),
                    random_id=0,
                    keyboard=main_menu_keyboard()
                )
                continue

            elif text == "Заказ":
                users[user_id]["step"] = 1
                vk.messages.send(
                    user_id=user_id,
                    message="👟 Введите название модели кроссовок:",
                    random_id=0
                )
                continue

            elif text == "О нас":
                vk.messages.send(
                    user_id=user_id,
                    message="👟 О нас:\nДоставляем кроссовки на заказ.",
                    random_id=0,
                    keyboard=main_menu_keyboard()
                )
                continue

            else:
                vk.messages.send(
                    user_id=user_id,
                    message="Выберите кнопку из меню.",
                    random_id=0,
                    keyboard=main_menu_keyboard()
                )
                continue

        # Шаг 1: модель
        if step == 1:
            users[user_id]["model"] = text
            users[user_id]["step"] = 2
            vk.messages.send(
                user_id=user_id,
                message="📏 Выберите размер EU:",
                random_id=0,
                keyboard=size_keyboard()
            )
            continue

        # Шаг 2: размер EU
        if step == 2:
            if text.isdigit() and 35 <= int(text) <= 45:
                users[user_id]["eu"] = text
                users[user_id]["step"] = 3
                vk.messages.send(
                    user_id=user_id,
                    message="📏 Напишите размер стельки в см:",
                    random_id=0
                )
            else:
                wrong_input(user_id, size_keyboard())
            continue

        # Шаг 3: размер стельки
        if step == 3:
            try:
                float(text.replace(",", "."))
                users[user_id]["insole"] = text
                users[user_id]["step"] = 4
                vk.messages.send(
                    user_id=user_id,
                    message="📸 Прикрепите фото товара (или напишите 'нет'):",
                    random_id=0
                )
            except:
                wrong_input(user_id)
            continue

        # Шаг 4: фото
        if step == 4:
            if not event.attachments and text.lower() != "нет":
                wrong_input(user_id)
                continue

            # Проверяем, есть ли фото
            if event.attachments:
                photo_status = "Фото приложено ✅"
            else:
                photo_status = "Фото не приложено ❌"

            model = users[user_id]["model"]
            eu = users[user_id]["eu"]
            insole = users[user_id]["insole"]

            # Сохраняем заказ в файл
            order_text = f"{user_id} | {model} | EU {eu} | Стелька {insole} | {photo_status}\n"
            with open("orders.txt", "a", encoding="utf-8") as f:
                f.write(order_text)

            # Отправляем администратору
            vk.messages.send(
                user_id=ADMIN_ID,
                message=(
                    f"🔥 Новый заказ!\n"
                    f"https://vk.com/id{user_id}\n"
                    f"Модель: {model}\n"
                    f"EU: {eu}\n"
                    f"Стелька: {insole}\n"
                    f"{photo_status}"
                ),
                random_id=0
            )

            # Подтверждаем пользователю
            vk.messages.send(
                user_id=user_id,
                message="✅ Заказ принят! Менеджер скоро свяжется.",
                random_id=0,
                keyboard=main_menu_keyboard()
            )

            # Сбрасываем пользователя в главное меню
            del users[user_id]