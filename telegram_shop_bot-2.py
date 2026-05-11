import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8671631936:AAF8Te8O7_STeFOOhxmHuZ4E8fs8KJbVjB8"
ADMIN_ID = 8763646336

PRODUCTS = {
    "p1": {"name": "T-Shirt Premium",  "price": 29.99, "stock": 50, "desc": "100% coton, tailles S-XL"},
    "p2": {"name": "Hoodie Confort",   "price": 59.99, "stock": 30, "desc": "Molleton doux 380g"},
    "p3": {"name": "Casquette Style",  "price": 24.99, "stock": 100,"desc": "Broderie premium"},
    "p4": {"name": "Totebag Eco",      "price": 14.99, "stock": 75, "desc": "Toile de jute 40x35cm"},
    "p5": {"name": "Carnet Artisanal", "price": 18.99, "stock": 45, "desc": "Papier recycle 200 pages"},
    "p6": {"name": "Mug Ceramique",    "price": 19.99, "stock": 60, "desc": "Ceramique 350ml"},
}

def get_cart(context):
    if "cart" not in context.user_data:
        context.user_data["cart"] = {}
    return context.user_data["cart"]

def cart_text(cart):
    if not cart:
        return "Votre panier est vide."
    lines = ["Votre panier :\n"]
    total = 0
    for pid, qty in cart.items():
        p = PRODUCTS[pid]
        sub = p["price"] * qty
        total += sub
        lines.append(f"{p['name']} x{qty} -- {sub:.2f}EUR")
    lines.append(f"\nTotal : {total:.2f}EUR")
    return "\n".join(lines)

def menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Voir le catalogue", callback_data="cat")],
        [InlineKeyboardButton("Mon panier",        callback_data="cart")],
        [InlineKeyboardButton("Contact",           callback_data="contact")],
    ])

def cat_kb():
    rows = []
    for pid, p in PRODUCTS.items():
        rows.append([InlineKeyboardButton(
            f"{p['name']} - {p['price']:.2f}EUR",
            callback_data=f"prod_{pid}"
        )])
    rows.append([InlineKeyboardButton("Menu principal", callback_data="menu")])
    return InlineKeyboardMarkup(rows)

def prod_kb(pid, qty):
    rows = [[InlineKeyboardButton("Ajouter au panier", callback_data=f"add_{pid}")]]
    if qty > 0:
        rows.append([InlineKeyboardButton(f"Retirer (x{qty})", callback_data=f"rem_{pid}")])
    rows.append([InlineKeyboardButton("Retour catalogue", callback_data="cat")])
    rows.append([InlineKeyboardButton("Mon panier", callback_data="cart")])
    return InlineKeyboardMarkup(rows)

def cart_kb(cart):
    rows = []
    if cart:
        rows.append([InlineKeyboardButton("Commander", callback_data="checkout")])
        rows.append([InlineKeyboardButton("Vider le panier", callback_data="clear")])
    rows.append([InlineKeyboardButton("Catalogue", callback_data="cat")])
    rows.append([InlineKeyboardButton("Menu principal", callback_data="menu")])
    return InlineKeyboardMarkup(rows)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"Bonjour {name} ! Bienvenue dans notre boutique.\n\nChoisissez une option :",
        reply_markup=menu_kb()
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data
    cart = get_cart(context)

    if d == "menu":
        await q.edit_message_text("Menu principal :", reply_markup=menu_kb())

    elif d == "cat":
        await q.edit_message_text("Notre Catalogue :", reply_markup=cat_kb())

    elif d.startswith("prod_"):
        pid = d[5:]
        p = PRODUCTS[pid]
        qty = cart.get(pid, 0)
        txt = f"{p['name']}\nPrix : {p['price']:.2f}EUR\nStock : {p['stock']}\n\n{p['desc']}"
        if qty:
            txt += f"\n\nDans votre panier : {qty}"
        await q.edit_message_text(txt, reply_markup=prod_kb(pid, qty))

    elif d.startswith("add_"):
        pid = d[4:]
        p = PRODUCTS[pid]
        cart[pid] = cart.get(pid, 0) + 1
        qty = cart[pid]
        txt = f"{p['name']}\nPrix : {p['price']:.2f}EUR\n\n{p['desc']}\n\nDans votre panier : {qty}"
        await q.edit_message_text(txt, reply_markup=prod_kb(pid, qty))

    elif d.startswith("rem_"):
        pid = d[4:]
        if pid in cart:
            if cart[pid] > 1:
                cart[pid] -= 1
            else:
                del cart[pid]
        qty = cart.get(pid, 0)
        p = PRODUCTS[pid]
        txt = f"{p['name']}\nPrix : {p['price']:.2f}EUR\n\n{p['desc']}"
        if qty:
            txt += f"\n\nDans votre panier : {qty}"
        await q.edit_message_text(txt, reply_markup=prod_kb(pid, qty))

    elif d == "cart":
        await q.edit_message_text(cart_text(cart), reply_markup=cart_kb(cart))

    elif d == "clear":
        context.user_data["cart"] = {}
        await q.edit_message_text("Panier vide.", reply_markup=menu_kb())

    elif d == "checkout":
        if not cart:
            await q.answer("Panier vide !", show_alert=True)
            return
        user = update.effective_user
        summary = cart_text(cart)
        await q.edit_message_text(f"Commande recue !\n\n{summary}\n\nEnvoyez votre nom et adresse.")
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"Nouvelle commande de {user.full_name}:\n\n{summary}"
            )
        except Exception as e:
            logger.warning(f"Admin notify failed: {e}")
        context.user_data["cart"] = {}

    elif d == "contact":
        await q.edit_message_text(
            "Contact : contact@votreshop.com\nHoraires : Lun-Ven 9h-18h",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Menu", callback_data="menu")]])
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text("Message recu !", reply_markup=menu_kb())
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Message de {user.full_name}:\n\n{update.message.text}"
        )
    except Exception as e:
        logger.warning(f"Forward failed: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    logger.info("Bot demarre !")
    app.run_polling()

if __name__ == "__main__":
    main()
