import os
import random
import string

from aiogram import types
from aiogram.types import InputFile

from bot.states import States
from model.predictor import model
from utils import messages, utils


async def welcome(msg: types.Message):
    await States.work.set()
    await msg.answer(messages.start)
    await msg.answer(messages.user_agreement, reply_markup=utils.form_reply_keyboard(["Да", "Нет"]))


async def user_agreement(msg: types.Message):
    if msg.text != "Да":
        await msg.reply(messages.error, reply_markup=utils.form_reply_keyboard(["Да", "Нет"]))
    else:
        await States.image.set()
        await msg.answer(messages.image)


async def image_handler(msg: types.Message):
    if msg.photo:
        images = msg.photo[-1]
    else:
        images = msg.document
    if isinstance(images, list):
        images = images[-1]

    path_to_none_edit_image = os.path.join('images', f"{msg.from_user.id}.jpeg")

    await images.download(path_to_none_edit_image)

    prediction = model(utils.prepare_image(path_to_none_edit_image))

    await msg.reply(messages.prediction.format(prediction), reply_markup=types.ReplyKeyboardRemove())

    await msg.reply_photo(caption=messages.describe, photo=InputFile(
        path_or_bytesio=path_to_none_edit_image  # Change to path to edited photo
    ))

    await msg.answer(messages.validating, reply_markup=utils.form_reply_keyboard(['Да', 'Нет', 'Не знаю']))

    await States.validating.set()


async def validating_answer_of_model(msg: types.Message):
    if msg.text == 'Да':
        await msg.reply(messages.ok)
        await msg.answer(messages.image)
        await States.image.set()
        os.remove(os.path.join('images', f"{msg.from_user.id}.jpeg"))
    elif msg.text == 'Не знаю':
        await msg.answer(messages.image)
        await States.image.set()
        os.remove(os.path.join('images', f"{msg.from_user.id}.jpeg"))
    else:
        await msg.reply(messages.non_ok, reply_markup=utils.form_reply_keyboard([
            'NonDemented', 'VeryMildDemented', 'MildDemented', 'ModerateDemented']
        ))
        await States.correcting.set()


async def correcting_answer_from_model(msg: types.Message):
    await States.image.set()

    match msg.text:
        case 'NonDemented':
            derictory = os.path.join('newData', 'NonDemented')
        case 'VeryMildDemented':
            derictory = os.path.join('newData', 'VeryMildDemented')
        case 'MildDemented':
            derictory = os.path.join('newData', 'MildDemented')
        case 'ModerateDemented':
            derictory = os.path.join('newData', 'ModerateDemented')
        case _:
            return

    rand_token = ''.join(random.choice(string.ascii_lowercase) for i in range(12))
    os.replace(os.path.join('images', f"{msg.from_user.id}.jpeg"),
               os.path.join(derictory, f"{rand_token}.jpeg"))

    await msg.reply(messages.SberSpasibo)
    await msg.answer(messages.image)
