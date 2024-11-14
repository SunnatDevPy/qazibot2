import pandas as pd
from aiogram import Router, html, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, InlineQuery, InlineQueryResultArticle, \
    InputTextMessageContent, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.buttuns.inline import admins
from bot.buttuns.simple import cancel_excel, admin_panel, excel
from db import User, Categorie, Product

admin_router = Router()


class AddAdmin(StatesGroup):
    user_id = State()


class ExcelImportState(StatesGroup):
    file_id = State()


@admin_router.message(F.text.startswith("Excel"))
async def count_book(message: Message):
    await message.answer("Tanlang", reply_markup=excel())


@admin_router.message(F.text == "⬅️Ortga")
async def count_book(message: Message):
    await message.answer("Settings", reply_markup=admin_panel())


@admin_router.message(F.text.in_(["Kategoriya kiritish", "Mahsulot kiritish", "Mahsulot o'zgartirish"]))
async def count_book(message: Message, state: FSMContext):
    text = message.text
    await message.answer("Tanlang", reply_markup=excel())
    if message.from_user.id in [5649321700, 279361769] + [i for i in await User.get_admins()]:
        await state.set_state(ExcelImportState.file_id)
        if text == "Kategoriya kiritish":
            await message.answer("Kategoriyaga tegishli excel fayl yuboring!", reply_markup=cancel_excel())
            await message.answer("Qatorlar ketma ketligi: \n1) id[1-9], \n2) title[salom, world]!")
        elif text == "Mahsulot kiritish":
            await message.answer("Mahxulotga tegishli excel fayl yuboring!", reply_markup=cancel_excel())
            await message.answer(
                "Qatorlar ketma ketligi: \n1) id[1-10000], \n2) category_id[1-1000], \n3) photo[link] bo'lmasa bosh qoldiring, \n4) title[salom], \n5) restoran_price[12000],\n6) optom_price[12000], \n7) type[dona/kg],\n8) description[zo'r mahsulot]: qo'shimcha ma'lumot!")
        elif text == "Mahsulot o'zgartirish":
            await state.update_data(excel=text)
            await message.answer("Mahxulotga tegishli excel fayl yuboring!", reply_markup=cancel_excel())
    else:
        await message.answer(f"Sizda huquq yo'q")


@admin_router.message(ExcelImportState.file_id)
async def count_book(message: Message, state: FSMContext, bot: Bot):
    if message.text == "❌":
        await state.clear()
        await message.answer("Admin panel", reply_markup=admin_panel())
    else:
        data = await state.get_data()
        file_info = await bot.get_file(message.document.file_id)

        file_path = file_info.file_path
        downloaded_file = await bot.download_file(file_path)
        with open("data.xlsx", "wb") as new_file:
            new_file.write(downloaded_file.getvalue())
        df = pd.read_excel('data.xlsx')
        text = ''
        brak = 0
        await message.answer("Bir oz kuting...", reply_markup=ReplyKeyboardRemove())
        for index, row in df.iterrows():
            if row.get('category_id'):
                try:
                    if data.get('excel'):
                        await Product.update(row['id'], category_id=row['category_id'], photo=row['photo'],
                                             title=row['title'], price=row["price"], type=row['type'],
                                             description=row['description'])
                    else:
                        await Product.create(id=row['id'], category_id=row['category_id'], photo=row['photo'],
                                             title=row['title'], price=row["price"], type=row['type'],
                                             description=row['description'])
                except:
                    if data.get('excel'):
                        await Product.update(row['id'], category_id=row['category_id'], photo=None,
                                             title=row['title'], price=row["price"], type=row['type'],
                                             description=row['description'])
                    else:
                        await Product.create(id=row['id'], category_id=row['category_id'], photo=None,
                                             title=row['title'], type=row['type'],
                                             description=row['description'], price=row["price"], )

            else:
                await Categorie.create(id=row['id'], title=row['title'])

                brak += 1
                text += f'{row["id"]}, '
        else:
            if brak != 0:
                await message.answer(text + "idlar zaynit", reply_markup=admin_panel())
            else:
                if data.get('excel'):
                    await message.answer("Muvoffaqiyatli o'zgartirildi", reply_markup=admin_panel())
                else:
                    await message.answer("Muvoffaqiyatli yuklandi", reply_markup=admin_panel())
        await state.clear()


@admin_router.callback_query(F.data.startswith('admins_'))
async def delete_admins(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_')
    await call.answer()
    if data[1] == 'add':
        await call.message.delete()
        await state.set_state(AddAdmin.user_id)
        await call.message.answer(html.bold("User idni kiriting"), parse_mode='HTML')
    if data[1] == 'delete':
        try:
            await User.update(id_=int(data[-1]), is_admin=False)
            await call.message.edit_text(html.bold("Adminlar ro'yxati"), parse_mode='HTML', reply_markup=await admins())
        except:
            await call.message.answer('Xatolik yuz berdi')
    if data[1] == 'back':
        await call.message.delete()
        await call.message.answer(html.bold("Admin panel"), parse_mode='HTML', reply_markup=admin_panel())


@admin_router.message(AddAdmin.user_id)
async def add_admin(call: Message, state: FSMContext):
    try:
        user = await User.get(int(call.text))
        if user:
            text = html.bold(f'''
#Admin qo'shildi
chat_id: <code>{user.id}</code>
Username: <code>@{user.username}</code>
                ''')
            await User.update(id_=user.id, is_admin=True)
            await call.answer(text, parse_mode='HTML')
            await call.answer(html.bold("Adminlar ro'yxati"), parse_mode='HTML', reply_markup=await admins())
        else:
            await call.answer(html.bold("Bunaqa id li user yo'q, bo'tga /start bergan bo'lish kerak"),
                              parse_mode='HTML')
    except:
        await call.answer(html.bold("Id kiritmadingiz"), parse_mode='HTML')
        await call.answer(html.bold("Adminlar ro'yxati"), parse_mode='HTML', reply_markup=await admins())
    await state.clear()


ITEMS_PER_PAGE = 10


# @admin_router.inline_query()
# async def inline_query_handler(inline_query: InlineQuery, bot: Bot):
#     query = inline_query.query  # Текст, который ввел пользователь
#     offset = int(inline_query.offset) if inline_query.offset else 0
#     user = await User.get(inline_query.from_user.id)
#     products = await Product.get_all()
#     paginated_products = products[offset:offset + ITEMS_PER_PAGE]
#     results = [
#         InlineQueryResultArticle(
#             id=str(i.id),
#             title=str(i.title),
#             description=f"Narxi: {str(i.optom_price) if user.idora_turi == 'Optom' else str(i.restoran_price)}",
#             input_message_content=InputTextMessageContent(
#                 message_text=f"{i.title}\n{str(i.optom_price) if user.idora_turi == 'Optom' else str(i.restoran_price)}\n{i.description}")
#         ) for i in paginated_products
#     ]
#     next_offset = str(offset + ITEMS_PER_PAGE) if offset + ITEMS_PER_PAGE < len(products) else ""
#     await bot.answer_inline_query(inline_query.id, results=results, cache_time=1, next_offset=next_offset)

def inls(id_):
    ikb = InlineKeyboardBuilder()
    ikb.row(InlineKeyboardButton(text="Buyurtma berish", callback_data=f"product_{id_}"))
    return ikb.as_markup()


@admin_router.inline_query()
async def inline_query_handler(inline_query: InlineQuery, bot: Bot):
    query = inline_query.query.strip().lower()  # Получаем и обрабатываем текст, который ввел пользователь
    offset = int(inline_query.offset) if inline_query.offset else 0
    user = await User.get(inline_query.from_user.id)

    # Получаем все продукты
    products = await Product.get_all()

    # Если введен текст запроса, фильтруем продукты по названию или описанию
    if query:
        products = [product for product in products if
                    query in product.title.lower() or query in product.description.lower()]

    # Применяем пагинацию
    paginated_products = products[offset:offset + ITEMS_PER_PAGE]

    # Формируем результаты инлайн-ответа
    results = [
        InlineQueryResultArticle(
            id=str(i.id),
            title=str(i.title),
            description=f"Narxi: {str(i.price)}",
            input_message_content=InputTextMessageContent(
                message_text=f"{i.title}\n{str(i.price)}\n{i.description}"),
            # reply_markup=inls(i.id)
        ) for i in paginated_products
    ]

    # Определяем следующий offset, если есть еще данные
    next_offset = str(offset + ITEMS_PER_PAGE) if offset + ITEMS_PER_PAGE < len(products) else ""

    await bot.answer_inline_query(inline_query.id, results=results, cache_time=1, next_offset=next_offset)
