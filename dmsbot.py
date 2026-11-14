import os
from dotenv import load_dotenv
import aiohttp
import asyncio
import time
import html
import traceback
import sys
import re
import json
import imaplib
import hashlib
import email
from datetime import datetime

from pyrogram import Client, filters, enums, idle
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import SessionPasswordNeeded, FloodWait, UserNotParticipant, UserAlreadyParticipant
from pyrogram.raw.functions.messages import GetChatInviteImporters, CheckChatInvite
from pyrogram.raw.types import InputUserEmpty, InputUser
from pyrogram.handlers import MessageHandler, CallbackQueryHandler, ChatJoinRequestHandler

# ================= ENVIRONMENT CONFIGURATION =================
load_dotenv()
def _env_int(name, default):
    try: return int(os.getenv(name, str(default)).strip())
    except (TypeError, ValueError): return default

def _env_int_list(name, default=""):
    raw = os.getenv(name, default)
    return [int(x.strip()) for x in raw.split(",") if x.strip().lstrip("-").isdigit()]

API_ID = _env_int("API_ID", 0)
API_HASH = os.getenv("API_HASH", "").strip()
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMINS = _env_int_list("ADMINS", "")
BOT_SESSION_NAME = os.getenv("BOT_SESSION_NAME", "DMSSBOT").strip()
TERMS_URL = os.getenv("TERMS_URL", "https://telegra.ph/Zentro-Ads-Terms-and-Conditions-08-22").strip()
GMAIL_USER = os.getenv("GMAIL_USER", "").strip()
GMAIL_PASS = os.getenv("GMAIL_PASS", "").strip()
FF_WORKERS = _env_int("FF_WORKERS", 20)
DATA_FILE = os.getenv("DATA_FILE", "dmss_data.json").strip()

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise RuntimeError("Missing API_ID, API_HASH or BOT_TOKEN in .env. Copy .env.example to .env and fill them in.")

bot = Client(BOT_SESSION_NAME, api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

# ================= 🌟 CUSTOMIZATION HUB (WITH YOUR CUSTOM EMOJI IDs) 🌟 =================
BTN_EMOJIS = {
    "start": "5780773956030043338",   # 🚀
    "user": "6267150926100829360",    # 👨‍🏫 (User/Profile)
    "money": "6030734193594470413",   # 💵
    "diamond": "6030811868078018748", # 💎
    "add": "6032733629719777782",     # ➕
    "cross": "6032606743500951856",   # ❌
    "tick": "6034905633336070030",    # ✅
    "home": "5780385815540535887",    # 🗽
    "shield": "6282846669335702032",  # 🔒
    "setting": "6033129724488715918", # 🧩
    "target": "6030880810893053589",  # 📍
    "globe": "6014898614814382254",   # 🌐
    "stats": "5972211201147408942",   # 📱
    "cal": "6014861794059752708",     # 🗓
    "gift": "5785281906459283269",    # 🎁
    "wait": "6267229004311303657",    # ⌛
    "crown": "5798670723975221399",   # 👑
    "ban": "6032707305865220377",     # 🚫
    "refresh": "6035353718684129368"  # 🔄
}

# ================= DEVELOPER CREDIT REMOVED =================

# ================= LANGUAGE / ONBOARDING =================
LANGUAGES = {
    "en": "🇬🇧 English", "ru": "🇷🇺 Русский", "fa": "🇮🇷 فارسی",
    "zh": "🇨🇳 中文", "es": "🇪🇸 Español", "fr": "🇫🇷 Français",
    "ar": "🇸🇦 العربية", "pt": "🇵🇹 Português", "id": "🇮🇩 Bahasa Indonesia",
    "hi": "🇮🇳 हिन्दी"
}
LANG_TEXT = {
 "en": {"choose":"🌐 <b>Choose Your Language</b>\nSelect the language you want to use in the bot.",
        "terms":"<b>Terms and Conditions</b>\n\nRead our Terms of Service Before going further in the bot.\n\nBy continuing in this bot you agree to our Terms of Service",
        "dashboard":"Dashboard","language_saved":"Language saved successfully.","welcome":"Welcome to the dashboard.",
        "back":"Back to Dashboard","cancel":"Cancel","help":"Available commands: /start, /language, /help, /status",
        "status":"Bot is online. Your account is active.",
        "add_session":"Add Session","remove_session":"Remove Session","my_account":"My Account","vip_premium":"VIP Premium",
        "set_msg":"Set Message","fast_fwd":"FAST Auto-Forward DM","join_req_dm":"JOIN REQ DM","invite_earn":"Invite & Earn",
        "open_menu":"Open Menu","updates":"Updates","community":"Community","change_lang":"Change Language 🌍","support":"Support"},
 "hi": {"choose":"🌐 <b>अपनी भाषा चुनें</b>\nबॉट में इस्तेमाल करने के लिए भाषा चुनें।",
        "terms":"<b>नियम और शर्तें</b>\n\nबॉट में आगे बढ़ने से पहले हमारी सेवा की शर्तें पढ़ें।\n\nइस बॉट में जारी रखकर आप हमारी सेवा की शर्तों से सहमत हैं।",
        "dashboard":"डैशबोर्ड","language_saved":"भाषा सेव हो गई।","welcome":"डैशबोर्ड में आपका स्वागत है।",
        "back":"डैशबोर्ड पर वापस","cancel":"रद्द करें","help":"कमांड: /start, /language, /help, /status",
        "status":"बॉट ऑनलाइन है। आपका अकाउंट सक्रिय है।",
        "add_session":"सेशन जोड़ें","remove_session":"सेशन हटाएं","my_account":"मेरा खाता","vip_premium":"VIP प्रीमियम",
        "set_msg":"संदेश सेट करें","fast_fwd":"फ़ास्ट ऑटो-फ़ॉरवर्ड DM","join_req_dm":"जॉइन रिक्वेषट DM","invite_earn":"आमंत्रित करें और कमाएं",
        "open_menu":"ओपन मेनू","updates":"अपडेट्स","community":"कम्युनिटी","change_lang":"भाषा बदलें 🌍","support":"सपोर्ट"},
 "ru":{"choose":"🌐 <b>Выберите язык</b>\nВыберите язык для использования бота.",
       "terms":"<b>Условия использования</b>\n\nПрочитайте наши Условия обслуживания перед продолжением работы в боте.\n\nПродолжая использовать этого бота, вы соглашаетесь с нашими Условиями обслуживания",
       "dashboard":"Панель управления","language_saved":"Язык успешно сохранён.","welcome":"Добро пожаловать в панель управления.",
       "back":"Назад в панель","cancel":"Отмена","help":"Доступные команды: /start, /language, /help, /status","status":"Бот в сети. Ваш аккаунт активен.",
       "add_session":"Добавить сессию","remove_session":"Удалить сессию","my_account":"Мой аккаунт","vip_premium":"VIP Премиум",
       "set_msg":"Установить сообщение","fast_fwd":"Быстрый автопересыл DM","join_req_dm":"DM по заявкам","invite_earn":"Приглашай и зарабатывай",
       "open_menu":"Открыть меню","updates":"Обновления","community":"Сообщество","change_lang":"Изменить язык 🌍","support":"Поддержка"},
 "fa":{"choose":"🌐 <b>زبان خود را انتخاب کنید</b>\nزبان موردنظر برای استفاده از ربات را انتخاب کنید.",
       "terms":"<b>شرایط و ضوابط</b>\n\nقبل از ادامه کار در ربات، شرایط خدمات ما را بخوانید.\n\nبا ادامه استفاده از این ربات، شما با شرایط خدمات ما موافقت می‌کنید",
       "dashboard":"داشبورد","language_saved":"زبان با موفقیت ذخیره شد.","welcome":"به داشبورد خوش آمدید.",
       "back":"بازگشت به داشبورد","cancel":"لغو","help":"دستورات موجود: /start, /language, /help, /status","status":"ربات آنلاین است. حساب شما فعال است.",
       "add_session":"افزودن نشست","remove_session":"حذف نشست","my_account":"حساب من","vip_premium":"وی‌آی‌پی پریمیوم",
       "set_msg":"تنظیم پیام","fast_fwd":"ارسال خودکار سریع DM","join_req_dm":"DM درخواست عضویت","invite_earn":"دعوت و کسب درآمد",
       "open_menu":"باز کردن منو","updates":"به‌روزرسانی‌ها","community":"انجمن","change_lang":"تغییر زبان 🌍","support":"پشتیبانی"},
 "zh":{"choose":"🌐 <b>选择语言</b>\n请选择您在机器人中使用的语言。",
       "terms":"<b>条款与条件</b>\n\n在继续使用机器人之前，请阅读我们的服务条款。\n\n继续使用此机器人即表示您同意我们的服务条款",
       "dashboard":"控制面板","language_saved":"语言已保存。","welcome":"欢迎使用控制面板.",
       "back":"返回控制面板","cancel":"取消","help":"可用命令：/start, /language, /help, /status","status":"机器人在线，您的账户正常。",
       "add_session":"添加会话","remove_session":"删除会话","my_account":"我的账户","vip_premium":"VIP高级版",
       "set_msg":"设置消息","fast_fwd":"快速自动转发DM","join_req_dm":"加群申请DM","invite_earn":"邀请并赚钱",
       "open_menu":"打开菜单","updates":"更新","community":"社区","change_lang":"更改语言 🌍","support":"支持"},
 "es":{"choose":"🌐 <b>Elige tu idioma</b>\nSelecciona el idioma que deseas usar en el bot.",
       "terms":"<b>Términos y Condiciones</b>\n\nLea nuestros Términos de Servicio antes de continuar en el bot.\n\nAl continuar en este bot, acepta nuestros Términos de Servicio",
       "dashboard":"Panel","language_saved":"Idioma guardado correctamente.","welcome":"Bienvenido al panel.",
       "back":"Volver al panel","cancel":"Cancelar","help":"Comandos disponibles: /start, /language, /help, /status","status":"El bot está en línea. Tu cuenta está activa.",
       "add_session":"Agregar sesión","remove_session":"Eliminar sesión","my_account":"Mi cuenta","vip_premium":"VIP Premium",
       "set_msg":"Establecer mensaje","fast_fwd":"Auto-reenvío rápido DM","join_req_dm":"DM de solicitudes","invite_earn":"Invitar y ganar",
       "open_menu":"Abrir menú","updates":"Actualizaciones","community":"Comunidad","change_lang":"Cambiar idioma 🌍","support":"Soporte"},
 "fr":{"choose":"🌐 <b>Choisissez votre langue</b>\nSélectionnez la langue à utiliser dans le bot.",
       "terms":"<b>Termes et Conditions</b>\n\nVeuillez lire nos conditions de service avant de continuer dans le bot.\n\nEn continuant dans ce bot, vous acceptez nos conditions de service",
       "dashboard":"Tableau de bord","language_saved":"Langue enregistrée.","welcome":"Bienvenue sur le tableau de bord.",
       "back":"Retour au tableau de bord","cancel":"Annuler","help":"Commandes disponibles : /start, /language, /help, /status","status":"Le bot est en ligne. Votre compte est actif.",
       "add_session":"Ajouter une session","remove_session":"Supprimer la session","my_account":"Mon compte","vip_premium":"VIP Premium",
       "set_msg":"Définir le message","fast_fwd":"DM de réacheminement rapide","join_req_dm":"DM de demande d'adhésion","invite_earn":"Inviter et gagner",
       "open_menu":"Ouvrir le menu","updates":"Mises à jour","community":"Communauté","change_lang":"Changer de langue 🌍","support":"Support"},
 "ar":{"choose":"🌐 <b>اختر لغتك</b>\nحدد اللغة التي تريد استخدامها في البوت.",
       "terms":"<b>الشروط والأحكام</b>\n\nاقرأ شروط الخدمة الخاصة بنا قبل المتابعة في البوت.\n\nمن خلال الاستمرار في هذا البوت، فإنك توافق على شروط الخدمة الخاصة بنا",
       "dashboard":"لوحة التحكم","language_saved":"تم حفظ اللغة بنجاح.","welcome":"مرحباً بك في لوحة التحكم.",
       "back":"العودة إلى لوحة التحكم","cancel":"إلغاء","help":"الأوامر المتاحة: /start, /language, /help, /status","status":"البوت متصل وحسابك نشط.",
       "add_session":"إضافة جلسة","remove_session":"إزالة الجلسة","my_account":"حسابي","vip_premium":"VIP المميز",
       "set_msg":"تعيين الرسالة","fast_fwd":"إرسال سريع تلقائي DM","join_req_dm":"DM طلب الانضمام","invite_earn":"دعوة واربح",
       "open_menu":"فتح القائمة","updates":"التحديثات","community":"المجتمع","change_lang":"تغيير اللغة 🌍","support":"الدعم"},
 "pt":{"choose":"🌐 <b>Escolha seu idioma</b>\nSelecione o idioma que deseja usar no bot.",
       "terms":"<b>Termos e Condições</b>\n\nLeia nossos Termos de Serviço antes de prosseguir no bot.\n\nAo continuar neste bot, você concorda com nossos Termos de Serviço",
       "dashboard":"Painel","language_saved":"Idioma salvo com sucesso.","welcome":"Bem-vindo ao painel.",
       "back":"Voltar ao painel","cancel":"Cancelar","help":"Comandos disponibles: /start, /language, /help, /status","status":"O bot está online. Sua conta está ativa.",
       "add_session":"Adicionar sessão","remove_session":"Remover sessão","my_account":"Minha conta","vip_premium":"VIP Premium",
       "set_msg":"Definir mensagem","fast_fwd":"Encaminhamento rápido DM","join_req_dm":"DM de solicitação","invite_earn":"Convidar e ganhar",
       "open_menu":"Abrir menu","updates":"Atualizações","community":"Comunidade","change_lang":"Mudar idioma 🌍","support":"Suporte"},
 "id":{"choose":"🌐 <b>Pilih Bahasa Anda</b>\nPilih bahasa yang ingin digunakan di bot.",
       "terms":"<b>Syarat dan Ketentuan</b>\n\nBaca Ketentuan Layanan kami sebelum melanjutkan di bot.\n\nDengan melanjutkan di bot ini, Anda menyetujui Ketentuan Layanan kami",
       "dashboard":"Dasbor","language_saved":"Bahasa berhasil disimpan.","welcome":"Selamat datang di dasbor.",
       "back":"Kembali ke dasbor","cancel":"Batal","help":"Perintah yang tersedia: /start, /language, /help, /status","status":"Bot sedang online. Akun Anda aktif.",
       "add_session":"Tambah Sesi","remove_session":"Hapus Sesi","my_account":"Akun Saya","vip_premium":"VIP Premium",
       "set_msg":"Atur Pesan","fast_fwd":"Penerusan Otomatis Cepat DM","join_req_dm":"DM Permintaan Gabung","invite_earn":"Undang & Menangkan",
       "open_menu":"Buka Menu","updates":"Pembaruan","community":"Komunitas","change_lang":"Ganti Bahasa 🌍","support":"Dukung"}
}

def lang_for(user_id):
    return (users_col.data.get(str(user_id), {}) or {}).get("language", "en")
def tr(user_id, key):
    lang = lang_for(user_id)
    return LANG_TEXT.get(lang, LANG_TEXT["en"]).get(key, LANG_TEXT["en"].get(key, key))
def language_keyboard():
    rows=[]; row=[]
    for code, label in LANGUAGES.items():
        row.append(ibtn(label, f"setlang_{code}", style="primary", icon=BTN_EMOJIS["globe"]))
        if len(row)==2: rows.append(row); row=[]
    if row: rows.append(row)
    return {"inline_keyboard": rows}

# ================= IST TIME HELPERS =================
def get_ist(): return time.gmtime(time.time() + 19800)
def get_ist_str(fmt="%Y-%m-%d"): return time.strftime(fmt, get_ist())
def get_ist_ts_str(ts, fmt="%d %b %Y, %I:%M %p"): return time.strftime(fmt, time.gmtime(ts + 19800))

# ================= GMAIL SETUP =================
def check_payment_in_gmail(utr_to_find):
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_PASS)
        mail.select("inbox")
        status, messages = mail.search(None, f'(TEXT "{utr_to_find}")')
        if status == "OK" and messages[0]:
            mail_ids = messages[0].split()
            for mail_id in mail_ids[-1:]: 
                status, msg_data = mail.fetch(mail_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain": body += part.get_payload(decode=True).decode(errors='ignore')
                        else: body = msg.get_payload(decode=True).decode(errors='ignore')
                        clean_body = re.sub(r'\s+', ' ', body).upper()
                        amounts = re.findall(r'(?:₹|RS\.?|INR)\s*([\d\.]+)', clean_body)
                        if utr_to_find in clean_body and amounts:
                            mail.logout(); return float(amounts[0]) 
        mail.logout(); return None 
    except Exception: return None

# ================= PREMIUM ANIMATED TEXT EMOJIS =================
def e(eid, fb=""): return f"<tg-emoji emoji-id='{eid}'>{fb}</tg-emoji>"

E_CHK = e("6034905633336070030")   # ✅
E_DIA = e("6030811868078018748")   # 💎
E_SHD = e("6282846669335702032")   # 🔒
E_WRN = e("6267039884016358504")   # ⚠️
E_LNK = e("6267115986541877538")   # ⛓
E_CAL = e("6014861794059752708")   # 🗓
E_MED = e("6266851803103499415")   # 🎖️
E_TRI = e("6035134679647000020")   # 🔺
E_START = e("5780773956030043338") # 🚀
E_PROF = e("6267150926100829360")  # 👨‍🏫
E_ADD = e("6032733629719777782")   # ➕
E_WAIT = e("6267229004311303657")  # ⌛
E_SYNC = e("6035353718684129368")  # 🔄
E_ACT = e("6267107057304868214")   # ⚡️
E_ADM = e("6033129724488715918")   # 🧩
E_STAT = e("5972211201147408942")  # 📱
E_MONEY = e("6030734193594470413") # 💵
E_PREM = e("6266961380604123114")  # ⚜️
E_PLAY = e("6266829404849050968")  # ▶️
E_STOP = e("6267262260243076354")  # 🛑
E_CROSS = e("6032606743500951856") # ❌
E_GLOBE = e("6014898614814382254") # 🌐
E_DOT = e("6032975852990370635")   # 🟢
E_ID = e("6035239240625820254")    # 🆔
E_GIFT = e("5785281906459283269")  # 🎁
E_CROWN = e("5798670723975221399") # 👑

# --- RAW API ENGINE FOR COLOR BUTTONS ---
def ibtn(text, cb=None, url=None, style="primary", icon=None):
    if style not in ["primary", "danger", "success"]:
        style = "primary"
    btn = {"text": str(text), "style": style}
    if cb: btn["callback_data"] = cb 
    if url: btn["url"] = url
    if icon: btn["icon_custom_emoji_id"] = icon
    return btn

class MockMessage:
    def __init__(self, chat_id, message_id):
        self.chat = type('Chat', (), {'id': chat_id})()
        self.id = message_id

    async def delete(self):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={"chat_id": self.chat.id, "message_id": self.id})

async def api_send(chat_id, text, kb=None, photo=None):
    payload = {"chat_id": chat_id, "parse_mode": "HTML"}
    if text and not photo: payload["text"] = text
    elif text and photo: payload["caption"] = text
    if photo: payload["photo"] = photo
    if kb: payload["reply_markup"] = kb
    
    method = "sendPhoto" if photo else "sendMessage"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            if data.get("ok"): 
                return MockMessage(chat_id, data["result"]["message_id"])
                
    try:
        standard_kb = None
        if kb and "inline_keyboard" in kb:
            pyro_btns = []
            for row in kb["inline_keyboard"]:
                pyro_row = []
                for b in row:
                    pyro_row.append(InlineKeyboardButton(text=b.get("text",""), callback_data=b.get("callback_data"), url=b.get("url")))
                pyro_btns.append(pyro_row)
            standard_kb = InlineKeyboardMarkup(pyro_btns)
            
        if photo:
            m = await bot.send_photo(chat_id, photo=photo, caption=text, reply_markup=standard_kb, parse_mode=enums.ParseMode.HTML)
        else:
            m = await bot.send_message(chat_id, text, reply_markup=standard_kb, parse_mode=enums.ParseMode.HTML)
        return MockMessage(chat_id, m.id)
    except Exception:
        return MockMessage(chat_id, None)

async def api_edit(chat_id, msg_id, text, kb=None):
    payload = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "HTML"}
    if kb: payload["reply_markup"] = kb
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            if data.get("ok"): 
                return MockMessage(chat_id, data["result"]["message_id"])
                
    try:
        standard_kb = None
        if kb and "inline_keyboard" in kb:
            pyro_btns = []
            for row in kb["inline_keyboard"]:
                pyro_row = []
                for b in row:
                    pyro_row.append(InlineKeyboardButton(text=b.get("text",""), callback_data=b.get("callback_data"), url=b.get("url")))
                pyro_btns.append(pyro_row)
            standard_kb = InlineKeyboardMarkup(pyro_btns)
        m = await bot.edit_message_text(chat_id, msg_id, text, reply_markup=standard_kb, parse_mode=enums.ParseMode.HTML)
        return MockMessage(chat_id, m.id)
    except Exception:
        return MockMessage(chat_id, msg_id)

async def safe_edit(query, text, kb=None):
    chat_id = query.message.chat.id
    msg_id = query.message.id
    if query.message.photo or query.message.video or query.message.document:
        await query.message.delete()
        return await api_send(chat_id, text, kb=kb)
    else:
        return await api_edit(chat_id, msg_id, text, kb=kb)

# ================= IN-MEMORY STORAGE =================
class _AsyncCursor:
    def __init__(self, items):
        self.items = items
    def __aiter__(self):
        self._i = 0
        return self
    async def __anext__(self):
        if self._i >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self._i]
        self._i += 1
        return item
    async def to_list(self, length=None):
        return self.items if length is None else self.items[:length]

class _MemoryCollection:
    def __init__(self, storage_key):
        self.storage_key = storage_key
        self.data = {}
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                root = json.load(f)
            self.data = root.get(storage_key, {}) if isinstance(root, dict) else {}
        except (OSError, ValueError, TypeError):
            self.data = {}

    def _persist(self):
        try:
            root = {}
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    root = json.load(f)
            root[self.storage_key] = self.data
            tmp = DATA_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(root, f, ensure_ascii=False)
            os.replace(tmp, DATA_FILE)
        except Exception as exc:
            print(f"Database save error ({self.storage_key}): {type(exc).__name__}")

    async def find_one(self, query):
        if query.get("_id") in self.data:
            return dict(self.data[query["_id"]])
        for doc in self.data.values():
            if all(doc.get(k) == v for k, v in query.items()):
                return dict(doc)
        return None

    async def insert_one(self, doc):
        self.data[doc["_id"]] = dict(doc)
        self._persist()
        return type("Result", (), {"inserted_id": doc["_id"]})()

    def _set_path(self, doc, path, value):
        parts = path.split(".")
        cur = doc
        for part in parts[:-1]:
            if part not in cur or not isinstance(cur[part], dict):
                cur[part] = {}
            cur = cur[part]
        cur[parts[-1]] = value

    def _get_path(self, doc, path, default=0):
        cur = doc
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur:
                return default
            cur = cur[part]
        return cur

    def _match(self, doc, query):
        for key, expected in query.items():
            actual = self._get_path(doc, key, None)
            if isinstance(expected, dict):
                if "$gt" in expected and not (actual is not None and actual > expected["$gt"]): return False
                if "$gte" in expected and not (actual is not None and actual >= expected["$gte"]): return False
                if "$lt" in expected and not (actual is not None and actual < expected["$lt"]): return False
                if "$lte" in expected and not (actual is not None and actual <= expected["$lte"]): return False
            elif actual != expected:
                return False
        return True

    async def update_one(self, query, update, upsert=False):
        doc = None
        key = query.get("_id")
        if key is not None and key in self.data:
            doc = self.data[key]
        else:
            for k, candidate in self.data.items():
                if self._match(candidate, query):
                    key, doc = k, candidate
                    break
        if doc is None:
            if not upsert:
                return type("Result", (), {"matched_count": 0, "modified_count": 0})()
            doc = dict(query)
            key = query.get("_id", str(len(self.data)))
            doc["_id"] = key
            self.data[key] = doc

        for op, fields in update.items():
            for path, value in fields.items():
                if op == "$set":
                    self._set_path(doc, path, value)
                elif op == "$inc":
                    self._set_path(doc, path, self._get_path(doc, path, 0) + value)
                elif op in ("$push", "$addToSet"):
                    arr = self._get_path(doc, path, [])
                    if not isinstance(arr, list): arr = []
                    if op == "$push" or value not in arr:
                        arr.append(value)
                    self._set_path(doc, path, arr)
        self._persist()
        return type("Result", (), {"matched_count": 1, "modified_count": 1})()

    async def count_documents(self, query):
        return sum(1 for doc in self.data.values() if self._match(doc, query))

    def find(self, query):
        return _AsyncCursor([dict(d) for d in self.data.values() if self._match(d, query)])

    def aggregate(self, pipeline):
        items = [dict(d) for d in self.data.values()]
        for stage in pipeline:
            if "$match" in stage:
                items = [d for d in items if self._match(d, stage["$match"])]
            elif "$sort" in stage:
                for field, direction in reversed(list(stage["$sort"].items())):
                    items.sort(key=lambda d: self._get_path(d, field, 0), reverse=(direction < 0))
            elif "$limit" in stage:
                items = items[:stage["$limit"]]
        return _AsyncCursor(items)

users_col = _MemoryCollection("users")
settings_col = _MemoryCollection("settings")
USER_STATES, ACTIVE_TASKS = {}, {}

DEFAULT_CONFIG = {
    "_id": "config", "price_1d_inr": "25", "price_1d_usd": "0.5", "price_3d_inr": "60", "price_3d_usd": "1.5",
    "price_7d_inr": "120", "price_7d_usd": "3", "price_1m_inr": "350", "price_1m_usd": "8",
    "upi_fampay": "not_set", "upi_manual": "not_set", "crypto": "not_set", "auto_payment_status": False,
    "free_trial_limit": 100, "msg_delay": 0, "log_channel": "none", "success_log_channel": "none", "leaderboard_channel": "none",
    "free_channel_id": "none", "free_channel_link": "none", "total_sales_inr": 0, "total_sales_usd": 0, "global_dms": 0, "sales_history": {},
    "qr_fampay": "none", "qr_manual": "none", "qr_crypto": "none", "fsub_channels": [
        {"id": "none", "title": "Updates Channel", "link": "https://t.me/sexders"},
        {"id": "none", "title": "Community Group", "link": "https://t.me/sexdersgc"}
    ],
    "reqall_id": "none", "reqall_link": "none", "website_link": "not_set", "pending_bot_link": "not_set", "forward_bot_link": "not_set",
    "support_link": "https://t.me/sexderz", "updates_link": "https://t.me/sexders", "community_link": "https://t.me/sexdersgc",
    "ldb_time": 21, "free_req_limit": 300, "ref_bonus": 50, "maintenance": False
}

async def init_db():
    if await settings_col.find_one({"_id": "config"}) is None:
        await settings_col.insert_one(dict(DEFAULT_CONFIG))

# ================= HELPER FUNCTIONS =================
async def get_user(user_id):
    user_id = str(user_id)
    today = get_ist_str("%Y-%m-%d")
    user = await users_col.find_one({"_id": user_id})
    if not user:
        user = {"_id": user_id, "username": "", "banned": False, "premium_expiry": 0, "sessions": [], "saved_channels": [], "custom_msg_type": "text", "custom_msg": "HELLO", "custom_caption": "", "total_dms": 0, "daily_dms": 0, "last_date": today, "messaged_users": {}, "pending_chats": [], "language": "", "terms_accepted": False}
        await users_col.insert_one(user)
    else:
        if user.get("last_date") != today:
            await users_col.update_one({"_id": user_id}, {"$set": {"daily_dms": 0, "last_date": today}})
            user["daily_dms"] = 0; user["last_date"] = today
    return user

async def is_premium(user_id): return (await get_user(user_id)).get("premium_expiry", 0) > time.time()

# ================= BACKGROUND TASKS =================
async def auto_leaderboard_task():
    while True:
        try:
            config = await settings_col.find_one({"_id": "config"})
            ldb_channel = config.get("leaderboard_channel", "none")
            ldb_time = int(config.get("ldb_time", 21))
            
            if ldb_channel != "none" and get_ist().tm_hour == ldb_time:
                today = get_ist_str("%Y-%m-%d")
                last_post = config.get("last_ldb_post", "")
                if last_post != today:
                    top_today = await users_col.aggregate([{"$match": {"last_date": today, "daily_dms": {"$gt": 0}}}, {"$sort": {"daily_dms": -1}}, {"$limit": 10}]).to_list(10)
                    if top_today:
                        text = f"{E_MED} <i><b>Daily DM Leaderboard ({today})</b></i> {E_MED}\n\n"
                        for i, u in enumerate(top_today):
                            un = f"(@{u['username']})" if u.get('username') and u['username'] != "N/A" else ""
                            text += f"<i><b>{i+1}.</b> <code>...{str(u['_id'])[-4:]}</code> {un} - {u['daily_dms']} DMs</i>\n"
                        text += f"\n{E_START} <i>Automatically Generated</i>"
                        try:
                            lc_id = int(ldb_channel) if str(ldb_channel).replace("-", "").isdigit() else ldb_channel
                            await api_send(lc_id, text)
                            await settings_col.update_one({"_id": "config"}, {"$set": {"last_ldb_post": today}})
                        except Exception: pass
        except: pass
        await asyncio.sleep(1800)

# ================= CORE HANDLERS =================
async def handle_join_requests(client, message):
    user_id = str(message.from_user.id); chat_id = str(message.chat.id)
    await users_col.update_one({"_id": user_id}, {"$addToSet": {"pending_chats": chat_id}}, upsert=True)

async def check_force_join(user_id):
    if int(user_id) in ADMINS: return True, []
    config = await settings_col.find_one({"_id": "config"})
    fsub_channels = config.get("fsub_channels", [])
    not_joined = []
    
    for i, ch in enumerate(fsub_channels):
        chat_id = str(ch.get("id"))
        link = ch.get("link", "")
        title = ch.get("title", f"Channel {i+1}")
        if not chat_id or chat_id == "none": continue
        try:
            if chat_id.startswith("-100"): await bot.get_chat_member(int(chat_id), int(user_id))
            elif "t.me/" in chat_id: await bot.get_chat_member(chat_id.split("/")[-1], int(user_id))
            else: await bot.get_chat_member(chat_id, int(user_id))
        except UserNotParticipant: not_joined.append((title, link))
        except Exception: not_joined.append((title, link))

    reqall_id = config.get("reqall_id", "none")
    if reqall_id != "none":
        reqall_link = config.get("reqall_link", "none")
        try:
            if str(reqall_id).startswith("-100"): await bot.get_chat_member(int(reqall_id), int(user_id))
            elif "t.me/" in str(reqall_id): await bot.get_chat_member(str(reqall_id).split("/")[-1], int(user_id))
            else: await bot.get_chat_member(reqall_id, int(user_id))
        except UserNotParticipant: not_joined.append(("Mandatory Request", reqall_link))
        except Exception: not_joined.append(("Mandatory Request", reqall_link))

    return len(not_joined) == 0, not_joined


async def get_dashboard_menu(user_id, first_name, config):
    text = f"""{E_PREM} <i><b>@SEXDERS MASS DM ENGINE - Dashboard</b></i> {E_PREM}
<i>Advanced High-Speed Marketing & Telegram Outreach System</i>

━━━━━━━━━━━━━━━━━━━━
{E_PROF} <i><b>User Profile:</b> {first_name}</i>
{E_ID} <i><b>Account ID:</b> <code>{user_id}</code></i>
{E_ACT} <i><b>Status:</b> {E_DOT} Active & Online</i>
━━━━━━━━━━━━━━━━━━━━

<i>Select an option below to manage your campaigns and settings:</i>"""

    updates_url = config.get("updates_link", "https://t.me/sexders")
    community_url = config.get("community_link", "https://t.me/sexdersgc")
    support_url = config.get("support_link", "https://t.me/sexderz")

    btns = [
        [ibtn(tr(user_id, "open_menu"), "open_menu", style="success", icon=BTN_EMOJIS["start"])],
        [ibtn(tr(user_id, "updates"), url=updates_url, style="primary", icon=BTN_EMOJIS["target"]),
         ibtn(tr(user_id, "community"), url=community_url, style="primary", icon=BTN_EMOJIS["globe"])],
        [ibtn(tr(user_id, "change_lang"), "change_lang_menu", style="primary", icon=BTN_EMOJIS["globe"]),
         ibtn(tr(user_id, "support"), url=support_url, style="primary", icon=BTN_EMOJIS["shield"])]
    ]
    return text, {"inline_keyboard": btns}


async def get_home_menu(user_id, first_name, config):
    free_limit = int(config.get('free_trial_limit') or 100)

    text = f"""{E_PREM} <i><b>@SEXDERS MASS DM ENGINE - Menu</b></i> {E_PREM}
<i>Advanced High-Speed Marketing & Telegram Outreach System - Main Menu</i>

<i>Welcome to the premier Telegram automation panel. Maximize your campaign reach with zero ban risk, utilizing our ultra-fast smart cloud nodes.</i>

━━━━━━━━━━━━━━━━━━━━
{E_PROF} <i><b>User Profile:</b> {first_name}</i>
{E_ID} <i><b>Account ID:</b> <code>{user_id}</code></i>
{E_ACT} <i><b>Node Status:</b> {E_DOT} Active & Online</i>
━━━━━━━━━━━━━━━━━━━━

{E_CHK} <i>Expand your outreach safely and efficiently.</i>
{E_GIFT} <i>Claim your <b>{free_limit} Free Trial DMs</b> today.</i>

"""

    # Main menu: session controls first, account tools next, then campaign actions.
    btns = [
        [ibtn(tr(user_id, "add_session"), "add_session", style="success", icon=BTN_EMOJIS["add"]),
         ibtn(tr(user_id, "remove_session"), "remove_session", style="danger", icon=BTN_EMOJIS["cross"])],
        [ibtn(tr(user_id, "my_account"), "my_account", style="primary", icon=BTN_EMOJIS["user"]),
         ibtn(tr(user_id, "vip_premium"), "buy_premium", style="danger", icon=BTN_EMOJIS["diamond"])],
        [ibtn(tr(user_id, "set_msg"), "set_msg", style="primary", icon=BTN_EMOJIS["setting"])],
        [ibtn(tr(user_id, "fast_fwd"), "ff_menu", style="primary", icon=BTN_EMOJIS["globe"])],
        [ibtn(tr(user_id, "join_req_dm"), "jr_dm", style="success", icon=BTN_EMOJIS["start"])],
        [ibtn(tr(user_id, "invite_earn"), "invite_earn", style="success", icon=BTN_EMOJIS["money"])],
        [ibtn(tr(user_id, "back"), "back_to_dashboard", style="danger", icon=BTN_EMOJIS["home"])]
    ]
    return text, {"inline_keyboard": btns}

async def get_chat_safely(client, raw_link, fallback_id):
    try:
        parsed_id = int(fallback_id) if str(fallback_id).lstrip('-').isdigit() else fallback_id
        return await client.get_chat(parsed_id)
    except Exception: pass
    link = str(raw_link).strip()
    if "t.me/" in link:
        if "+" in link or "joinchat" in link:
            hash_str = link.split("+")[-1].replace("/", "") if "+" in link else link.split("joinchat/")[-1].replace("/", "")
            try: return await client.join_chat(link)
            except UserAlreadyParticipant:
                try:
                    res = await client.invoke(CheckChatInvite(hash=hash_str))
                    title = getattr(res, 'title', None)
                    if not title and hasattr(res, 'chat'): title = getattr(res.chat, 'title', None)
                    if title:
                        async for d in client.get_dialogs(limit=5000):
                            if d.chat and d.chat.title == title: return d.chat
                except Exception: pass
            except Exception: pass
        else:
            username = "@" + link.split("t.me/")[-1].split("/")[0].replace("@", "")
            try: return await client.get_chat(username)
            except Exception: pass
    parsed_id_str = str(fallback_id)
    async for d in client.get_dialogs(limit=5000):
        if str(d.chat.id) == parsed_id_str or (d.chat.username and d.chat.username.lower() == parsed_id_str.replace("@", "").lower()): return d.chat
    raise Exception("Chat Link Unresolved! Ensure the link is valid or the alt account is Admin in the target group.")

async def check_and_show_stats(client, user_id, user_data, config, input_link, msg_to_edit, save_new=False):
    userbot = None
    try:
        userbot = Client(f"check_{user_id}_{int(time.time())}", api_id=API_ID, api_hash=API_HASH, session_string=user_data['sessions'][0], in_memory=True)
        await userbot.start(); await asyncio.sleep(1) 
        chat = await get_chat_safely(userbot, input_link, input_link)
        real_chat_id = chat.id; chat_title = chat.title
        
        try:
            peer = await userbot.resolve_peer(real_chat_id)
            r = await userbot.invoke(GetChatInviteImporters(peer=peer, requested=True, offset_date=0, offset_user=InputUserEmpty(), limit=1))
            pending_count = getattr(r, "count", 0)
        except Exception as api_err:
            if "CHAT_ADMIN_REQUIRED" in str(api_err):
                await userbot.stop()
                err_text = f"{E_WRN} <i><b>Admin Privileges Required!</b>\n\nYour connected session account MUST be an Admin in <b>{html.escape(chat_title)}</b> to read join requests.\n\nPromote your account with 'Add Users' permissions, then try again.</i>"
                btn = {"inline_keyboard": [[ibtn("Back Menu", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]}
                return await api_edit(msg_to_edit.chat.id, msg_to_edit.id, err_text, btn)
            pending_count = 0
            
        await userbot.stop()
        
        if user_id not in USER_STATES: USER_STATES[user_id] = {}
        USER_STATES[user_id]["link"] = str(real_chat_id); USER_STATES[user_id]["raw_link"] = str(input_link); USER_STATES[user_id]["state"] = None 
        
        if save_new:
            new_ch = {"id": str(real_chat_id), "title": chat_title, "link": str(input_link)}
            exists = any(str(existing.get("id")) == str(real_chat_id) for existing in user_data.get("saved_channels", []))
            if not exists: await users_col.update_one({"_id": user_id}, {"$push": {"saved_channels": new_ch}})
        
        msg_delay = int(config.get("msg_delay") or 0)
        expected_sec = int(pending_count) * msg_delay
        h, rem = divmod(expected_sec, 3600); m, s = divmod(rem, 60)
        duration_str = f"{h}h {m}m" if h > 0 else (f"{m}m {s}s" if m > 0 else f"{s}s")
        
        USER_STATES[user_id]["pending"] = int(pending_count)
        stats_text = f"{E_CHK} <i><b>Channel Found:</b> {html.escape(chat_title)}\n{E_PROF} <b>Total Pending Requests:</b> {pending_count}\n{E_WAIT} <b>Estimated Duration:</b> ~{duration_str}</i>"
        await api_edit(msg_to_edit.chat.id, msg_to_edit.id, stats_text)
        if USER_STATES[user_id].get("jr_mode") and int(pending_count) == 0:
            USER_STATES.pop(user_id, None)
            return await api_send(user_id, f"{E_WRN} <i><b>No pending join requests found.</b>\nTurn ON 'Approve new members' in your channel, wait for requests to arrive, then try again.</i>", {"inline_keyboard": [[ibtn("Back to Main Menu", "back_home", style="primary", icon=BTN_EMOJIS["home"])]]})
            
        sessions = user_data['sessions']
        if len(sessions) <= 1:
            USER_STATES[user_id]["sess_idx"] = "all"; USER_STATES[user_id]["state"] = "WAITING_LIMIT"
            await api_send(user_id, f"{E_STAT} <i><b>How many DMs would you like to send?</b>\n(Tap Send to All, or send a number - max {pending_count})</i>", limit_kb(user_id))
        else:
            text = f"{E_SYNC} <i><b>Multiple Accounts Detected!</b>\nSelect which account to deploy:</i>"
            btns = [[ibtn(f"Account {i+1}", f"selsess_{i}", style="primary", icon=BTN_EMOJIS["user"])] for i in range(len(sessions))]
            btns.append([ibtn("Deploy All Accounts", "selsess_all", style="success", icon=BTN_EMOJIS["tick"])])
            btns.append([ibtn("Cancel", "back_home", style="danger", icon=BTN_EMOJIS["cross"])])
            await api_send(user_id, text, {"inline_keyboard": btns})
    except Exception as e_err: 
        if userbot:
            try: await userbot.stop()
            except: pass
        err_text = f"{E_CROSS} <i><b>Channel Connection Failed:</b>\n<code>{html.escape(str(e_err))}</code>\n\nEnsure the invite link is valid and your account is a member/admin.</i>"
        try: await api_edit(msg_to_edit.chat.id, msg_to_edit.id, err_text, {"inline_keyboard": [[ibtn("Back", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]})
        except: await api_send(user_id, err_text)

# ================= JOIN REQUEST COLLECTOR =================
async def _cache_users(client, users):
    try:
        await client.fetch_peers(users)
    except Exception:
        try:
            rows = [(u.id, u.access_hash, "bot" if getattr(u, "bot", False) else "user", getattr(u, "username", None), getattr(u, "phone", None))
                    for u in users if getattr(u, "access_hash", None) is not None]
            await client.storage.update_peers(rows)
        except Exception: pass

async def collect_join_request_users(client, chat_id, max_count=None):
    """Fetch user ids of pending join requests and cache their access hashes so DMs can be delivered."""
    peer = await client.resolve_peer(chat_id)
    ids, offset_date, offset_user = [], 0, InputUserEmpty()
    while True:
        r = await client.invoke(GetChatInviteImporters(peer=peer, requested=True, offset_date=offset_date, offset_user=offset_user, limit=100))
        if not r.importers: break
        await _cache_users(client, r.users)
        ids.extend(i.user_id for i in r.importers)
        if len(r.importers) < 100 or (max_count and len(ids) >= max_count): break
        last = r.importers[-1]
        u = next((x for x in r.users if x.id == last.user_id), None)
        if u is None or getattr(u, "access_hash", None) is None: break
        offset_date = last.date
        offset_user = InputUser(user_id=u.id, access_hash=u.access_hash)
    return ids

# ULTRA FAST CONCURRENT SENDING ENGINE
PERMANENT_FAILS = {"UserIsBlocked", "UserPrivacyRestricted", "InputUserDeactivated", "UserDeactivated"}

async def bounded_send(semaphore, client, target_id, m_type, m_cont, m_cap):
    """Returns (ok, error_name)."""
    async with semaphore:
        for attempt in range(2):
            try:
                if m_type == "photo": await client.send_photo(target_id, photo=m_cont, caption=m_cap)
                elif m_type == "forward_link":
                    src_chat, m_id = m_cont.split("|")
                    src_chat = int(src_chat) if src_chat.lstrip("-").isdigit() else src_chat
                    await client.forward_messages(target_id, src_chat, int(m_id))
                else: await client.send_message(target_id, m_cont)
                return True, None
            except FloodWait as fw:
                if attempt == 0 and fw.value <= 60:
                    await asyncio.sleep(fw.value + 1); continue
                return False, "FloodWait"
            except Exception as ex:
                return False, type(ex).__name__
        return False, "Unknown"

def limit_kb(user_id):
    st = USER_STATES.get(user_id, {})
    rows = []
    if st.get("jr_mode") and st.get("pending"):
        rows.append([ibtn(f"Send to All ({st['pending']})", "jr_all", style="success", icon=BTN_EMOJIS["start"])])
    rows.append([ibtn("Cancel", "back_home", style="danger", icon=BTN_EMOJIS["cross"])])
    return {"inline_keyboard": rows}

def msg_display(u):
    t = u.get("custom_msg_type", "text")
    if t == "photo": return "[Photo Message]"
    if t == "forward_link": return f"[Forward Link] {u.get('custom_msg')}"
    return html.escape(str(u.get("custom_msg", "HELLO")))[:300]

# ================= LIVE PROGRESS + CAMPAIGN ENGINE =================
STOP_KB = {"inline_keyboard": [[ibtn("Stop", "stop_task", style="danger", icon=BTN_EMOJIS["cross"])], [ibtn("Back to Dashboard", "back_home", style="primary", icon=BTN_EMOJIS["home"])]]}


def build_progress_text(title, st, target, status):
    elapsed = max(1, int(time.time() - st["start"]))
    m, s = divmod(elapsed, 60); h, m = divmod(m, 60)
    t = f"{h}h {m}m {s}s" if h else f"{m}m {s}s"
    speed = st["sent"] / elapsed
    try:
        denominator = max(1, int(st.get("total") or 0))
        processed = sum(int(st.get(k, 0) or 0) for k in ("sent", "failed", "blocked", "privacy", "skipped"))
        percent = min(100.0, (processed / denominator) * 100.0)
    except Exception:
        percent = 0.0
    last = f"\n{E_WRN} <b>Last Error:</b> {html.escape(st['last_err'])}" if st["last_err"] else ""
    return (f"{E_START} <i><b>{title}</b> - {status}\n\n"
            f"{E_TRI} <b>Target:</b> {target}\n"
            f"{E_STAT} <b>Total:</b> {st['total']}\n"
            f"📊 <b>Progress:</b> {percent:.1f}%\n"
            f"{E_CHK} <b>Sent:</b> {st['sent']}\n"
            f"{E_CROSS} <b>Failed:</b> {st['failed']}\n"
            f"{E_STOP} <b>Blocked:</b> {st['blocked']}\n"
            f"{E_SHD} <b>Privacy Restricted:</b> {st['privacy']}\n"
            f"{E_PLAY} <b>Skipped (Already Sent):</b> {st['skipped']}\n"
            f"{E_ACT} <b>Speed:</b> {speed:.1f}/s\n"
            f"{E_WAIT} <b>Elapsed:</b> {t}{last}</i>")

async def _show(msg, user_id, text, kb=None):
    try:
        if msg is not None and getattr(msg, "id", None): return await api_edit(msg.chat.id, msg.id, text, kb)
    except Exception: pass
    return await api_send(user_id, text, kb)

async def progress_updater(user_id, msg, title, st, target):
    while not st["done"]:
        await asyncio.sleep(2)
        if st["done"] or msg is None or not getattr(msg, "id", None): continue
        task = ACTIVE_TASKS.get(user_id) or {}
        status = "Paused" if task.get("status") == "paused" else ("Stopping..." if task.get("status") == "stopped" else "Running")
        try: await api_edit(msg.chat.id, msg.id, build_progress_text(title, st, target, status), STOP_KB)
        except Exception: pass

async def cap_limit(user_id, wanted):
    """Free users can only send what is left of their trial. Returns (limit, remaining_or_None)."""
    if await is_premium(user_id): return wanted, None
    u = await get_user(user_id); cfg = await settings_col.find_one({"_id": "config"})
    rem = max(0, int(cfg.get("free_trial_limit", 100)) + int(u.get("bonus_dms", 0)) - int(u.get("total_dms", 0)))
    return min(wanted, rem), rem

async def launch_campaign(user_id, limit, channel_link, raw_link, sess_idx, is_free, client):
    """Reserve the slot and start instantly. Returns False if a campaign is already running."""
    user_id = str(user_id)
    if user_id in ACTIVE_TASKS: return False
    ACTIVE_TASKS[user_id] = {"status": "running", "sent": 0, "limit": limit, "start_time": time.time(), "target": "Preparing..."}
    asyncio.create_task(setup_and_execute_dm(user_id, limit, "flt_all", 0, is_free, channel_link, raw_link, sess_idx, client))
    return True

async def setup_and_execute_dm(user_id, limit, filter_type, delay_mins, is_free, channel_link, raw_link, sess_idx, client):
    user_id = str(user_id)
    is_alt_dms = (channel_link == "ALT_DMS")
    title = "FAST Auto-Forward DM" if is_alt_dms else "Join Req DM"
    st = {"total": 0, "sent": 0, "failed": 0, "blocked": 0, "privacy": 0, "skipped": 0, "reserved": 0, "last_err": "", "start": time.time(), "done": False}
    clients, progress, updater = [], None, None
    messaged_list, chat_id_str, target_disp, stop_note, ran, status = [], "", "-", "", False, "Completed"
    try:
        ACTIVE_TASKS.setdefault(user_id, {"status": "running", "sent": 0, "limit": limit, "start_time": time.time(), "target": "Preparing..."})
        user_data = await get_user(user_id)
        config = await settings_col.find_one({"_id": "config"})
        msg_delay = int(config.get("msg_delay") or 0)
        un = f"(@{user_data.get('username')})" if user_data.get('username') and user_data.get('username') != "N/A" else ""

        progress = await api_send(user_id, f"{E_SYNC} <i><b>{title}</b>\nConnecting accounts and fetching targets...</i>", STOP_KB)
        if delay_mins > 0: await asyncio.sleep(delay_mins * 60)

        sessions_db = user_data.get("sessions", [])
        try: sessions_to_use = sessions_db if sess_idx == "all" else [sessions_db[int(sess_idx)]]
        except Exception: sessions_to_use = sessions_db[:1]

        async def _start(idx, s):
            c = Client(f"ub_{user_id}_{int(time.time())}_{idx}", api_id=API_ID, api_hash=API_HASH, session_string=s, in_memory=True)
            await c.start(); return c
        started = await asyncio.gather(*[_start(i, s) for i, s in enumerate(sessions_to_use)], return_exceptions=True)
        clients = [c for c in started if not isinstance(c, Exception)]
        if not clients:
            return await _show(progress, user_id, f"{E_WRN} <i><b>All selected sessions are invalid or expired!</b> Please re-add your session.</i>")

        chat_id_to_use, chat_title = "ALT_DMS", "All Private Chats"
        if not is_alt_dms:
            target_raw = str(config.get("free_channel_link", "none")) if is_free else str(raw_link)
            fallback_id = config.get("free_channel_id", "none") if is_free else channel_link
            try:
                chat = await get_chat_safely(clients[0], target_raw, fallback_id)
                chat_id_to_use = chat.id; chat_title = chat.title
            except Exception as ce:
                return await _show(progress, user_id, f"{E_WRN} <i><b>Could not access channel:</b> {html.escape(str(ce))}</i>")

        target_disp = html.escape(chat_title)
        ACTIVE_TASKS[user_id]["target"] = target_disp
        chat_id_str = str(chat_id_to_use)
        if not is_alt_dms: messaged_list = list(user_data.get("messaged_users", {}).get(chat_id_str, []))

        log_channel = config.get("log_channel", "none")
        if log_channel != "none":
            try:
                lc_id = int(log_channel) if str(log_channel).replace("-", "").isdigit() else log_channel
                await api_send(lc_id, f"{E_START} <i><b>{title} Order</b>\nUser: <code>{user_id}</code> {un}\nTarget: {target_disp}\nLimit: {limit}</i>")
            except Exception: pass

        ran = True
        try:
            queues, pool = {}, list(clients)
            if is_alt_dms:
                seen, total_q = set(), 0
                for c in clients:
                    me_id = getattr(getattr(c, "me", None), "id", 0)
                    q = asyncio.Queue()
                    async for dialog in c.get_dialogs():
                        if dialog.chat and dialog.chat.type == enums.ChatType.PRIVATE:
                            tid = dialog.chat.id
                            if tid in (777000, me_id) or tid in seen: continue
                            seen.add(tid); q.put_nowait(tid)
                    queues[id(c)] = q; total_q += q.qsize()
            else:
                need = int(limit) + len(messaged_list) + 50
                res_all = await asyncio.gather(*[collect_join_request_users(c, chat_id_to_use, need) for c in clients], return_exceptions=True)
                pool, ids, first_err = [], None, None
                for c, res in zip(clients, res_all):
                    if isinstance(res, Exception): first_err = first_err or res; continue
                    pool.append(c)
                    if ids is None: ids = res
                if not pool:
                    raise Exception(f"Could not read join requests - make your session account an Admin (Add Users permission) in the channel. ({first_err})")
                messaged_set = set(str(x) for x in messaged_list)
                shared = asyncio.Queue()
                for t in ids:
                    if str(t) in messaged_set: st["skipped"] += 1
                    else: shared.put_nowait(t)
                for c in pool: queues[id(c)] = shared
                total_q = shared.qsize()

            st["total"] = min(total_q, int(limit))
            ACTIVE_TASKS[user_id]["limit"] = st["total"]
            m_type = user_data.get("custom_msg_type", "text")
            m_cont = user_data.get("custom_msg") or "HELLO"
            m_cap = user_data.get("custom_caption", "")

            sem = asyncio.Semaphore(FF_WORKERS * max(1, len(pool)))
            flooded = set()
            updater = asyncio.create_task(progress_updater(user_id, progress, title, st, target_disp))

            async def worker(c, q):
                while True:
                    task = ACTIVE_TASKS.get(user_id)
                    while task and task.get("status") == "paused":
                        await asyncio.sleep(1); task = ACTIVE_TASKS.get(user_id)
                    if not task or task.get("status") == "stopped": return
                    if id(c) in flooded or st["reserved"] >= limit: return
                    try: tid = q.get_nowait()
                    except asyncio.QueueEmpty: return
                    st["reserved"] += 1
                    ok, err = await bounded_send(sem, c, tid, m_type, m_cont, m_cap)
                    if ok:
                        st["sent"] += 1
                        if not is_alt_dms: messaged_list.append(str(tid))
                        task = ACTIVE_TASKS.get(user_id)
                        if task: task["sent"] = st["sent"]
                    else:
                        st["reserved"] -= 1
                        if err in ("PeerFlood", "FloodWait"):
                            flooded.add(id(c)); st["last_err"] = err
                            if not is_alt_dms: q.put_nowait(tid)   # let another account take it
                            return
                        if err == "UserIsBlocked": st["blocked"] += 1
                        elif err == "UserPrivacyRestricted": st["privacy"] += 1
                        else: st["failed"] += 1; st["last_err"] = err
                        if err in PERMANENT_FAILS and not is_alt_dms: messaged_list.append(str(tid))
                    if msg_delay > 0: await asyncio.sleep(msg_delay)

            await asyncio.gather(*[worker(c, queues[id(c)]) for c in pool for _ in range(FF_WORKERS)])

            task = ACTIVE_TASKS.get(user_id) or {}
            left = any(not q.empty() for q in set(queues.values()))
            if task.get("status") == "stopped": status = "Stopped"
            elif flooded and left and st["sent"] < limit:
                status = "Stopped (Telegram limit)"
                stop_note = "\n" + f"{E_WRN} <i>Telegram limited your account(s) (PeerFlood). Try again later.</i>"
        except Exception as e_dm:
            status = "Error"; st["last_err"] = str(e_dm)[:300]
    except Exception as general_error:
        status = "Error"; st["last_err"] = str(general_error)[:300]
        if not ran: await _show(progress, user_id, f"{E_CROSS} <i><b>Campaign Guard Triggered:</b>\n<code>{html.escape(str(general_error))}</code></i>")
    finally:
        st["done"] = True
        if updater:
            updater.cancel()
            try: await updater
            except BaseException: pass
        if clients: await asyncio.gather(*[c.stop() for c in clients], return_exceptions=True)
        if ran:
            today = get_ist_str("%Y-%m-%d")
            set_fields = {"last_date": today}
            if not is_alt_dms: set_fields[f"messaged_users.{chat_id_str}"] = messaged_list
            history_item = {
                "date": get_ist_str("%Y-%m-%d %H:%M:%S"),
                "title": str(title)[:80],
                "target": str(target_disp)[:100],
                "sent": int(st.get("sent", 0)),
                "failed": int(st.get("failed", 0)),
                "blocked": int(st.get("blocked", 0)),
                "status": str(status)[:30],
            }
            await users_col.update_one(
                {"_id": user_id},
                {"$inc": {"total_dms": st["sent"], "daily_dms": st["sent"]},
                 "$set": set_fields,
                 "$push": {"campaign_history": {"$each": [history_item], "$slice": -50}}},
                upsert=True
            )
            await settings_col.update_one({"_id": "config"}, {"$inc": {"global_dms": st["sent"]}})
            await _show(progress, user_id, build_progress_text(title, st, target_disp, status) + stop_note)
            try:
                cfg2 = await settings_col.find_one({"_id": "config"}); success_log = cfg2.get("success_log_channel", "none")
                if success_log != "none":
                    slc_id = int(success_log) if str(success_log).replace("-", "").isdigit() else success_log
                    await api_send(slc_id, f"{E_CHK} <i><b>{title} Completed</b>\nUser: <code>{user_id}</code>\nTarget: {target_disp}\nTotal Sent: {st['sent']}</i>")
            except Exception: pass
        ACTIVE_TASKS.pop(user_id, None)

# ================= ROUTE HANDLERS =================

async def show_force_join_prompt(chat_id, not_joined_list):
    text = f"{E_WRN} <i><b>Subscription Verification Required!</b>\n\nPlease join our official channel and community group before continuing.</i>"
    btn_list = []
    row = []
    for i, (idx, link) in enumerate(not_joined_list):
        fixed_link = link if str(link).startswith("http") else f"https://t.me/{str(link).replace('@','')}"
        row.append(ibtn(str(idx), url=fixed_link, style="primary", icon=BTN_EMOJIS["target"]))
        if len(row) == 2:
            btn_list.append(row)
            row = []
    if row:
        btn_list.append(row)
    btn_list.append([ibtn("I Have Joined", "check_join", style="success", icon=BTN_EMOJIS["tick"])])
    return await api_send(chat_id, text, {"inline_keyboard": btn_list})

async def route_user_after_onboarding(user_id, first_name, config, client_or_query=None, is_query=False):
    if int(user_id) not in ADMINS:
        joined, not_joined_list = await check_force_join(user_id)
        if not joined:
            if is_query:
                text = f"{E_WRN} <i><b>Subscription Verification Required!</b>\n\nPlease join our official channel and community group before continuing.</i>"
                btn_list = []
                row = []
                for idx, link in not_joined_list:
                    fixed_link = link if str(link).startswith("http") else f"https://t.me/{str(link).replace('@','')}"
                    row.append(ibtn(str(idx), url=fixed_link, style="primary", icon=BTN_EMOJIS["target"]))
                    if len(row) == 2:
                        btn_list.append(row)
                        row = []
                if row:
                    btn_list.append(row)
                btn_list.append([ibtn("I Have Joined", "check_join", style="success", icon=BTN_EMOJIS["tick"])])
                return await safe_edit(client_or_query, text, {"inline_keyboard": btn_list})
            else:
                return await show_force_join_prompt(user_id, not_joined_list)

    text, btn = await get_dashboard_menu(user_id, first_name, config)
    if is_query:
        return await safe_edit(client_or_query, text, kb=btn)
    else:
        return await api_send(user_id, text, kb=btn)


async def start_cmd(client, message):
    try:
        user_id = str(message.chat.id)
        u = await get_user(user_id)
        if not u.get("language"):
            await api_send(user_id, tr(user_id, "choose"), kb=language_keyboard())
            return
        if not u.get("terms_accepted"):
            await send_terms(user_id)
            return
        config = await settings_col.find_one({"_id": "config"})
        first_name = html.escape(message.from_user.first_name if message.from_user else "User")
        await route_user_after_onboarding(user_id, first_name, config, client_or_query=None, is_query=False)
    except Exception as e_start:
        print(f"Error in start_cmd: {type(e_start).__name__}")

async def send_terms(user_id):
    terms_kb = {"inline_keyboard": [[ibtn("Terms & Conditions", url=TERMS_URL, style="primary", icon=BTN_EMOJIS["shield"])], [ibtn("Agree", "terms_agree", style="success", icon=BTN_EMOJIS["tick"])]]}
    await api_send(user_id, tr(user_id, "terms"), kb=terms_kb)

async def language_cmd(client, message):
    user_id = str(message.chat.id)
    await api_send(user_id, tr(user_id, "choose"), kb=language_keyboard())

async def cancel_cmd(client, message):
    user_id = str(message.chat.id)
    USER_STATES.pop(user_id, None)
    await api_send(user_id, f"{E_CROSS} <i>Current process cancelled.</i>",
                   {"inline_keyboard": [[ibtn("Back to Dashboard", "back_home", style="primary", icon=BTN_EMOJIS["home"])]]})

async def help_cmd(client, message):
    user_id = str(message.chat.id)
    await api_send(user_id, tr(user_id, "help"), kb={"inline_keyboard":[[ibtn(tr(user_id,"back"),"back_home",style="primary",icon=BTN_EMOJIS["home"])]]})

async def status_cmd(client, message):
    user_id = str(message.chat.id)
    await api_send(user_id, tr(user_id, "status"), kb={"inline_keyboard":[[ibtn(tr(user_id,"back"),"back_home",style="primary",icon=BTN_EMOJIS["home"])]]})

async def shortcut_cmds(client, message):
    user_id = str(message.chat.id); cmd = message.command[0]; config = await settings_col.find_one({"_id": "config"})
    
    if int(user_id) not in ADMINS:
        joined, _ = await check_force_join(user_id)
        if not joined: return await api_send(user_id, f"{E_CROSS} <i><b>Please use /start to verify channels first.</b></i>")

    if user_id not in USER_STATES: USER_STATES[user_id] = {}

    if cmd == "myaccount":
        has_prem = await is_premium(user_id); u = await get_user(user_id)
        if has_prem:
            exp_str = get_ist_ts_str(u['premium_expiry'])
            status = f"{E_DIA} <i>VIP Premium\n{E_CAL} <b>Expiry:</b> {exp_str}</i>"
        else: status = f"{E_WAIT} <i>Free Tier</i>"
        text = f"{E_PROF} <i><b>User Account Details:</b>\n\n{E_ID} <b>ID:</b> <code>{user_id}</code>\n{E_SHD} <b>Plan Status:</b> {status}\n{E_ACT} <b>Connected Sessions:</b> {len(u.get('sessions', []))}\n{E_STAT} <b>Lifetime DMs Sent:</b> {u.get('total_dms', 0)}</i>"
        await api_send(user_id, text, {"inline_keyboard": [[ibtn("Reset DM History", "reset_history", style="danger", icon=BTN_EMOJIS["cross"])]]})

    elif cmd == "buypremium":
        text = f"{E_PREM} <i><b>VIP Subscription Plans</b>\n\n<b>1 Day:</b> ₹{config.get('price_1d_inr')} | ${config.get('price_1d_usd')}\n<b>3 Days:</b> ₹{config.get('price_3d_inr')} | ${config.get('price_3d_usd')}\n<b>7 Days:</b> ₹{config.get('price_7d_inr')} | ${config.get('price_7d_usd')}\n<b>1 Month:</b> ₹{config.get('price_1m_inr')} | ${config.get('price_1m_usd')}\n\nSelect a subscription plan below:</i>"
        btn = {"inline_keyboard": [[ibtn("1 Day Plan", "plan_1", style="primary", icon=BTN_EMOJIS["diamond"]), ibtn("3 Days Plan", "plan_3", style="primary", icon=BTN_EMOJIS["diamond"])], [ibtn("7 Days Plan", "plan_7", style="success", icon=BTN_EMOJIS["diamond"]), ibtn("1 Month Plan", "plan_30", style="success", icon=BTN_EMOJIS["crown"])]]}
        await api_send(user_id, text, btn)

    elif cmd == "massdm":
        u = await get_user(user_id)
        if not u.get("sessions"): return await api_send(user_id, f"{E_CROSS} <i><b>No Active Sessions Found!</b> Please connect an account first.</i>")
        USER_STATES[user_id] = {"state": "WAITING_DM_LINK", "is_free_ch": False, "jr_mode": True}
        await api_send(user_id, f"{E_START} <i><b>Join Req DM</b>\nPlease provide your channel invite link.</i>")

async def dm_controls(client, message):
    user_id = str(message.chat.id); cmd = message.command[0]
    if user_id not in ACTIVE_TASKS: return await api_send(user_id, f"{E_CROSS} <i><b>No active campaign currently running.</b></i>")
    if cmd == "chk":
        task = ACTIVE_TASKS[user_id]
        await api_send(user_id, f"{E_STAT} <i><b>Campaign Progress:</b> {task.get('status', 'running').title()}\n{E_TRI} <b>Target:</b> {task.get('target', 'Unknown')}\n{E_CHK} <b>Delivered:</b> {task.get('sent', 0)} / {task.get('limit', 0)}</i>")
    elif cmd == "pause": ACTIVE_TASKS[user_id]["status"] = "paused"; await api_send(user_id, f"{E_WAIT} <i><b>Campaign Paused!</b> Use /resume to continue.</i>")
    elif cmd == "resume": ACTIVE_TASKS[user_id]["status"] = "running"; await api_send(user_id, f"{E_PLAY} <i><b>Campaign Resumed!</b></i>")
    elif cmd == "stop": ACTIVE_TASKS[user_id]["status"] = "stopped"; await api_send(user_id, f"{E_STOP} <i><b>Campaign Halted!</b> Finalizing results...</i>")

async def check_total_public(client, message):
    config = await settings_col.find_one({"_id": "config"})
    await api_send(message.chat.id, f"{E_STAT} <i><b>Global Platform Metrics:</b>\nTotal Messages Delivered Worldwide: <b>{config.get('global_dms', 0)}</b></i>")

# ================= 🎛️ BUTTON-BASED ADMIN DASHBOARD =================
async def get_admin_dashboard(config):
    auto_status = f"{E_DOT} ACTIVE" if config.get("auto_payment_status", False) else f"{E_STOP} DISABLED"
    maint_status = f"{E_STOP} ON" if config.get("maintenance", False) else f"{E_DOT} OFF"
    total_users = await users_col.count_documents({})
    active_now = len(ACTIVE_TASKS)

    text = f"""{E_ADM} <i><b>Master Administration Terminal</b></i>

━━━━━━━━━━━━━━━━━━━━
{E_STAT} <i><b>Server Health & System Metrics:</b></i>
{E_PROF} <i><b>Total Registered Users:</b> <code>{total_users}</code></i>
{E_ACT} <i><b>Active DM Processes:</b> <code>{active_now}</code></i>
{E_GLOBE} <i><b>Lifetime Delivered DMs:</b> <code>{config.get('global_dms', 0)}</code></i>
{E_MONEY} <i><b>Gross Sales Revenue:</b> <code>₹{config.get('total_sales_inr', 0)}</code></i>
━━━━━━━━━━━━━━━━━━━━
{E_ADM} <i><b>Automated Operations:</b></i>
• <i><b>Instant UPI Payment Gateway:</b> {auto_status}</i>
• <i><b>Maintenance Mode:</b> {maint_status}</i>
• <i><b>Support Link:</b> {html.escape(str(config.get('support_link') or ''))}</i>
━━━━━━━━━━━━━━━━━━━━
<i>Select any category below to manage configurations:</i>"""

    btns = [
        [ibtn("Stats & Insights", "adm_stats", style="primary", icon=BTN_EMOJIS["stats"]), ibtn("Sales & Revenue", "adm_sales", style="success", icon=BTN_EMOJIS["money"])],
        [ibtn("Broadcast Message", "adm_broadcast", style="success", icon=BTN_EMOJIS["globe"])],
        [ibtn("Payment Gateways", "adm_cat_pay", style="primary", icon=BTN_EMOJIS["money"]), ibtn("Subscription Pricing", "adm_cat_price", style="primary", icon=BTN_EMOJIS["diamond"])],
        [ibtn("Channels & ForceSub", "adm_cat_channels", style="primary", icon=BTN_EMOJIS["target"]), ibtn("User Directory", "adm_cat_users", style="primary", icon=BTN_EMOJIS["user"])],
        [ibtn("Operational Limits", "adm_cat_limits", style="primary", icon=BTN_EMOJIS["setting"]), ibtn("Set Support Link", "adm_ask_supportlink", style="success", icon=BTN_EMOJIS["target"])],
        [
            ibtn(f"{'Disable' if config.get('auto_payment_status') else 'Enable'} Auto-Pay", "adm_toggle_auto", style="danger" if config.get('auto_payment_status') else "success", icon=BTN_EMOJIS["tick"]),
            ibtn(f"Maintenance: {'OFF' if config.get('maintenance') else 'ON'}", "adm_toggle_maint", style="success" if config.get('maintenance') else "danger", icon=BTN_EMOJIS["shield"])
        ],
        [ibtn("Exit Admin Terminal", "adm_close", style="danger", icon=BTN_EMOJIS["cross"])]
    ]
    return text, {"inline_keyboard": btns}

async def admin_panel(client, message):
    if message.from_user.id not in ADMINS: return
    config = await settings_col.find_one({"_id": "config"})
    text, kb = await get_admin_dashboard(config)
    await api_send(message.chat.id, text, kb=kb)

# Legacy commands support
async def master_admin_cmds(client, message):
    if message.from_user.id not in ADMINS: return
    cmd = message.command[0]
    
    if cmd == "toggleauto":
        config = await settings_col.find_one({"_id": "config"})
        current = config.get("auto_payment_status", False)
        await settings_col.update_one({"_id": "config"}, {"$set": {"auto_payment_status": not current}})
        await api_send(message.chat.id, f"{E_CHK} <i>Auto-Approve status toggled to: {'ON' if not current else 'OFF'}.</i>")
        
    elif cmd in ["setfreerequest"]:
        if len(message.command) < 2: return await api_send(message.chat.id, f"{E_CROSS} <i>Usage: <code>/{cmd} [Link]</code></i>")
        await settings_col.update_one({"_id": "config"}, {"$set": {"free_request_link": message.command[1]}})
        await api_send(message.chat.id, f"{E_CHK} <i>Free request link updated successfully.</i>")
        
    elif cmd == "maintenance":
        if len(message.command) < 2: return await api_send(message.chat.id, f"{E_CROSS} <i>Usage: <code>/maintenance [on/off]</code></i>")
        val = message.command[1].lower() == "on"
        await settings_col.update_one({"_id": "config"}, {"$set": {"maintenance": val}})
        await api_send(message.chat.id, f"{E_CHK} <i>Maintenance mode set to {'ON' if val else 'OFF'}.</i>")
        
    elif cmd == "reqall":
        if len(message.command) == 1:
            await settings_col.update_one({"_id": "config"}, {"$set": {"reqall_id": "none"}})
            await api_send(message.chat.id, f"{E_CHK} <i>Mandatory request channel disabled.</i>")
        elif len(message.command) >= 3:
            await settings_col.update_one({"_id": "config"}, {"$set": {"reqall_id": message.command[1], "reqall_link": message.command[2]}})
            await api_send(message.chat.id, f"{E_CHK} <i>Mandatory request channel updated.</i>")
            
    elif cmd in ["setfampay", "setmanual", "setcrypto"]:
        key = cmd.replace("set", "upi_") if "crypto" not in cmd else "crypto"
        await settings_col.update_one({"_id": "config"}, {"$set": {key: message.command[1]}})
        await api_send(message.chat.id, f"{E_CHK} <i>Configuration parameter updated.</i>")
            
    elif cmd in ["setprice1d", "setprice3d", "setprice7d", "setprice1m"]:
        tk = cmd.replace("setprice", "")
        await settings_col.update_one({"_id": "config"}, {"$set": {f"price_{tk}_inr": message.command[1], f"price_{tk}_usd": message.command[2]}})
        await api_send(message.chat.id, f"{E_CHK} <i>Subscription rate updated.</i>")
        
    elif cmd in ["setlogchannel", "setsuccesslog", "setleaderboard", "setfreechannel"]:
        k = cmd.replace("set", "")
        if "freechannel" in cmd: await settings_col.update_one({"_id": "config"}, {"$set": {"free_channel_id": message.command[1], "free_channel_link": message.command[2]}})
        else: await settings_col.update_one({"_id": "config"}, {"$set": {f"{k}_channel" if "log" not in cmd else k: message.command[1]}})
        await api_send(message.chat.id, f"{E_CHK} <i>System channel route updated.</i>")
        
    elif cmd in ["setfreetrial", "setldbtime", "setdelay", "setfreereq", "setrefbonus"]:
        if len(message.command) < 2: return await api_send(message.chat.id, f"{E_CROSS} <i>Usage: <code>/{cmd} [Number]</code></i>")
        km = {"setfreetrial": "free_trial_limit", "setdelay": "msg_delay", "setldbtime": "ldb_time", "setfreereq": "free_req_limit", "setrefbonus": "ref_bonus"}
        await settings_col.update_one({"_id": "config"}, {"$set": {km[cmd]: int(message.command[1])}})
        await api_send(message.chat.id, f"{E_CHK} <i>Value updated successfully.</i>")
        
    elif cmd == "ongoing":
        if not ACTIVE_TASKS: return await api_send(message.chat.id, "<i>No tasks are running currently.</i>")
        text = f"{E_SYNC} <i><b>Ongoing Campaigns:</b></i>\n"
        for uid, t in ACTIVE_TASKS.items(): text += f"<i>ID: <code>{uid}</code> | Target: {t['target']} | Sent: {t['sent']}/{t['limit']}</i>\n"
        await api_send(message.chat.id, text)
        
    elif cmd == "sales":
        config = await settings_col.find_one({"_id": "config"}); history = config.get("sales_history", {})
        t_str = get_ist_str("%Y-%m-%d"); y_str = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400 + 19800))
        l_30 = sum(history.get(time.strftime("%Y-%m-%d", time.gmtime(time.time() - (i * 86400) + 19800)), 0) for i in range(30))
        text = f"{E_MONEY} <i><b>Revenue Tracker</b>\n\n{E_CAL} <b>Today's Sales:</b> ₹{history.get(t_str, 0)}\n{E_WAIT} <b>Yesterday's Sales:</b> ₹{history.get(y_str, 0)}\n{E_CAL} <b>Last 30 Days:</b> ₹{l_30}\n\n{E_CROWN} <b>Total Lifetime Sales:</b> ₹{config.get('total_sales_inr', 0)}</i>"
        await api_send(message.chat.id, text)
        
    elif cmd == "giveprem":
        t, d = message.command[1], int(message.command[2])
        u = await get_user(t); cur = time.time()
        nex = (u.get("premium_expiry", 0) + (d * 86400)) if u.get("premium_expiry", 0) > cur else (cur + (d * 86400))
        await users_col.update_one({"_id": t}, {"$set": {"premium_expiry": nex}})
        await api_send(message.chat.id, f"{E_CHK} <i>VIP Access granted to user {t}.</i>")
        
    elif cmd == "removeprem":
        await users_col.update_one({"_id": message.command[1]}, {"$set": {"premium_expiry": 0}})
        await api_send(message.chat.id, f"{E_CHK} <i>VIP Access revoked.</i>")

async def shared_admin_cmds(client, message):
    if message.from_user.id not in ADMINS: return
    cmd = message.command[0]
    
    if cmd == "stats":
        t_u = await users_col.count_documents({})
        await api_send(message.chat.id, f"{E_STAT} <i><b>Platform Statistics:</b>\nTotal Registered Users: {t_u}</i>")
    elif cmd == "checkuser":
        u = await get_user(message.command[1]); is_p = "Yes" if u.get('premium_expiry',0) > time.time() else "No"
        await api_send(message.chat.id, f"{E_PROF} <i>User: <code>{u['_id']}</code>\nPremium: {is_p}\nDMs Sent: {u.get('total_dms', 0)}\nSessions: {len(u.get('sessions', []))}</i>")
    elif cmd == "clearsession":
        await users_col.update_one({"_id": message.command[1]}, {"$set": {"sessions": []}})
        await api_send(message.chat.id, f"{E_CHK} <i>Sessions wiped for specified user.</i>")
    elif cmd == "banuser":
        await users_col.update_one({"_id": message.command[1]}, {"$set": {"banned": True}})
        await api_send(message.chat.id, f"{E_CHK} <i>User account suspended.</i>")
    elif cmd == "unbanuser":
        await users_col.update_one({"_id": message.command[1]}, {"$set": {"banned": False}})
        await api_send(message.chat.id, f"{E_CHK} <i>User account restored.</i>")
    elif cmd == "broadcast":
        if not message.reply_to_message: return await api_send(message.chat.id, f"{E_WRN} <i>Reply to any message with <code>/broadcast</code></i>")
        c = 0
        status_msg = await api_send(message.chat.id, f"{E_SYNC} <i>Broadcasting in progress...</i>")
        async for u in users_col.find({}):
            try: 
                await message.reply_to_message.copy(int(u["_id"]))
                c += 1
                await asyncio.sleep(0.05) 
            except: pass
        await api_edit(status_msg.chat.id, status_msg.id, f"{E_CHK} <i><b>Broadcast Completed!</b> Sent to {c} users.</i>")

@bot.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    try: await query.answer()
    except: pass
    user_id = str(query.message.chat.id); data = query.data; config = await settings_col.find_one({"_id": "config"})

    # ================= 🎛️ ADMIN CALLBACK ROUTES =================
    if data.startswith("adm_"):
        if int(query.from_user.id) not in ADMINS:
            return await query.answer("Access Denied: Admins Only.", show_alert=True)

        if data == "adm_home":
            text, kb = await get_admin_dashboard(config)
            return await safe_edit(query, text, kb)

        elif data == "adm_close":
            return await query.message.delete()

        elif data == "adm_stats":
            t_u = await users_col.count_documents({})
            g_d = config.get("global_dms", 0)
            text = f"""{E_STAT} <i><b>Platform Statistics Overview</b>\n\n{E_PROF} <b>Total Users in Database:</b> <code>{t_u}</code>\n{E_START} <b>Global Lifetime DMs:</b> <code>{g_d}</code>\n{E_ACT} <b>Concurrent Live Campaigns:</b> <code>{len(ACTIVE_TASKS)}</code></i>"""
            btn = {"inline_keyboard": [[ibtn("Back to Dashboard", "adm_home", style="danger", icon=BTN_EMOJIS["cross"])]]}
            return await safe_edit(query, text, kb=btn)

        elif data == "adm_sales":
            history = config.get("sales_history", {})
            t_str = get_ist_str("%Y-%m-%d"); y_str = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400 + 19800))
            l_30 = sum(history.get(time.strftime("%Y-%m-%d", time.gmtime(time.time() - (i * 86400) + 19800)), 0) for i in range(30))
            text = f"""{E_MONEY} <i><b>Sales & Revenue Insights</b>\n\n{E_CAL} <b>Today's Revenue:</b> ₹{history.get(t_str, 0)}\n{E_WAIT} <b>Yesterday's Revenue:</b> ₹{history.get(y_str, 0)}\n{E_CAL} <b>Last 30 Days:</b> ₹{l_30}\n━━━━━━━━━━━━━━━━━━━━\n{E_CROWN} <b>Total Gross Sales:</b> ₹{config.get('total_sales_inr', 0)}</i>"""
            btn = {"inline_keyboard": [[ibtn("Back to Dashboard", "adm_home", style="danger", icon=BTN_EMOJIS["cross"])]]}
            return await safe_edit(query, text, kb=btn)

        elif data == "adm_toggle_auto":
            current = config.get("auto_payment_status", False)
            await settings_col.update_one({"_id": "config"}, {"$set": {"auto_payment_status": not current}})
            config["auto_payment_status"] = not current
            text, kb = await get_admin_dashboard(config)
            return await safe_edit(query, text, kb)

        elif data == "adm_toggle_maint":
            current = config.get("maintenance", False)
            await settings_col.update_one({"_id": "config"}, {"$set": {"maintenance": not current}})
            config["maintenance"] = not current
            text, kb = await get_admin_dashboard(config)
            return await safe_edit(query, text, kb)

        elif data == "adm_cat_pay":
            text = f"""{E_MONEY} <i><b>Payment Gateway & QR Management</b>\n\n{E_DOT} <b>Instant Auto Approval:</b> {'ENABLED' if config.get('auto_payment_status') else 'DISABLED'}\n{E_MONEY} <b>Smart FamPay UPI:</b> <code>{config.get('upi_fampay', 'Not Set')}</code>\n{E_MONEY} <b>Manual UPI VPA:</b> <code>{config.get('upi_manual', 'Not Set')}</code>\n{E_DIA} <b>USDT (TRC-20):</b> <code>{config.get('crypto', 'Not Set')}</code>\n\nSelect a configuration parameter to modify:</i>"""
            btn = {"inline_keyboard": [
                [ibtn("Set FamPay UPI", "adm_ask_fampay", style="primary", icon=BTN_EMOJIS["money"]), ibtn("Set Manual UPI", "adm_ask_manual", style="primary", icon=BTN_EMOJIS["money"])],
                [ibtn("Set Crypto Address", "adm_ask_crypto", style="primary", icon=BTN_EMOJIS["diamond"])],
                [ibtn("Upload FamPay QR", "adm_ask_fampayqr", style="primary", icon=BTN_EMOJIS["setting"]), ibtn("Upload Manual QR", "adm_ask_manualqr", style="primary", icon=BTN_EMOJIS["setting"])],
                [ibtn("Upload Crypto QR", "adm_ask_cryptoqr", style="primary", icon=BTN_EMOJIS["setting"])],
                [ibtn("Back to Dashboard", "adm_home", style="danger", icon=BTN_EMOJIS["cross"])]
            ]}
            return await safe_edit(query, text, kb=btn)

        elif data == "adm_cat_price":
            text = f"""{E_DIA} <i><b>Subscription Pricing Architecture</b>\n\n<b>1 Day Access:</b> ₹{config.get('price_1d_inr')} | ${config.get('price_1d_usd')}\n<b>3 Days Access:</b> ₹{config.get('price_3d_inr')} | ${config.get('price_3d_usd')}\n<b>7 Days Access:</b> ₹{config.get('price_7d_inr')} | ${config.get('price_7d_usd')}\n<b>1 Month Access:</b> ₹{config.get('price_1m_inr')} | ${config.get('price_1m_usd')}\n\nSelect a plan to edit its pricing:</i>"""
            btn = {"inline_keyboard": [
                [ibtn("Edit 1 Day Plan", "adm_ask_p_1d", style="primary", icon=BTN_EMOJIS["diamond"]), ibtn("Edit 3 Days Plan", "adm_ask_p_3d", style="primary", icon=BTN_EMOJIS["diamond"])],
                [ibtn("Edit 7 Days Plan", "adm_ask_p_7d", style="success", icon=BTN_EMOJIS["diamond"]), ibtn("Edit 1 Month Plan", "adm_ask_p_1m", style="success", icon=BTN_EMOJIS["crown"])],
                [ibtn("Back to Dashboard", "adm_home", style="danger", icon=BTN_EMOJIS["cross"])]
            ]}
            return await safe_edit(query, text, kb=btn)

        # === CHANNELS MANAGEMENT HUB ===
        elif data == "adm_cat_channels":
            fsubs = config.get("fsub_channels", [])
            fsub_text = ""
            if not fsubs:
                fsub_text = "<i>No subscription channels added yet.</i>\n"
            else:
                for idx, c in enumerate(fsubs):
                    fsub_text += f"<i><b>{idx+1}.</b> {html.escape(c.get('title','Channel'))} (<code>{c.get('id')}</code>)</i>\n"

            text = f"""{E_GLOBE} <i><b>Subscription Channels & Routing Setup</b>\n\n<b>Active Force-Sub Channels ({len(fsubs)}):</b>\n{fsub_text}\n<b>System Routes:</b>\n• <b>Mandatory Request ID:</b> <code>{config.get('reqall_id')}</code>\n• <b>Free Target Channel:</b> <code>{config.get('free_channel_id')}</code>\n• <b>Order Log Channel:</b> <code>{config.get('log_channel')}</code>\n• <b>Success Log Channel:</b> <code>{config.get('success_log_channel')}</code>\n• <b>Daily Leaderboard:</b> <code>{config.get('leaderboard_channel')}</code>\n\nSelect an action below:</i>"""
            
            btn = {"inline_keyboard": [
                [ibtn("➕ Add New Channel", "adm_add_channel", style="success", icon=BTN_EMOJIS["add"]), ibtn("🗑️ Remove Channels", "adm_manage_channels", style="danger", icon=BTN_EMOJIS["cross"])],
                [ibtn("Mandatory Request", "adm_ask_reqall", style="primary", icon=BTN_EMOJIS["shield"]), ibtn("Free Target Channel", "adm_ask_freech", style="primary", icon=BTN_EMOJIS["gift"])],
                [ibtn("Order Log Channel", "adm_ask_logch", style="primary", icon=BTN_EMOJIS["stats"]), ibtn("Success Log Channel", "adm_ask_succlog", style="primary", icon=BTN_EMOJIS["tick"])],
                [ibtn("Daily Leaderboard", "adm_ask_ldbch", style="primary", icon=BTN_EMOJIS["crown"])],
                [ibtn("Back to Dashboard", "adm_home", style="danger", icon=BTN_EMOJIS["cross"])]
            ]}
            return await safe_edit(query, text, kb=btn)

        elif data == "adm_add_channel":
            USER_STATES[user_id] = {"state": "ADM_WAIT_ADD_CHANNEL"}
            text = f"""{E_ADD} <i><b>Add Subscription Channel</b>\n\nYou can add a channel by doing ANY of the following:\n\n1️⃣ <b>Forward any message</b> directly from your target channel here.\n2️⃣ Send the <b>Channel ID</b> (e.g., <code>-1001234567890</code>).\n3️⃣ Send the <b>Channel Username or Public Link</b> (e.g., <code>@mychannel</code> or <code>https://t.me/mychannel</code>).\n\n⚠️ <b>Note:</b> Ensure this bot is promoted to <b>Admin</b> in the channel to verify subscribers and generate links.</i>"""
            btn = {"inline_keyboard": [[ibtn("Cancel", "adm_cat_channels", style="danger", icon=BTN_EMOJIS["cross"])]]}
            return await safe_edit(query, text, kb=btn)

        elif data == "adm_manage_channels":
            fsubs = config.get("fsub_channels", [])
            if not fsubs:
                return await query.answer("No channels available to remove!", show_alert=True)
            
            btn_rows = []
            for idx, ch in enumerate(fsubs):
                title = ch.get("title", f"Channel {idx+1}")[:20]
                btn_rows.append([ibtn(f"Remove: {title}", f"adm_delch_{idx}", style="danger", icon=BTN_EMOJIS["cross"])])
            btn_rows.append([ibtn("Back", "adm_cat_channels", style="primary", icon=BTN_EMOJIS["cross"])])
            
            text = f"{E_GLOBE} <i><b>Manage Channels:</b>\nClick on any channel below to remove it from verification:</i>"
            return await safe_edit(query, text, {"inline_keyboard": btn_rows})

        elif data.startswith("adm_delch_"):
            idx = int(data.split("_")[2])
            fsubs = config.get("fsub_channels", [])
            if 0 <= idx < len(fsubs):
                removed = fsubs.pop(idx)
                await settings_col.update_one({"_id": "config"}, {"$set": {"fsub_channels": fsubs}})
                await query.answer(f"Channel '{removed.get('title')}' removed.", show_alert=True)
            config = await settings_col.find_one({"_id": "config"})
            text, kb = await get_admin_dashboard(config)
            return await safe_edit(query, text, kb)

        elif data == "adm_cat_limits":
            text = f"""{E_ADM} <i><b>Operational Parameters & Throttling</b>\n\n{E_GIFT} <b>Free Trial DM Allowance:</b> <code>{config.get('free_trial_limit')}</code>\n{E_WAIT} <b>Message Sending Delay:</b> <code>{config.get('msg_delay')}s</code>\n{E_MED} <b>Leaderboard Scheduled Hour:</b> <code>{config.get('ldb_time')}:00 IST</code>\n{E_MONEY} <b>Referral Bonus Reward:</b> <code>{config.get('ref_bonus')} DMs</code>\n{E_PROF} <b>Free Target Member Cap:</b> <code>{config.get('free_req_limit')}</code>\n\nSelect a parameter to modify:</i>"""
            btn = {"inline_keyboard": [
                [ibtn("Set Free Trial Allowance", "adm_ask_freetrial", style="success", icon=BTN_EMOJIS["gift"]), ibtn("Set Sending Delay", "adm_ask_delay", style="primary", icon=BTN_EMOJIS["wait"])],
                [ibtn("Set Leaderboard Schedule", "adm_ask_ldbtime", style="primary", icon=BTN_EMOJIS["cal"]), ibtn("Set Referral Bonus", "adm_ask_refbonus", style="success", icon=BTN_EMOJIS["add"])],
                [ibtn("Back to Dashboard", "adm_home", style="danger", icon=BTN_EMOJIS["cross"])]
            ]}
            return await safe_edit(query, text, kb=btn)

        elif data == "adm_cat_users":
            text = f"""{E_PROF} <i><b>User Management & Authorization</b>\n\nInspect user records, grant or revoke VIP access, clear stored sessions, or issue suspensions directly.</i>"""
            btn = {"inline_keyboard": [
                [ibtn("Inspect User Record", "adm_ask_checkuser", style="primary", icon=BTN_EMOJIS["user"]), ibtn("Wipe User Sessions", "adm_ask_clearsess", style="danger", icon=BTN_EMOJIS["cross"])],
                [ibtn("Grant VIP Access", "adm_ask_giveprem", style="success", icon=BTN_EMOJIS["crown"]), ibtn("Revoke VIP Access", "adm_ask_remprem", style="danger", icon=BTN_EMOJIS["ban"])],
                [ibtn("Suspend User", "adm_ask_banuser", style="danger", icon=BTN_EMOJIS["ban"]), ibtn("Reactivate User", "adm_ask_unbanuser", style="success", icon=BTN_EMOJIS["tick"])],
                [ibtn("Back to Dashboard", "adm_home", style="danger", icon=BTN_EMOJIS["cross"])]
            ]}
            return await safe_edit(query, text, kb=btn)

        elif data == "adm_broadcast":
            USER_STATES[user_id] = {"state": "ADM_WAITING_BROADCAST"}
            return await safe_edit(query, f"{E_GLOBE} <i><b>Create Broadcast Announcement:</b>\n\nPlease send or forward any message (Text, Media, Caption, etc.) you wish to broadcast to all registered bot users.</i>", {"inline_keyboard": [[ibtn("Cancel", "adm_cancel", style="danger", icon=BTN_EMOJIS["cross"])]]})

        # --- Sub-Action Prompt Triggers ---
        elif data.startswith("adm_ask_"):
            action = data.replace("adm_ask_", "")
            USER_STATES[user_id] = {"state": f"ADM_WAIT_{action.upper()}"}
            prompts = {
                "fampay": f"{E_TRI} <i>Please provide the new <b>Smart FamPay UPI ID</b> (e.g. <code>user@fam</code>):</i>",
                "manual": f"{E_TRI} <i>Please provide the new <b>Manual UPI ID</b> (e.g. <code>name@upi</code>):</i>",
                "crypto": f"{E_TRI} <i>Please provide the new <b>USDT (TRC-20) Crypto Address</b>:</i>",
                "fampayqr": f"{E_TRI} <i><b>Send a photo</b> of the FamPay QR Code (or send <code>none</code> to remove):</i>",
                "manualqr": f"{E_TRI} <i><b>Send a photo</b> of the Manual UPI QR Code (or send <code>none</code> to remove):</i>",
                "cryptoqr": f"{E_TRI} <i><b>Send a photo</b> of the Crypto QR Code (or send <code>none</code> to remove):</i>",
                "p_1d": f"{E_TRI} <i>Provide <b>1 Day Plan Price</b> in format: <code>INR USD</code> (e.g. <code>25 0.5</code>):</i>",
                "p_3d": f"{E_TRI} <i>Provide <b>3 Days Plan Price</b> in format: <code>INR USD</code> (e.g. <code>60 1.5</code>):</i>",
                "p_7d": f"{E_TRI} <i>Provide <b>7 Days Plan Price</b> in format: <code>INR USD</code> (e.g. <code>120 3</code>):</i>",
                "p_1m": f"{E_TRI} <i>Provide <b>1 Month Plan Price</b> in format: <code>INR USD</code> (e.g. <code>350 8</code>):</i>",
                "reqall": f"{E_TRI} <i>Provide Mandatory Request channel in format: <code>Chat_ID Invite_Link</code> (or <code>none</code>):</i>",
                "freech": f"{E_TRI} <i>Provide Free Target channel in format: <code>Chat_ID Invite_Link</code>:</i>",
                "logch": f"{E_TRI} <i>Provide Order Log Channel ID (e.g. <code>-100...</code>):</i>",
                "succlog": f"{E_TRI} <i>Provide Success Log Channel ID (e.g. <code>-100...</code>):</i>",
                "ldbch": f"{E_TRI} <i>Provide Daily Leaderboard Channel ID (e.g. <code>-100...</code>):</i>",
                "freetrial": f"{E_TRI} <i>Enter new Free Trial DM limit (e.g. <code>100</code>):</i>",
                "delay": f"{E_TRI} <i>Enter message delay interval in seconds (e.g. <code>0</code> or <code>1</code>):</i>",
                "ldbtime": f"{E_TRI} <i>Enter Leaderboard Posting Hour (0-23 in IST):</i>",
                "refbonus": f"{E_TRI} <i>Enter bonus DMs awarded per referral (e.g. <code>50</code>):</i>",
                "checkuser": f"{E_TRI} <i>Enter the Telegram User ID to inspect:</i>",
                "clearsess": f"{E_TRI} <i>Enter the Telegram User ID whose sessions you wish to wipe:</i>",
                "giveprem": f"{E_TRI} <i>Enter User ID and duration in format: <code>User_ID Days</code> (e.g. <code>12345678 30</code>):</i>",
                "remprem": f"{E_TRI} <i>Enter the User ID to revoke VIP access:</i>",
                "banuser": f"{E_TRI} <i>Enter the User ID to suspend:</i>",
                "unbanuser": f"{E_TRI} <i>Enter the User ID to reactivate:</i>",
                "supportlink": f"{E_TRI} <i>Send the new <b>Support Link</b> shown on the 'Contact Support' button (e.g. <code>https://t.me/yourusername</code> or <code>@yourusername</code>):</i>"
            }
            prompt_text = prompts.get(action, f"{E_TRI} <i>Please provide the updated parameter:</i>")
            btn = {"inline_keyboard": [[ibtn("Cancel", "adm_cancel", style="danger", icon=BTN_EMOJIS["cross"])]]}
            return await safe_edit(query, prompt_text, kb=btn)

        elif data == "adm_cancel":
            USER_STATES.pop(user_id, None)
            text, kb = await get_admin_dashboard(config)
            return await safe_edit(query, text, kb)

    # ================= USER CALLBACK ROUTES =================
    if data == "coming_soon": pass
    
    elif data == "check_join":
        joined, not_joined_list = await check_force_join(user_id)
        if not joined:
            text = f"{E_WRN} <i><b>Subscription Verification Required!</b>\n\nTo ensure quality service, please join our official channels before continuing.</i>"
            btn_list = []; row = []
            for i, (idx, link) in enumerate(not_joined_list):
                fixed_link = link if str(link).startswith("http") else f"https://t.me/{str(link).replace('@','')}"
                row.append(ibtn(f"{idx}", url=fixed_link, style="primary", icon=BTN_EMOJIS["target"]))
                if len(row) == 2: btn_list.append(row); row = []
            if row: btn_list.append(row)
            btn_list.append([ibtn("I Have Joined", "check_join", style="success", icon=BTN_EMOJIS["tick"])])
            
            try: await api_edit(user_id, query.message.id, text, {"inline_keyboard": btn_list})
            except: pass
            
            return await query.answer("You have not joined all channels yet! Please verify.", show_alert=True)
            
        first_name = html.escape(query.from_user.first_name if query.from_user else "User")
        text, btn = await get_home_menu(user_id, first_name, config)
        await query.message.delete()
        await api_send(user_id, text, kb=btn)

    elif data == "invite_earn":
        bot_info = await client.get_me()
        invite_link = f"https://t.me/{bot_info.username}?start={user_id}"
        text = f"{E_GIFT} <i><b>Invite & Earn Rewards</b>\n\nShare your link with friends to earn complimentary DM credits whenever they activate the bot!\n\n{E_LNK} <b>Your Unique Referral Link:</b>\n`{invite_link}`</i>"
        btn = {"inline_keyboard": [[ibtn("Back", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]}
        await safe_edit(query, text, kb=btn)

    elif data == "my_account":
        has_prem = await is_premium(user_id); u = await get_user(user_id)
        if has_prem:
            exp_str = get_ist_ts_str(u['premium_expiry'])
            status = f"{E_DIA} <i>VIP Premium\n{E_CAL} <b>Expires:</b> {exp_str}</i>"
        else: status = f"{E_WAIT} <i>Free Tier</i>"
            
        history = u.get("campaign_history", []) or []
        text = f"{E_PROF} <i><b>User Account Details:</b>\n\n{E_ID} <b>Account ID:</b> <code>{user_id}</code>\n{E_SHD} <b>Plan Status:</b> {status}\n{E_ACT} <b>Active Sessions:</b> {len(u.get('sessions', []))}\n{E_STAT} <b>Total Sent Messages:</b> {u.get('total_dms', 0)}\n{E_CAL} <b>Campaigns:</b> {len(history)}</i>"
        btn = {"inline_keyboard": [[ibtn("Campaign History", "campaign_history", style="primary", icon=BTN_EMOJIS["cal"])], [ibtn("Reset DM History", "reset_history", style="danger", icon=BTN_EMOJIS["cross"])], [ibtn("Back to Menu", "back_home", style="primary", icon=BTN_EMOJIS["home"])]]}
        await safe_edit(query, text, kb=btn)

    elif data == "campaign_history":
        u = await get_user(user_id)
        history = (u.get("campaign_history", []) or [])[-10:][::-1]
        if not history:
            body = "No campaign history found yet."
        else:
            rows = []
            for item in history:
                rows.append(
                    f"• <b>{html.escape(str(item.get('date', 'Unknown date')))}</b> — "
                    f"{html.escape(str(item.get('title', 'Campaign')))}\n"
                    f"  Sent: <b>{int(item.get('sent', 0))}</b> | "
                    f"Failed: <b>{int(item.get('failed', 0))}</b> | "
                    f"Status: <b>{html.escape(str(item.get('status', 'Unknown')))}</b>"
                )
            body = "\n\n".join(rows)
        await safe_edit(query, f"{E_CAL} <b>Recent Campaign History (Last 10)</b>\n\n{body}",
                        {"inline_keyboard": [[ibtn("Back to Account", "my_account", style="primary", icon=BTN_EMOJIS["user"])],
                                             [ibtn("Back to Dashboard", "back_home", style="danger", icon=BTN_EMOJIS["home"])]]})

    elif data == "remove_session":
        await users_col.update_one({"_id": user_id}, {"$set": {"sessions": []}})
        await safe_edit(query, f"{E_CHK} <i><b>All active Telegram sessions cleared successfully!</b></i>", {"inline_keyboard": [[ibtn("Back to Menu", "back_home", style="primary", icon=BTN_EMOJIS["home"])]]})

    elif data == "buy_premium":
        text = f"{E_PREM} <i><b>VIP Subscription Plans</b>\n\n<b>1 Day Access:</b> ₹{config.get('price_1d_inr')} | ${config.get('price_1d_usd')}\n<b>3 Days Access:</b> ₹{config.get('price_3d_inr')} | ${config.get('price_3d_usd')}\n<b>7 Days Access:</b> ₹{config.get('price_7d_inr')} | ${config.get('price_7d_usd')}\n<b>1 Month Access:</b> ₹{config.get('price_1m_inr')} | ${config.get('price_1m_usd')}\n\nSelect a plan to proceed:</i>"
        btn = {"inline_keyboard": [[ibtn("1 Day Plan", "plan_1", style="primary", icon=BTN_EMOJIS["diamond"]), ibtn("3 Days Plan", "plan_3", style="primary", icon=BTN_EMOJIS["diamond"])], [ibtn("7 Days Plan", "plan_7", style="success", icon=BTN_EMOJIS["diamond"]), ibtn("1 Month Plan", "plan_30", style="success", icon=BTN_EMOJIS["crown"])], [ibtn("Back to Menu", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]}
        await safe_edit(query, text, kb=btn)

    elif data.startswith("plan_"):
        days = int(data.split("_")[1])
        btn = {"inline_keyboard": [
            [ibtn("Instant Auto UPI Approval", f"pay_fampay_{days}", style="success", icon=BTN_EMOJIS["tick"])],
            [ibtn("Manual Admin Verification", f"pay_manual_{days}", style="primary", icon=BTN_EMOJIS["money"])],
            [ibtn("Crypto (USDT TRC-20)", f"pay_crypto_{days}", style="primary", icon=BTN_EMOJIS["diamond"])],
            [ibtn("Back to Plans", "buy_premium", style="danger", icon=BTN_EMOJIS["cross"])]
        ]}
        text = f"{E_MONEY} <i><b>Select Payment Method for {days} Days Plan:</b></i>"
        await safe_edit(query, text, kb=btn)

    elif data.startswith("pay_"):
        parts = data.split("_"); mthd = parts[1]; days = int(parts[2])
        price_inr = config.get(f"price_{days}d_inr") if days != 30 else config.get("price_1m_inr")
        price_usd = config.get(f"price_{days}d_usd") if days != 30 else config.get("price_1m_usd")
        
        if mthd == "fampay":
            if not config.get("auto_payment_status", False):
                return await query.answer("Auto-Approval is offline. Please choose Manual Payment.", show_alert=True)
            text = f"{E_MONEY} <i><b>Instant Auto-Approval Payment ({days} Days):</b>\n\n1. Transfer exactly <b>₹{price_inr}</b> to:\n<code>{config.get('upi_fampay', 'Not Set')}</code>\n2. Click 'I Have Paid' and provide the <b>UTR / Transaction ID</b>.\n\nAutomated bank verification will process your access in seconds.</i>"
            btn = {"inline_keyboard": [[ibtn("I Have Paid", f"sub_fampay_{days}_{price_inr}", style="success", icon=BTN_EMOJIS["tick"])], [ibtn("Back", f"plan_{days}", style="danger", icon=BTN_EMOJIS["cross"])]]}
            qr_photo = config.get("qr_fampay")
        elif mthd == "crypto":
            text = f"{E_DIA} <i><b>Crypto Payment ({days} Days):</b>\n\nTransfer exactly <b>${price_usd}</b> (USDT.TRC20) to:\n<code>{config.get('crypto', 'Not Set')}</code>\n\nSubmit your Transaction Hash for verification.</i>"
            btn = {"inline_keyboard": [[ibtn("I Have Paid", f"sub_man_{days}_{price_usd}", style="success", icon=BTN_EMOJIS["tick"])], [ibtn("Back", f"plan_{days}", style="danger", icon=BTN_EMOJIS["cross"])]]}
            qr_photo = config.get("qr_crypto")
        else: 
            text = f"{E_MONEY} <i><b>Manual UPI Transfer ({days} Days):</b>\n\n1. Transfer exactly <b>₹{price_inr}</b> to:\n<code>{config.get('upi_manual', 'Not Set')}</code>\n\n2. Click 'I Have Paid' and send the UTR & payment screenshot.</i>"
            btn = {"inline_keyboard": [[ibtn("I Have Paid", f"sub_man_{days}_{price_inr}", style="success", icon=BTN_EMOJIS["tick"])], [ibtn("Back", f"plan_{days}", style="danger", icon=BTN_EMOJIS["cross"])]]}
            qr_photo = config.get("qr_manual")

        await query.message.delete()
        if qr_photo and str(qr_photo).lower() not in ["not_set", "none", "null"] and len(str(qr_photo)) > 5:
            await api_send(user_id, text, kb=btn, photo=qr_photo)
        else: 
            await api_send(user_id, text, kb=btn)

    elif data.startswith("sub_fampay_"):
        parts = data.split("_")
        days = int(parts[2]); price = parts[3]
        USER_STATES[user_id] = {"state": "WAITING_FAMPAY_UTR", "days": days, "price": price}
        await query.message.delete()
        await api_send(user_id, f"{E_STAT} <i><b>Smart Payment Verification</b>\n\nPlease submit the <b>UTR Number</b> or <b>Transaction ID</b> below:\nExample: 312345678901</i>")

    elif data.startswith("sub_man_"):
        parts = data.split("_")
        days = int(parts[2]); price = parts[3]
        USER_STATES[user_id] = {"state": "WAITING_MANUAL_UTR", "days": days, "price": price}
        await query.message.delete()
        await api_send(user_id, f"{E_STAT} <i><b>Manual Verification (Step 1/2)</b>\n\nPlease send your <b>UTR Number / Transaction Hash</b> first:</i>")

    elif data == "add_session":
        USER_STATES[user_id] = {"state": "WAITING_PHONE"}
        text = f"{E_WAIT} <i><b>Session Account Generator</b>\nPlease enter your phone number with country code:\nExample: <code>+1234567890</code></i>"
        await safe_edit(query, text, {"inline_keyboard": [[ibtn("Cancel", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]})

    elif data == "start_dm":
        u = await get_user(user_id)
        if not u.get("sessions"): return await safe_edit(query, f"{E_WRN} <i><b>No Connected Accounts!</b> Please add an account session first.</i>", {"inline_keyboard": [[ibtn("ADD SESSION", "add_session", style="success", icon=BTN_EMOJIS["add"])], [ibtn("Back", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]})
        has_prem = await is_premium(user_id)
        rem_free = max(0, int(config.get("free_trial_limit", 100)) + int(u.get("bonus_dms", 0)) - int(u.get("total_dms", 0)))
        if not has_prem and rem_free <= 0: return await safe_edit(query, f"{E_WRN} <i><b>Trial Limit Reached!</b>\nYour free test allowance has ended. Please upgrade to VIP.</i>", {"inline_keyboard": [[ibtn("BUY PREMIUM", "buy_premium", style="success", icon=BTN_EMOJIS["diamond"])], [ibtn("Back", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]})
            
        custom_msg_type = u.get("custom_msg_type", "text")
        if custom_msg_type == "photo": msg_disp = "[Photo Message]"
        elif custom_msg_type == "forward_link": msg_disp = f"[Forward Link] {u.get('custom_msg')}"
        else: msg_disp = html.escape(u.get("custom_msg", "HELLO"))
        
        text = f"{E_PLAY} <i><b>Campaign Launch Terminal</b>\n\n{E_GLOBE} <b>Queued Content:</b>\n<code>{msg_disp}</code>\n\nChoose your audience or update your message below:</i>"
        btn = {"inline_keyboard": [
            [ibtn("Target Channel Join Requests", "tgt_own", style="primary", icon=BTN_EMOJIS["target"]), ibtn("Target Dialog DMs", "tgt_alt_dms", style="success", icon=BTN_EMOJIS["user"])], 
            [ibtn("Target Admin Free Channel", "tgt_free", style="primary", icon=BTN_EMOJIS["target"])], 
            [ibtn("Update Content", "set_msg", style="danger", icon=BTN_EMOJIS["setting"]), ibtn("Set Public Post", "set_fwd_msg", style="danger", icon=BTN_EMOJIS["globe"])], 
            [ibtn("Back to Main Menu", "back_home", style="primary", icon=BTN_EMOJIS["home"])]
        ]}
        await safe_edit(query, text, btn)

    elif data == "jr_dm":
        if user_id in ACTIVE_TASKS: return await api_send(user_id, f"{E_WRN} <i>A campaign is already running. Press <b>Stop</b> on it first.</i>")
        u = await get_user(user_id)
        if not u.get("sessions"): return await safe_edit(query, f"{E_WRN} <i><b>No Connected Accounts!</b> Please add an account session first.</i>", {"inline_keyboard": [[ibtn("ADD SESSION", "add_session", style="success", icon=BTN_EMOJIS["add"])], [ibtn("Back", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]})
        has_prem = await is_premium(user_id)
        rem_free = max(0, int(config.get("free_trial_limit", 100)) + int(u.get("bonus_dms", 0)) - int(u.get("total_dms", 0)))
        if not has_prem and rem_free <= 0: return await safe_edit(query, f"{E_WRN} <i><b>Trial Limit Reached!</b>\nYour free test allowance has ended. Please upgrade to VIP.</i>", {"inline_keyboard": [[ibtn("BUY PREMIUM", "buy_premium", style="success", icon=BTN_EMOJIS["diamond"])], [ibtn("Back", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]})
        t = u.get("custom_msg_type", "text")
        if t == "photo": msg_disp = "[Photo Message]"
        elif t == "forward_link": msg_disp = f"[Forward Link] {u.get('custom_msg')}"
        else: msg_disp = html.escape(u.get("custom_msg", "HELLO"))
        USER_STATES[user_id] = {"state": "WAITING_LINK", "is_free_ch": False, "jr_mode": True}
        await safe_edit(query, f"{E_TRI} <i><b>Join Req DM</b>\n\n{E_GLOBE} <b>Current Message:</b>\n<code>{msg_disp}</code>\n\nSend your <b>channel invite link</b> (your session account must be Admin there):\nExample: <code>https://t.me/+joinhash</code></i>", {"inline_keyboard": [[ibtn("Cancel", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]})

    elif data == "set_msg":
        USER_STATES[user_id] = {"state": "WAITING_FWD_LINK"}
        await safe_edit(query, f"{E_GLOBE} <i><b>Set Message</b>\n\nSend the message used for <b>Join Req DM</b> and <b>FAST Auto-Forward DM</b>:\n\n1️⃣ <b>Text</b>\n2️⃣ <b>Photo with Caption</b>\n3️⃣ A <b>public post link</b> / forwarded channel post (sent as forward)</i>", {"inline_keyboard": [[ibtn("Cancel", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]})

    elif data == "set_fwd_msg":
        USER_STATES[user_id] = {"state": "WAITING_FWD_LINK"}
        prompt = f"{E_LNK} <i><b>Set Forwarded Campaign Post</b>\n\nYou may do ANY of the following:\n\n1️⃣ Send a <b>Public Post Link</b> (e.g. <code>https://t.me/channel/123</code>)\n2️⃣ <b>Forward any post</b> directly from a public channel here.\n3️⃣ Send standard <b>Text</b> or a <b>Photo</b>.</i>"
        await safe_edit(query, prompt, {"inline_keyboard": [[ibtn("Cancel", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]})

    elif data == "tgt_own":
        u = await get_user(user_id); saved_channels = u.get("saved_channels", []); text = f"{E_TRI} <i><b>Target Audience Selection</b>\n\nSelect a previously used channel from below, or add a new channel.</i>"
        btns = []
        for i, ch in enumerate(saved_channels):
            title = ch.get("title", "Saved Channel")[:25] + ".." if len(ch.get("title", "")) > 25 else ch.get("title", "Saved Channel")
            btns.append([ibtn(f"{title}", f"usech_{i}", style="primary", icon=BTN_EMOJIS["globe"])])
        btns.append([ibtn("Add New Target Channel", "add_new_ch", style="success", icon=BTN_EMOJIS["add"])])
        if saved_channels: btns.append([ibtn("Clear History", "clear_saved_ch", style="danger", icon=BTN_EMOJIS["cross"])])
        btns.append([ibtn("Back", "back_home", style="primary", icon=BTN_EMOJIS["home"])])
        await safe_edit(query, text, {"inline_keyboard": btns})

    elif data == "clear_saved_ch":
        await users_col.update_one({"_id": user_id}, {"$set": {"saved_channels": []}})
        await safe_edit(query, f"{E_TRI} <i><b>Target Audience Selection</b>\n\nChannel history cleared.</i>", {"inline_keyboard": [[ibtn("Add New Target Channel", "add_new_ch", style="success", icon=BTN_EMOJIS["add"])], [ibtn("Back", "back_home", style="primary", icon=BTN_EMOJIS["home"])]]})

    elif data == "add_new_ch":
        USER_STATES[user_id] = {"state": "WAITING_LINK", "is_free_ch": False}
        await safe_edit(query, f"{E_TRI} <i>Please provide your target channel invite link:\nExample: <code>https://t.me/+joinhash</code></i>", {"inline_keyboard": [[ibtn("Cancel", "tgt_own", style="danger", icon=BTN_EMOJIS["cross"])]]})

    elif data == "tgt_alt_dms":
        u = await get_user(user_id)
        sessions = u.get('sessions', [])
        USER_STATES[user_id] = {"is_free_ch": False, "link": "ALT_DMS", "raw_link": "ALT_DMS"}
        
        if len(sessions) <= 1:
            USER_STATES[user_id]["sess_idx"] = "all"
            USER_STATES[user_id]["state"] = "WAITING_LIMIT"
            await safe_edit(query, f"{E_STAT} <i><b>How many DMs would you like to send?</b>\n(Please send a numeric amount)</i>", {"inline_keyboard": [[ibtn("Cancel", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]})
        else:
            text = f"{E_SYNC} <i><b>Multiple Accounts Detected!</b>\nSelect which account's active dialogs to target:</i>"
            btns = [[ibtn(f"Account {i+1}", f"selsess_{i}", style="primary", icon=BTN_EMOJIS["user"])] for i in range(len(sessions))]
            btns.append([ibtn("Target All Accounts", "selsess_all", style="success", icon=BTN_EMOJIS["tick"])])
            btns.append([ibtn("Cancel", "back_home", style="danger", icon=BTN_EMOJIS["cross"])])
            await safe_edit(query, text, {"inline_keyboard": btns})

    elif data.startswith("usech_"):
        u = await get_user(user_id); idx = int(data.split("_")[1]); saved_channels = u.get("saved_channels", [])
        if idx < len(saved_channels):
            USER_STATES[user_id] = {"is_free_ch": False}
            msg = await api_send(user_id, f"{E_SYNC} <i><b>Analyzing Channel & Tracking Requests...</b></i>")
            asyncio.create_task(check_and_show_stats(client, user_id, u, config, saved_channels[idx].get("link") or saved_channels[idx]["id"], msg, save_new=False))

    elif data == "tgt_free":
        u = await get_user(user_id)
        if config.get("free_channel_id", "none") == "none": return await query.answer("Admin has not configured a free target channel!", show_alert=True)
        USER_STATES[user_id] = {"is_free_ch": True}
        msg = await api_send(user_id, f"{E_SYNC} <i><b>Analyzing Free Target Channel...</b></i>")
        asyncio.create_task(check_and_show_stats(client, user_id, u, config, config.get("free_channel_link"), msg, save_new=False))

    elif data.startswith("selsess_"):
        if user_id not in USER_STATES:
            return await api_send(user_id, f"{E_WRN} <i><b>Session timed out!</b> Please start again from the main menu.</i>", {"inline_keyboard": [[ibtn("Back to Menu", "back_home", style="primary", icon=BTN_EMOJIS["home"])]]})
        USER_STATES[user_id]["sess_idx"] = data.split("_")[1]
        USER_STATES[user_id]["state"] = "WAITING_LIMIT"
        _mx = USER_STATES[user_id].get("pending")
        await safe_edit(query, f"{E_STAT} <i><b>How many DMs would you like to send?</b>\n(Tap Send to All, or send a number{f' - max {_mx}' if _mx else ''})</i>", limit_kb(user_id))

    elif data.startswith("flt_"):
        if user_id not in USER_STATES:
            return await api_send(user_id, f"{E_WRN} <i><b>Session timed out!</b> Please start again from the main menu.</i>", {"inline_keyboard": [[ibtn("Back to Menu", "back_home", style="primary", icon=BTN_EMOJIS["home"])]]})
        USER_STATES[user_id]["filter"] = data
        btn = {"inline_keyboard": [[ibtn("Launch Now", "sch_0", style="success", icon=BTN_EMOJIS["start"])], [ibtn("In 30 Minutes", "sch_30", style="primary", icon=BTN_EMOJIS["start"])], [ibtn("In 1 Hour", "sch_60", style="primary", icon=BTN_EMOJIS["start"])], [ibtn("Cancel", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]}
        await safe_edit(query, f"{E_CAL} <i><b>Campaign Timing:</b>\n\nWhen should the message sequence begin dispatching?</i>", btn)

    elif data.startswith("sch_"):
        delay = int(data.split("_")[1])
        u_state = USER_STATES.get(user_id, {})
        if not u_state:
            return await api_send(user_id, f"{E_WRN} <i><b>Session timed out!</b> Please re-launch your campaign.</i>")
            
        asyncio.create_task(setup_and_execute_dm(
            user_id, 
            u_state.get("limit", 0), 
            u_state.get("filter", "flt_all"), 
            delay, 
            u_state.get("is_free_ch", False), 
            u_state.get("link"), 
            u_state.get("raw_link"), 
            u_state.get("sess_idx", "all"), 
            client
        ))
        USER_STATES.pop(user_id, None)
        await safe_edit(query, f"{E_CHK} <i><b>Campaign Setup Finished!</b>\nThe automation engine will run in the background. Use <code>/chk</code> to observe real-time progress.</i>")

    elif data == "ff_menu":
        u = await get_user(user_id); sessions = u.get("sessions", [])
        if not sessions: return await safe_edit(query, f"{E_WRN} <i><b>No Connected Accounts!</b> Please add an account session first.</i>", {"inline_keyboard": [[ibtn("ADD SESSION", "add_session", style="success", icon=BTN_EMOJIS["add"])], [ibtn("Back", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]})
        text = f"{E_GLOBE} <i><b>FAST Auto-Forward DM</b>\n\nSends your set message to <b>every private chat</b> of your connected account(s) at high speed.\n\n{E_PROF} <b>Connected Accounts:</b> {len(sessions)}\n{E_GLOBE} <b>Set Message:</b> <code>{msg_display(u)}</code></i>"
        btn = {"inline_keyboard": [
            [ibtn("Start Forwarding", "ff_start", style="success", icon=BTN_EMOJIS["start"])],
            [ibtn("Preview", "ff_preview", style="primary", icon=BTN_EMOJIS["globe"])],
            [ibtn("Cancel", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]
        ]}
        await safe_edit(query, text, btn)

    elif data == "ff_preview":
        u = await get_user(user_id)
        t = u.get("custom_msg_type", "text"); body = u.get("custom_msg") or "HELLO"
        kb = {"inline_keyboard": [[ibtn("Start Forwarding", "ff_start", style="success", icon=BTN_EMOJIS["start"])], [ibtn("Back", "ff_menu", style="primary", icon=BTN_EMOJIS["home"])]]}
        head = f"{E_GLOBE} <i><b>Message Preview</b></i>\n\n"
        if t == "photo":
            await api_send(user_id, head + html.escape((u.get("custom_caption") or "")[:800]), kb, photo=body)
        elif t == "forward_link":
            src_chat, mid = body.split("|")
            try:
                await bot.forward_messages(int(user_id), int(src_chat) if src_chat.lstrip("-").isdigit() else src_chat, int(mid))
                await api_send(user_id, f"{E_GLOBE} <i><b>Preview above</b> - this post is sent as a forward.</i>", kb)
            except Exception:
                await api_send(user_id, head + f"<i>Forwarded post:</i> <code>{html.escape(str(body))}</code>", kb)
        else:
            await api_send(user_id, head + html.escape(str(body))[:3500], kb)

    elif data == "ff_start":
        u = await get_user(user_id)
        if not u.get("sessions"): return await safe_edit(query, f"{E_WRN} <i><b>No Connected Accounts!</b> Please add an account session first.</i>", {"inline_keyboard": [[ibtn("ADD SESSION", "add_session", style="success", icon=BTN_EMOJIS["add"])], [ibtn("Back", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]})
        if user_id in ACTIVE_TASKS: return await api_send(user_id, f"{E_WRN} <i>A campaign is already running. Press <b>Stop</b> on it first.</i>")
        lim, rem = await cap_limit(user_id, 10**9)
        if lim <= 0: return await safe_edit(query, f"{E_WRN} <i><b>Trial Limit Reached!</b>\nYour free test allowance has ended. Please upgrade to VIP.</i>", {"inline_keyboard": [[ibtn("BUY PREMIUM", "buy_premium", style="success", icon=BTN_EMOJIS["diamond"])], [ibtn("Back", "back_home", style="danger", icon=BTN_EMOJIS["cross"])]]})
        await launch_campaign(user_id, lim, "ALT_DMS", "ALT_DMS", "all", False, client)

    elif data == "jr_all":
        st = USER_STATES.get(user_id)
        if not st or not st.get("jr_mode") or not st.get("pending"):
            return await api_send(user_id, f"{E_WRN} <i><b>Session timed out!</b> Please press Join Req DM again.</i>")
        if user_id in ACTIVE_TASKS: return await api_send(user_id, f"{E_WRN} <i>A campaign is already running. Press <b>Stop</b> on it first.</i>")
        st = USER_STATES.pop(user_id)
        lim, rem = await cap_limit(user_id, int(st["pending"]))
        if lim <= 0: return await api_send(user_id, f"{E_WRN} <i><b>Trial Limit Reached!</b> Please upgrade to VIP.</i>")
        await safe_edit(query, f"{E_CHK} <i><b>Starting Join Req DM...</b></i>")
        await launch_campaign(user_id, lim, st.get("link"), st.get("raw_link"), st.get("sess_idx", "all"), st.get("is_free_ch", False), client)

    elif data == "stop_task":
        task = ACTIVE_TASKS.get(user_id)
        if task: task["status"] = "stopped"

    elif data == "reset_history":
        await users_col.update_one({"_id": user_id}, {"$set": {"messaged_users": {}}})
        await api_send(user_id, f"{E_CHK} <i><b>DM history cleared!</b> Join Req DM will treat all requests as new again.</i>", {"inline_keyboard": [[ibtn("Back to Menu", "back_home", style="primary", icon=BTN_EMOJIS["home"])]]})

    elif data == "how_to_use":
        text = f"{E_ADM} <i><b>Documentation & Terms</b>\n\n1. Connect your account sessions via the main menu.\n2. Ensure your account holds Admin permissions in target groups.\n3. Set your message via 'Set Message', then use 'FAST Auto-Forward DM' or 'Join Req DM'.\n\nAll subscriptions and orders are final. Use responsibly.</i>"
        await safe_edit(query, text, {"inline_keyboard": [[ibtn("Back to Menu", "back_home", style="primary", icon=BTN_EMOJIS["home"])]]})

    elif data.startswith("setlang_"):
        code_lang = data.split("_", 1)[1]
        if code_lang not in LANGUAGES: return
        u = await get_user(user_id)
        await users_col.update_one({"_id": user_id}, {"$set": {"language": code_lang}}, upsert=True)
        if not u.get("terms_accepted"):
            await safe_edit(query, tr(user_id, "terms"), {"inline_keyboard": [[ibtn("Terms & Conditions", url=TERMS_URL, style="primary", icon=BTN_EMOJIS["shield"])], [ibtn("Agree", "terms_agree", style="success", icon=BTN_EMOJIS["tick"])]]})
        else:
            first_name = html.escape(query.from_user.first_name if query.from_user else "User")
            await route_user_after_onboarding(user_id, first_name, config, client_or_query=query, is_query=True)
        return

    elif data in ("terms_agree", "terms_dashboard"):
        current_user = await get_user(user_id)
        if not current_user.get("terms_accepted"):
            await users_col.update_one({"_id": user_id}, {"$set": {"terms_accepted": True, "terms_accepted_at": int(time.time())}}, upsert=True)
        first_name = html.escape(query.from_user.first_name if query.from_user else "User")
        await route_user_after_onboarding(user_id, first_name, config, client_or_query=query, is_query=True)

    elif data == "open_menu":
        if int(user_id) not in ADMINS:
            joined, not_joined_list = await check_force_join(user_id)
            if not joined:
                return await query.answer("Please join the required channel and group first!", show_alert=True)
        first_name = html.escape(query.from_user.first_name if query.from_user else "User")
        text, btn = await get_home_menu(user_id, first_name, config)
        await safe_edit(query, text, kb=btn)

    elif data == "change_lang_menu":
        await safe_edit(query, tr(user_id, "choose"), kb=language_keyboard())

    elif data == "back_to_dashboard":
        first_name = html.escape(query.from_user.first_name if query.from_user else "User")
        await route_user_after_onboarding(user_id, first_name, config, client_or_query=query, is_query=True)

    elif data == "cancel_flow":
        USER_STATES.pop(user_id, None)
        first_name = html.escape(query.from_user.first_name if query.from_user else "User")
        text, btn = await get_home_menu(user_id, first_name, config)
        await safe_edit(query, f"{E_CROSS} <i>Current process cancelled.</i>\\n\\n{text}", kb=btn)

    elif data == "back_home":
        first_name = html.escape(query.from_user.first_name if query.from_user else "User")
        text, btn = await get_home_menu(user_id, first_name, config)
        await safe_edit(query, text, kb=btn)

async def admin_manual_approve(client, query):
    if query.from_user.id not in ADMINS: return
    action, target, days = query.data.split("_")[0:3]; days = int(days)
    
    if action == "manapp":
        u = await get_user(target); current_time = time.time()
        nex = max(current_time, u.get("premium_expiry", 0)) + (days * 86400)
        await users_col.update_one({"_id": target}, {"$set": {"premium_expiry": nex}})
        exp_str = get_ist_ts_str(nex)
        try: await api_send(target, f"{E_DIA} <i><b>Payment Approved by Administrator! ({days} Days)</b>\n\n{E_GIFT} <b>VIP Status Valid Until:</b>\n{E_CAL} <b>{exp_str}</b></i>")
        except: pass
        
        payload = {"chat_id": query.message.chat.id, "message_id": query.message.id, "caption": query.message.caption + f"\n\n{E_CHK} <b>APPROVED BY ADMIN</b>", "parse_mode": "HTML"}
        async with aiohttp.ClientSession() as session:
            await session.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageCaption", json=payload)
    else:
        payload = {"chat_id": query.message.chat.id, "message_id": query.message.id, "caption": query.message.caption + f"\n\n{E_CROSS} <b>REJECTED BY ADMIN</b>", "parse_mode": "HTML"}
        async with aiohttp.ClientSession() as session:
            await session.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageCaption", json=payload)
        try: await api_send(target, f"{E_WRN} <i><b>Payment rejected by administrator.</b> Contact support if funds were deducted.</i>")
        except: pass

async def handle_states(client, message):
    if not message.text and not message.photo and not message.forward_from_chat: return
    user_id = str(message.chat.id)
    if message.text and message.text.startswith("/"):
        if user_id in USER_STATES: USER_STATES.pop(user_id, None)
        return

    try:
        if user_id not in USER_STATES: return
        state = USER_STATES[user_id].get("state")
        config = await settings_col.find_one({"_id": "config"})

        # ================= 🛠️ ADMIN STATE HANDLERS =================
        if state and state.startswith("ADM_WAIT_"):
            val = message.text.strip() if message.text else ""

            # Dynamic Multiple Channel Addition via Forward, ID, or Link
            if state == "ADM_WAIT_ADD_CHANNEL":
                USER_STATES.pop(user_id, None)
                chat_id, chat_title, chat_link = None, None, None

                # 1. Check if forwarded message from chat
                if message.forward_from_chat:
                    chat_id = str(message.forward_from_chat.id)
                    chat_title = message.forward_from_chat.title or "Channel"
                    if message.forward_from_chat.username:
                        chat_link = f"https://t.me/{message.forward_from_chat.username}"
                    else:
                        try:
                            chat_link = await client.export_chat_invite_link(int(chat_id))
                        except Exception:
                            chat_link = f"https://t.me/c/{chat_id.replace('-100', '')}"

                # 2. Check if sent as text (ID, username, or link)
                elif val:
                    target = val
                    if "t.me/" in val and not ("+" in val or "joinchat" in val):
                        target = "@" + val.split("t.me/")[-1].split("/")[0].replace("@", "")
                    elif val.lstrip("-").isdigit():
                        target = int(val)
                    try:
                        c_info = await client.get_chat(target)
                        chat_id = str(c_info.id)
                        chat_title = c_info.title or "Channel"
                        if c_info.username:
                            chat_link = f"https://t.me/{c_info.username}"
                        elif c_info.invite_link:
                            chat_link = c_info.invite_link
                        else:
                            try:
                                chat_link = await client.export_chat_invite_link(c_info.id)
                            except Exception:
                                chat_link = f"https://t.me/c/{chat_id.replace('-100', '')}"
                    except Exception as err:
                        return await api_send(user_id, f"{E_CROSS} <i><b>Failed to resolve channel:</b> <code>{err}</code>\nEnsure the bot is added as an Admin in that channel.</i>", {"inline_keyboard": [[ibtn("Try Again", "adm_add_channel", style="primary", icon=BTN_EMOJIS["add"])]]})
                else:
                    return await api_send(user_id, f"{E_WRN} <i>Please forward a post or send a valid Channel ID/Username.</i>")

                fsubs = config.get("fsub_channels", [])
                if any(str(c.get("id")) == str(chat_id) for c in fsubs):
                    return await api_send(user_id, f"{E_WRN} <i>This channel is already registered!</i>", {"inline_keyboard": [[ibtn("Back to Channels", "adm_cat_channels", style="primary", icon=BTN_EMOJIS["target"])]]})

                fsubs.append({"id": chat_id, "title": chat_title, "link": chat_link})
                await settings_col.update_one({"_id": "config"}, {"$set": {"fsub_channels": fsubs}})
                return await api_send(user_id, f"{E_CHK} <i><b>Channel successfully added!</b>\n\n<b>Title:</b> {html.escape(chat_title)}\n<b>ID:</b> <code>{chat_id}</code>\n<b>Link:</b> {chat_link}</i>", {"inline_keyboard": [[ibtn("View Channels", "adm_cat_channels", style="success", icon=BTN_EMOJIS["target"])]]})

            USER_STATES.pop(user_id, None)

            # Payments
            if state == "ADM_WAIT_FAMPAY":
                await settings_col.update_one({"_id": "config"}, {"$set": {"upi_fampay": val}})
                return await api_send(user_id, f"{E_CHK} <i>FamPay UPI updated to: <code>{val}</code></i>", {"inline_keyboard": [[ibtn("Return to Gateways", "adm_cat_pay", style="primary", icon=BTN_EMOJIS["money"])]]})

            elif state == "ADM_WAIT_MANUAL":
                await settings_col.update_one({"_id": "config"}, {"$set": {"upi_manual": val}})
                return await api_send(user_id, f"{E_CHK} <i>Manual UPI updated to: <code>{val}</code></i>", {"inline_keyboard": [[ibtn("Return to Gateways", "adm_cat_pay", style="primary", icon=BTN_EMOJIS["money"])]]})

            elif state == "ADM_WAIT_CRYPTO":
                await settings_col.update_one({"_id": "config"}, {"$set": {"crypto": val}})
                return await api_send(user_id, f"{E_CHK} <i>Crypto Address updated to: <code>{val}</code></i>", {"inline_keyboard": [[ibtn("Return to Gateways", "adm_cat_pay", style="primary", icon=BTN_EMOJIS["diamond"])]]})

            elif state in ["ADM_WAIT_FAMPAYQR", "ADM_WAIT_MANUALQR", "ADM_WAIT_CRYPTOQR"]:
                k = state.replace("ADM_WAIT_", "").lower()
                if message.photo:
                    await settings_col.update_one({"_id": "config"}, {"$set": {f"qr_{k.replace('qr','')}": message.photo.file_id}})
                    return await api_send(user_id, f"{E_CHK} <i>QR Code updated successfully!</i>", {"inline_keyboard": [[ibtn("Return to Gateways", "adm_cat_pay", style="primary", icon=BTN_EMOJIS["money"])]]})
                elif val.lower() == "none":
                    await settings_col.update_one({"_id": "config"}, {"$set": {f"qr_{k.replace('qr','')}": "none"}})
                    return await api_send(user_id, f"{E_CHK} <i>QR Code removed.</i>", {"inline_keyboard": [[ibtn("Return to Gateways", "adm_cat_pay", style="primary", icon=BTN_EMOJIS["money"])]]})
                else:
                    return await api_send(user_id, f"{E_WRN} <i>Please provide a photo or type 'none'.</i>")

            # Pricing
            elif state in ["ADM_WAIT_P_1D", "ADM_WAIT_P_3D", "ADM_WAIT_P_7D", "ADM_WAIT_P_1M"]:
                plan_map = {"ADM_WAIT_P_1D": "1d", "ADM_WAIT_P_3D": "3d", "ADM_WAIT_P_7D": "7d", "ADM_WAIT_P_1M": "1m"}
                p_code = plan_map[state]
                parts = val.split()
                if len(parts) != 2:
                    return await api_send(user_id, f"{E_WRN} <i>Invalid format! Use: <code>INR USD</code> (e.g. <code>25 0.5</code>)</i>")
                await settings_col.update_one({"_id": "config"}, {"$set": {f"price_{p_code}_inr": parts[0], f"price_{p_code}_usd": parts[1]}})
                return await api_send(user_id, f"{E_CHK} <i>Pricing for {p_code.upper()} updated: ₹{parts[0]} | ${parts[1]}</i>", {"inline_keyboard": [[ibtn("Return to Pricing", "adm_cat_price", style="primary", icon=BTN_EMOJIS["diamond"])]]})

            # Single Route Channels
            elif state == "ADM_WAIT_REQALL":
                if val.lower() == "none":
                    await settings_col.update_one({"_id": "config"}, {"$set": {"reqall_id": "none", "reqall_link": "none"}})
                    return await api_send(user_id, f"{E_CHK} <i>Mandatory Request Channel Disabled.</i>", {"inline_keyboard": [[ibtn("Return to Channels", "adm_cat_channels", style="primary", icon=BTN_EMOJIS["target"])]]})
                parts = val.split()
                if len(parts) >= 2:
                    await settings_col.update_one({"_id": "config"}, {"$set": {"reqall_id": parts[0], "reqall_link": parts[1]}})
                    return await api_send(user_id, f"{E_CHK} <i>Mandatory Request Channel set!</i>", {"inline_keyboard": [[ibtn("Return to Channels", "adm_cat_channels", style="primary", icon=BTN_EMOJIS["target"])]]})
                return await api_send(user_id, f"{E_WRN} <i>Format: <code>Chat_ID Invite_Link</code></i>")

            elif state == "ADM_WAIT_FREECH":
                parts = val.split()
                if len(parts) >= 2:
                    await settings_col.update_one({"_id": "config"}, {"$set": {"free_channel_id": parts[0], "free_channel_link": parts[1]}})
                    return await api_send(user_id, f"{E_CHK} <i>Free Target Channel configured!</i>", {"inline_keyboard": [[ibtn("Return to Channels", "adm_cat_channels", style="primary", icon=BTN_EMOJIS["target"])]]})
                return await api_send(user_id, f"{E_WRN} <i>Format: <code>Chat_ID Invite_Link</code></i>")

            elif state in ["ADM_WAIT_LOGCH", "ADM_WAIT_SUCCLOG", "ADM_WAIT_LDBCH"]:
                field_map = {"ADM_WAIT_LOGCH": "log_channel", "ADM_WAIT_SUCCLOG": "success_log_channel", "ADM_WAIT_LDBCH": "leaderboard_channel"}
                f_name = field_map[state]
                await settings_col.update_one({"_id": "config"}, {"$set": {f_name: val}})
                return await api_send(user_id, f"{E_CHK} <i>{f_name} route updated to: <code>{val}</code></i>", {"inline_keyboard": [[ibtn("Return to Channels", "adm_cat_channels", style="primary", icon=BTN_EMOJIS["target"])]]})

            # Limits & Delays
            elif state in ["ADM_WAIT_FREETRIAL", "ADM_WAIT_DELAY", "ADM_WAIT_LDBTIME", "ADM_WAIT_REFBONUS"]:
                if not val.isdigit():
                    return await api_send(user_id, f"{E_WRN} <i>Value must be numeric!</i>")
                limit_map = {"ADM_WAIT_FREETRIAL": "free_trial_limit", "ADM_WAIT_DELAY": "msg_delay", "ADM_WAIT_LDBTIME": "ldb_time", "ADM_WAIT_REFBONUS": "ref_bonus"}
                f_name = limit_map[state]
                await settings_col.update_one({"_id": "config"}, {"$set": {f_name: int(val)}})
                return await api_send(user_id, f"{E_CHK} <i>{f_name} updated to: <code>{val}</code></i>", {"inline_keyboard": [[ibtn("Return to Limits", "adm_cat_limits", style="primary", icon=BTN_EMOJIS["setting"])]]})

            # Support Link
            elif state == "ADM_WAIT_SUPPORTLINK":
                link = val.strip()
                if link.startswith("@"): link = "https://t.me/" + link[1:]
                elif link.startswith("t.me/"): link = "https://" + link
                if not (link.startswith("https://") or link.startswith("http://")) or " " in link:
                    return await api_send(user_id, f"{E_WRN} <i>Invalid link. Send a link like <code>https://t.me/username</code> or <code>@username</code>.</i>")
                await settings_col.update_one({"_id": "config"}, {"$set": {"support_link": link}})
                USER_STATES.pop(user_id, None)
                return await api_send(user_id, f"{E_CHK} <i><b>Support link updated!</b>\n<code>{html.escape(link)}</code></i>", {"inline_keyboard": [[ibtn("Admin Dashboard", "adm_home", style="primary", icon=BTN_EMOJIS["target"])]]})

            # User Controls
            elif state == "ADM_WAIT_CHECKUSER":
                u = await get_user(val)
                is_p = "Yes" if u.get('premium_expiry',0) > time.time() else "No"
                details = f"""{E_PROF} <i><b>User Information:</b>\n\n{E_ID} <b>User ID:</b> <code>{u['_id']}</code>\n{E_DIA} <b>VIP Status:</b> {is_p}\n{E_STAT} <b>Lifetime DMs Sent:</b> {u.get('total_dms', 0)}\n{E_ACT} <b>Connected Sessions:</b> {len(u.get('sessions', []))}\n{E_STOP} <b>Suspended:</b> {'Yes' if u.get('banned') else 'No'}</i>"""
                return await api_send(user_id, details, {"inline_keyboard": [[ibtn("Return to User Directory", "adm_cat_users", style="primary", icon=BTN_EMOJIS["user"])]]})

            elif state == "ADM_WAIT_CLEARSESS":
                await users_col.update_one({"_id": val}, {"$set": {"sessions": []}})
                return await api_send(user_id, f"{E_CHK} <i>Sessions cleared for user: <code>{val}</code></i>", {"inline_keyboard": [[ibtn("Return to User Directory", "adm_cat_users", style="primary", icon=BTN_EMOJIS["user"])]]})

            elif state == "ADM_WAIT_GIVEPREM":
                parts = val.split()
                if len(parts) != 2 or not parts[1].isdigit():
                    return await api_send(user_id, f"{E_WRN} <i>Format: <code>User_ID Days</code> (e.g. <code>12345678 30</code>)</i>")
                t, d = parts[0], int(parts[1])
                u = await get_user(t); cur = time.time()
                nex = (u.get("premium_expiry", 0) + (d * 86400)) if u.get("premium_expiry", 0) > cur else (cur + (d * 86400))
                await users_col.update_one({"_id": t}, {"$set": {"premium_expiry": nex}})
                return await api_send(user_id, f"{E_CHK} <i>VIP Access granted to {t} for {d} days!</i>", {"inline_keyboard": [[ibtn("Return to User Directory", "adm_cat_users", style="primary", icon=BTN_EMOJIS["crown"])]]})

            elif state == "ADM_WAIT_REMPREM":
                await users_col.update_one({"_id": val}, {"$set": {"premium_expiry": 0}})
                return await api_send(user_id, f"{E_CHK} <i>VIP Access revoked for user: <code>{val}</code></i>", {"inline_keyboard": [[ibtn("Return to User Directory", "adm_cat_users", style="primary", icon=BTN_EMOJIS["ban"])]]})

            elif state == "ADM_WAIT_BANUSER":
                await users_col.update_one({"_id": val}, {"$set": {"banned": True}})
                return await api_send(user_id, f"{E_CHK} <i>User {val} has been suspended!</i>", {"inline_keyboard": [[ibtn("Return to User Directory", "adm_cat_users", style="primary", icon=BTN_EMOJIS["ban"])]]})

            elif state == "ADM_WAIT_UNBANUSER":
                await users_col.update_one({"_id": val}, {"$set": {"banned": False}})
                return await api_send(user_id, f"{E_CHK} <i>User {val} has been reactivated!</i>", {"inline_keyboard": [[ibtn("Return to User Directory", "adm_cat_users", style="primary", icon=BTN_EMOJIS["tick"])]]})

        # Broadcast State
        elif state == "ADM_WAITING_BROADCAST":
            USER_STATES.pop(user_id, None)
            c = 0
            status_msg = await api_send(user_id, f"{E_SYNC} <i><b>Broadcasting message to all users...</b></i>")
            async for u in users_col.find({}):
                try:
                    await message.copy(int(u["_id"]))
                    c += 1
                    await asyncio.sleep(0.05)
                except: pass
            return await api_edit(status_msg.chat.id, status_msg.id, f"{E_CHK} <i><b>Broadcast Completed!</b> Delivered to {c} users.</i>", {"inline_keyboard": [[ibtn("Admin Dashboard", "adm_home", style="primary", icon=BTN_EMOJIS["target"])]]})

        # ================= REGULAR USER STATES =================
        elif state == "WAITING_FWD_LINK":
            msg_disp = ""
            if message.forward_from_chat and getattr(message.forward_from_chat, 'username', None):
                ch_username = message.forward_from_chat.username
                msg_id = message.forward_from_message_id
                await users_col.update_one({"_id": user_id}, {"$set": {"custom_msg_type": "forward_link", "custom_msg": f"{ch_username}|{msg_id}", "custom_caption": ""}})
                msg_disp = f"[Forwarded Post] @{ch_username}/{msg_id}"
                
            elif message.text and re.match(r"^https?://t\.me/(?:c/\d+|[A-Za-z0-9_]{4,})/\d+(?:/\d+)?/?(?:\?\S*)?$", message.text.strip()):
                m = re.match(r"^https?://t\.me/(?:(c)/(\d+)|([A-Za-z0-9_]{4,}))/(\d+)(?:/(\d+))?", message.text.strip())
                if m.group(1):
                    src_chat = f"-100{m.group(2)}"
                    msg_id = m.group(5) or m.group(4)
                else:
                    src_chat = m.group(3)
                    msg_id = m.group(5) or m.group(4)
                await users_col.update_one({"_id": user_id}, {"$set": {"custom_msg_type": "forward_link", "custom_msg": f"{src_chat}|{msg_id}", "custom_caption": ""}})
                msg_disp = f"[Forward Link] {src_chat}/{msg_id}"

            elif message.text:
                await users_col.update_one({"_id": user_id}, {"$set": {"custom_msg_type": "text", "custom_msg": message.text, "custom_caption": ""}})
                msg_disp = html.escape(message.text)
                
            elif message.photo:
                await users_col.update_one({"_id": user_id}, {"$set": {"custom_msg_type": "photo", "custom_msg": message.photo.file_id, "custom_caption": message.caption or ""}})
                msg_disp = "[Photo Message]"
                
            else:
                USER_STATES.pop(user_id, None)
                return await api_send(user_id, f"{E_WRN} <i>Invalid format. Please send text, photo, link, or forward a post.</i>")
                
            USER_STATES.pop(user_id, None)
            text = f"{E_CHK} <i><b>Message Saved!</b>\n\n{E_GLOBE} <b>Queued Content:</b>\n<code>{msg_disp}</code>\n\nThis message will be used for Join Req DM.</i>"
            btn = {"inline_keyboard": [
                [ibtn("JOIN REQ DM", "jr_dm", style="success", icon=BTN_EMOJIS["start"])],
                [ibtn("Set Message", "set_msg", style="primary", icon=BTN_EMOJIS["setting"]), ibtn("FAST Auto-Forward DM", "ff_menu", style="primary", icon=BTN_EMOJIS["globe"])],
                [ibtn("Back to Main Menu", "back_home", style="primary", icon=BTN_EMOJIS["home"])]
            ]}
            await api_send(user_id, text, kb=btn)

        elif state == "WAITING_FAMPAY_UTR":
            utr = message.text.strip() if message.text else ""
            if not utr or len(utr) < 5 or not utr.isalnum(): 
                USER_STATES.pop(user_id, None)
                return await api_send(user_id, f"{E_WRN} <i>Invalid UTR/Transaction reference. Please try again.</i>")
            
            user_state_data = USER_STATES.pop(user_id, {})
            days = user_state_data.get("days", 1)
            price = float(user_state_data.get("price", 0.0))
            
            msg = await api_send(user_id, f"{E_SYNC} <i><b>Verifying bank records for ID: {utr}...</b></i>")
            paid_amount = await asyncio.to_thread(check_payment_in_gmail, utr)
            
            if paid_amount and paid_amount >= price:
                u = await get_user(user_id); current_time = time.time()
                today_date = get_ist_str("%Y-%m-%d")
                
                nex = max(current_time, u.get("premium_expiry", 0)) + (days * 86400)
                await users_col.update_one({"_id": user_id}, {"$set": {"premium_expiry": nex}})
                exp_str = get_ist_ts_str(nex)
                await api_edit(msg.chat.id, msg.id, f"{E_DIA} <i><b>Payment Verified Automatically! ({days} Days)</b>\n\n{E_CHK} Reference ID: <code>{utr}</code>\n{E_MONEY} Amount: ₹{paid_amount}\n\n{E_GIFT} <b>VIP Status Valid Until:</b>\n{E_CAL} <b>{exp_str}</b></i>")
                try: await api_send(ADMINS[0], f"{E_DIA} <i><b>Auto-Approval Log</b>\n{E_PROF} User ID: <code>{user_id}</code>\n{E_MONEY} Paid: ₹{paid_amount} ({days} Days)\n{E_ID} Ref: <code>{utr}</code></i>")
                except: pass
                await settings_col.update_one({"_id": "config"}, {"$inc": {"total_sales_inr": paid_amount, f"sales_history.{today_date}": paid_amount}})
            else:
                await api_edit(msg.chat.id, msg.id, f"{E_WRN} <i><b>Payment Record Not Found!</b>\nCould not verify ₹{price} for ID <code>{utr}</code>. If just transferred, wait 1-2 minutes and re-submit.</i>")

        elif state == "WAITING_MANUAL_UTR":
            utr = message.text.strip() if message.text else ""
            if not utr or len(utr) < 5:
                USER_STATES.pop(user_id, None)
                return await api_send(user_id, f"{E_WRN} <i>Invalid reference ID. Process cancelled.</i>")
            
            USER_STATES[user_id]["utr"] = utr
            USER_STATES[user_id]["state"] = "WAITING_MANUAL_SS"
            await api_send(user_id, f"{E_STAT} <i><b>Step 2/2:</b> Please send the <b>Payment Screenshot</b>:</i>")

        elif state == "WAITING_MANUAL_SS":
            if not message.photo: 
                USER_STATES.pop(user_id, None)
                return await api_send(user_id, f"{E_WRN} <i>Please attach a valid photo screenshot. Process aborted.</i>")
                
            user_state_data = USER_STATES.pop(user_id, {})
            days = user_state_data.get("days", 1)
            utr = user_state_data.get("utr", "Unknown")
            
            btn = {"inline_keyboard": [[ibtn("Approve", f"manapp_{user_id}_{days}", style="success", icon=BTN_EMOJIS["tick"]), ibtn("Reject", f"manrej_{user_id}_{days}", style="danger", icon=BTN_EMOJIS["cross"])]]}
            for admin in ADMINS:
                try: await api_send(admin, f"{E_MONEY} <i><b>Manual Payment Pending Verification!</b>\n{E_PROF} User ID: <code>{user_id}</code>\nName: {message.from_user.first_name}\n{E_CAL} Duration: {days} Days\n{E_CHK} UTR/Hash: <code>{utr}</code></i>", kb=btn, photo=message.photo.file_id)
                except: pass
            await api_send(user_id, f"{E_WAIT} <i><b>Submission Received!</b> Sent to admins for prompt review.</i>")

        elif state == "WAITING_PHONE":
            phone = message.text.replace(" ", "") if message.text else ""
            if not phone:
                USER_STATES.pop(user_id, None)
                return await api_send(user_id, f"{E_WRN} <i>Invalid phone number. Please try again.</i>")
            
            if phone.isdigit() and not phone.startswith("+"):
                phone = "+" + phone
                
            msg = await api_send(user_id, f"{E_SYNC} <i>Connecting to Telegram cloud servers...</i>")
            temp_client = Client(f"session_{user_id}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
            await temp_client.connect()
            try:
                code_info = await temp_client.send_code(phone)
                USER_STATES[user_id].update({"state": "WAITING_OTP", "phone": phone, "phone_code_hash": code_info.phone_code_hash, "temp_client": temp_client})
                await api_edit(msg.chat.id, msg.id, f"{E_STAT} <i><b>OTP Code Dispatched!</b>\n\n{E_CHK} <b>Send with spaces between digits:</b> <code>1 2 3 4 5</code></i>")
            except Exception as e_phone: 
                USER_STATES.pop(user_id, None)
                await api_edit(msg.chat.id, msg.id, f"{E_WRN} <i><b>Error:</b> {e_phone}</i>")
                try: await temp_client.disconnect()
                except: pass

        elif state == "WAITING_OTP":
            otp = message.text.replace(" ", "") if message.text else ""
            if not otp:
                USER_STATES.pop(user_id, None)
                return await api_send(user_id, f"{E_WRN} <i>Invalid OTP. Please try again.</i>")
                
            user_state_data = USER_STATES.get(user_id, {})
            temp_client = user_state_data.get("temp_client")
            if not temp_client:
                USER_STATES.pop(user_id, None)
                return await api_send(user_id, f"{E_WRN} <i>Session expired. Please start over.</i>")
                
            msg = await api_send(user_id, f"{E_SYNC} <i>Authenticating OTP code...</i>")
            try:
                await temp_client.sign_in(user_state_data.get("phone"), user_state_data.get("phone_code_hash"), otp)
                ss = await temp_client.export_session_string()
                await users_col.update_one({"_id": user_id}, {"$push": {"sessions": ss}})
                await api_edit(msg.chat.id, msg.id, f"{E_CHK} <i><b>Session Connected Successfully!</b>\nRedirecting to Menu...</i>")
                await temp_client.disconnect(); USER_STATES.pop(user_id, None)
                
                await asyncio.sleep(1.5); config = await settings_col.find_one({"_id": "config"})
                first_name = html.escape(message.from_user.first_name if message.from_user else "User")
                text, btn = await get_home_menu(user_id, first_name, config)
                await api_send(user_id, text, kb=btn)
            except SessionPasswordNeeded:
                USER_STATES[user_id]["state"] = "WAITING_PASSWORD"
                await api_edit(msg.chat.id, msg.id, f"{E_SHD} <i><b>Two-Step Verification (2FA) Password Required:</b></i>")
            except Exception as e_otp: 
                USER_STATES.pop(user_id, None)
                await api_edit(msg.chat.id, msg.id, f"{E_WRN} <i><b>Error:</b> {e_otp}</i>")
                try: await temp_client.disconnect()
                except: pass
                
        elif state == "WAITING_PASSWORD":
            user_state_data = USER_STATES.get(user_id, {})
            temp_client = user_state_data.get("temp_client")
            if not temp_client:
                USER_STATES.pop(user_id, None)
                return
                
            msg = await api_send(user_id, f"{E_SYNC} <i>Verifying 2FA password...</i>")
            try:
                await temp_client.check_password(message.text)
                ss = await temp_client.export_session_string()
                await users_col.update_one({"_id": user_id}, {"$push": {"sessions": ss}})
                await api_edit(msg.chat.id, msg.id, f"{E_CHK} <i><b>Session Connected Successfully!</b>\nRedirecting to Menu...</i>")
                await temp_client.disconnect(); USER_STATES.pop(user_id, None)
                
                await asyncio.sleep(1.5); config = await settings_col.find_one({"_id": "config"})
                first_name = html.escape(message.from_user.first_name if message.from_user else "User")
                text, btn = await get_home_menu(user_id, first_name, config)
                await api_send(user_id, text, kb=btn)
            except Exception as e_pwd: 
                USER_STATES.pop(user_id, None)
                await api_edit(msg.chat.id, msg.id, f"{E_WRN} <i><b>Error:</b> {e_pwd}</i>")
                try: await temp_client.disconnect()
                except: pass
            
        elif state == "WAITING_LINK":
            msg = await api_send(user_id, f"{E_SYNC} <i>Analyzing channel parameters...</i>")
            user_data = await get_user(user_id); config = await settings_col.find_one({"_id": "config"})
            asyncio.create_task(check_and_show_stats(client, user_id, user_data, config, message.text.strip(), msg, save_new=True))
            
        elif state == "WAITING_DM_LINK":
            msg = await api_send(user_id, f"{E_SYNC} <i>Analyzing channel parameters...</i>")
            user_data = await get_user(user_id); config = await settings_col.find_one({"_id": "config"})
            asyncio.create_task(check_and_show_stats(client, user_id, user_data, config, message.text.strip(), msg, save_new=False))

        elif state == "WAITING_LIMIT":
            if not message.text or not message.text.isdigit(): 
                USER_STATES.pop(user_id, None)
                return await api_send(user_id, f"{E_WRN} <i>Please provide a valid numeric value.</i>")
                
            if int(message.text) <= 0:
                return await api_send(user_id, f"{E_WRN} <i>Please send a number greater than 0.</i>")

            if USER_STATES[user_id].get("jr_mode"):
                if user_id in ACTIVE_TASKS:
                    USER_STATES.pop(user_id, None)
                    return await api_send(user_id, f"{E_WRN} <i>A campaign is already running. Press <b>Stop</b> on it first.</i>")
                st = USER_STATES.pop(user_id)
                n, pend = int(message.text), int(st.get("pending") or 0)
                if pend and n > pend: n = pend
                n, rem = await cap_limit(user_id, n)
                if n <= 0: return await api_send(user_id, f"{E_WRN} <i><b>Trial Limit Reached!</b> Please upgrade to VIP.</i>")
                await launch_campaign(user_id, n, st.get("link"), st.get("raw_link"), st.get("sess_idx", "all"), st.get("is_free_ch", False), client)
                return

            USER_STATES[user_id]["limit"] = int(message.text); USER_STATES[user_id]["state"] = None
            btn = {"inline_keyboard": [[ibtn("All Audience", "flt_all", style="primary", icon=BTN_EMOJIS["user"])], [ibtn("Recently Online", "flt_recent", style="success", icon=BTN_EMOJIS["tick"])], [ibtn("Active Members", "flt_active", style="primary", icon=BTN_EMOJIS["user"])], [ibtn("VIP Premium Only", "flt_premium", style="danger", icon=BTN_EMOJIS["diamond"])]]}
            await api_send(user_id, f"{E_ADM} <i><b>Target Audience Filtering:</b>\nSelect user audience to engage:</i>", kb=btn)
            
    except Exception as e_state:
        USER_STATES.pop(user_id, None)
        await api_send(message.chat.id, f"{E_WRN} <i><b>Encountered Error:</b>\n<code>{html.escape(str(e_state))}</code></i>")

# ================= DYNAMIC HANDLER BINDER =================
bot.add_handler(MessageHandler(start_cmd, filters.command("start") & filters.private))
bot.add_handler(MessageHandler(language_cmd, filters.command(["language", "lang"]) & filters.private))
bot.add_handler(MessageHandler(help_cmd, filters.command("help") & filters.private))
bot.add_handler(MessageHandler(cancel_cmd, filters.command("cancel") & filters.private))
bot.add_handler(MessageHandler(status_cmd, filters.command("status") & filters.private))
bot.add_handler(MessageHandler(shortcut_cmds, filters.command(["buypremium", "massdm", "myaccount"]) & filters.private))
bot.add_handler(MessageHandler(check_total_public, filters.command(["total", "totaldms"]) & filters.private))
bot.add_handler(MessageHandler(admin_panel, filters.command("admin")))
bot.add_handler(MessageHandler(master_admin_cmds, filters.command(["setwebsitelink", "toggleauto", "reqall", "setfampay", "setmanual", "setcrypto", "setfampayqr", "setmanualqr", "setcryptoqr", "setprice1d", "setprice3d", "setprice7d", "setprice1m", "setlogchannel", "setsuccesslog", "setleaderboard", "setfreechannel", "setfreerequest", "setfreetrial", "setfreereq", "setldbtime", "setrefbonus", "setdelay", "ongoing", "sales", "giveprem", "removeprem", "maintenance"])))
bot.add_handler(MessageHandler(shared_admin_cmds, filters.command(["stats", "checkuser", "clearsession", "banuser", "unbanuser", "broadcast"])))
bot.add_handler(MessageHandler(dm_controls, filters.command(["chk", "pause", "resume", "stop"]) & filters.private))
bot.add_handler(MessageHandler(handle_states, filters.private & filters.incoming), group=1)
bot.add_handler(CallbackQueryHandler(cb_handler))
bot.add_handler(CallbackQueryHandler(admin_manual_approve, filters.regex(r"^manapp_") | filters.regex(r"^manrej_")), group=1)
bot.add_handler(ChatJoinRequestHandler(handle_join_requests))

# ================= SYSTEM LAUNCHER =================
async def start_bot():
    print("-----------------------------------")
    await init_db()
    print("-----------------------------------")
    await bot.start()
    print(f"BOT STARTED: {(await bot.get_me()).username}")
    asyncio.create_task(auto_leaderboard_task())
    await idle()
    print("Shutting down...")
    await bot.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())