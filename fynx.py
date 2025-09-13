import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# ==========================
# 🔑 Настройки
# ==========================
API_TOKEN = "8376508422:AAEYUiLyvBtXCfJBril_VpHku6BA77_3BJU"
ADMIN_ID = 1347186841
GROUP_ID = -1003055132178

# ==========================
# Логирование
# ==========================
logging.basicConfig(level=logging.INFO)

# ==========================
# Инициализация
# ==========================
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Хранилище заявок
clients_data = {}

# ==========================
# FSM
# ==========================
class OrderForm(StatesGroup):
    choosing_service = State()
    choosing_subservice = State()
    describing_product = State()
    leaving_contact = State()
    typing_contact = State()  # новое состояние для ввода контакта

# ==========================
# Клавиатуры
# ==========================
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌐 Создание сайтов")],
        [KeyboardButton(text="🤖 Создание Telegram-ботов")],
        [KeyboardButton(text="🛡 Поддержка и обеспечение")],
    ],
    resize_keyboard=True
)

sites_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌐 Сайт-визитка")],
        [KeyboardButton(text="🛒 Интернет-магазин")],
        [KeyboardButton(text="🏢 Корпоративный сайт")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True
)

bots_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🤖 Чат-бот для бизнеса")],
        [KeyboardButton(text="📢 Бот для рассылки")],
        [KeyboardButton(text="💬 Клиентский бот-помощник")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True
)

support_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔒 Поддержка сайтов")],
        [KeyboardButton(text="🤖 Поддержка ботов")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True
)

back_only = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)

contact_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📞 Оставить номер/ник")],
        [KeyboardButton(text="👤 Связаться с админом")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)

# ==========================
# Хендлеры
# ==========================
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(OrderForm.choosing_service)
    await message.answer(
        "Добро пожаловать в компанию *Fynx*!\n\n"
        "Мы предлагаем услуги:\n"
        "🌐 Создание сайтов\n"
        "🤖 Создание Telegram-ботов\n"
        "🛡 Поддержка и обеспечение\n\n"
        "Выберите интересующую услугу ниже 👇\n\n"
        "Для прямой связи с админом: @Nonam1n",
        reply_markup=main_menu,
        parse_mode="Markdown"
    )

# ---------- Выбор услуги ----------
@dp.message(OrderForm.choosing_service)
async def choose_service(message: Message, state: FSMContext):
    text = message.text
    if text == "🌐 Создание сайтов":
        await state.update_data(service="Создание сайтов")
        await state.set_state(OrderForm.choosing_subservice)
        await message.answer("Мы создаём разные виды сайтов. Какой вас интересует?", reply_markup=sites_menu)
    elif text == "🤖 Создание Telegram-ботов":
        await state.update_data(service="Создание Telegram-ботов")
        await state.set_state(OrderForm.choosing_subservice)
        await message.answer("Мы разрабатываем разные виды ботов. Какой нужен вам?", reply_markup=bots_menu)
    elif text == "🛡 Поддержка и обеспечение":
        await state.update_data(service="Поддержка и обеспечение")
        await state.set_state(OrderForm.choosing_subservice)
        await message.answer("Выберите направление поддержки:", reply_markup=support_menu)
    else:
        await message.answer("Пожалуйста, используйте кнопки ниже 👇", reply_markup=main_menu)

# ---------- Подуслуга ----------
@dp.message(OrderForm.choosing_subservice)
async def choose_subservice(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.set_state(OrderForm.choosing_service)
        await message.answer("Выберите услугу:", reply_markup=main_menu)
        return
    await state.update_data(subservice=message.text)
    await state.set_state(OrderForm.describing_product)
    await message.answer("Опишите ваш продукт или задачу подробнее ✍️", reply_markup=back_only)

# ---------- Описание продукта ----------
@dp.message(OrderForm.describing_product)
async def describe_product(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.set_state(OrderForm.choosing_subservice)
        data = await state.get_data()
        service = data.get("service")
        if service == "Создание сайтов":
            await message.answer("Выберите вид сайта:", reply_markup=sites_menu)
        elif service == "Создание Telegram-ботов":
            await message.answer("Выберите вид бота:", reply_markup=bots_menu)
        else:
            await message.answer("Выберите направление:", reply_markup=support_menu)
        return
    await state.update_data(description=message.text)
    await state.set_state(OrderForm.leaving_contact)
    await message.answer(
        "Как нам с вами связаться?\nВы можете оставить номер, ник или выбрать контакт через кнопки.",
        reply_markup=contact_menu
    )

# ---------- Контакты ----------
@dp.message(OrderForm.leaving_contact)
async def leaving_contact_handler(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await state.set_state(OrderForm.describing_product)
        await message.answer("Опишите ваш продукт подробнее ✍️", reply_markup=back_only)
        return
    if message.text == "👤 Связаться с админом":
        await message.answer("Вы можете написать напрямую: @Nonam1n")
        return
    if message.text == "📞 Оставить номер/ник":
        await state.set_state(OrderForm.typing_contact)
        await message.answer("Напишите ваш номер или ник:")
        return

# ---------- Ввод контакта ----------
@dp.message(OrderForm.typing_contact)
async def receive_contact(message: Message, state: FSMContext):
    contact = message.text.strip()
    username = f"@{message.from_user.username}" if message.from_user.username else "Без ника"
    await state.update_data(contact=contact, username=username)
    data = await state.get_data()

    text = (
        f"📩 Новая заявка!\n\n"
        f"🛠 Услуга: {data.get('service')}\n"
        f"📌 Подуслуга: {data.get('subservice')}\n"
        f"✍️ Описание: {data.get('description')}\n"
        f"📞 Контакт: {data.get('contact')}\n"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve:{message.from_user.id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{message.from_user.id}")
            ]
        ]
    )
    clients_data[message.from_user.id] = data
    await bot.send_message(ADMIN_ID, text, reply_markup=kb)
    await message.answer("Спасибо! Ваша заявка отправлена администратору ✅")

# ---------- Одобрение/отклонение ----------
@dp.callback_query(F.data.startswith("approve:"))
async def approve_client(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])
    data = clients_data.get(user_id)
    if not data:
        await callback.answer("Данные не найдены.", show_alert=True)
        return
    text = (
        f"✅ Одобрен клиент:\n\n"
        f"🛠 Услуга: {data.get('service')}\n"
        f"📌 Подуслуга: {data.get('subservice')}\n"
        f"✍️ Описание: {data.get('description')}\n"
        f"📞 Контакт: {data.get('contact')}"
    )
    await bot.send_message(GROUP_ID, text)
    await callback.answer("Заявка одобрена и отправлена в группу!")
    await callback.message.edit_text("Заявка была одобрена.")

@dp.callback_query(F.data.startswith("reject:"))
async def reject_client(callback: CallbackQuery):
    await callback.answer("Заявка отклонена.")
    await callback.message.edit_text("Заявка была отклонена администратором.")

# ==========================
# Запуск
# ==========================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
