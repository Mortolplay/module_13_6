from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = KeyboardButton(text='Рассчитать')
button_2 = KeyboardButton(text='Информация')
kb.add(button_1)
kb.add(button_2)

ikb = InlineKeyboardMarkup()
i_button_1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
i_button_2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
ikb.row(i_button_1, i_button_2)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(text='Рассчитать')
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=ikb)

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5;'
                              'для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161.')
    await call.answer()

@dp.message_handler(text='Привет')
async def start(message):
    await message.answer(f'Привет! Я бот помогающий Вашему здоровью.\n'
                         f'Чтобы начать, нажмите "Рассчитать"', reply_markup=kb)

@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()
    await call.answer()

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer(f'Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer(f'Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])

    calories_m = 10 * weight + 6.25 * growth - 5 * age + 5
    calories_w = 10 * weight + 6.25 * growth - 5 * age - 161

    global a
    global g
    global w
    global c_m
    global c_w
    a = age
    g = growth
    w = weight
    c_m = calories_m
    c_w = calories_w
    await message.answer('Расчёт произведён, посмотрите информацию')

    @dp.message_handler(text='Информация')
    async def inform(message):
        await message.answer(f'Ваш возраст:  {a}\nВаш рост:      {g}\nВаш вес:          {w}\n'
                             f'Ваша норма калорий: {c_m}, если вы мужчина\n    '
                             f'                                      {c_w}, если вы женщина')

    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
