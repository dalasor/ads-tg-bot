from copy import deepcopy

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from keyboards.keyboards import *
from services.services import *
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
from database.database import user_dict_template, users_db

# Инициализируем роутер уровня модуля
router = Router()


# Этот хэндлер будет срабатывать на команду "/start"
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_EN['/start'])
    if message.from_user.id not in users_db:
        users_db[message.from_user.id] = deepcopy(user_dict_template)


# Этот хэндлер будет срабатывать на команду "/help"
@router.message(Command(commands=['help']))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_EN['/help'])


@router.message(Command(commands=['search']))
async def process_search_articles(message: Message):
    await message.answer(text=LEXICON_EN['/search'], reply_markup=yes_no)


@router.message(F.text == '✅')
async def process_yeap_answer(message: Message):
    await message.answer(text='Choose the month', reply_markup=kb_month)


@router.message(F.text == '❌')
async def process_no_answer(message: Message):
    await message.answer(text='Ok, honey')


@router.message(F.text == 'Current')
async def process_current_month(message: Message):
    cur_month = datetime.now().strftime('%Y-%m')
    users_db[message.from_user.id]['query'] = simple_query(f'pubdate:[{cur_month} TO {cur_month}]')
    await message.answer(text=f'Your query now:\n\n {users_db[message.from_user.id]["query"]}', reply_markup=kb_search)


@router.message(F.text == 'Previous')
async def process_prev_month(message: Message):
    pre_month = (datetime.now() + relativedelta(months=-1)).strftime('%Y-%m')
    users_db[message.from_user.id]['query'] = simple_query(f'pubdate:[{pre_month} TO {pre_month}]')
    await message.answer(text=f'Your query now:\n\n {users_db[message.from_user.id]["query"]}', reply_markup=kb_search)


@router.message(F.text == 'Search!')
async def process_main_search(message: Message):
    bibcodes = search_ads(q=users_db[message.from_user.id]['query'])
    bibcodes = check_bibcodes(bibcodes=bibcodes)

    n = len(bibcodes)
    r = n % 5
    d = n // 5 + (r != 0)

    users_db[message.from_user.id]['current_page'] = 1
    users_db[message.from_user.id]['total_pages'] = d
    users_db[message.from_user.id]['residue'] = r

    if d == 1:
        if n == 5:
            end_ind = n
        else:
            end_ind = r
    else:
        end_ind = 5

    articles = export_ads(bibcodes=bibcodes)
    names, urls, arxivs, abstracts = parse_info(articles)

    users_db[message.from_user.id]['names'] = names
    users_db[message.from_user.id]['urls'] = urls
    users_db[message.from_user.id]['arxivs'] = arxivs
    users_db[message.from_user.id]['abstracts'] = abstracts

    n_btns = {str(v): str(v) for v in [i for i in range(1, end_ind + 1)]}

    await message.answer(text=LEXICON_EN['founded'].format(n))
    text = '\n\n'.join([f'<b>[<u>{str(i + 1)}</u>]</b> ' + name for i, name in enumerate(names[:end_ind])])
    await message.answer(text=text,
                         parse_mode=ParseMode.HTML,
                         reply_markup=create_pg_inline_kb('backward',
                                                          f'{users_db[message.from_user.id]["current_page"]}/{d}',
                                                          'forward',
                                                          **n_btns)
                         )


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
# во время взаимодействия пользователя с сообщением-книгой
@router.callback_query(F.data == 'forward')
async def process_forward_press(callback: CallbackQuery):
    if users_db[callback.from_user.id]['current_page'] < users_db[callback.from_user.id]['total_pages']:
        users_db[callback.from_user.id]['current_page'] += 1

        text, n_btns = text_builder(callback.from_user.id)

        await callback.message.edit_text(
            text=text,
            reply_markup=create_pg_inline_kb('backward',
                                             f'{users_db[callback.from_user.id]["current_page"]}/'
                                             f'{users_db[callback.from_user.id]["total_pages"]}',
                                             'forward',
                                             **n_btns)
        )
    await callback.answer()


# Этот хэндлер будет срабатывать на нажатие инлайн-кнопки "вперед"
# во время взаимодействия пользователя с сообщением-книгой
@router.callback_query(F.data == 'backward')
async def process_backward_press(callback: CallbackQuery):
    if users_db[callback.from_user.id]['current_page'] > 1:
        users_db[callback.from_user.id]['current_page'] -= 1

        text, n_btns = text_builder(callback.from_user.id)

        await callback.message.edit_text(
            text=text,
            reply_markup=create_pg_inline_kb('backward',
                                             f'{users_db[callback.from_user.id]["current_page"]}/'
                                             f'{users_db[callback.from_user.id]["total_pages"]}',
                                             'forward',
                                             **n_btns)
        )
    await callback.answer()


# Хэндлер, реагирующий на выбор номера
@router.callback_query(F.data.isdigit())
async def process_digit_press(callback: CallbackQuery):
    ind = int(callback.data) - 1
    name = users_db[callback.from_user.id]['names'][ind]
    arxiv = users_db[callback.from_user.id]['arxivs'][ind]
    url = users_db[callback.from_user.id]['urls'][ind]
    abstract = users_db[callback.from_user.id]['abstracts'][ind]
    text = name + '\n\n<code>' + arxiv + '</code>\n\n' + '<b>Abstract</b>: ' + clean_latex(abstract)

    await callback.message.edit_text(
        text=text,
        reply_markup=create_nums_inline_kb(url)
    )



@router.callback_query(F.data == 'Back')
async def process_back_press(callback: CallbackQuery):
    text, n_btns = text_builder(callback.from_user.id)
    await callback.message.edit_text(
        text=text,
        reply_markup=create_pg_inline_kb('backward',
                                         f'{users_db[callback.from_user.id]["current_page"]}/'
                                         f'{users_db[callback.from_user.id]["total_pages"]}',
                                         'forward',
                                         **n_btns)
    )


# @router.callback_query(F.data == 'add_fav')
# async def process_favorite_press(callback: CallbackQuery):
#