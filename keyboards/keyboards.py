from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon import LEXICON_EN

# ------- Создаем клавиатуру через ReplyKeyboardBuilder -------

# Создаем кнопки с ответами согласия и отказа
button_yes = KeyboardButton(text=LEXICON_EN['yes_button'])
button_no = KeyboardButton(text=LEXICON_EN['no_button'])

# Инициализируем билдер для клавиатуры с кнопками "Давай" и "Не хочу!"
yes_no_builder = ReplyKeyboardBuilder()

# Добавляем кнопки в билдер с аргументом width=2
yes_no_builder.row(button_yes, button_no, width=2)

# Создаем клавиатуру с кнопками "Давай!" и "Не хочу!"
yes_no: ReplyKeyboardMarkup = yes_no_builder.as_markup(
    # one_time_keyboard=True,
    resize_keyboard=True
)

kb_month = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Current'), KeyboardButton(text='Previous')]],
    resize_keyboard=True,
    # one_time_keyboard=True
)

kb_search = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Search!'), KeyboardButton(text='Remake')]],
    resize_keyboard=True,
    one_time_keyboard=True
)


# # Создаем объекты инлайн-кнопок
# url_button_1 = InlineKeyboardButton(
#     text='Курс "Телеграм-боты на Python и AIOgram"',
#     url='https://stepik.org/120924'
# )
# url_button_2 = InlineKeyboardButton(
#     text='Документация Telegram Bot API',
#     url='https://core.telegram.org/bots/api'
# )
#
# # Создаем объект инлайн-клавиатуры
# keyboard = InlineKeyboardMarkup(
#     inline_keyboard=[[url_button_1],
#                      [url_button_2]]
# )


# Функция для генерации инлайн-клавиатур "на лету"
def create_pg_inline_kb(*args: str,
                        **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons_pg: list[InlineKeyboardButton] = []
    buttons_num: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons_pg.append(InlineKeyboardButton(
                text=LEXICON_EN[button] if button in LEXICON_EN else button,
                callback_data=button))

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons_pg, width=3)

    if kwargs:
        for button, text in kwargs.items():
            buttons_num.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

    # Распаковываем список с кнопками второго ряда в билдер методом row c параметром width
    kb_builder.row(*buttons_num)

    favorits_btn = '⭐ Favorites ⭐'
    kb_builder.row(InlineKeyboardButton(
                    text=favorits_btn,
                    callback_data=favorits_btn))

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


back_btn = InlineKeyboardButton(
    text='Back',
    callback_data='Back')

add_btn = InlineKeyboardButton(
    text='Add to Favorities',
    callback_data='add_fav')


def create_nums_inline_kb(url: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    link_btn = InlineKeyboardButton(
        text='ADS Link',
        url=url)

    kb_builder.row(*[link_btn, add_btn, back_btn], width=1)

    return kb_builder.as_markup()
