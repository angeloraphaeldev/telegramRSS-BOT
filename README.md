# 📡 Telegram RSS Bot

Um bot simples, leve e extensível para gerar **feeds RSS** de canais públicos do Telegram, YouTube, Threads da Meta, newsletters e muito mais. Ideal para acompanhar conteúdos de forma centralizada em leitores como **Feedly**, **Inoreader** ou seu leitor RSS favorito.

---

## ⚙️ Funcionalidades

✅ Gerar RSS de canais públicos do Telegram  
✅ Gerar RSS de canais do YouTube, perfis do Threads e newsletters (via RSSHub)  
✅ Listar todos os feeds já consultados  
✅ Exportar para arquivo `.opml` (compatível com Feedly, NetNewsWire, etc.)  
✅ Persistência simples via arquivo de texto  
✅ Interface via comandos do Telegram  

---

## 🚀 Demonstração

📲 **Exemplo de uso:**

1. Envie `canalnews` → o bot responde:  
   `https://rsshub.app/telegram/channel/canalnews`

2. Use `/youtube UC4JX40jDee_tINbkjycV4Sg` → o bot responde com o RSS do canal

3. Use `/exportar` → você recebe um arquivo `.opml` com todos os canais salvos

---

## 📥 Instalação

1. Clone o projeto:

```bash
git clone https://github.com/seunome/telegramRSS-BOT.git
cd telegramRSS-BOT
