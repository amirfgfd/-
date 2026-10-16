import asyncio
import logging
import random
import sys
from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# توکن ربات شما
TOKEN = "8277541821:AAFQbBaabVYF7tsxUlSr7vba0CyJAkvQJ4I"

# لیست ذخیره‌سازی موقت شرکت‌کنندگان
participants = set()

# راه‌اندازی لاگ‌گیر برای نمایش وضعیت در ترمینال
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# دکمه‌های شیشه‌ای ربات
def get_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎉 شرکت در قرعه‌کشی", callback_data="join_giveaway")],
            [InlineKeyboardButton(text="👥 تعداد شرکت‌کنندگان", callback_data="check_count")]
        ]
    )

dp = Dispatcher()

# دستور استارت
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_name = html.quote(message.from_user.first_name)
    welcome_text = (
        f"سلام {user_name} عزیز! 🌟\n\n"
        f"به ربات رسمی قرعه‌کشی خوش آمدید.\n"
        f"برای شرکت در قرعه‌کشی روی دکمه زیر کلیک کنید:"
    )
    await message.answer(welcome_text, reply_markup=get_keyboard(), parse_mode=ParseMode.HTML)

# مدیریت کلیک روی دکمه شرکت در قرعه‌کشی
@dp.callback_query(F.data == "join_giveaway")
async def join_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id in participants:
        await callback.answer("شما قبلاً در قرعه‌کشی ثبت‌نام کرده‌اید! ✅", show_alert=True)
    else:
        participants.add(user_id)
        await callback.answer("ثبت‌نام شما با موفقیت انجام شد! 🍀", show_alert=True)

# مدیریت دکمه استعلام تعداد شرکت‌کنندگان
@dp.callback_query(F.data == "check_count")
async def count_callback(callback: CallbackQuery):
    count = len(participants)
    await callback.answer(f"تاکنون {count} نفر در قرعه‌کشی شرکت کرده‌اند.", show_alert=True)

# دستور ادمین برای انجام قرعه‌کشی و انتخاب برنده (دستور /draw)
@dp.message(Command("draw"))
async def draw_winner(message: Message):
    if not participants:
        await message.answer("هنوز هیچ‌کس در قرعه‌کشی شرکت نکرده است!")
        return
    
    winner_id = random.choice(list(participants))
    try:
        chat_member = await message.bot.get_chat_member(chat_id=winner_id, user_id=winner_id)
        winner_name = chat_member.user.full_name
        winner_mention = f"<a href='tg://user?id={winner_id}'>{html.quote(winner_name)}</a>"
    except Exception:
        winner_mention = f"کاربر با آیدی <code>{winner_id}</code>"

    await message.answer(
        f"🎉 **قرعه‌کشی به پایان رسید!** 🎉\n\n"
        f"برنده خوش‌اقبال ما: {winner_mention}\n\n"
        f"مبارکت باشه! 🏆",
        parse_mode=ParseMode.HTML
    )
    participants.clear()

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
