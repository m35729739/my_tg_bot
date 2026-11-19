import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

# ВСТАВЬ СВОЙ НОВЫЙ ТОКЕН СЮДА (между кавычками)
BOT_TOKEN = "8342166744:AAEIY9ezk7VWynIBnpwVsaXKvYyFHl-LejQ"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище состояния для каждого чата
auction_state = {}

async def announce_winner(chat_id, place, leader_name):
    await bot.send_message(
        chat_id, 
        f"🏆 *{place} МЕСТО!*\n"
        f"Победитель: {leader_name}\n"
        f"Поздравляем! 🎉",
        parse_mode="Markdown"
    )

async def timer_countdown(chat_id, leader_id, leader_name, place):
    try:
        await asyncio.sleep(180)  # 3 минуты (180 секунд)
        
        state = auction_state.get(chat_id)
        if state and state.get("leader_id") == leader_id:
            await announce_winner(chat_id, place, leader_name)
            del auction_state[chat_id]
            
    except asyncio.CancelledError:
        pass

@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_message(message: Message):
    # Игнорируем ботов и команды (начинающиеся с /)
    if message.from_user.is_bot or (message.text and message.text.startswith("/")):
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    
    current_state = auction_state.get(chat_id)
    
    # Если пишет тот же лидер, ничего не делаем (таймер не сбрасывается)
    if current_state and current_state["leader_id"] == user_id:
        return
    
    # Отменяем предыдущий таймер
    if current_state and current_state.get("timer_task"):
        current_state["timer_task"].cancel()
    
    # Определяем, за какое место идет битва (по умолчанию 1-е)
    place = current_state.get("current_place", "1-е") if current_state else "1-е"
    
    task = asyncio.create_task(timer_countdown(chat_id, user_id, user_name, place))
    
    auction_state[chat_id] = {
        "leader_id": user_id,
        "leader_name": user_name,
        "timer_task": task,
        "current_place": place
    }
    
    # Бот отвечает на сообщение в чате
    await message.reply(
        f"👤 *{user_name}* теперь ЛИДЕР!\n"
        f"У него есть 3 минуты, чтобы удержать позицию. ⏳\n"
        f"_(Битва за {place} место)_",
        parse_mode="Markdown"
    )

# Команда для смены места (например, напиши в чат /place 2, чтобы начать битву за 2-е место)
@dp.message(F.text.startswith("/place"))
async def change_place(message: Message):
    chat_id = message.chat.id
    args = message.text.split()
    if len(args) > 1:
        new_place = args[1]
        if chat_id not in auction_state:
            auction_state[chat_id] = {}
        auction_state[chat_id]["current_place"] = new_place
        await message.reply(f"✅ Теперь играем за *{new_place} место*!", parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())