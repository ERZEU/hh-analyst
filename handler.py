import asyncio
import json
from contextlib import suppress
from datetime import time, datetime
from aiogram import Router, flags
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram import F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram import types
from aiogram.methods.send_message import SendMessage
from aiogram.utils.chat_action import ChatActionSender
from main import bot
from keyboards import make_inline_keyboard_double, NumbersCallFactory, make_inline_keyboard
from controller import *

router = Router()
module = "parse"


class StateCls(StatesGroup):
    name_vac_state = State()
    name_reg_state = State()


change_variable = {
    "График з/п": "1",
    "График з/п по регионам": "2",
    "Гистограмма навыков": "3",
    "Диаграмма регионов": "4",
    "Сохранить в xlsx": "5"
}


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    if message.from_user.id == message.chat.id:
        await message.answer(text="Привет! Давай начнем с названия вакансии. "
                                  "\nВведи слово или предложение для поиска по полю 'НАЗВАНИЕ ВАКАНСИИ'...")
        await state.set_state(StateCls.name_vac_state)


@router.message(StateCls.name_vac_state)
async def stage(message: Message, state: FSMContext):
    await state.update_data(name_vac=message.text)
    await message.answer(text="Отлично! Теперь укажи регион, в котором нужно искать...")
    await state.set_state(StateCls.name_reg_state)


@router.message(StateCls.name_reg_state)
async def stage(message: Message, state: FSMContext):
    await state.update_data(name_reg=message.text)
    data = await state.get_data()
    await message.answer(text=f'Мне нужно найти вакансии по параметрам:'
                              f'\n Название вакансии: {data["name_vac"]}'
                              f'\n Регион: {data["name_reg"]}'
                              f'\n Все верно?',
                         reply_markup=make_inline_keyboard_double(par={"Да": "cfn", "Отмена": "cnl"},
                                                                  module=module,
                                                                  action="complete"))


@router.callback_query(NumbersCallFactory.filter(F.value == f'{module}_cfn'))
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="Ищу подходяшие вакансии...")
    async with ChatActionSender.typing(bot=bot, chat_id=callback.message.chat.id):
        data = await state.get_data()
        df = get_vac(name_vac=data["name_vac"], name_area=data["name_reg"])
        await state.update_data(df=df)
        # obj_fun.save(mas_vac=df)
        # result = FSInputFile('vacancies.xlsx')
        await callback.message.edit_text(text="Кажется я что-то нашел!")
        # await callback.message.answer_document(result)
        #
        # obj_fun.graph_zp(df)
        # zp = FSInputFile('saved.png')
        # await callback.message.answer_photo(zp)
    await callback.message.answer(text="Выберите действие...",
                                  reply_markup=make_inline_keyboard(change_variable, module))


@router.callback_query(NumbersCallFactory.filter(F.value == "1"))
async def stage(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    graph_zp(data["df"])
    zp = FSInputFile('1.png')
    await callback.message.answer_photo(zp)


@router.callback_query(NumbersCallFactory.filter(F.value == "2"))
async def stage(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    graph_zp_region(data["df"])
    zp = FSInputFile('2.png')
    await callback.message.answer_photo(zp)


@router.callback_query(NumbersCallFactory.filter(F.value == "3"))
async def stage(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    graph_names(data["df"])
    zp = FSInputFile('3.png')
    await callback.message.answer_photo(zp)


@router.callback_query(NumbersCallFactory.filter(F.value == "4"))
async def stage(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    graph_region(data["df"])
    zp = FSInputFile('4.png')
    await callback.message.answer_photo(zp)


@router.callback_query(NumbersCallFactory.filter(F.value == "5"))
async def stage(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    save(data["df"])
    zp = FSInputFile('vacancies.xlsx')
    await callback.message.answer_document(zp)


@router.callback_query(NumbersCallFactory.filter(F.value == f'{module}_cnl'))
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(text="Как скажешь! если вновь понадоблюсь введи команду /start ")
