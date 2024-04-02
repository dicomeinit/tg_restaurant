import datetime

from decimal import Decimal
from os import getenv

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InputMediaPhoto, KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.markdown import hbold

from bot_restaurant.api import ApiClient


TOKEN = getenv("BOT_TOKEN")

form_router = Router()

api_client = ApiClient(base_url="http://127.0.0.1:8000")


class Form(StatesGroup):
    menu = State()
    first = State()
    second = State()
    drink = State()
    quantity = State()
    check_user_order = State()
    check_user_order_second = State()
    phone = State()
    order = State()
    items = State()


def message_product_builder(product):
    return f"{hbold(product['name'])}\n" f"{product['description']}\n" f"Ціна: {product['price']} грн"


def message_products_builder(products):
    return "\n".join([message_product_builder(product) for product in products])


def message_menu_builder(menu):
    return (
        f"{hbold(menu['name'])}\n"
        f"{menu['date']}\n"
        f"Страви: {', '.join([product['name'] for product in menu['products']])}"
    )


def items_message_builder(items):
    result_array = []
    for item in items:
        name = item["name"]
        quantity = item["quantity"]
        product_price = Decimal(item["product_price"])
        total_price = quantity * product_price
        result_array.append(f"{name} [{quantity} шт.] x {product_price} = {total_price}")
    return "\n".join(result_array)


@form_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привіт, {hbold(message.from_user.full_name)}! "
        f"Це бот для замовлення їжі. Будь ласка, оберіть страву, яку хочете замовити."
    )
    await get_product_categories(message)


async def get_product_categories(message: Message):
    menu = await api_client.get_menu()
    if not menu:
        await message.answer("Меню тимчасово недоступне, спробуйте пізніше. Для перезапуску натисніть /start")
        return
    await message.answer(message_menu_builder(menu[0]))
    await message.answer(
        f"Оберіть, що ви хочете: {hbold('Перше')}, {hbold('Друге')}, {hbold('Напої')}.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Перше"),
                    KeyboardButton(text="Друге"),
                    KeyboardButton(text="Напої"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )


@form_router.message(Form.check_user_order)
async def check_user_order(message: Message, state: FSMContext):
    quantity = message.text
    await state.update_data(quantity=quantity)
    await message.answer(
        "Бажаєте ще щось замовити?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Так"),
                    KeyboardButton(text="Ні"),
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )
    await state.set_state(Form.check_user_order_second)


@form_router.message(Form.check_user_order_second)
async def check_user_order_second(message: Message, state: FSMContext):
    data = await state.get_data()
    product_name = data.get("product_name")
    quantity = data.get("quantity")
    items = data.get("items", [])
    items.append({"name": product_name, "quantity": quantity})
    await state.update_data(items=items)
    if message.text == "Так":
        await get_product_categories(message)
        await state.set_state(Form.menu)
    else:
        await phone_handler(message, state)


async def products_handler(message: Message, state: FSMContext, product_type: str) -> None:
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    products = await api_client.get_products(product_type=product_type, date=date)
    if not products:
        await message.answer("Відсутні страви за вашим запитом =(")
        await state.set_state(Form.menu)
        await get_product_categories(message)
        return
    await message.reply_media_group(
        media=[InputMediaPhoto(media=product["image_url"], caption=product["name"]) for product in products]
    )

    await message.answer(
        message_products_builder(products),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=product["name"]) for product in products]],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )
    await state.set_state(Form.quantity)


@form_router.message(F.text == "Перше")
async def first_handler(message: Message, state: FSMContext) -> None:
    await products_handler(message, state, "first")


@form_router.message(F.text == "Друге")
async def second_handler(message: Message, state: FSMContext) -> None:
    await products_handler(message, state, "second")


@form_router.message(F.text == "Напої")
async def second_handler(message: Message, state: FSMContext) -> None:
    await products_handler(message, state, "drink")


@form_router.message(Form.quantity)
async def quantity_handler(message: Message, state: FSMContext) -> None:
    product_name = message.text
    await state.update_data(product_name=product_name)
    await message.answer("Скільки порцій ви хочете замовити?")
    await state.set_state(Form.check_user_order)


async def phone_handler(message: Message, state: FSMContext) -> None:
    contact_keyboard = KeyboardButton(text="Поділитись номером телефону", request_contact=True)
    await message.answer(
        "Надішліть ваш номер телефону",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[contact_keyboard]],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )
    await state.set_state(Form.order)


@form_router.message(Form.order)
async def order_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    items = data.get("items")
    phone = message.contact.phone_number
    user_id = message.from_user.id
    items_for_order = []
    for item in items:
        product = await api_client.get_product(item["name"])
        items_for_order.append({"product": product["id"], "quantity": item["quantity"]})

    order = {"items": items_for_order, "user_id": user_id, "username": message.from_user.full_name, "phone": phone}
    result = await api_client.create_order(order)
    await message.answer(
        f"Замовлення створено!\n"
        f"Номер: #{result['order_id']} Сума замовлення: {result['total_price']}.\n"
        f"-------------------------------------------\n"
        f"{items_message_builder(result['items'])}\n\n"
        f"Дякуємо за замовлення! Оператор зв'яжеться з вами найближчим часом.\n\n"
        f"Для продовження натисніть /start",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.clear()
