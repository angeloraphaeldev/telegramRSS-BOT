from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import os

load_dotenv()
tg_TOKEN = os.getenv("tg_TOKEN")

if not tg_TOKEN:
    raise ValueError("Token do Telegram não encontrado. Verifique a variável tg_TOKEN no .env.")

CAMINHO_ARQUIVO = "canais.txt"
ARQUIVO_OPML = "rssfeeds.opml"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Envie o nome do canal público (sem @) e eu te darei o link RSS.\nDigite /help para mais opções."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Comandos disponíveis:\n"
        "/start - Início\n"
        "/help - Ajuda\n"
        "/canais - Lista de canais salvos\n"
        "/exportar - Exporta os feeds em OPML\n"
        "/youtube <id/url> - RSS de canal YouTube\n"
        "/thread <username> - RSS de perfil Threads\n"
        "/newsletter <url> - RSS de newsletter Substack\n"
        "\n📨 Ou envie só o nome de um canal do Telegram."
    )

async def listar_canais(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(CAMINHO_ARQUIVO):
        await update.message.reply_text("Nenhum canal registrado ainda.")
        return

    with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
        canais = sorted(set(l.strip() for l in f if l.strip()))

    if canais:
        lista_formatada = '\n'.join(f"• {c}" for c in canais)
        await update.message.reply_text(f"📋 Canais registrados:\n\n{lista_formatada}")
    else:
        await update.message.reply_text("Nenhum canal registrado ainda.")

async def gerar_rss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    canal = update.message.text.strip().replace('@', '')

    if not canal.isalnum():
        await update.message.reply_text("❌ Nome de canal inválido. Envie apenas letras e números.")
        return

    rss_link = f'https://rsshub.app/telegram/channel/{canal}'
    await update.message.reply_text(f'🔗 Link RSS do canal Telegram:\n{rss_link}')

    with open(CAMINHO_ARQUIVO, "a", encoding="utf-8") as f:
        f.write(f"{canal}\n")

async def exportar_opml(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(CAMINHO_ARQUIVO):
        await update.message.reply_text("Nenhum canal para exportar.")
        return

    with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
        canais = sorted(set(l.strip() for l in f if l.strip()))

    if not canais:
        await update.message.reply_text("Nenhum canal para exportar.")
        return

    with open(ARQUIVO_OPML, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<opml version="2.0">\n')
        f.write('  <head>\n')
        f.write('    <title>Telegram RSS Feeds</title>\n')
        f.write('  </head>\n')
        f.write('  <body>\n')

        for canal in canais:
            link = f"https://rsshub.app/telegram/channel/{canal}"
            f.write(f'    <outline text="{canal}" title="{canal}" type="rss" xmlUrl="{link}" />\n')

        f.write('  </body>\n')
        f.write('</opml>\n')

    await update.message.reply_text("🗂️ Exportando feeds em formato OPML...")
    await update.message.reply_document(InputFile(ARQUIVO_OPML, filename=ARQUIVO_OPML))

async def youtube_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Use: /youtube <canal_id ou url>")
        return

    entrada = context.args[0].strip()
    canal_id = entrada.split("/")[-1]  # suporta link completo
    link = f"https://rsshub.app/youtube/channel/{canal_id}"
    await update.message.reply_text(f"▶️ RSS do YouTube:\n{link}")

async def thread_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Use: /thread <username>")
        return

    username = context.args[0].replace('@', '')
    link = f"https://rsshub.app/threads/profile/{username}"
    await update.message.reply_text(f"🧵 RSS do Threads:\n{link}")

async def newsletter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Use: /newsletter <url>")
        return

    url = context.args[0]
    link = f"https://rsshub.app/substack/{url.replace('https://', '').replace('http://', '').split('.')[0]}"
    await update.message.reply_text(f"📰 RSS da newsletter:\n{link}")


def main():
    app = Application.builder().token(tg_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("canais", listar_canais))
    app.add_handler(CommandHandler("exportar", exportar_opml))

    app.add_handler(CommandHandler("youtube", youtube_command))
    app.add_handler(CommandHandler("thread", thread_command))
    app.add_handler(CommandHandler("newsletter", newsletter_command))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, gerar_rss))

    app.run_polling()

if __name__ == "__main__":
    main()
