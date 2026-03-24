import os
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

TOKEN = os.getenv("VK_TOKEN")
ADMIN_ID = 312757194  # твой VK ID

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

users = {}  # состояние пользователей

# Главное меню
def main_menu_keyboard():
    kb = VkKeyboard(one_time=False)
    kb.add_button("Частые вопросы", VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("Заказ", VkKeyboardColor.POSITIVE)
    kb.add_button("О нас", VkKeyboardColor.SECONDARY)
    return kb.get_keyboard()

# Клавиатура для раздела FAQ
def faq_keyboard():
    kb = VkKeyboard(one_time=True)
    kb.add_button("Другой вопрос", VkKeyboardColor.POSITIVE)
    kb.add_line()
    kb.add_button("Назад", VkKeyboardColor.SECONDARY)
    return kb.get_keyboard()

# Клавиатура выбора размера
def size_keyboard():
    kb = VkKeyboard(one_time=True)
    for i, s in enumerate(range(35, 46)):
        kb.add_button(str(s), VkKeyboardColor.PRIMARY)
        if (i + 1) % 5 == 0:
            kb.add_line()
    return kb.get_keyboard()

# Сообщение при неправильном вводе
def wrong_input(user_id, keyboard=None):
    vk.messages.send(
        user_id=user_id,
        message="❗ Пожалуйста, используйте кнопки или введите корректные данные.",
        random_id=0,
        keyboard=keyboard
    )

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id = event.user_id
        text = event.text.strip()

        if user_id not in users:
            users[user_id] = {"step": 0}
            vk.messages.send(
                user_id=user_id,
                message="👋 Привет! Выбери действие:",
                random_id=0,
                keyboard=main_menu_keyboard()
            )
            continue

        step = users[user_id]["step"]

        # Главное меню
        if step == 0:
            if text == "Частые вопросы":
                users[user_id]["step"] = "faq"
                vk.messages.send(
                    user_id=user_id,
                    message="ЧАСТЫЕ ВОПРОСЫ\n\n"
                    "💲Как формируется цена?\n" 
                    "Формула расчета цены:\n"
                    "(Стоимость товара*курс юаня) + 15% + стоимость доставки\n" "= итоговая цена\n\n"   
                    "Мы заказываем из Китая с площадки Poizon, поэтому\n" "опираемся на курс юаня.\n"
                    "15% - наша комиссия\n"
                    "Стоимость доставки = 800 руб/кг\n\n"
                    "📦Как долго будет идти товар?\n"
                    "Доставка длится от 10 до 17 дней\n"
                    "Мы будем на связи все время, пока товар не будет доставлен🙌🏻\n\n"
                    "💰Что с оплатой?\n"
                    "Оплата производится сразу.\n"
                    "Цена самого товара + цена доставки\n\n"
                    "ТОВАР ВОЗВРАТУ И ОБМЕНУ НЕ ПОДЛЕЖИТ.\n\n" 
                    "🤷Что делать, если я не знаю, что хочу?\n" 
                    "Если вы затрудняетесь с выбором – мы с удовольствием поможем!\n"
                    "Вы можете описать, что примерно вы хотели бы: в каком цвете, для каких целей и другие характеристики.\n"
                    "Мы сделаем все возможное, чтобы вы нашли ту самую модель 🤍\n\n"
                    "Если вы не нашли здесь свой вопрос, то напишите его и менеджер свяжется с вами!",
                    random_id=0,
                    keyboard=faq_keyboard()
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
                    message="О НАС\n\n"
                            "IFE — молодая компания, которая занимается продажей оригинальных кроссовок и одежды.\n"
                            "Поставляем напрямую от производителя, так что в качестве можете не сомневаться.\n"
                            "Готовы пройти любые проверки 🙌🏻\n\n"
                            "У нас более 50 довольных клиентов.\n"
                            "Отзывы можно посмотреть в разделе «Отзывы» в нашем сообществе.\n\n"
                            "Мы готовы удовлетворить любой ваш запрос: редкая модель, необычный цвет, большой/маленький размер!\n\n"
                            "Ждем вас в нашем сообществе!🤍",
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

        # Раздел FAQ
        if step == "faq":
            if text == "Назад":
                users[user_id]["step"] = 0
                vk.messages.send(
                    user_id=user_id,
                    message="👋 Главное меню:",
                    random_id=0,
                    keyboard=main_menu_keyboard()
                )
                continue
            elif text == "Другой вопрос":
                users[user_id]["step"] = "custom_question"
                vk.messages.send(
                    user_id=user_id,
                    message="✏️ Напишите ваш вопрос, и менеджер свяжется с вами:",
                    random_id=0
                )
                continue
            else:
                wrong_input(user_id, faq_keyboard())
                continue

        # Пользователь пишет свой вопрос
        if step == "custom_question":
            user_question = text
            # Отправляем администратору
            vk.messages.send(
                user_id=ADMIN_ID,
                message=f"❓ Новый вопрос от https://vk.com/id{user_id}:\n{user_question}",
                random_id=0
            )
            vk.messages.send(
                user_id=user_id,
                message="✅ Ваш вопрос принят! Менеджер скоро свяжется с вами.",
                random_id=0,
                keyboard=main_menu_keyboard()
            )
            users[user_id]["step"] = 0
            continue

        # Шаги оформления заказа
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

        if step == 4:
            if not event.attachments and text.lower() != "нет":
                wrong_input(user_id)
                continue

            photo_status = "Фото приложено ✅" if event.attachments else "Фото не приложено ❌"
            model = users[user_id]["model"]
            eu = users[user_id]["eu"]
            insole = users[user_id]["insole"]

            order_text = f"{user_id} | {model} | EU {eu} | Стелька {insole} | {photo_status}\n"
            with open("orders.txt", "a", encoding="utf-8") as f:
                f.write(order_text)

            vk.messages.send(
                user_id=ADMIN_ID,
                message=f"🔥 Новый заказ!\nhttps://vk.com/id{user_id}\nМодель: {model}\nEU: {eu}\nСтелька: {insole}\n{photo_status}",
                random_id=0
            )

            vk.messages.send(
                user_id=user_id,
                message="✅ Заказ принят! Менеджер скоро свяжется.",
                random_id=0,
                keyboard=main_menu_keyboard()
            )
            users[user_id]["step"] = 0