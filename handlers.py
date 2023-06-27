from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram import flags
from aiogram.fsm.context import FSMContext
from states import Gen

import kb
import text
import requests_file

router = Router()


@router.callback_query(F.data == "get_crypto_currency")
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.waiting_for_cryptocurrency)
    await clbck.message.edit_text(text.gen_crypto)
    await clbck.message.answer(text.gen_exit, reply_markup=kb.iexit_kb)


@router.message(Gen.waiting_for_cryptocurrency)
@flags.chat_action("typing")
async def generate_text(msg: Message, state: FSMContext):
    prompt = msg.text
    if(prompt.__contains__("меню")):
        await state.clear()
        return await menu_handler(prompt, state)
    try:
        mesg = await msg.answer(text.gen_wait)
        res = await requests_file.get_crypto_currency(prompt)
        result = await requests_file.format_value_data(res)
    except Exception as e:
        return await mesg.edit_text(text.gen_error, reply_markup=kb.iexit_kb)
    await mesg.edit_text(result, disable_web_page_preview=True)


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)


@router.message(F.text == "Меню")
@router.message(F.text == "Выйти в меню")
@router.message(F.text == "◀️ Выйти в меню")
@router.message(Command(commands=["menu"]))
async def menu_handler(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(text.menu, reply_markup=kb.menu)
