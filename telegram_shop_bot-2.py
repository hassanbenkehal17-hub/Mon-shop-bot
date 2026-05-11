"""
🛍️ Telegram Shop Bot - Produits Physiques
==========================================
Dépendances : pip install python-telegram-bot==20.7

Configuration :
  1. Créez un bot via @BotFather sur Telegram → obtenez BOT_TOKEN
  2. Remplacez BOT_TOKEN et ADMIN_CHAT_ID ci-dessous
  3. Lancez : python telegram_shop_bot.py
"""

import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

# ─── CONFIG ────────────────────────────────────────────────────────────────────
BOT_TOKEN   = "8671631936:AAF8Te8O7_STeFOOhxmHuZ4E8fs8KJbVjB8"
ADMIN_CHAT_ID = 8763646336
CURRENCY    = "€"

# ─── CATALOGUE ─────────────────────────────────────────────────────────────────
PRODUCTS = {
    "p1": {
        "name": "T-Shirt Premium",
        "price": 29.99,
        "description": "100% coton biologique, coupe unisexe. Disponible en S, M, L, XL.",
        "emoji": "👕",
        "stock": 50,
        "image": None,   # URL image optionnelle
    },
    "p2": {
        "name": "Hoodie Confort",
        "price": 59.99,
        "description": "Molleton doux 380g, poche kangourou. Lavable en machine.",
        "emoji": "🧥",
        "stock": 30,
        "image": None,
    },
    "p3": {
        "name": "Casquette Style",
        "price": 24.99,
        "description": "Broderie premium, réglable. Taille unique.",
        "emoji": "🧢",
        "stock": 100,
        "image": None,
    },
    "p4": {
        "name": "Totebag Éco",
        "price": 14.99,
        "description": "Toile de jute naturelle, 40x35cm. Résistant et stylé.",
        "emoji": "👜",
        "stock": 75,
        "image": None,
    },
    "p5": {
        "name": "Carnet Artisanal",
        "price": 18.99,
        "description": "Papier recyclé 200 pages, couverture cuir végétal.",
        "emoji": "📓",
        "stock": 45,
        "image": None,
    },
    "p6": {
        "name": "Mug Céramique",
        "price": 19.99,
        "description": "Céramique artisanale 350ml. Passez au lave-vaisselle.",
        "emoji": "☕",
        "stock": 60,
        "image": None,
    },
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def get_cart(context: ContextTypes.DEFAULT_TYPE) -> dict:
    if "cart" not in context.user_data:
        context.user_data["cart"] = {}
    return context.user_data["cart"]

def cart_total(cart: dict) -> float:
    return sum(PRODUCTS[pid]["price"] * qty for pid, qty in cart.items() if pid in PRODUCTS)

def cart_summary(cart: dict) -> str:
    if not cart:
        return "🛒 Votre panier est vide."
    lines = ["🛒 *Votre panier :*\n"]
    for pid, qty in cart.items():
        p = PRODUCTS[pid]
        subtotal = p["price"] * qty
        lines.append(f"{p['emoji']} {p['name']} x{qty} — {subtotal:.2f}{CURRENCY}")
    lines.append(f"\n💰 *Total : {cart_total(cart):.2f}{CURRENCY}*")
    return "\n".join(lines)

# ─── KEYBOARDS ─────────────────────────────────────────────────────────────────

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ Voir le catalogue", callback_data="catalogue")],
        [InlineKeyboardButton("🛒 Mon panier",        callback_data="cart")],
        [InlineKeyboardButton("📞 Contact / Aide",    callback_data="contact")],
    ])

def catalogue_keyboard(page=0):
    items = list(PRODUCTS.items())
    per_page = 3
    start = page * per_page
    chunk = items[start:start + per_page]
    rows = []
    for pid, p in chunk:
        rows.append([InlineKeyboardButton(
            f"{p['emoji']} {p['name']} — {p['price']:.2f}{CURRENCY}",
            callback_data=f"product_{pid}"
        )])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ Précédent", callback_data=f"cat_page_{page-1}"))
    if start + per_page < len(items):
        nav.append(InlineKeyboardButton("Suivant ▶️", callback_data=f"cat_page_{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton("🏠 Menu principal", callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)

def product_keyboard(pid: str, qty_in_cart: int):
    rows = [
        [
            InlineKeyboardButton("➕ Ajouter au panier", callback_data=f"add_{pid}"),
        ],
    ]
    if qty_in_cart > 0:
        rows.append([
            InlineKeyboardButton(f"➖ Retirer ({qty_in_cart} dans panier)", callback_data=f"remove_{pid}"),
        ])
    rows.append([InlineKeyboardButton("◀️ Catalogue",       callback_data="catalogue")])
    rows.append([InlineKeyboardButton("🛒 Voir mon panier", callback_data="cart")])
    return InlineKeyboardMarkup(rows)

def cart_keyboard(cart: dict):
    rows = []
    if cart:
        rows.append([InlineKeyboardButton("✅ Passer la commande", callback_data="checkout")])
        rows.append([InlineKeyboardButton("🗑️ Vider le panier",   callback_data="clear_cart")])
    rows.append([InlineKeyboardButton("🛍️ Continuer mes achats", callback_data="catalogue")])
    rows.append([InlineKeyboardButton("🏠 Menu principal",        callback_data="main_menu")])
    return InlineKeyboardMarkup(rows)

# ─── HANDLERS ──────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Bonjour *{user.first_name}* !\n\n"
        "Bienvenue dans notre boutique en ligne 🛍️\n"
        "Parcourez notre catalogue et ajoutez vos articles préférés au panier.\n\n"
        "Utilisez le menu ci-dessous pour commencer :",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *Aide*\n\n"
        "/start — Revenir au menu principal\n"
        "/catalogue — Voir les produits\n"
        "/panier — Voir votre panier\n"
        "/aide — Afficher cette aide",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    cart = get_cart(context)

    # ── Menu principal ──────────────────────────────────────────────────────────
    if data == "main_menu":
        await query.edit_message_text(
            "🏠 *Menu principal*\nQue souhaitez-vous faire ?",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

    # ── Catalogue ───────────────────────────────────────────────────────────────
    elif data == "catalogue" or data.startswith("cat_page_"):
        page = int(data.split("_")[-1]) if data.startswith("cat_page_") else 0
        total_pages = -(-len(PRODUCTS) // 3)
        await query.edit_message_text(
            f"🛍️ *Notre Catalogue* (page {page+1}/{total_pages})\n\n"
            "Choisissez un produit pour voir les détails :",
            parse_mode="Markdown",
            reply_markup=catalogue_keyboard(page)
        )

    # ── Fiche produit ───────────────────────────────────────────────────────────
    elif data.startswith("product_"):
        pid = data.split("_", 1)[1]
        p = PRODUCTS.get(pid)
        if not p:
            await query.edit_message_text("❌ Produit introuvable.")
            return
        qty = cart.get(pid, 0)
        stock_txt = f"✅ En stock ({p['stock']} dispo)" if p["stock"] > 0 else "❌ Rupture de stock"
        text = (
            f"{p['emoji']} *{p['name']}*\n\n"
            f"💰 Prix : *{p['price']:.2f}{CURRENCY}*\n"
            f"📦 {stock_txt}\n\n"
            f"📝 {p['description']}"
        )
        if qty:
            text += f"\n\n🛒 Dans votre panier : *{qty}*"
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=product_keyboard(pid, qty)
        )

    # ── Ajouter au panier ───────────────────────────────────────────────────────
    elif data.startswith("add_"):
        pid = data.split("_", 1)[1]
        p = PRODUCTS.get(pid)
        if not p or p["stock"] <= 0:
            await query.answer("❌ Produit indisponible.", show_alert=True)
            return
        current_qty = cart.get(pid, 0)
        if current_qty >= p["stock"]:
            await query.answer("⚠️ Stock maximum atteint.", show_alert=True)
            return
        cart[pid] = current_qty + 1
        await query.answer(f"✅ {p['name']} ajouté au panier !")
        # Rafraîchir la fiche produit
        qty = cart[pid]
        stock_txt = f"✅ En stock ({p['stock']} dispo)"
        text = (
            f"{p['emoji']} *{p['name']}*\n\n"
            f"💰 Prix : *{p['price']:.2f}{CURRENCY}*\n"
            f"📦 {stock_txt}\n\n"
            f"📝 {p['description']}\n\n"
            f"🛒 Dans votre panier : *{qty}*"
        )
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=product_keyboard(pid, qty)
        )

    # ── Retirer du panier ───────────────────────────────────────────────────────
    elif data.startswith("remove_"):
        pid = data.split("_", 1)[1]
        p = PRODUCTS.get(pid)
        if pid in cart:
            if cart[pid] > 1:
                cart[pid] -= 1
            else:
                del cart[pid]
        qty = cart.get(pid, 0)
        await query.answer(f"➖ {p['name']} retiré.")
        text = (
            f"{p['emoji']} *{p['name']}*\n\n"
            f"💰 Prix : *{p['price']:.2f}{CURRENCY}*\n\n"
            f"📝 {p['description']}"
        )
        if qty:
            text += f"\n\n🛒 Dans votre panier : *{qty}*"
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=product_keyboard(pid, qty)
        )

    # ── Panier ──────────────────────────────────────────────────────────────────
    elif data == "cart":
        await query.edit_message_text(
            cart_summary(cart),
            parse_mode="Markdown",
            reply_markup=cart_keyboard(cart)
        )

    # ── Vider le panier ─────────────────────────────────────────────────────────
    elif data == "clear_cart":
        context.user_data["cart"] = {}
        await query.edit_message_text(
            "🗑️ Votre panier a été vidé.",
            reply_markup=main_menu_keyboard()
        )

    # ── Checkout ────────────────────────────────────────────────────────────────
    elif data == "checkout":
        if not cart:
            await query.answer("Votre panier est vide !", show_alert=True)
            return
        user = update.effective_user
        # Résumé commande
        summary = cart_summary(cart)
        order_text = (
            f"🎉 *Commande reçue !*\n\n"
            f"{summary}\n\n"
            f"📬 Pour finaliser votre commande, envoyez-nous :\n"
            f"1️⃣ Votre nom complet\n"
            f"2️⃣ Votre adresse de livraison\n"
            f"3️⃣ Votre numéro de téléphone\n\n"
            f"Un conseiller vous contactera pour le paiement. ✅"
        )
        await query.edit_message_text(order_text, parse_mode="Markdown")

        # Notifier l'admin
        admin_msg = (
            f"🛎️ *Nouvelle commande !*\n"
            f"👤 Client : {user.full_name} (@{user.username or 'N/A'}, ID: {user.id})\n\n"
            f"{summary}"
        )
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=admin_msg,
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.warning(f"Impossible de notifier l'admin : {e}")

        # Vider le panier après commande
        context.user_data["cart"] = {}

    # ── Contact ─────────────────────────────────────────────────────────────────
    elif data == "contact":
        await query.edit_message_text(
            "📞 *Contact & Aide*\n\n"
            "Pour toute question :\n"
            "📧 Email : contact@votroshop.com\n"
            "💬 Telegram : @VotreAdmin\n"
            "⏰ Disponible : Lun-Ven 9h-18h\n\n"
            "Délais de livraison : 3-5 jours ouvrés 📦",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Menu principal", callback_data="main_menu")]
            ])
        )

async def unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les messages texte libres (ex: adresse après checkout)"""
    await update.message.reply_text(
        "💬 Message reçu ! Un conseiller va vous répondre bientôt.\n\n"
        "En attendant, revenez au menu :",
        reply_markup=main_menu_keyboard()
    )
    # Transférer à l'admin
    user = update.effective_user
    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=(
                f"💬 *Message client*\n"
                f"👤 {user.full_name} (@{user.username or 'N/A'}, ID: {user.id})\n\n"
                f"📝 {update.message.text}"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.warning(f"Impossible de transférer le message : {e}")

# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",     start))
    app.add_handler(CommandHandler("aide",      help_command))
    app.add_handler(CommandHandler("help",      help_command))
    app.add_handler(CommandHandler("catalogue", lambda u, c: u.message.reply_text(
        "🛍️ Catalogue :", reply_markup=catalogue_keyboard()
    )))
    app.add_handler(CommandHandler("panier", lambda u, c: u.message.reply_text(
        cart_summary(get_cart(c)), parse_mode="Markdown",
        reply_markup=cart_keyboard(get_cart(c))
    )))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_message))

    print("🤖 Bot démarré ! Appuyez sur Ctrl+C pour arrêter.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
