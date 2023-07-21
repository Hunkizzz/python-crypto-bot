import asyncio
import logging

import requests
from aiogram import Bot, Dispatcher
from aiogram import F, Router
from aiogram import flags
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, ReplyKeyboardRemove
from flask import Flask, request
from keycloak import KeycloakOpenID

import config
import kb
import requests_file
import text
from states import Gen

app = Flask(__name__)
router = Router()

tokens = {}

# Create KeycloakOpenID instance
keycloak_openid = KeycloakOpenID(server_url=config.keycloak_url,
                                 client_id=config.client_id,
                                 realm_name=config.realm,
                                 client_secret_key=config.client_secret)


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
            res = await requests_file.get_crypto_currency(tokens.get(str(msg.from_user.id)), prompt)
            result = await requests_file.format_value_data(res)
    except Exception as e:
        return await mesg.answer(text.gen_error, reply_markup=kb.cancel_kb)
    await mesg.edit_text(result, disable_web_page_preview=True, reply_markup=kb.menu)


async def send_auth_link(message: Message):
    # Generate the authorization URL
    auth_url = keycloak_openid.auth_url(
        redirect_uri=f"{config.app_url}/auth",
        scope="openid",
        state=message.from_user.id
    )

    # Create an InlineKeyboardMarkup with the authorization URL button
    keyboard = [
        [InlineKeyboardButton(text="📝 Authenticate", url=auth_url), ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer("Please authenticate to proceed.", reply_markup=keyboard)


@app.route("/auth")
async def callback_handler():
    code = request.args.get("code")
    state = request.args.get("state")
    session_state = request.args.get("session_state")

    # Process the code, state, and session_state parameters
    # ...
    # Exchange the authorization code for an access token
    # token = keycloak_openid.token(code=code)

    # Step 3: Exchange the authorization code for an access token
    token_endpoint = f"{config.keycloak_url}/realms/{config.realm}/protocol/openid-connect/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": config.client_id,
        "client_secret": config.client_secret,
        "code": code,
        "redirect_uri": f"{config.app_url}/auth"
    }
    response = requests.post(token_endpoint, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        tokens[state] = access_token
        return f"You have been successfully authorized!\n Please close this tab and return to the bot!\n Have a nice day"
    else:
        print(f"Token retrieval failed with status code {response.status_code}")
        return None

    # Extract the JWT token from the token response
    # jwt_token = token.get("access_token")

    return "Callback processed successfully"
    # Get the access token using the authorization code
    # access_token = await get_token(code)

    # Store the access token (JWT) in the state
    # async with state.proxy() as data:
    #     data["jwt"] = access_token

    # await message.answer("Authorization successful. You can now perform actions.")


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
    await send_auth_link(message)
    await message.answer(text.greet.format(name=message.from_user.full_name), reply_markup=kb.menu)


@router.message(F.text == "Меню")
@router.message(F.text == "Выйти в меню")
@router.message(F.text == "◀️ Выйти в меню")
async def menu_handler(msg: Message, state: FSMContext):
    await state.clear()
    await msg.edit_text(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)


async def telegram_bot():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


def flask_app():
    app.run(host="localhost", port=8005)


def main():
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(telegram_bot()),
        loop.run_in_executor(None, flask_app),
    ]
    loop.run_until_complete(asyncio.gather(*tasks))


if __name__ == "__main__":
    main()
