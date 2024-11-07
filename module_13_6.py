from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

api = "..."
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

# kb = ReplyKeyboardMarkup(resize_keyboard=True)
# button_calc = KeyboardButton(text='Рассчитать')
# button_info = KeyboardButton(text='Информация')
# kb.add(button_calc)
# kb.add(button_info)
inline_keyboard = InlineKeyboardMarkup(row_width=1)
button_calories = InlineKeyboardButton("Рассчитать норму калорий", callback_data='calories')
button_formulas = InlineKeyboardButton("Формулы расчёта", callback_data='formulas')
inline_keyboard.add(button_calories, button_formulas)


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.', reply_markup=inline_keyboard)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(text='Рассчитать')
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=inline_keyboard)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    formula_message = (
        "Формула Миффлина-Сан Жеора:\n"
        "Для мужчин:\n"
        "BMR = 10 * Вес(кг) + 6.25 * Рост(см) - 5 * Возраст(г) + 5\n"
        "Для женщин:\n"
        "BMR = 10 * Вес(кг) + 6.25 * Рост(см) - 5 * Возраст(г) - 161")
    await call.message.answer(formula_message)


@dp.callback_query_handler(text='calories')
async def set_age(call: types.CallbackQuery):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state: FSMContext):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state: FSMContext):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])
    bmr = 10 * weight + 6.25 * growth - 5 * age + 5
    # Формула Миффлина - Сан Жеора для расчета калорий (применим для мужчин)
    await message.answer(f'Ваша норма калорий: {bmr:.2f} ккал в день.')
    await state.finish()


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
