from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class NumbersCallFactory(CallbackData, prefix="fabnum"):
    module: str
    value: str
    action: str


def make_inline_keyboard_double(par: dict[str], module, action):
    keyboard_builder = InlineKeyboardBuilder()

    for text_but, val_but in par.items():
        keyboard_builder.button(text=text_but,
                                callback_data=NumbersCallFactory(module=module,
                                                                 value=f'{module}_{val_but}',
                                                                 action=action))
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()


def make_inline_keyboard(par: dict[str], module, action="switch"):
    keyboard_builder = InlineKeyboardBuilder()

    for text_but, val_but in par.items():
        keyboard_builder.button(text="🔵 "+text_but,
                                callback_data=NumbersCallFactory(module=module, value=val_but, action=action))
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()
