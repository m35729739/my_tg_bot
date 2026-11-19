import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

BOT_TOKEN = "8342166744:AAHaL_dgi7Pg-FFcq_eS82Z9iOeTFXbFItA"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

GIFT_ID = "5170145012310081615"
MIN_MSG = 10
MAX_MSG = 50

auction_state = {}

@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_message(message: Message):
    if message.from_user.is_bot or (message.text and message.text.startswith("/")):
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    
    if chat_id not in auction_state:
        auction_state[chat_id] = {
            "counter": 0,
            "target": random.randint(MIN_MSG, MAX_MSG)
        }
    
    state = auction_state[chat_id]
    state["counter"] += 1
    
    if state["counter"] >= state["target"]:
        try:
            await bot.send_gift(
                user_id=user_id,
                gift_id=GIFT_ID,
                text="Поздравляем! Вы выиграли сердечко 💝 от @Doxej и @Hukyu"
            )
            
            await message.answer(
                f"🎁 **ДЖЕКПОТ!**\n"
                f"Победитель: {user_name}!\n"
                f"Поздравляем! Вы выиграли сердечко 💝 от @Doxej и @Hukyu (Подарок придет не позднее 2 часов)",
                parse_mode="Markdown"
            )
        except Exception as e:
            await message.answer(f"⚠️ Ошибка при отправке: {e}")
        
        state["counter"] = 0
        state["target"] = random.randint(MIN_MSG, MAX_MSG)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
