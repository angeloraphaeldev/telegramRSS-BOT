import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

tg_TOKEN = os.getenv("tg_TOKEN")
FEEDS_FILE = "feeds.json"
OPML_FILE = "feeds.opml"

if not tg_TOKEN:
    raise ValueError("Token do Telegram não encontrado. Verifique a variável tg_TOKEN.")

def load_feeds():
    if os.path.exists(FEEDS_FILE):
        with open(FEEDS_FILE, "r") as f:
            return json.load(f)
    return []

def save_feeds(feeds):
    with open(FEEDS_FILE, "w") as f:
        json.dump(feeds, f, indent=2)

def add_feed(title, url, site_url):
    feeds = load_feeds()
    if any(feed["xmlUrl"] == url for feed in feeds):
        return False
    feeds.append({"title": title, "xmlUrl": url, "htmlUrl": site_url})
    save_feeds(feeds)
    return True

def export_to_opml():
    feeds = load_feeds()
    outline_items = "".join(
        f'<outline type="rss" text="{f["title"]}" title="{f["title"]}" xmlUrl="{f["xmlUrl"]}" htmlUrl="{f["htmlUrl"]}" />\n'
        for f in feeds
    )
    opml = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<opml version=\"1.0\">
  <head>
    <title>Meus Feeds</title>
  </head>
  <body>
    {outline_items}  </body>
</opml>
"""
    with open(OPML_FILE, "w") as f:
        f.write(opml)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Envie um nome de canal público (Telegram, Threads, YouTube) para gerar o link RSS. Use /help para mais informações.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
Comandos disponíveis:
/start - Inicia o bot
/help - Mostra esta mensagem
/list - Lista todos os feeds salvos
/export - Exporta os feeds para OPML compatível com Feedly
""")

async def list_feeds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feeds = load_feeds()
    if not feeds:
        await update.message.reply_text("Nenhum feed salvo ainda.")
    else:
        resposta = "Feeds salvos:\n" + "\n".join(f"- {f['title']}: {f['xmlUrl']}" for f in feeds)
        await update.message.reply_text(resposta)

async def export_feeds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    export_to_opml()
    await update.message.reply_document(document=open(OPML_FILE, "rb"), filename=OPML_FILE)

async def gerar_rss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()

    if texto.startswith("https://www.youtube.com/@"):
        username = texto.split("@")[-1]
        url = f"https://rsshub.app/youtube/user/{username}"
        title = f"YouTube: @{username}"
        site = f"https://www.youtube.com/@{username}"

    elif "threads.net" in texto:
        username = texto.split("/")[-1].strip()
        url = f"https://rsshub.app/threads/{username}"
        title = f"Threads: {username}"
        site = f"https://www.threads.net/{username}"

    else:
        canal = texto.replace("@", "")
        url = f"https://rsshub.app/telegram/channel/{canal}"
        title = f"Telegram: {canal}"
        site = f"https://t.me/{canal}"

    added = add_feed(title, url, site)
    msg = f"RSS gerado: {url}\n(Esse link pode ser usado no Feedly, Inoreader, etc.)"
    if not added:
        msg += "\n⚠️ Este feed já foi adicionado."

    await update.message.reply_text(msg)

def main():
    app = Application.builder().token(tg_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("list", list_feeds))
    app.add_handler(CommandHandler("export", export_feeds))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gerar_rss))

    print("Bot iniciado.")
    app.run_polling()

if __name__ == "__main__":
    main()
