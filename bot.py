import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
ADMIN_ID = 312757194
TOKEN = "vk1.a.2jU3Z96fiZcGSjidO2iXaNEfDx7Fx5tbbW2ChJ_gZUCXLpPe5fQgAV-88leU74OqIp230eMv1qx3S_abW1POGqI1fen5YNh2rLnC4KB3LtwJqJXA48N22e_4VtxWeQMp5DRPt3TAQjC6aPbeWKVXtD1aHbuFWyEJoQRVtL4rfGUFyowMMVwMdyKaQU7UZU6ziXJYAkYVVEqDKpOoeo_m0w"

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

users = {}

def brand_keyboard():
    kb = VkKeyboard()
    kb.add_button("Nike", VkKeyboardColor.PRIMARY)
    kb.add_button("Adidas", VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("FAQ", VkKeyboardColor.SECONDARY)
    return kb.get_keyboard()

def size_keyboard():
    kb = VkKeyboard()
    kb.add_button("40", VkKeyboardColor.PRIMARY)
    kb.add_button("41", VkKeyboardColor.PRIMARY)
    kb.add_button("42", VkKeyboardColor.PRIMARY)
    kb.add_button("43", VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("FAQ", VkKeyboardColor.SECONDARY)
    return kb.get_keyboard()

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:

        user = event.user_id
        text = event.text

        if text.lower() == "faq":
            vk.messages.send(
                user_id=user,
                message="📦 Доставка 3-5 дней\n💰 Оплата при получении\n🔁 Обмен есть",
                random_id=0,
                keyboard=brand_keyboard()
            )
            continue

        if user not in users:
            vk.messages.send(
                user_id=user,
                message="Привет 👟 Выбери бренд",
                random_id=0,
                keyboard=brand_keyboard()
            )
            users[user] = {}
            continue

        if text in ["Nike", "Adidas"]:
            users[user]["brand"] = text

            vk.messages.send(
                user_id=user,
                message="Выбери размер",
                random_id=0,
                keyboard=size_keyboard()
            )
            continue

        if text in ["40", "41", "42", "43"]:
            brand = users[user]["brand"]
            size = text

            # запись заказа
            with open("orders.txt", "a", encoding="utf-8") as f:
                f.write(f"{user} | {brand} | {size}\n")

            # уведомление админу
            vk.messages.send(
                user_id=ADMIN_ID,
                message=f"🔥 Новый заказ\nКлиент: https://vk.com/id{user}\n{brand} размер {size}",
                random_id=0
            )
            

            vk.messages.send(
                user_id=user,
                message=f"✅ Заказ принят\n{brand} размер {size}\nМенеджер скоро напишет",
                random_id=0,
                keyboard=brand_keyboard()
            )

            del users[user]