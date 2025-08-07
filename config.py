load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
FONT_DIR = os.getenv('FONT_DIR', './fonts')
CLEANUP_DELAY = int(os.getenv('CLEANUP_DELAY', '600'))