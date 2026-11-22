# ===================================================================
# i18n.py - Ko'p tillik qatlam (Uz / En / Ru)
# Barcha xabarlar shu yerda. `t(lang, key)` orqali olinadi.
# ===================================================================

from __future__ import annotations

from src.models import Lang

TRANSLATIONS: dict[str, dict[str, str]] = {
    "uz": {
        # --- Umumiy / Start ---
        "start": "🚀 <b>{first}</b> xush kelibsiz!\n\n"
                 "ℹ️ Bu bot orqali <b>Telegram Stars</b> sotib oling yoki o'z postlaringizga stars yo'llang.\n\n"
                 "👇 Quyidagi bo'limlardan birini tanlang:",
        "start_not_subscribed": "⚠️ <b>Botdan foydalanish uchun kanal(lar)imizga obuna bo'lishingiz kerak!</b>\n\n{channels}\n\nObuna bo'lgach \"✅ Tekshirish\" tugmasini bosing.",
        "start_bot_inactive": "⛔️ Bot vaqtincha ishlamayapti. Iltimos keyinroq urinib ko'ring.",
        "check_subscribe": "✅ Tekshirish",
        "subscribe_alert": "⚠️ <b>Botdan foydalanish uchun avval kanal(lar)ga obuna bo'ling!</b>",
        "back": "◀️ Orqaga",
        "menu_buy": "🛒 Stars sotib olish",
        "menu_wallet": "👛 Balans",
        "menu_topup": "💳 Hisobni to'ldirish",
        "menu_gift": "🎁 Gift",
        "menu_subscribe": "♻️ Postga stars",
        "menu_stats": "📊 Statistika",
        "menu_pricing": "💲 Narxlar",
        "menu_help": "❓ Yordam / FAQ",
        "menu_personal": "👤 Shaxsiy kabinet",
        "menu_referral": "👥 Referal tizimi",
        "menu_referral": "👥 Referal",

        # --- Referal dasturi ---
        "referral_info": "👥 <b>Referal dasturi</b>\n\n"
                         "Har bir taklif qilgan do'stingiz botga kirib, "
                         "<b>birinchi xarid</b> qilsa, hisobingizga "
                         "<b>{bonus} so'm</b> bonus tushadi!\n\n"
                         "🔗 <b>Sizning havolangiz:</b>\n<code>{link}</code>\n\n"
                         "Do'stingiz shu havola orqali botga kirsin. "
                         "Har bir foydalanuvchi uchun bonus <b>faqat bir marta</b> to'lanadi.\n\n"
                         "📊 Taklif qilinganlar: <b>{count}</b>\n"
                         "💵 To'plagan bonus: <b>{earned} so'm</b>\n\n"
                         "🕓 Oxirgi referallar:\n{refs}",
        "referral_list_empty": "Hozircha referallar yo'q. Havolangizni do'stlaringizga ulashing!",
        "referral_bonus_received": "🎉 <b>Tabriklaymiz!</b>\n\n"
                                   "Taklif qilgan foydalanuvchingiz birinchi xaridni amalga oshirdi.\n"
                                   "Hisobingizga <b>{amount} so'm</b> bonus qo'shildi 👥\n\n"
                                   "Balansingizni ko'rish uchun 👛 bo'limiga o'ting.",

        # --- Narxlar ---
        "pricing_text": "📈 <b>Stars narxlari</b>\n\n{prices}\n\n"
                        "💰 To'lov: karta yoki online API orqali\n"
                        "⚡️ Real vaqtda yetkazib berish",

        # --- Sotib olish (buy) ---
        "buy_choose": "🛒 <b>Paketni tanlang:</b>\n\n{prices}\n\n"
                      "Hisobingiz: <b>{balance} so'm</b>\n"
                      "Balansdan (so'm) to'lash uchun <b>👛 Balansdan</b> tugmasini tanlang.",
        "buy_package": "⭐ {amount} Stars",
        "buy_from_balance": "💳 Balansdan to'lash",
        "buy_method": "💳 <b>To'lov usulini tanlang</b> — {amount} Stars paketi uchun.",
        "method_card": "💳 Karta orqali",
        "method_api": "🔗 Online API",
        "method_balance": "👛 Balansdan",
        "card_pay_instructions": "💳 <b>To'lovni amalga oshiring</b>\n\n"
                                 "Paket: <b>{amount} Stars</b>\n"
                                 "Summa: <b>{price} so'm</b>\n\n"
                                 "Karta raqami:\n<b><code>{card}</code></b>\n\n"
                                 "To'lov qilib bo'lgach pastdagi tugmani bosing — admin buyurtmani tekshiradi.",
        "card_paid": "📤 To'lov qildim",
        "card_paid_note": "💰 <b>To'lov ma'lumotini yuboring</b>\n\n"
                          "To'lov haqida ma'lumot (chek, summa) yozing yoki rasm/tasdiq yuboring. "
                          "So'ng buyurtma admin tasdig'iga yuboriladi.",
        "order_created_user": "✅ Buyurtma yaratildi!\n\n"
                              "📦 Buyurtma: <b>#{order_id}</b>\n"
                              "⭐ Paket: <b>{amount} Stars</b>\n"
                              "💰 To'lov: <b>{method}</b>\n"
                              "Status: <b>⏳ Kutmoqda</b>",
        "order_status_for_user": "📦 <b>Buyurtma #{order_id}</b>\n"
                                 "Paket: <b>{amount} Stars</b>\n"
                                 "Status: {status}\n"
                                 "{note}",
        "api_order_creating": "🔗 <b>Buyurtma API orqali yuborilmoqda...</b>",
        "api_order_success": "✅ <b>Buyurtma yetkazildi!</b>\n\n"
                             "⭐ <b>+{amount} Stars</b> hisobingizga qo'shildi.",
        "api_order_failed": "❌ <b>Buyurtma bajarilmadi.</b>\n\n"
                            "Iltimos, admin bilan bog'laning yoki to'lov vositasini o'zgartiring.",
        "insufficient_balance": "⚠️ <b>Balansingiz yetarli emas!</b>\n\n"
                                "Sizda: {balance} Stars\n"
                                "Kerak: {need} Stars",
        "insufficient_sum": "⚠️ <b>Hisobingizda yetarli mablag' yo'q!</b>\n\n"
                            "Sizda: {balance} so'm\n"
                            "Kerak: {need} so'm",
        "balance_buy_ok": "🧾 <b>Balansdan to'landi!</b>\n\n"
                          "💸 -{price} so'm (buyurtma #{order_id})\n"
                          "⭐ +{amount} Stars qo'shildi.\n"
                          "Qolgan hisob: <b>{balance} so'm</b>",
        "balance_deducted": "🧾 <b>Balansdan to'landi!</b>\n\n"
                            "⭐ +{amount} Stars qo'shildi (buyurtma #{order_id}).\n"
                            "Yangi balans: <b>{balance} Stars</b>",

        # --- Balans ---
        "wallet_title": "👛 <b>Hisobingiz</b>\n\n"
                        "💵 Pul (hisob): <b>{sum} so'm</b>\n"
                        "⭐ Stars: <b>{balance} Stars</b>\n"
                        "{progress}\n\n"
                        "📊 Jami sotib olingan: <b>{bought}</b>\n"
                        "📤 Jami sotilgan: <b>{sold}</b>\n"
                        "🎁 Olingan giftlar: <b>{gifted}</b>",
        "wallet_topup": "💳 <b>Hisobni so'mda to'ldirish</b>\n\n"
                        "Karta orqali yoki online to'lov bilan <b>naqd pul (so'm)</b> "
                        "hisobingizga tushadi. Keyin ushbu puldan <b>Stars sotib ola</b> olasiz.",
        "topup_sum_prompt": "💵 <b>To'ldiriladigan miqdorni so'mda yuboring</b>\n"
                            "Masalan: <code>100000</code>\n"
                            "Bekor qilish: /start",
        "topup_card_pay": "💳 <b>To'lovni amalga oshiring</b>\n\n"
                          "Miqdor: <b>{amount} so'm</b>\n\n"
                          "Karta raqami:\n<b><code>{card}</code></b>\n\n"
                          "To'lov qilib bo'lgach tasdiq (chek, skrinshot) yuboring — "
                          "admin hisobingizni to'ldiradi.",
        "topup_sent_user": "⏳ <b>So'rovingiz yuborildi!</b>\n\n"
                           "Admin to'lovni tekshirib, hisobingizga "
                           "<b>{amount} so'm</b> qo'shadi.",
        "order_rejected_user": "❌ <b>Buyurtma #{order_id} bekor qilindi.</b>\n\n"
                               "Pul hisobingizga qo'shilmadi. Savol bo'lsa admin bilan bog'laning.",
        "topup_api_success": "✅ <b>Hisob to'ldirildi!</b>\n\n"
                             "🆕 Pul hisobi: <b>{balance} so'm</b>",
        "topup_sent_admin": "💰 <b>Yangi hisob to'ldirish so'rovi</b>\n\n"
                            "📋 Bot ID: <code>{uid}</code>\n"
                            "👤 {user}\n"
                            "💵 Summa: <b>{amount} so'm</b>\n"
                            "📄 Chek: {proof}",
        "topup_enough": "✅ <b>Balans to'ldirildi!</b>\n\n"
                        "🆕 Pul hisobi: <b>{balance} so'm</b>",
        "wallet_history": "📜 <b>Hisob harakati</b>\n\n{history}\n\n",
        "tx_none": "Hozircha harakatlar yo'q.",

        # --- Gift ---
        "gift_menu": "🎁 <b>Gift bo'limi</b>\n\n"
                     "Bu yerda Telegram gift olishingiz yoki yuborishingiz mumkin.\n\n"
                     "👛 Hisobingiz: <b>{balance} so'm</b>",
        "gift_buy": "🎁 Gift sotib olish",
        "gift_send": "📤 Gift yuborish",
        "gift_choose_pack": "🎁 <b>Gift paketini tanlang</b> - gift akkauntingizga avtomatik yuboriladi.",
        "gift_choose_catalog": "🎁 <b>Gift tanlang</b> — quyidagilardan birini bosing (narxi so'mlik hisobingizdan yechiladi):",
        "gift_empty": "😕 <b>Hozircha giftlar yo'q.</b>\n\n"
                      "Giftlar tez orada qo'shiladi. Admin panel orqali boshqariladi.",
        "gift_need_phone": "🎁 <b>Gift: {name}</b>\n\n"
                           "💰 Narxi: <b>{price} so'm</b>\n"
                           "⭐ Stars: <b>{stars}</b>\n\n"
                           "Qabul qiluvchining <b>@username</b> yoki <b>telefon raqamini</b> yuboring:\n"
                           "(masalan: <code>@ali</code> yoki <code>+998901234567</code>)\n\n"
                           "Akkaunt ulangan bo'lishi kerak.",
        "gift_sent": "✅ <b>Gift yetkazildi!</b>\n\n"
                     "🎁 <b>{amount} Stars</b> gift (— {name}) yo'llandi.\n"
                     "Qolgan hisob: <b>{balance} so'm</b>",
        "gift_received": "🎁 <b>Yangi gift!</b>\n\n"
                         "Akkauntingizga {amount} Stars gift tushdi.",
        "invalid_phone": "⚠️ Noto'g'ri format. @username yoki telefon raqam yuboring.\n"
                         "Namuna: <code>@ali</code> yoki <code>+998901234567</code>",

        # --- Postga stars ---
        "post_stars_request": "📝 <b>Postga stars berish</b>\n\n"
                              "Qancha stars kerakligini tanlang 👇",
        "post_custom_amount": "✍️ O'zim kiritaman",
        "post_stars_custom_prompt": "🔢 <b>Qancha stars kerakligini yozing</b>\n\n"
                                   "Bitta son kiriting, masalan: <code>200</code>",
        "post_stars_bad_amount": "⚠️ <b>Noto'g'ri son.</b>\n\n"
                                 "Bitta butun son yozing, masalan: <code>200</code>\n"
                                 "Minimal: {min_stars} ⭐",
        "post_stars_ask_link": "🔗 <b>Post havolasini yuboring</b>\n\n"
                               "Masalan:\n<code>https://t.me/username/123</code>",
        "post_stars_bad_link": "⚠️ <b>Noto'g'ri havola.</b>\n\n"
                               "Telegram post havolasini yuboring, masalan:\n"
                               "<code>https://t.me/username/123</code>",
        "post_stars_summary": "✅ <b>Ma'lumotlar</b>\n\n"
                              "⭐ Stars: <b>{amount}</b>\n"
                              "🔗 Post: <code>{link}</code>\n"
                              "💵 To'lanadigan summa: <b>{price} so'm</b>\n"
                              "👛 Hisobingiz: <b>{balance} so'm</b>\n\n"
                              "Tasdiqlasangiz summa hisobingizdan yechiladi va postga yuboriladi.",
        "post_confirm": "✅ Tasdiqlash",
        "post_cancel": "❌ Bekor qilish",
        "post_cancelled": "❌ <b>Bekor qilindi.</b>\n\n"
                          "Summa hisobingizda qoldi: <b>{balance} so'm</b>",
        "post_insufficient": "⚠️ <b>Hisobingizni to'ldiring.</b>\n\n"
                             "Balansingizda yetarli pul yo'q.\n"
                             "Sizda: <b>{balance} so'm</b>\n"
                             "Kerak: <b>{need} so'm</b>\n\n"
                             "Hisobni 👛 orqali to'ldiring.",
        "post_paid_ok": "✅ <b>Buyurtma qabul qilindi!</b>\n\n"
                        "📦 Buyurtma: #{order_id}\n"
                        "⭐ Stars: <b>{amount}</b>\n"
                        "🔗 Post: <code>{link}</code>\n"
                        "💵 To'landi: <b>{price} so'm</b>\n\n"
                        "🕐 En yaqin vaqtda postingizga yuboriladi.",
        "post_no_price": "⚠️ Admin narxni hali o'rnatmagan. "
                         "Iltimos, keyinroq urinib ko'ring.",
        "no_price": "⚠️ Narx belgilanmagan. Admin narxlarni o'rnatgach urinib ko'ring.",
        "post_stars_sent_admin": "📝 <b>Yangi post-stars so'rovi</b>\n\n"
                                 "ID: #{order_id}\n"
                                 "Foydalanuvchi: {user}\n"
                                 "Stars: <b>{amount}</b>\n"
                                 "Link: {link}\n\n"
                                 "Tasdiqlaysizmi?",
        "post_approved_user": "✅ <b>Postingizga tasdiqlandi!</b>\n\n"
                              "⭐ +{amount} Stars postgA yuborildi.",
        "post_approval_failed": "⚠️ <b>Postga stars yuborilmadi.</b>\n\n"
                                "{reason}",
        "post_rejected_user": "❌ <b>Postga stars so'rovi rad etildi.</b>\n\n"
                              "{reason}",
        "approve_button": "✅ Tasdiqlash",
        "reject_button": "❌ Rad etish",

        # --- Admin xabarlari ---
        "admin_new_order": "🆕 <b>Yangi buyurtma!</b>\n\n"
                           "Buyurtma: #{order_id}\n"
                           "Foydalanuvchi: {user}\n"
                           "Paket: <b>{amount} Stars</b>\n"
                           "To'lov: <b>{method}</b>\n"
                           "Izoh: {note}",
        "admin_approved": "✅ Buyurtma <b>#{order_id}</b> tasdiqlandi.",
        "admin_rejected": "❌ Buyurtma <b>#{order_id}</b> rad etildi.",

        # --- Admin panel ---
        "admin_panel": "🛠 <b>Admin paneli</b>\n\nTegishli bo'limni tanlang:",
        "admin_orders": "📦 Buyurtmalar",
        "admin_orders_pending": "⏳ Kutayotgan buyurtmalar:\n\n{orders}",
        "admin_orders_none": "Kutayotgan buyurtmalar yo'q.",
        "admin_users": "👥 Foydalanuvchilar",
        "admin_users_count": "👥 <b>Foydalanuvchilar</b>\n\nJami: {total}\n\n"
                             "Bir foydalanuvchini ko'rish uchun ID yuboring:",
        "admin_stats": "📊 Statistika",
        "admin_settings": "⚙️ Sozlamalar",
        "admin_accounts": "🔑 Akkauntlar",
        "admin_gifts": "🎁 Gift boshqarish",
        "admin_broadcast": "📣 Reklama / Xabar",
        "admin_faq": "❓ Javoblar / Yordam",
        "admin_vip": "👑 VIP sozlamalar",
        "admin_toggle": "🔋 Botni {'ON' | 'OFF'} qilish",
        "admin_bot_active": "✅ Bot holati: <b>Aktiv</b>",
        "admin_bot_inactive": "⛔️ Bot holati: <b>Nofaol</b>",
        "admin_toggled": "🔄 Bot holati yangilandi: {status}",
        "admin_send_new_price": "🖊 Yangi narxni yuboring\nFormati: <b>kirish_narx_karta:std</b>\n"
                                "Masalan: 15=30000,30=55000,50=90000,100=170000",
        "admin_price_updated": "✅ Narxlar yangilandi!", 
        "admin_invalid_format": "⚠️ Noto'g'ri format. Qaytadan yuboring.",

        # --- FAQ ---
        "faq": "❓ <b>Tez-tez so'raladigan savollar</b>\n\n"
               "1) Stars qancha vaqtda yetib boradi?\n"
               "   ➡️ Odatda 1-5 daqiqada.\n\n"
               "2) To'lov usullari?\n"
               "   ➡️ Karta yoki online API.\n\n"
               "3) Gift qanday olinadi?\n"
               "   ➡️ Akkaunt ulansangiz avtomatik keladi.\n\n"
               "4) Qaytarish sharti?\n"
               "   ➡️ Buyurtma tasdiqlangach qaytarilmaydi.\n\n"
               "Savolingiz qolsa <b>{admin}</b> ga murojaat qiling.",
        "in_development": "🚧 Bo'lim rivojlanmoqda...",

        # --- Statistika ---
        "stats_daily": "📊 <b>Kunlik sotuvlar</b>\n\nSotilgan: <b>{sold}</b> Stars\n"
                       "Summa: <b>{sum}</b>\nBuyurtmalar: <b>{count}</b>",
    },
    "en": {
        "start": "🚀 Welcome, <b>{first}</b>!\n\n"
                 "ℹ️ Buy <b>Telegram Stars</b> or send stars to your posts with this bot.\n\n"
                 "👇 Choose a section below:",
        "start_not_subscribed": "⚠️ <b>You must join our channel(s) to use the bot!</b>\n\n{channels}\n\nAfter subscribing press \"✅ Check\".",
        "start_bot_inactive": "⛔️ Bot temporarily unavailable. Try later.",
        "check_subscribe": "✅ Check",
        "subscribe_alert": "⚠️ <b>You must join our channel(s) first to use the bot!</b>",
        "back": "◀️ Back",
        "menu_buy": "🛒 Buy Stars",
        "menu_wallet": "👛 Balance",
        "menu_topup": "💳 Top up balance",
        "menu_gift": "🎁 Gift",
        "menu_subscribe": "♻️ Stars on post",
        "menu_stats": "📊 Statistics",
        "menu_pricing": "💲 Pricing",
        "menu_help": "❓ Help / FAQ",
        "menu_personal": "👤 Account",
        "menu_referral": "👥 Referral",

        # --- Referral program ---
        "referral_info": "👥 <b>Referral program</b>\n\n"
                         "When a friend you invited joins the bot and makes "
                         "their <b>first purchase</b>, you get "
                         "<b>{bonus} UZS</b>!\n\n"
                         "🔗 <b>Your link:</b>\n<code>{link}</code>\n\n"
                         "Share this link with friends. The bonus is paid "
                         "<b>only once</b> per referred user.\n\n"
                         "📊 Referrals: <b>{count}</b>\n"
                         "💵 Bonus earned: <b>{earned} UZS</b>\n\n"
                         "🕓 Latest referrals:\n{refs}",
        "referral_list_empty": "No referrals yet. Share your link with friends!",
        "referral_bonus_received": "🎉 <b>Congratulations!</b>\n\n"
                                   "A user you referred made their first purchase.\n"
                                   "<b>{amount} UZS</b> bonus was added to your balance 👥\n\n"
                                   "Check it in the 👛 Balance section.",
        "pricing_text": "📈 <b>Stars prices</b>\n\n{prices}\n\n"
                        "💰 Payment: card or online API\n⚡️ Instant delivery",
        "buy_choose": "🛒 <b>Choose a package:</b>\n\n{prices}\n\n"
                      "Your balance: <b>{balance} UZS</b>\n"
                      "To pay from balance choose <b>👛 From balance</b>.",
        "buy_package": "⭐ {amount} Stars",
        "buy_from_balance": "💳 Pay from balance",
        "buy_method": "💳 <b>Choose payment method</b> — for {amount} Stars.",
        "method_card": "💳 Card",
        "method_api": "🔗 Online API",
        "method_balance": "👛 From balance",
        "card_pay_instructions": "💳 <b>Make the payment</b>\n\n"
                                 "Package: <b>{amount} Stars</b>\nAmount: <b>{price}</b>\n\n"
                                 "Card number:\n<b><code>{card}</code></b>\n\n"
                                 "Press the button after paying — admin will check.",
        "card_paid": "📤 I've paid",
        "card_paid_note": "💰 <b>Send payment details</b>\n\n"
                          "Write payment info (receipt, amount) or send a screenshot. "
                          "The order then goes to admin approval.",
        "order_created_user": "✅ Order created!\n\n"
                              "📦 Order: <b>#{order_id}</b>\n"
                              "⭐ Package: <b>{amount} Stars</b>\n"
                              "💰 Payment: <b>{method}</b>\n"
                              "Status: <b>⏳ Pending</b>",
        "order_status_for_user": "📦 <b>Order #{order_id}</b>\n"
                                 "Package: <b>{amount} Stars</b>\n"
                                 "Status: {status}\n{note}",
        "api_order_creating": "🔗 <b>Sending order to API...</b>",
        "api_order_success": "✅ <b>Order delivered!</b>\n\n⭐ <b>+{amount} Stars</b> added to your balance.",
        "api_order_failed": "❌ <b>Order failed.</b>\n\nPlease contact admin or change payment method.",
        "insufficient_balance": "⚠️ <b>Insufficient balance!</b>\n\nYou have: {balance} Stars\nNeed: {need} Stars",
        "insufficient_sum": "⚠️ <b>Insufficient funds!</b>\n\nYou have: {balance} UZS\nNeed: {need} UZS",
        "balance_buy_ok": "🧾 <b>Paid from balance!</b>\n\n"
                          "💸 -{price} UZS (order #{order_id})\n"
                          "⭐ +{amount} Stars added.\n"
                          "Remaining: <b>{balance} UZS</b>",
        "balance_deducted": "🧾 <b>Paid from balance!</b>\n\n⭐ +{amount} Stars added (order #{order_id}).\nNew balance: <b>{balance} Stars</b>",
        "wallet_title": "👛 <b>Your balance</b>\n\n"
                        "💵 Money: <b>{sum} UZS</b>\n"
                        "⭐ Stars: <b>{balance} Stars</b>\n{progress}\n\n"
                        "📊 Bought total: <b>{bought}</b>\n📤 Sold total: <b>{sold}</b>\n🎁 Gifts received: <b>{gifted}</b>",
        "wallet_topup": "💳 <b>Top up balance in UZS</b>\n\n"
                        "Add <b>money (UZS)</b> by card or online payment, "
                        "then buy <b>Stars</b> with it.",
        "topup_sum_prompt": "💵 <b>Send the amount to top up in UZS</b>\n"
                            "Example: <code>100000</code>\n"
                            "Cancel: /start",
        "topup_card_pay": "💳 <b>Make the payment</b>\n\n"
                          "Amount: <b>{amount} UZS</b>\n\n"
                          "Card number:\n<b><code>{card}</code></b>\n\n"
                          "After paying send a proof (receipt, screenshot) — "
                          "admin will top up your balance.",
        "topup_sent_user": "⏳ <b>Request sent!</b>\n\n"
                           "After admin checks the payment, "
                           "<b>{amount} UZS</b> will be added to your balance.",
        "order_rejected_user": "❌ <b>Order #{order_id} was rejected.</b>\n\n"
                               "No money was added. Contact admin if you have questions.",
        "topup_api_success": "✅ <b>Balance topped up!</b>\n\n"
                             "🆕 Money balance: <b>{balance} UZS</b>",
        "topup_sent_admin": "💰 <b>New top-up request</b>\n\n"
                            "📋 Bot ID: <code>{uid}</code>\n"
                            "👤 {user}\n"
                            "💵 Amount: <b>{amount} UZS</b>\n"
                            "📄 Proof: {proof}",
        "topup_enough": "✅ <b>Balance topped up!</b>\n\n🆕 Money balance: <b>{balance} UZS</b>",
        "wallet_history": "📜 <b>Transaction history</b>\n\n{history}\n\n",
        "tx_none": "No transactions yet.",
        "gift_menu": "🎁 <b>Gift section</b>\n\nBuy or send Telegram gifts.\n\n👛 Balance: <b>{balance} UZS</b>",
        "gift_buy": "🎁 Buy gift",
        "gift_send": "📤 Send gift",
        "gift_choose_pack": "🎁 <b>Choose gift package</b> — the gift will be auto-sent to your account.",
        "gift_choose_catalog": "🎁 <b>Choose a gift</b> — press one below (price is deducted from your UZS balance):",
        "gift_empty": "😕 <b>No gifts available yet.</b>\n\nGifts will be added soon (managed via admin panel).",
        "gift_need_phone": "🎁 <b>Gift: {name}</b>\n\n"
                           "💰 Price: <b>{price} UZS</b>\n"
                           "⭐ Stars: <b>{stars}</b>\n\n"
                           "Send the recipient's <b>@username</b> or <b>phone number</b>:\n"
                           "(e.g. <code>@ali</code> or <code>+998901234567</code>)\n\nThe account must be connected.",
        "gift_sent": "✅ <b>Gift delivered!</b>\n\n🎁 <b>{amount} Stars</b> gift ({name}) sent.\nBalance: <b>{balance} UZS</b>",
        "gift_received": "🎁 <b>New gift!</b>\n\n{amount} Stars gift received on your account.",
        "invalid_phone": "⚠️ Invalid format. Send @username or phone number.\nExample: <code>@ali</code> or <code>+998901234567</code>",
"post_stars_request": "📝 <b>Give stars to post</b>\n\nChoose how many stars you need 👇",
        "post_custom_amount": "✍️ Enter myself",
        "post_stars_custom_prompt": "🔢 <b>How many stars?</b>\n\n"
                                   "Send a number, e.g.: <code>200</code>",
        "post_stars_bad_amount": "⚠️ <b>Invalid number.</b>\n\n"
                                 "Send a whole number, e.g.: <code>200</code>\n"
                                 "Minimum: {min_stars} ⭐",
        "post_stars_ask_link": "🔗 <b>Send the post link</b>\n\nExample:\n<code>https://t.me/username/123</code>",
        "post_stars_bad_link": "⚠️ <b>Invalid link.</b>\n\nSend a Telegram post link, e.g.:\n"
                               "<code>https://t.me/username/123</code>",
        "post_stars_summary": "✅ <b>Summary</b>\n\n"
                              "⭐ Stars: <b>{amount}</b>\n"
                              "🔗 Post: <code>{link}</code>\n"
                              "💵 Amount to pay: <b>{price} UZS</b>\n"
                              "👛 Your balance: <b>{balance} UZS</b>\n\n"
                              "If you confirm, the amount will be deducted and sent to the post.",
        "post_confirm": "✅ Confirm",
        "post_cancel": "❌ Cancel",
        "post_cancelled": "❌ <b>Cancelled.</b>\n\n"
                          "Your balance is untouched: <b>{balance} UZS</b>",
        "post_insufficient": "⚠️ <b>Replenish your account.</b>\n\n"
                             "Your balance is insufficient.\n"
                             "You have: <b>{balance} UZS</b>\n"
                             "Need: <b>{need} UZS</b>\n\n"
                             "Top up via 👛.",
        "post_paid_ok": "✅ <b>Order accepted!</b>\n\n"
                        "📦 Order: #{order_id}\n"
                        "⭐ Stars: <b>{amount}</b>\n"
                        "🔗 Post: <code>{link}</code>\n"
                        "💵 Paid: <b>{price} UZS</b>\n\n"
                        "🕐 Will be sent to your post shortly.",
        "post_no_price": "⚠️ The admin has not set a price yet. "
                         "Please try again later.",
        "no_price": "⚠️ Price not configured. Try again after the admin sets prices.",
        "post_stars_sent_admin": "📝 <b>New post-stars request</b>\n\n"
                                 "ID: #{order_id}\nUser: {user}\nStars: <b>{amount}</b>\nLink: {link}\n\nApprove?",
        "post_approved_user": "✅ <b>Post approved!</b>\n\n⭐ +{amount} Stars sent to your post.",
        "post_approval_failed": "⚠️ <b>Stars not sent to the post.</b>\n\n{reason}",
        "post_rejected_user": "❌ <b>Post stars rejected.</b>\n\n{reason}",
        "approve_button": "✅ Approve",
        "reject_button": "❌ Reject",
        "admin_new_order": "🆕 <b>New order!</b>\n\nOrder: #{order_id}\nUser: {user}\n"
                           "Package: <b>{amount} Stars</b>\nPayment: <b>{method}</b>\nNote: {note}",
        "admin_approved": "✅ Order <b>#{order_id}</b> approved.",
        "admin_rejected": "❌ Order <b>#{order_id}</b> rejected.",
        "admin_panel": "🛠 <b>Admin panel</b>\n\nChoose section:",
        "admin_orders": "📦 Orders",
        "admin_orders_pending": "⏳ Pending orders:\n\n{orders}",
        "admin_orders_none": "No pending orders.",
        "admin_users": "👥 Users",
        "admin_users_count": "👥 <b>Users</b>\n\nTotal: {total}\n\nSend an ID to view a user:",
        "admin_stats": "📊 Statistics",
        "admin_settings": "⚙️ Settings",
        "admin_accounts": "🔑 Accounts",
        "admin_gifts": "🎁 Gift management",
        "admin_broadcast": "📣 Broadcast",
        "admin_faq": "❓ FAQ / Help",
        "admin_vip": "👑 VIP settings",
        "admin_toggle": "🔋 Toggle bot ON/OFF",
        "admin_bot_active": "✅ Bot status: <b>Active</b>",
        "admin_bot_inactive": "⛔️ Bot status: <b>Inactive</b>",
        "admin_toggled": "🔄 Bot status updated: {status}",
        "admin_send_new_price": "🖊 Send new prices\nFormat: <b>amount=price</b>, comma separated\nExample: 15=30000,30=55000",
        "admin_price_updated": "✅ Prices updated!",
        "admin_invalid_format": "⚠️ Invalid format. Send again.",
        "faq": "❓ <b>Frequently Asked Questions</b>\n\n"
               "1) How fast are Stars delivered?\n   ➡️ Usually 1-5 minutes.\n\n"
               "2) Payment methods?\n   ➡️ Card or online API.\n\n"
               "3) How to get gifts?\n   ➡️ Connect your account and it arrives automatically.\n\n"
               "4) Refund policy?\n   ➡️ No refunds after order approval.\n\n"
               "More questions? Contact <b>{admin}</b>.",
        "in_development": "🚧 Section under development...",
        "stats_daily": "📊 <b>Daily sales</b>\n\nSold: <b>{sold}</b> Stars\nSum: <b>{sum}</b>\nOrders: <b>{count}</b>",
    },
    "ru": {
        "start": "🚀 Добро пожаловать, <b>{first}</b>!\n\n"
                 "ℹ️ Покупайте <b>Telegram Stars</b> или отправляйте звёзды на свои посты.\n\n"
                 "👇 Выберите раздел:",
        "start_not_subscribed": "⚠️ <b>Для использования бота нужно подписаться на наш(и) канал(ы)!</b>\n\n{channels}\n\nПосле подписки нажмите «✅ Проверить».",
        "start_bot_inactive": "⛔️ Бот временно недоступен. Попробуйте позже.",
        "check_subscribe": "✅ Проверить",
        "subscribe_alert": "⚠️ <b>Для использования бота сначала подпишитесь на канал(ы)!</b>",
        "back": "◀️ Назад",
        "menu_buy": "🛒 Купить звёзды",
        "menu_wallet": "👛 Баланс",
        "menu_topup": "💳 Пополнить баланс",
        "menu_gift": "🎁 Подарок",
        "menu_subscribe": "♻️ Звёзды на пост",
        "menu_stats": "📊 Статистика",
        "menu_pricing": "💲 Цены",
        "menu_help": "❓ Помощь / FAQ",
        "menu_personal": "👤 Кабинет",
        "menu_referral": "👥 Реферальная",

        # --- Реферальная программа ---
        "referral_info": "👥 <b>Реферальная программа</b>\n\n"
                         "Когда друг, которого вы пригласили, зайдёт в бота "
                         "и совершит <b>первую покупку</b>, вам начислится "
                         "<b>{bonus} сум</b>!\n\n"
                         "🔗 <b>Ваша ссылка:</b>\n<code>{link}</code>\n\n"
                         "Отправляйте её друзьям. Бонус выплачивается "
                         "<b>только один раз</b> за каждого приглашённого.\n\n"
                         "📊 Приглашено: <b>{count}</b>\n"
                         "💵 Получено бонусов: <b>{earned} сум</b>\n\n"
                         "🕓 Последние рефералы:\n{refs}",
        "referral_list_empty": "Пока рефералов нет. Поделитесь своей ссылкой с друзьями!",
        "referral_bonus_received": "🎉 <b>Поздравляем!</b>\n\n"
                                   "Приглашённый вами пользователь совершил первую покупку.\n"
                                   "На ваш баланс начислено <b>{amount} сум</b> 👥\n\n"
                                   "Посмотреть можно в разделе 👛 Баланс.",
        "pricing_text": "📈 <b>Цены на звёзды</b>\n\n{prices}\n\n"
                        "💰 Оплата: карта или онлайн API\n⚡️ Мгновенная доставка",
        "buy_choose": "🛒 <b>Выберите пакет:</b>\n\n{prices}\n\n"
                      "Ваш баланс: <b>{balance} сум</b>.\n"
                      "Для оплаты с баланса выберите <b>👛 С баланса</b>.",
        "buy_package": "⭐ {amount} звёзд",
        "buy_from_balance": "💳 Оплатить с баланса",
        "buy_method": "💳 <b>Выберите способ оплаты</b> — за {amount} звёзд.",
        "method_card": "💳 Карта",
        "method_api": "🔗 Онлайн API",
        "method_balance": "👛 С баланса",
        "card_pay_instructions": "💳 <b>Произведите оплату</b>\n\n"
                                 "Пакет: <b>{amount} звёзд</b>\nСумма: <b>{price}</b>\n\n"
                                 "Номер карты:\n<b><code>{card}</code></b>\n\n"
                                 "Нажмите кнопку после оплаты — админ проверит.",
        "card_paid": "📤 Я оплатил",
        "card_paid_note": "💰 <b>Отправьте данные об оплате</b>\n\n"
                          "Напишите информацию (чек, сумму) или отправьте скрин. "
                          "Заказ уйдёт на подтверждение админу.",
        "order_created_user": "✅ Заказ создан!\n\n"
                              "📦 Заказ: <b>#{order_id}</b>\n"
                              "⭐ Пакет: <b>{amount} звёзд</b>\n"
                              "💰 Оплата: <b>{method}</b>\n"
                              "Статус: <b>⏳ Ожидание</b>",
        "order_status_for_user": "📦 <b>Заказ #{order_id}</b>\n"
                                 "Пакет: <b>{amount} звёзд</b>\n"
                                 "Статус: {status}\n{note}",
        "api_order_creating": "🔗 <b>Заказ отправляется в API...</b>",
        "api_order_success": "✅ <b>Заказ выполнен!</b>\n\n⭐ <b>+{amount} звёзд</b> добавлено на баланс.",
        "api_order_failed": "❌ <b>Заказ не выполнен.</b>\n\nСвяжитесь с админом или смените способ оплаты.",
        "insufficient_balance": "⚠️ <b>Недостаточно баланса!</b>\n\nУ вас: {balance} звёзд\nНужно: {need} звёзд",
        "insufficient_sum": "⚠️ <b>Недостаточно средств!</b>\n\nУ вас: {balance} сум\nНужно: {need} сум",
        "balance_buy_ok": "🧾 <b>Оплачено с баланса!</b>\n\n"
                          "💸 -{price} сум (заказ #{order_id})\n"
                          "⭐ +{amount} звёзд добавлено.\n"
                          "Остаток: <b>{balance} сум</b>",
        "balance_deducted": "🧾 <b>Оплачено с баланса!</b>\n\n⭐ +{amount} звёзд добавлено (заказ #{order_id}).\nНовый баланс: <b>{balance} звёзд</b>",
"wallet_title": "👛 <b>Ваш баланс</b>\n\n"
                        "💵 Деньги: <b>{sum} сум</b>\n"
                        "⭐ Звёзды: <b>{balance} звёзд</b>\n{progress}\n\n"
                        "📊 Куплено всего: <b>{bought}</b>\n📤 Продано всего: <b>{sold}</b>\n🎁 Подарков получено: <b>{gifted}</b>",
        "wallet_topup": "💳 <b>Пополнение в сумах</b>\n\n"
                        "Пополните <b>наличные (сум)</b> картой или онлайн-оплатой, "
                        "а затем купите <b>звёзды</b> за эти деньги.",
        "topup_sum_prompt": "💵 <b>Отправьте сумму пополнения в сумах</b>\n"
                            "Например: <code>100000</code>\n"
                            "Отмена: /start",
        "topup_card_pay": "💳 <b>Произведите оплату</b>\n\n"
                          "Сумма: <b>{amount} сум</b>\n\n"
                          "Номер карты:\n<b><code>{card}</code></b>\n\n"
                          "После оплаты отправьте чек/скрин — админ пополнит баланс.",
        "topup_sent_user": "⏳ <b>Запрос отправлен!</b>\n\n"
                           "После проверки админ добавит <b>{amount} сум</b> на ваш баланс.",
        "order_rejected_user": "❌ <b>Заказ #{order_id} отклонён.</b>\n\n"
                               "Деньги не начислены. Свяжитесь с админом при вопросах.",
        "topup_api_success": "✅ <b>Баланс пополнен!</b>\n\n"
                             "🆕 Денежный баланс: <b>{balance} сум</b>",
        "topup_sent_admin": "💰 <b>Новый запрос на пополнение</b>\n\n"
                            "📋 Bot ID: <code>{uid}</code>\n"
                            "👤 {user}\n"
                            "💵 Сумма: <b>{amount} сум</b>\n"
                            "📄 Чек: {proof}",
        "topup_enough": "✅ <b>Баланс пополнен!</b>\n\n🆕 Денежный баланс: <b>{balance} сум</b>",
        "wallet_history": "📜 <b>История операций</b>\n\n{history}\n\n",
        "tx_none": "Пока операций нет.",
        "gift_menu": "🎁 <b>Раздел подарков</b>\n\nПокупка и отправка подарков Telegram.\n\n👛 Баланс: <b>{balance} сум</b>",
        "gift_buy": "🎁 Купить подарок",
        "gift_send": "📤 Отправить подарок",
        "gift_choose_pack": "🎁 <b>Выберите пакет подарка</b> — подарок будет отправлен на ваш аккаунт автоматически.",
        "gift_choose_catalog": "🎁 <b>Выберите подарок</b> — нажмите ниже (цена спишется с сумового баланса):",
        "gift_empty": "😕 <b>Подарков пока нет.</b>\n\nПодарки скоро появятся (управляется в админ-панели).",
        "gift_need_phone": "🎁 <b>Подарок: {name}</b>\n\n"
                           "💰 Цена: <b>{price} сум</b>\n"
                           "⭐ Звёзды: <b>{stars}</b>\n\n"
                           "Отправьте <b>@username</b> или <b>номер телефона</b> получателя:\n"
                           "(например <code>@ali</code> или <code>+998901234567</code>)\n\nАккаунт должен быть подключён.",
        "gift_sent": "✅ <b>Подарок доставлен!</b>\n\n🎁 <b>{amount} звёзд</b> ({name}) отправлено.\nБаланс: <b>{balance} сум</b>",
        "gift_received": "🎁 <b>Новый подарок!</b>\n\nНа ваш аккаунт пришёл подарок на {amount} звёзд.",
        "invalid_phone": "⚠️ Неверный формат. Отправьте @username или номер телефона.\nПример: <code>@ali</code> или <code>+998901234567</code>",
"post_stars_request": "📝 <b>Отправка звёзд на пост</b>\n\nВыберите, сколько звёзд вам нужно 👇",
        "post_custom_amount": "✍️ Введу сам",
        "post_stars_custom_prompt": "🔢 <b>Сколько звёзд нужно?</b>\n\n"
                                   "Напишите число, например: <code>200</code>",
        "post_stars_bad_amount": "⚠️ <b>Неверное число.</b>\n\n"
                                 "Напишите целое число, например: <code>200</code>\n"
                                 "Минимум: {min_stars} ⭐",
        "post_stars_ask_link": "🔗 <b>Отправьте ссылку на пост</b>\n\nНапример:\n<code>https://t.me/username/123</code>",
        "post_stars_bad_link": "⚠️ <b>Неверная ссылка.</b>\n\nОтправьте ссылку на пост в Telegram, например:\n"
                               "<code>https://t.me/username/123</code>",
        "post_stars_summary": "✅ <b>Данные</b>\n\n"
                              "⭐ Звёзды: <b>{amount}</b>\n"
                              "🔗 Пост: <code>{link}</code>\n"
                              "💵 К оплате: <b>{price} сум</b>\n"
                              "👛 Ваш баланс: <b>{balance} сум</b>\n\n"
                              "При подтверждении сумма спишется и будет отправлена на пост.",
        "post_confirm": "✅ Подтвердить",
        "post_cancel": "❌ Отменить",
        "post_cancelled": "❌ <b>Отменено.</b>\n\n"
                          "Сумма осталась на счёте: <b>{balance} сум</b>",
        "post_insufficient": "⚠️ <b>Пополните счёт.</b>\n\n"
                             "Недостаточно средств.\n"
                             "У вас: <b>{balance} сум</b>\n"
                             "Нужно: <b>{need} сум</b>\n\n"
                             "Пополните через 👛.",
        "post_paid_ok": "✅ <b>Заказ принят!</b>\n\n"
                        "📦 Заказ: #{order_id}\n"
                        "⭐ Звёзды: <b>{amount}</b>\n"
                        "🔗 Пост: <code>{link}</code>\n"
                        "💵 Оплачено: <b>{price} сум</b>\n\n"
                        "🕐 Будет отправлено на ваш пост в ближайшее время.",
        "post_no_price": "⚠️ Администратор ещё не установил цену. "
                         "Пожалуйста, попробуйте позже.",
        "no_price": "⚠️ Цена не настроена. Попробуйте позже, когда админ установит цены.",
        "post_stars_sent_admin": "📝 <b>Новый запрос звёзд на пост</b>\n\n"
                                 "ID: #{order_id}\nПользователь: {user}\nЗвёзды: <b>{amount}</b>\nСсылка: {link}\n\nПодтверждаете?",
        "post_approved_user": "✅ <b>Пост подтверждён!</b>\n\n⭐ +{amount} звёзд отправлено на пост.",
        "post_approval_failed": "⚠️ <b>Звёзды не отправлены на пост.</b>\n\n{reason}",
        "post_rejected_user": "❌ <b>Звёзды на пост отклонены.</b>\n\n{reason}",
        "approve_button": "✅ Подтвердить",
        "reject_button": "❌ Отклонить",
        "admin_new_order": "🆕 <b>Новый заказ!</b>\n\nЗаказ: #{order_id}\nПользователь: {user}\n"
                           "Пакет: <b>{amount} звёзд</b>\nОплата: <b>{method}</b>\nЗаметка: {note}",
        "admin_approved": "✅ Заказ <b>#{order_id}</b> подтверждён.",
        "admin_rejected": "❌ Заказ <b>#{order_id}</b> отклонён.",
        "admin_panel": "🛠 <b>Панель администратора</b>\n\nВыберите раздел:",
        "admin_orders": "📦 Заказы",
        "admin_orders_pending": "⏳ Ожидающие заказы:\n\n{orders}",
        "admin_orders_none": "Ожидающих заказов нет.",
        "admin_users": "👥 Пользователи",
        "admin_users_count": "👥 <b>Пользователи</b>\n\nВсего: {total}\n\nОтправьте ID для просмотра:",
        "admin_stats": "📊 Статистика",
        "admin_settings": "⚙️ Настройки",
        "admin_accounts": "🔑 Аккаунты",
        "admin_gifts": "🎁 Управление подарками",
        "admin_broadcast": "📣 Рассылка",
        "admin_faq": "❓ FAQ / Помощь",
        "admin_vip": "👑 VIP настройки",
        "admin_toggle": "🔋 Вкл/выкл бота",
        "admin_bot_active": "✅ Статус: <b>Активен</b>",
        "admin_bot_inactive": "⛔️ Статус: <b>Неактивен</b>",
        "admin_toggled": "🔄 Статус обновлён: {status}",
        "admin_send_new_price": "🖊 Отправьте новые цены\nФормат: <b>количество=цена</b>, через запятую\nПример: 15=30000,30=55000",
        "admin_price_updated": "✅ Цены обновлены!",
        "admin_invalid_format": "⚠️ Неверный формат. Отправьте снова.",
        "faq": "❓ <b>Частые вопросы</b>\n\n"
               "1) Как быстро доставляются звёзды?\n   ➡️ Обычно 1-5 минут.\n\n"
               "2) Способы оплаты?\n   ➡️ Карта или онлайн API.\n\n"
               "3) Как получить подарки?\n   ➡️ Подключите аккаунт, придёт автоматически.\n\n"
               "4) Возврат?\n   ➡️ После подтверждения возврат не предусмотрен.\n\n"
               "Вопросы? Пишите <b>{admin}</b>.",
        "in_development": "🚧 Раздел в разработке...",
        "stats_daily": "📊 <b>Продажи за день</b>\n\nПродано: <b>{sold}</b> звёзд\nСумма: <b>{sum}</b>\nЗаказов: <b>{count}</b>",
    },
}

# Statuslarni chiroyli ko'rsatish uchun
STATUS_LABELS: dict[str, dict[str, str]] = {
    "pending": {"uz": "⏳ Kutmoqda", "en": "⏳ Pending", "ru": "⏳ Ожидание"},
    "processing": {"uz": "⚙️ Jarayonda", "en": "⚙️ Processing", "ru": "⚙️ В процессе"},
    "approved": {"uz": "✅ Tasdiqlandi", "en": "✅ Approved", "ru": "✅ Подтверждён"},
    "rejected": {"uz": "❌ Rad etildi", "en": "❌ Rejected", "ru": "❌ Отклонён"},
    "done": {"uz": "✅ Yetkazildi", "en": "✅ Delivered", "ru": "✅ Доставлен"},
    "canceled": {"uz": "🚫 Bekor qilindi", "en": "🚫 Canceled", "ru": "🚫 Отменён"},
}


def t(lang: str, key: str, **kwargs: object) -> str:
    """Berilgan tildagi xabarni qaytaradi, so'ng formatlaydi."""
    lang = lang if lang in TRANSLATIONS else "uz"
    msg = TRANSLATIONS[lang].get(key) or TRANSLATIONS["uz"].get(key, key)
    try:
        return msg.format(**kwargs)
    except (KeyError, IndexError):
        return msg


def status_label(lang: str, status: str) -> str:
    """Buyurtma statusining chiroyli matni."""
    d = STATUS_LABELS.get(status, {})
    return d.get(lang, d.get("en", status))


def normalize_lang(value: str | None) -> str:
    """Kiritilgan tilni standartlashtiradi (default: uz)."""
    if value in ("uz", "en", "ru"):
        return value
    return "uz"


def lang_choice_keyboard_labels() -> list[str]:
    return ["🇺🇿 O'zbekcha", "🇬🇧 English", "🇷🇺 Русский"]