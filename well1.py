from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
from openai import OpenAI

# Установите свой API-ключ OpenAI
client = OpenAI(api_key='')

# Инициализация бота и диспетчера
TOKEN = ""
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

# Определение состояний
class UserStates(StatesGroup):
    chat = State()

# Функция для получения ответа от GPT-4
def get_chatgpt_response(messages):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content

# Обработчик команды /start
@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(UserStates.chat)
    await state.update_data(messages=[{"role": "system", "content": "Ты - пиратский помощник. Отвечай как настоящий пират!"}])
    await message.answer("Начните общение с ChatGPT (введите 'exit', чтобы выйти):")

# Обработчик сообщений
@router.message(UserStates.chat)
async def chat_handler(message: Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    messages = user_data.get("messages", [{"role": "system", "content": "Ты - пиратский помощник. Отвечай как настоящий пират!"}])

    if message.text.lower() == 'exit':
        await state.clear()
        await message.answer("Чат завершен.")
        return

    messages.append({"role": "user", "content": message.text})
    response = get_chatgpt_response(messages)
    messages.append({"role": "assistant", "content": response})

    await state.update_data(messages=messages)
    await message.answer(response)

# Запуск поллинга
async def main() -> None:
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())