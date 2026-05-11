"📝 cart)
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
    app = Application.builder().token(BOT_TOKEN
