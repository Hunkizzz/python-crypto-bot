from aiogram import F, Router, types
from aiogram.filters import Command, Text
from aiogram.types import Message, CallbackQuery
from aiogram import flags
from aiogram.fsm.context import FSMContext

from states import Gen
from aiogram.types import Message, ReplyKeyboardRemove

import kb
import text
import requests_file

router = Router()


@router.callback_query(F.data == "get_crypto_currency")
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.waiting_for_cryptocurrency)
    await clbck.message.edit_text(text.gen_crypto)
    await clbck.message.answer(text.gen_exit, reply_markup=kb.cancel_kb)


@router.message(Gen.waiting_for_cryptocurrency)
@flags.chat_action("typing")
async def generate_text(msg: Message, state: FSMContext):
    prompt = msg.text
    try:
        mesg = await msg.answer(text.gen_wait)
        if prompt.casefold() == "cancel":
            await cancel_handler(mesg, state)
            return
        else:
            res = await requests_file.get_crypto_currency(prompt)
            result = await requests_file.format_value_data(res)
    except Exception as e:
        return await mesg.answer(text.gen_error, reply_markup=kb.cancel_kb)
    await mesg.edit_text(result, disable_web_page_preview=True, reply_markup=kb.menu)


@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        text="Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(text.menu, reply_markup=kb.menu)


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Gen.default)
    await message.answer(
        text=text.menu,
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(text.greet.format(name=message.from_user.full_name), reply_markup=kb.menu)


@router.message(F.text == "Меню")
@router.message(F.text == "Выйти в меню")
@router.message(F.text == "◀️ Выйти в меню")
async def menu_handler(msg: Message, state: FSMContext):
    await state.clear()
    await msg.edit_text(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)
