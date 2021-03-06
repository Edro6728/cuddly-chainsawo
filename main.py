import asyncio
import os

import pyrogram
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from tortoise import Tortoise

from models import bannedUser

try:
    from dotenv import load_dotenv

    load_dotenv()
except:
    pass

try:
    API_ID = os.environ["18403498"]

    API_HASH = os.environ["2c0b01283b1b67f7087a92cc81cd91f8"]

    TOKEN = os.environ["5189783350:AAFvjgai8wPU3uVMEiNmEZeTMW3KOtHUzFw"]

    CHANNEL_ID = os.environ["-1001308022020"]

    ADMIN_GROUP = int(os.environ["5269789045"])

    DATABASE_URL = os.environ["DATABASE_URL"]
except Exception as e:
    print("config not set", e)
    exit()

bot = pyrogram.Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)

start_message = """
Hola, bienvenido al bot de Confesiones. π

Puede contactarnos por este bot.
"""

accepted_message = """
Felicidades!! π, su confesion ha sido aceptada por la administracion π y sera publicada pronto en el respectivo canal. π
"""

cancelled_message = """
Lo sentimos π su confesion ha sido rechazada, mejor suerte la proxima. π
"""

about_text = """
This bot was created by @Unknown_user_2386 for entertainment purpose of S3KAIπ­EXTRA channel.
GitHub repo: https://github.com/Christian0510/ConfBot
"""

required_len_not_reached = """
Lo sentimos, su confesion no alcanza la cantidad de caracteres minimos requeridos. (x>20)
"""

banned_message = """
Ha sido baneado del uso del bot, contacte con la administracion para apelar
"""

unbanned_message = """
Ha sido desbaneado
"""


@bot.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply(start_message)


@bot.on_message(filters.command("about"))
async def about(_, message: Message):
    await message.reply(about_text, parse_mode=None)


@bot.on_message(filters.command("info"))
async def info(_, message: Message):
    await message.reply(
        f"Chat ID: {message.chat.id}\n Message ID: {message.message_id}"
    )


@bot.on_message(filters.command("help") & filters.channel)
async def channel_help(_, message: Message):
    await message.reply(f"`{message.chat.id}`")


@bot.on_callback_query()
async def response(_, callback_query: CallbackQuery):
    option, user_id = callback_query.data.split("_")
    user_id = int(user_id)
    type = callback_query.message.media

    if option == "accepted":
        if type == "photo":
            channel_message = await callback_query.message.copy(
                CHANNEL_ID,
                f"{callback_query.message.caption}\nπ€ @{(await bot.get_me()).username}\n Main Channel: @Anime_S3kai",
                reply_markup=None,
            )
        elif type == "voice":
            channel_message = await callback_query.message.copy(
                CHANNEL_ID,
                f"π€ @{(await bot.get_me()).username}\n Main Channel: @Anime_S3kai",
                reply_markup=None,
            )
        else:
            channel_message = await bot.send_message(
                CHANNEL_ID,
                f"{callback_query.message.text}\nπ€ @{(await bot.get_me()).username}\n Main Channel: @Anime_S3kai",
                reply_markup=None,
            )
        await callback_query.message.edit(
            text=f"t.me/{CHANNEL_ID[1:]}/{channel_message.message_id}",
            reply_markup=None,
        )
        await bot.send_message(user_id, accepted_message)
        return

    elif option == "cancelled":
        await bot.send_message(user_id, cancelled_message)

    elif option == "unban":
        banned = await bannedUser.filter(user_id=int(user_id)).first()
        await banned.delete()
        await callback_query.message.edit("User unbanned", reply_markup=None)
        await bot.send_message(user_id, unbanned_message)
        return

    await callback_query.message.edit(
        text="Done",
        reply_markup=None,
    )


@bot.on_message(filters.private & ~filters.sticker)
async def send_message(_, message: Message):
    user_id = message.chat.id

    banned = await bannedUser.filter(user_id=int(user_id)).first()

    if banned:
        await message.reply(banned_message)
        return

    if message.text and len(message.text) < 20:
        await message.reply(required_len_not_reached)
        return

    await message.copy(
        ADMIN_GROUP,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Aceptar", callback_data=f"accepted_{user_id}"
                    ),
                    InlineKeyboardButton(
                        "Cancelar", callback_data=f"cancelled_{user_id}"
                    ),
                ]
            ]
        ),
    )


@bot.on_message(filters.command("banano"))
async def banano(_, message: Message):
    message = message.reply_to_message

    user_id = int(
        message.reply_markup.inline_keyboard[0][0].callback_data.split("_")[1]
    )

    banned = bannedUser(user_id=int(user_id))
    await banned.save()
    await message.edit(
        f"{message.text[:4000]}\n\n`Banned user`",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Unban",
                        callback_data=f"unban_{user_id}",
                    ),
                ]
            ]
        ),
    )
    await bot.send_message(user_id, banned_message)


@bot.on_message(filters.command(["respond"]))
async def respond_to_user(_, message: Message):

    try:
        args = message.text.split(None, 1)[1]
        user_id = int(
            message.reply_to_message.reply_markup.inline_keyboard[0][
                0
            ].callback_data.split("_")[1]
        )
        await bot.send_message(user_id, text=args)
    except IndexError:
        await message.reply("Por favor agrega los argumentos XD so Juan.")
    except AttributeError:
        await message.reply(
            "Responde al mensaje del usuario que quieres responder animal π€§"
        )

    await message.reply("Se ha enviado su respuesta exitosamente.")


async def init():
    # Here we connect to a SQLite DB file.
    # also specify the app name of "models"
    # which contain models from "app.models"
    await Tortoise.init(
        db_url=DATABASE_URL.replace("postgresql://", "postgres://", 1),
        modules={"models": ["models"]},
    )
    # Generate the schema
    await Tortoise.generate_schemas(safe=True)


if __name__ == "__main__":
    print("Bot started")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
    bot.run()
