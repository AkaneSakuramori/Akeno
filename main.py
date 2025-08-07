import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from config import BOT_TOKEN, FONT_DIR, CLEANUP_DELAY
from fonts import FontManager
from encoder import build_ffmpeg_command, encode_with_progress
import asyncio
from pathlib import Path

logging.basicConfig(level=logging.INFO)

# States
SETTINGS, UPLOAD = range(2)

# In-memory storage
user_settings = {}
queues = {}
font_manager = FontManager(FONT_DIR)
font_manager.load_fonts()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🤖 Welcome! Use /settings to configure encoding.')

async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Please send settings as: crf,fps,codec,audio_bitrate'
    )
    return SETTINGS

async def save_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        crf, fps, codec, audio_bitrate = update.message.text.split(',')
        user_settings[update.effective_user.id] = {
            'crf': int(crf), 'fps': int(fps),
            'codec': codec, 'audio_bitrate': audio_bitrate
        }
        await update.message.reply_text('✅ Settings saved.')
    except Exception as e:
        await update.message.reply_text('❌ Invalid format. Try again.')
        return SETTINGS
    return ConversationHandler.END

async def addfont_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        font_file = await update.message.document.get_file()
        path = font_manager.add_font(await font_file.download_as_bytearray(), update.message.document.file_name)
        await update.message.reply_text(f'✅ Font added: {path.name}')
    else:
        await update.message.reply_text('❌ Send a TTF/OTF file.')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🚫 Operation cancelled.')
    return ConversationHandler.END

async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    files = update.message.document or update.message.video
    # Simplified: expect two separate messages, track queue
    # ... implement queue logic
    await update.message.reply_text('Processing...')
    # Download files, build output path
    # Get settings or defaults
    settings = user_settings.get(user_id, {
        'crf': 23, 'fps': 30, 'codec': 'libx264', 'audio_bitrate': '128k'
    })
    # Font detection
    ass_path = '/path/to/sub.ass'
    font_path = font_manager.get_font_path('default')
    cmd = build_ffmpeg_command('/path/to/video.mp4', ass_path, '/path/to/out.mp4', settings, font_path)
    def progress_cb(line):
        # parse time, update message
        pass
    code = encode_with_progress(cmd, progress_cb)
    if code == 0:
        await update.message.reply_text('✅ Done!')
    else:
        await update.message.reply_text('❌ Encoding failed.')

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler('settings', settings_cmd)],
        states={SETTINGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_settings)]},
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    app.add_handler(CommandHandler('start', start))
    app.add_handler(conv)
    app.add_handler(CommandHandler('addfont', addfont_cmd))
    app.add_handler(CommandHandler('cancel', cancel))
    app.add_handler(MessageHandler(filters.ALL, handle_files))
    app.run_polling()


---