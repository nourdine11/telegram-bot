from telegram import Update
import os
from PIL import Image
from rembg import remove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import instaloader
import re

TOKEN = '6643340774:AAEBa35de_5vZtSuqC3VYtfjSXykEPH3LtQ'

# Instaloader setup
L = instaloader.Instaloader()

# Login with your credentials (update with your details)
username = 'Davidluiz9631'
password = '123456789iop'
L.login(username, password)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Hello! I am NourdineBot. To start please click on /start !')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text='I am here to help you, please click on "/" to see the set of commands 😊 !')

async def process_image(photo_name: str) -> str:
    name, _ = os.path.splitext(photo_name)
    output_photo_path = f'./processed/{name}.png'
    input = Image.open(f'./drive/{photo_name}')
    output = remove(input)
    output.save(output_photo_path)
    os.remove(f'./drive/{photo_name}')
    return output_photo_path

async def process_image_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Please send me the picture.')

async def instagram_video_downloader(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text='To download your video or reel, please send me the URL...')

async def download_instagram_video(url: str) -> str:
    try:
        shortcode = re.search(r'/reel/([a-zA-Z0-9-_]+)/?', url)
        if not shortcode:
            raise ValueError("Shortcode not found in URL")
        shortcode = shortcode.group(1)

        # Télécharger la vidéos
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        video_path = f'./downloaded/{shortcode}.mp4'
        os.makedirs('./downloaded/', exist_ok=True)
        L.download_post(post, target='./downloaded/')
        print(" the video is downloded with successfuly")

        return video_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

async def handle_instagram_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    if 'instagram.com' in message_text:
        # Find Instagram links
        urls = re.findall(r'(https?://[^\s]+)', message_text)
        for url in urls:
            video_path = await download_instagram_video(url)
            if video_path:
                await context.bot.send_video(chat_id=update.effective_chat.id, video=open(video_path, 'rb'))
                os.remove(video_path)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text='Could not download the video. Please check the link and try again.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if filters.PHOTO.check_update(update):
        file_id = update.message.photo[-1].file_id
        unique_file_id = update.message.photo[-1].file_unique_id
        photo_name = f'{unique_file_id}.jpg'
    
    elif filters.Document.IMAGE:
        file_id = update.message.document.file_id
        _, f_ext = os.path.splitext(update.message.document.file_name)
        unique_file_id = update.message.document.file_unique_id
        photo_name = f'{unique_file_id}.{f_ext}'
    photo_file = await context.bot.get_file(file_id)
    await photo_file.download_to_drive(custom_path=f'./drive/{photo_name}')
    await context.bot.send_message(chat_id=update.effective_chat.id, text='We are processing your photo, please wait...')
    processed_image = await process_image(photo_name)
    await context.bot.send_document(chat_id=update.effective_chat.id, document=processed_image)
    os.remove(processed_image)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    # Command handlers
    help_handler = CommandHandler('help', help)
    start_handler = CommandHandler('start', start)
    handler_message = MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_message)
    process_image_handler = CommandHandler('process_image', process_image_command)
    instagram_down_handler = CommandHandler('instagram_video_download', instagram_video_downloader)
    instagram_link_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram_link)

    # Register commands
    application.add_handler(help_handler)
    application.add_handler(start_handler)
    application.add_handler(handler_message)
    application.add_handler(process_image_handler)
    application.add_handler(instagram_down_handler)
    application.add_handler(instagram_link_handler)

    # Keep the bot running
    application.run_polling()
