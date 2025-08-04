#!/usr/bin/env python3
"""
Telegram Anonymous Chat Bot
Fitur: Hobi, Pro Search, Media, Leaderboard, Quiz Poin/Pro, Block, Group, Moderasi Gambar, Feedback, Poll, Mode Rahasia, Multi-Language, Broadcast Pemenang Sensor
"""

import logging
import sqlite3
import random
import time
from datetime import datetime, timedelta
import requests

from telegram import (
    Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton,
    KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto, LabeledPrice, Poll
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes, PreCheckoutQueryHandler, JobQueue
)

# ========== Konfigurasi ==========
BOT_TOKEN = "YOUR_BOT_TOKEN"
OWNER_ID = 123456789
DB_PATH = "bot_database.db"
LANGS = ["English", "Indonesian"]
GENDERS = ["Male", "Female", "Other"]
HOBBIES = ["Music", "Sports", "Gaming", "Travel", "Reading", "Cooking", "Drawing", "Coding", "Photography", "Other"]
PRO_WEEK_PRICE = 1000
PRO_MONTH_PRICE = 3500
MODERATION_WORDS = ["anjing", "babi", "kontol", "bangsat", "memek", "ngentot"]
REPORT_REASONS = ["Spam", "SARA", "Pornografi", "Kata Kasar", "Penipuan", "Lainnya"]
QUIZ_LIMIT_WINNERS = 5
NSFW_API_KEY = "YOUR_MODERATECONTENT_API_KEY"
NSFW_API_URL = "https://api.moderatecontent.com/moderate/"

# ========== Logging ==========
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== State ==========
PROFILE_GENDER, PROFILE_AGE, PROFILE_BIO, PROFILE_PHOTO, PROFILE_LANG, PROFILE_HOBBY = range(6)
SEARCH_TYPE, SEARCH_GENDER, SEARCH_HOBBY, SEARCH_AGE_MIN, SEARCH_AGE_MAX = range(6, 11)
QUIZ_ANSWER = 11

# ========== Menu Keyboard ==========
MAIN_MENU = ReplyKeyboardMarkup([
    [KeyboardButton("Find a partner"), KeyboardButton("Search Pro")],
    [KeyboardButton("My Profile"), KeyboardButton("Upgrade to Pro")],
    [KeyboardButton("Play Quiz"), KeyboardButton("Join Group")],
], resize_keyboard=True)

CHAT_MENU = ReplyKeyboardMarkup([
    [KeyboardButton("Next"), KeyboardButton("Stop"), KeyboardButton("Feedback"), KeyboardButton("Poll")],
    [KeyboardButton("Secret Mode")],
], resize_keyboard=True)

GROUP_MENU = ReplyKeyboardMarkup([
    [KeyboardButton("Leave Group"), KeyboardButton("Poll")],
], resize_keyboard=True)

# ========== Quiz Questions ==========
QUIZ_QUESTIONS = [
    {"q": "Apa ibu kota Indonesia?", "a": "Jakarta"},
    {"q": "2 + 5 = ?", "a": "7"},
    {"q": "Siapa pencipta lagu Indonesia Raya?", "a": "WR Supratman"},
]
current_quiz = {}

# ========== Database Layer ==========
def db():
    return sqlite3.connect(DB_PATH)

def init_db():
    with db() as conn:
        c = conn.cursor()
        # Profil user
        c.execute('''CREATE TABLE IF NOT EXISTS user_profiles (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            gender TEXT,
            age INTEGER,
            bio TEXT,
            photo_id TEXT,
            language TEXT,
            pro_expires_at INTEGER,
            is_banned INTEGER DEFAULT 0,
            banned_until INTEGER DEFAULT 0,
            hobbies TEXT,
            points INTEGER DEFAULT 0
        )''')
        # Laporan
        c.execute('''CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter_id INTEGER,
            reported_id INTEGER,
            reason TEXT,
            timestamp INTEGER
        )''')
        # Block list
        c.execute('''CREATE TABLE IF NOT EXISTS block_list (
            user_id INTEGER,
            blocked_id INTEGER,
            PRIMARY KEY(user_id, blocked_id)
        )''')
        # Antrian chat
        c.execute('''CREATE TABLE IF NOT EXISTS chat_queue (
            user_id INTEGER PRIMARY KEY,
            gender_pref TEXT,
            hobby_pref TEXT,
            age_min INTEGER,
            age_max INTEGER,
            is_pro INTEGER DEFAULT 0
        )''')
        # Chat session
        c.execute('''CREATE TABLE IF NOT EXISTS sessions (
            user_id INTEGER PRIMARY KEY,
            partner_id INTEGER,
            started_at INTEGER,
            secret_mode INTEGER DEFAULT 0
        )''')
        # Group chat
        c.execute('''CREATE TABLE IF NOT EXISTS groups (
            group_id INTEGER PRIMARY KEY AUTOINCREMENT,
            members TEXT,
            started_at INTEGER
        )''')
        # Quiz winners
        c.execute('''CREATE TABLE IF NOT EXISTS quiz_winners (
            quiz_id INTEGER,
            user_id INTEGER,
            prize TEXT
        )''')
        # Feedback
        c.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            partner_id INTEGER,
            rating INTEGER,
            comment TEXT,
            timestamp INTEGER
        )''')
        # Polls
        c.execute('''CREATE TABLE IF NOT EXISTS polls (
            poll_id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            options TEXT,
            responses TEXT,
            created_at INTEGER
        )''')
    logger.info("Database initialized.")

# ========== Decorator ==========
def check_ban_status(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        with db() as conn:
            c = conn.cursor()
            c.execute("SELECT is_banned, banned_until FROM user_profiles WHERE user_id=?", (user_id,))
            row = c.fetchone()
            if row and row[0]:
                banned_until = row[1]
                if banned_until > int(time.time()):
                    await update.message.reply_text("🚫 Kamu di-ban hingga " + datetime.fromtimestamp(banned_until).strftime("%Y-%m-%d %H:%M"))
                    return
                else:
                    c.execute("UPDATE user_profiles SET is_banned=0, banned_until=0 WHERE user_id=?", (user_id,))
                    conn.commit()
            return await func(update, context, *args, **kwargs)
    return wrapper

def owner_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_user.id != OWNER_ID:
            await update.message.reply_text("❌ Hanya owner yang bisa menggunakan perintah ini.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def auto_update_profile(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        with db() as conn:
            c = conn.cursor()
            c.execute("SELECT user_id FROM user_profiles WHERE user_id=?", (user.id,))
            if not c.fetchone():
                c.execute("INSERT INTO user_profiles (user_id, username) VALUES (?,?)", (user.id, user.username))
            else:
                c.execute("UPDATE user_profiles SET username=? WHERE user_id=?", (user.username, user.id))
            conn.commit()
        return await func(update, context, *args, **kwargs)
    return wrapper

# ========== Helper ==========
def is_pro(user_id):
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT pro_expires_at FROM user_profiles WHERE user_id=?", (user_id,))
        row = c.fetchone()
        return bool(row and row[0] and row[0] > int(time.time()))

def get_profile(user_id):
    with db() as conn:
        c = conn.cursor()
        c.execute("""SELECT gender, age, bio, photo_id, hobbies, points FROM user_profiles WHERE user_id=?""", (user_id,))
        row = c.fetchone()
        if row:
            data = dict(zip(["gender", "age", "bio", "photo_id", "hobbies", "points"], row))
            data["hobbies"] = data["hobbies"].split(",") if data["hobbies"] else []
            return data
        return {}

def profile_complete(user_id):
    profile = get_profile(user_id)
    return all([profile.get("gender"), profile.get("age"), profile.get("bio"), profile.get("photo_id")])

def is_in_chat(user_id):
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT partner_id FROM sessions WHERE user_id=?", (user_id,))
        return c.fetchone() is not None

def is_blocked(user_id, target_id):
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM block_list WHERE user_id=? AND blocked_id=?", (user_id, target_id))
        return c.fetchone() is not None

def mask_username(username):
    if not username:
        return "User" + "".join(random.choices("0123456789", k=4))
    if len(username) <= 4:
        return username[0] + "**" + username[-1]
    return username[:2] + "*"*(len(username)-3) + username[-1]

def add_session(user_id, partner_id, secret_mode=False):
    now = int(time.time())
    with db() as conn:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO sessions (user_id, partner_id, started_at, secret_mode) VALUES (?,?,?,?)", (user_id, partner_id, now, int(secret_mode)))
        c.execute("INSERT OR REPLACE INTO sessions (user_id, partner_id, started_at, secret_mode) VALUES (?,?,?,?)", (partner_id, user_id, now, int(secret_mode)))
        conn.commit()

def end_session(user_id):
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT partner_id FROM sessions WHERE user_id=?", (user_id,))
        row = c.fetchone()
        if row:
            partner_id = row[0]
            c.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
            c.execute("DELETE FROM sessions WHERE user_id=?", (partner_id,))
            conn.commit()
            return partner_id
    return None

def find_partner(user_id, gender_pref=None, hobby_pref=None, age_min=None, age_max=None):
    # Cari pasangan yang belum terhubung dan tidak diblok
    with db() as conn:
        c = conn.cursor()
        block_ids = [row[0] for row in c.execute("SELECT blocked_id FROM block_list WHERE user_id=?", (user_id,))]
        query = "SELECT u.user_id, u.hobbies FROM user_profiles u LEFT JOIN sessions s ON u.user_id=s.user_id WHERE u.user_id!=? AND s.user_id IS NULL AND u.is_banned=0"
        params = [user_id]
        if gender_pref:
            query += " AND u.gender=?"
            params.append(gender_pref)
        if age_min and age_max:
            query += " AND u.age BETWEEN ? AND ?"
            params += [age_min, age_max]
        c.execute(query, tuple(params))
        partners = c.fetchall()
        # Prioritas: gender + hobi
        if hobby_pref:
            for pid, hobbies_str in partners:
                if pid in block_ids: continue
                hobbies = hobbies_str.split(",") if hobbies_str else []
                if hobby_pref in hobbies:
                    return pid
            # Fallback: gender saja
            for pid, hobbies_str in partners:
                if pid in block_ids: continue
                return pid
            return None
        else:
            for pid, hobbies_str in partners:
                if pid in block_ids: continue
                return pid
            return None

# ========== Command Handler ==========
@check_ban_status
@auto_update_profile
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not profile_complete(user_id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Lengkapi Profil", callback_data="complete_profile")],
            [InlineKeyboardButton("Lanjutkan & Cari Acak", callback_data="skip_profile")]
        ])
        await update.message.reply_text(
            "👋 Selamat datang di Anonymous Chat!\nProfilmu belum lengkap.",
            reply_markup=keyboard
        )
        return
    await update.message.reply_text(
        f"👋 Selamat datang!\n\nPerintah utama:\n"
        "/profile - Atur profilmu\n"
        "/upgrade - Upgrade ke Pro\n"
        "/stop - Akhiri chat\n"
        "/next - Cari partner baru\n"
        "/report - Laporkan partner\n"
        "/playquiz - Main quiz\n"
        "/joingroup - Join group\n"
        "/feedback - Feedback chat\n"
        "/poll - Polling anonim\n"
        "/help - Bantuan\n",
        reply_markup=MAIN_MENU
    )

@check_ban_status
@auto_update_profile
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Bot Anonymous Chat:\n"
        "• 'Find a partner' - Cari partner acak\n"
        "• 'Search Pro' - Cari partner Pro (gender/hobi)\n"
        "• 'My Profile' - Atur profilmu\n"
        "• 'Upgrade to Pro' - Beli langganan Pro\n"
        "• 'Play Quiz' - Main quiz dan dapat Pro/poin\n"
        "• 'Join Group' - Grup anonim\n"
        "• /report - Laporkan partner\n"
        "• /ban, /unban, /grant_pro, /broadcast, /adminstats (Owner)\n"
        "• /stop, /next - Akhiri/Cari chat baru\n"
        "• /feedback - Feedback chat\n"
        "• /poll - Polling chat/group\n"
        "• /secretmode - Aktifkan mode pesan rahasia",
        reply_markup=MAIN_MENU
    )

# ========== Profile Conversation ==========
@check_ban_status
@auto_update_profile
async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 Gender? (Pilih salah satu)",
        reply_markup=ReplyKeyboardMarkup([GENDERS], one_time_keyboard=True, resize_keyboard=True)
    )
    return PROFILE_GENDER

async def profile_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gender = update.message.text
    if gender not in GENDERS:
        await update.message.reply_text("Gender tidak valid. Ulangi.")
        return PROFILE_GENDER
    context.user_data['gender'] = gender
    await update.message.reply_text("Usia kamu?")
    return PROFILE_AGE

async def profile_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age = int(update.message.text)
    except:
        await update.message.reply_text("Usia harus angka. Ulangi.")
        return PROFILE_AGE
    context.user_data['age'] = age
    await update.message.reply_text("Bio singkat kamu?")
    return PROFILE_BIO

async def profile_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bio = update.message.text
    context.user_data['bio'] = bio
    await update.message.reply_text("Kirim foto profil kamu.")
    return PROFILE_PHOTO

async def profile_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    photo_id = photo.file_id
    context.user_data['photo_id'] = photo_id
    await update.message.reply_text("Pilih bahasa botmu.",
        reply_markup=ReplyKeyboardMarkup([LANGS], one_time_keyboard=True, resize_keyboard=True))
    return PROFILE_LANG

async def profile_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.message.text
    if lang not in LANGS:
        await update.message.reply_text("Bahasa tidak valid. Ulangi.")
        return PROFILE_LANG
    context.user_data['language'] = lang
    await update.message.reply_text("Pilih hobi kamu (bisa lebih dari satu, pisahkan dengan koma).\nContoh: Music, Coding",
        reply_markup=ReplyKeyboardMarkup([HOBBIES], one_time_keyboard=True, resize_keyboard=True))
    return PROFILE_HOBBY

async def profile_hobby(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hobbies = update.message.text
    hobby_list = [h.strip() for h in hobbies.split(",") if h.strip() in HOBBIES]
    user_id = update.effective_user.id
    with db() as conn:
        c = conn.cursor()
        c.execute("UPDATE user_profiles SET gender=?, age=?, bio=?, photo_id=?, language=?, hobbies=? WHERE user_id=?",
                  (context.user_data['gender'], context.user_data['age'], context.user_data['bio'], context.user_data['photo_id'], context.user_data['language'], ",".join(hobby_list), user_id))
        conn.commit()
    await update.message.reply_text("✅ Profil kamu telah diperbarui!", reply_markup=MAIN_MENU)
    return ConversationHandler.END

async def profile_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Profil batal diatur.", reply_markup=MAIN_MENU)
    return ConversationHandler.END

# ========== Search Pro Conversation ==========
@check_ban_status
@auto_update_profile
async def search_pro_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_pro(user_id):
        await update.message.reply_text("🚫 Fitur ini hanya untuk Pro. Silakan /upgrade dulu.", reply_markup=MAIN_MENU)
        return
    if not profile_complete(user_id):
        await update.message.reply_text("Profil belum lengkap. /profile dulu.", reply_markup=MAIN_MENU)
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Gender", callback_data="search_gender"),
         InlineKeyboardButton("Hobi", callback_data="search_hobby"),
         InlineKeyboardButton("Gender & Hobi", callback_data="search_gender_hobby")]
    ])
    await update.message.reply_text("Pilih tipe pencarian partner:", reply_markup=keyboard)
    return SEARCH_TYPE

async def search_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "search_gender":
        await query.answer()
        await query.edit_message_text("Gender partner yang kamu cari?", reply_markup=ReplyKeyboardMarkup([GENDERS], one_time_keyboard=True, resize_keyboard=True))
        context.user_data['search_mode'] = "gender"
        return SEARCH_GENDER
    elif query.data == "search_hobby":
        await query.answer()
        await query.edit_message_text("Hobi partner yang kamu cari?", reply_markup=ReplyKeyboardMarkup([HOBBIES], one_time_keyboard=True, resize_keyboard=True))
        context.user_data['search_mode'] = "hobby"
        return SEARCH_HOBBY
    elif query.data == "search_gender_hobby":
        await query.answer()
        await query.edit_message_text("Gender partner yang kamu cari?", reply_markup=ReplyKeyboardMarkup([GENDERS], one_time_keyboard=True, resize_keyboard=True))
        context.user_data['search_mode'] = "gender_hobby"
        return SEARCH_GENDER

async def search_gender_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gender_pref = update.message.text
    context.user_data['gender_pref'] = gender_pref
    if context.user_data.get('search_mode') == "gender_hobby":
        await update.message.reply_text("Hobi partner yang kamu cari?", reply_markup=ReplyKeyboardMarkup([HOBBIES], one_time_keyboard=True, resize_keyboard=True))
        return SEARCH_HOBBY
    else:
        await update.message.reply_text("Umur minimum partner?")
        return SEARCH_AGE_MIN

async def search_hobby_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hobby_pref = update.message.text
    context.user_data['hobby_pref'] = hobby_pref
    if context.user_data.get('search_mode') == "hobby":
        await update.message.reply_text("Umur minimum partner?")
        return SEARCH_AGE_MIN
    else:
        await update.message.reply_text("Umur minimum partner?")
        return SEARCH_AGE_MIN

async def search_age_min_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age_min = int(update.message.text)
    except:
        await update.message.reply_text("Umur harus angka.")
        return SEARCH_AGE_MIN
    context.user_data['age_min'] = age_min
    await update.message.reply_text("Umur maksimum partner?")
    return SEARCH_AGE_MAX

async def search_age_max_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age_max = int(update.message.text)
    except:
        await update.message.reply_text("Umur harus angka.")
        return SEARCH_AGE_MAX
    context.user_data['age_max'] = age_max
    user_id = update.effective_user.id
    gender_pref = context.user_data.get('gender_pref')
    hobby_pref = context.user_data.get('hobby_pref')
    age_min = context.user_data['age_min']
    age_max = context.user_data['age_max']
    partner_id = find_partner(user_id, gender_pref, hobby_pref, age_min, age_max)
    if partner_id:
        add_session(user_id, partner_id)
        await update.message.reply_text("✅ Partner ditemukan! Mulai ngobrol.", reply_markup=CHAT_MENU)
        await context.bot.send_message(partner_id, "✅ Partner ditemukan! Mulai ngobrol.", reply_markup=CHAT_MENU)
    else:
        await update.message.reply_text("😔 Partner sesuai kriteria belum ditemukan.", reply_markup=MAIN_MENU)
    return ConversationHandler.END

# ========== Quiz/Permainan ==========
async def play_quiz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Pilih quiz random
    quiz_id = random.randint(1000, 9999)
    q_data = random.choice(QUIZ_QUESTIONS)
    current_quiz[quiz_id] = {"question": q_data["q"], "answer": q_data["a"].lower(), "winners": []}
    context.user_data['quiz_id'] = quiz_id
    await update.message.reply_text(f"Quiz #{quiz_id} : {q_data['q']}\nJawab dengan /answer <jawaban>")
    context.bot_data['quiz_id'] = quiz_id

async def answer_quiz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if 'quiz_id' not in context.user_data:
        await update.message.reply_text("Tidak ada quiz aktif yang kamu ikuti.")
        return
    quiz_id = context.user_data['quiz_id']
    answer = ' '.join(update.message.text.split()[1:]).lower()
    quiz = current_quiz.get(quiz_id)
    if not quiz:
        await update.message.reply_text("Quiz tidak aktif.")
        return
    if user_id in quiz["winners"]:
        await update.message.reply_text("Kamu sudah menang di quiz ini.")
        return
    if len(quiz["winners"]) >= QUIZ_LIMIT_WINNERS:
        await update.message.reply_text("Limit pemenang sudah habis.")
        return
    if answer == quiz["answer"]:
        quiz["winners"].append(user_id)
        with db() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO quiz_winners (quiz_id, user_id, prize) VALUES (?,?,?)", (quiz_id, user_id, "pending"))
            conn.commit()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Tukar Pro 1 hari", callback_data=f"quizpro_{quiz_id}"),
             InlineKeyboardButton("Ambil 1 poin", callback_data=f"quizpoin_{quiz_id}")]
        ])
        await update.message.reply_text("Selamat! Pilih hadiahmu:", reply_markup=keyboard)
        # Broadcast pemenang dengan username sensor
        winners_masked = [mask_username(update.effective_user.username)]
        await context.bot.send_message(OWNER_ID, f"🎉 Pemenang Quiz #{quiz_id}: {winners_masked}")
    else:
        await update.message.reply_text("Jawaban salah.")

async def quiz_reward_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    quiz_id = int(query.data.split("_")[1])
    if query.data.startswith("quizpro_"):
        expires_at = int(time.time()) + 86400
        with db() as conn:
            c = conn.cursor()
            c.execute("UPDATE user_profiles SET pro_expires_at=? WHERE user_id=?", (expires_at, user_id))
            c.execute("UPDATE quiz_winners SET prize=? WHERE quiz_id=? AND user_id=?", ("pro", quiz_id, user_id))
            conn.commit()
        await query.answer()
        await query.edit_message_text("✅ Pro aktif 1 hari!")
    elif query.data.startswith("quizpoin_"):
        with db() as conn:
            c = conn.cursor()
            c.execute("UPDATE user_profiles SET points=points+1 WHERE user_id=?", (user_id,))
            c.execute("UPDATE quiz_winners SET prize=? WHERE quiz_id=? AND user_id=?", ("poin", quiz_id, user_id))
            conn.commit()
        await query.answer()
        await query.edit_message_text("✅ Kamu dapat 1 poin! Bisa ditukar Pro nanti.")

# ========== Poin Tukar Pro ==========
async def redeem_points_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT points FROM user_profiles WHERE user_id=?", (user_id,))
        row = c.fetchone()
        points = row[0] if row else 0
    await update.message.reply_text(f"Poinmu: {points}\nTukar 7 poin untuk Pro 7 hari? /tukarpro7")

async def tukarpro7_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT points FROM user_profiles WHERE user_id=?", (user_id,))
        row = c.fetchone()
        points = row[0] if row else 0
        if points >= 7:
            expires_at = int(time.time()) + 7*86400
            c.execute("UPDATE user_profiles SET pro_expires_at=?, points=points-7 WHERE user_id=?", (expires_at, user_id))
            conn.commit()
            await update.message.reply_text("✅ Pro aktif 7 hari!")
        else:
            await update.message.reply_text("Poinmu belum cukup.")

# ========== Block User ==========
async def report_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT partner_id FROM sessions WHERE user_id=?", (user_id,))
        row = c.fetchone()
        if not row:
            await update.message.reply_text("Kamu tidak sedang chat siapapun.")
            return
        partner_id = row[0]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(reason, callback_data=f"report_{reason}") for reason in REPORT_REASONS],
        [InlineKeyboardButton("Block User", callback_data=f"block_{partner_id}")]
    ])
    await update.message.reply_text("Pilih alasan report atau block:", reply_markup=keyboard)

async def report_reason_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if query.data.startswith("report_"):
        reason = query.data.replace("report_", "")
        with db() as conn:
            c = conn.cursor()
            c.execute("SELECT partner_id FROM sessions WHERE user_id=?", (user_id,))
            row = c.fetchone()
            if not row:
                await query.answer()
                await query.edit_message_text("Kamu tidak sedang chat siapapun.")
                return
            reported_id = row[0]
            c.execute("INSERT INTO reports (reporter_id, reported_id, reason, timestamp) VALUES (?,?,?,?)",
                      (user_id, reported_id, reason, int(time.time())))
            conn.commit()
        await query.answer()
        await query.edit_message_text("✅ Laporan terkirim ke Owner. Terima kasih.")
        await context.bot.send_message(OWNER_ID, f"🚩 Report: {mask_username(query.from_user.username)} melaporkan {mask_username('')} Alasan: {reason}")
    elif query.data.startswith("block_"):
        blocked_id = int(query.data.split("_")[1])
        with db() as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO block_list (user_id, blocked_id) VALUES (?,?)", (user_id, blocked_id))
            conn.commit()
        await query.answer()
        await query.edit_message_text("✅ User diblok. Kamu tidak akan match dengan user ini lagi.")

# ========== Group Chat ==========
async def join_group_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with db() as conn:
        c = conn.cursor()
        # Cari group belum penuh
        c.execute("SELECT group_id, members FROM groups WHERE LENGTH(members) < 30")
        row = c.fetchone()
        if row:
            gid, members_str = row
            members = members_str.split(",") if members_str else []
            if str(user_id) not in members:
                members.append(str(user_id))
            c.execute("UPDATE groups SET members=? WHERE group_id=?", (",".join(members), gid))
            conn.commit()
            await update.message.reply_text(f"✅ Bergabung ke grup #{gid}. Mulai ngobrol!", reply_markup=GROUP_MENU)
        else:
            # Buat group baru
            c.execute("INSERT INTO groups (members, started_at) VALUES (?,?)", (str(user_id), int(time.time())))
            gid = c.lastrowid
            conn.commit()
            await update.message.reply_text(f"✅ Grup #{gid} dibuat. Tunggu member lain...", reply_markup=GROUP_MENU)

async def leave_group_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT group_id, members FROM groups WHERE members LIKE ?", (f"%{user_id}%",))
        row = c.fetchone()
        if row:
            gid, members_str = row
            members = [mid for mid in members_str.split(",") if mid != str(user_id)]
            c.execute("UPDATE groups SET members=? WHERE group_id=?", (",".join(members), gid))
            conn.commit()
            await update.message.reply_text(f"Kamu keluar dari grup #{gid}.", reply_markup=MAIN_MENU)
        else:
            await update.message.reply_text("Kamu tidak sedang di grup.")

# ========== Moderasi Gambar ==========
def is_nsfw(file_url):
    # Pakai ModerateContent API
    resp = requests.get(NSFW_API_URL, params={"key": NSFW_API_KEY, "url": file_url})
    if resp.ok:
        js = resp.json()
        rating = js.get("rating_label")
        return rating and rating != "everyone"
    return False

# ========== Forward Message (Media, Moderasi, Rahasia) ==========
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT partner_id, secret_mode FROM sessions WHERE user_id=?", (user_id,))
        row = c.fetchone()
        if not row:
            await update.message.reply_text("Kamu belum terhubung dengan siapapun. Cari partner dulu.", reply_markup=MAIN_MENU)
            return
        partner_id, secret_mode = row
    # Moderasi kata kasar
    if hasattr(update.message, "text") and update.message.text:
        if any(word.lower() in update.message.text.lower() for word in MODERATION_WORDS):
            await update.message.reply_text("⚠️ Kata kasar terdeteksi! Jangan diulang.")
            await context.bot.send_message(OWNER_ID, f"⚠️ Kata kasar oleh {mask_username(update.effective_user.username)}: {update.message.text}")
            return
    # Moderasi gambar
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_url = await context.bot.get_file(file_id)
        if is_nsfw(file_url.file_path):
            await update.message.reply_text("🚫 Gambar tidak aman (NSFW).")
            await context.bot.send_message(OWNER_ID, f"NSFW image by {mask_username(update.effective_user.username)}")
            return
        await context.bot.send_photo(partner_id, file_id, caption=update.message.caption)
        if secret_mode:
            await context.bot.delete_message(partner_id, update.message.message_id)
    elif update.message.video:
        await context.bot.send_video(partner_id, update.message.video.file_id, caption=update.message.caption)
        if secret_mode:
            await context.bot.delete_message(partner_id, update.message.message_id)
    elif update.message.voice:
        await context.bot.send_voice(partner_id, update.message.voice.file_id)
        if secret_mode:
            await context.bot.delete_message(partner_id, update.message.message_id)
    elif update.message.sticker:
        await context.bot.send_sticker(partner_id, update.message.sticker.file_id)
    elif update.message.text:
        await context.bot.send_message(partner_id, update.message.text)
        if secret_mode:
            await context.bot.delete_message(partner_id, update.message.message_id)

# ========== Next & Stop ==========
@check_ban_status
@auto_update_profile
async def next_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = end_session(user_id)
    if partner_id:
        await update.message.reply_text("Partner diakhiri. Mencari partner baru...", reply_markup=MAIN_MENU)
        await context.bot.send_message(partner_id, "Partner mengakhiri chat. Kamu kembali ke menu.", reply_markup=MAIN_MENU)
        await start(update, context)
    else:
        await update.message.reply_text("Kamu tidak sedang dalam chat.")

@check_ban_status
@auto_update_profile
async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = end_session(user_id)
    if partner_id:
        await update.message.reply_text("Chat diakhiri.", reply_markup=MAIN_MENU)
        await context.bot.send_message(partner_id, "Partner mengakhiri chat. Kamu kembali ke menu.", reply_markup=MAIN_MENU)
    else:
        await update.message.reply_text("Kamu tidak sedang dalam chat.")

# ========== Feedback ==========
async def feedback_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT partner_id FROM sessions WHERE user_id=?", (user_id,))
        row = c.fetchone()
        if not row:
            await update.message.reply_text("Kamu tidak sedang chat siapapun.")
            return
        partner_id = row[0]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⭐️⭐️⭐️⭐️⭐️", callback_data=f"fb_5"),
         InlineKeyboardButton("⭐️⭐️⭐️⭐️", callback_data=f"fb_4"),
         InlineKeyboardButton("⭐️⭐️⭐️", callback_data=f"fb_3"),
         InlineKeyboardButton("⭐️⭐️", callback_data=f"fb_2"),
         InlineKeyboardButton("⭐️", callback_data=f"fb_1")]
    ])
    await update.message.reply_text("Beri rating untuk partnermu!", reply_markup=keyboard)

async def feedback_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    rating = int(query.data.split("_")[1])
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT partner_id FROM sessions WHERE user_id=?", (user_id,))
        row = c.fetchone()
        partner_id = row[0] if row else None
        c.execute("INSERT INTO feedback (user_id, partner_id, rating, comment, timestamp) VALUES (?,?,?,?,?)",
                  (user_id, partner_id, rating, "", int(time.time())))
        conn.commit()
    await query.answer()
    await query.edit_message_text("Terima kasih atas feedbackmu!")

# ========== Poll ==========
async def poll_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Kirim pertanyaan polling (opsi pisahkan dengan koma):\nContoh: Apakah kamu suka fitur baru?,Ya,Tidak")

async def poll_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.split(",")
    if len(parts) < 2:
        await update.message.reply_text("Format salah.")
        return
    question = parts[0]
    options = parts[1:]
    poll_msg = await update.message.reply_poll(question, options, is_anonymous=True)
    with db() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO polls (question, options, responses, created_at) VALUES (?,?,?,?)",
                  (question, ",".join(options), "", int(time.time())))
        conn.commit()

# ========== Secret Mode ==========
async def secret_mode_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    with db() as conn:
        c = conn.cursor()
        c.execute("UPDATE sessions SET secret_mode=1 WHERE user_id=?", (user_id,))
        conn.commit()
    await update.message.reply_text("Mode rahasia aktif. Pesanmu akan dihapus otomatis setelah dibaca.")

# ========== Leaderboard & Broadcast ==========
async def daily_leaderboard_job(context: ContextTypes.DEFAULT_TYPE):
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM user_profiles")
        user_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM sessions")
        chat_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM reports WHERE timestamp > ?", (int(time.time())-86400,))
        report_count = c.fetchone()[0]
        c.execute("SELECT user_id, points FROM user_profiles ORDER BY points DESC LIMIT 5")
        top_users = c.fetchall()
    leaderboard = "\n".join([f"{i+1}. {mask_username('')} - {p} poin" for i, (uid, p) in enumerate(top_users)])
    await context.bot.send_message(OWNER_ID,
        f"📊 Leaderboard Harian\nUser: {user_count}\nChat: {chat_count}\nReport 24h: {report_count}\nTop Poin:\n{leaderboard}")

def broadcast_quiz_winners(context: ContextTypes.DEFAULT_TYPE, quiz_id):
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT user_id, prize FROM quiz_winners WHERE quiz_id=?", (quiz_id,))
        winners = c.fetchall()
    winners_masked = [f"{mask_username('')} - {prize}" for uid, prize in winners]
    msg = f"🎉 Pemenang Quiz #{quiz_id} Hari Ini:\n" + "\n".join(winners_masked)
    # Broadcast ke semua user
    with db() as conn:
        c = conn.cursor()
        c.execute("SELECT user_id FROM user_profiles")
        user_ids = [row[0] for row in c.fetchall()]
    for uid in user_ids:
        try:
            context.bot.send_message(uid, msg)
        except Exception:
            continue

# ========== Handler Registrasi ==========
def main():
    init_db()
    application = Application.builder().token(BOT_TOKEN).build()

    # Command
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("profile", profile_cmd))
    application.add_handler(CommandHandler("upgrade", help_cmd)) # implementasi payment bisa tambah
    application.add_handler(CommandHandler("search", start))
    application.add_handler(CommandHandler("searchpro", search_pro_cmd))
    application.add_handler(CommandHandler("playquiz", play_quiz_cmd))
    application.add_handler(CommandHandler("answer", answer_quiz_cmd))
    application.add_handler(CommandHandler("tukarpro7", tukarpro7_cmd))
    application.add_handler(CommandHandler("redeem", redeem_points_cmd))
    application.add_handler(CommandHandler("joingroup", join_group_cmd))
    application.add_handler(CommandHandler("leavegroup", leave_group_cmd))
    application.add_handler(CommandHandler("next", next_cmd))
    application.add_handler(CommandHandler("stop", stop_cmd))
    application.add_handler(CommandHandler("report", report_cmd))
    application.add_handler(CommandHandler("feedback", feedback_cmd))
    application.add_handler(CommandHandler("poll", poll_cmd))
    application.add_handler(CommandHandler("secretmode", secret_mode_cmd))
    
    # Profile Conversation
    profile_conv = ConversationHandler(
        entry_points=[CommandHandler("profile", profile_cmd)],
        states={
            PROFILE_GENDER: [MessageHandler(filters.TEXT, profile_gender)],
            PROFILE_AGE: [MessageHandler(filters.TEXT, profile_age)],
            PROFILE_BIO: [MessageHandler(filters.TEXT, profile_bio)],
            PROFILE_PHOTO: [MessageHandler(filters.PHOTO, profile_photo)],
            PROFILE_LANG: [MessageHandler(filters.TEXT, profile_lang)],
            PROFILE_HOBBY: [MessageHandler(filters.TEXT, profile_hobby)],
        },
        fallbacks=[CommandHandler("cancel", profile_cancel)]
    )
    application.add_handler(profile_conv)

    # Search Pro Conversation
    search_conv = ConversationHandler(
        entry_points=[CommandHandler("searchpro", search_pro_cmd)],
        states={
            SEARCH_TYPE: [CallbackQueryHandler(search_type_callback)],
            SEARCH_GENDER: [MessageHandler(filters.TEXT, search_gender_step)],
            SEARCH_HOBBY: [MessageHandler(filters.TEXT, search_hobby_step)],
            SEARCH_AGE_MIN: [MessageHandler(filters.TEXT, search_age_min_step)],
            SEARCH_AGE_MAX: [MessageHandler(filters.TEXT, search_age_max_step)],
        },
        fallbacks=[]
    )
    application.add_handler(search_conv)

    # Quiz reward
    application.add_handler(CallbackQueryHandler(quiz_reward_callback, pattern=r"^quiz(pro|poin)_"))

    # Report & block
    application.add_handler(CallbackQueryHandler(report_reason_callback, pattern=r"^(report_|block_)"))

    # Feedback
    application.add_handler(CallbackQueryHandler(feedback_callback, pattern=r"^fb_"))

    # Polling
    application.add_handler(MessageHandler(filters.Regex("^Poll$"), poll_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, poll_message))

    # Forward message (media, teks, voice dsb)
    application.add_handler(MessageHandler(
        filters.ALL & ~filters.COMMAND, forward_message
    ))

    # Group chat
    application.add_handler(MessageHandler(filters.Regex("^Join Group$"), join_group_cmd))
    application.add_handler(MessageHandler(filters.Regex("^Leave Group$"), leave_group_cmd))

    # Secret mode
    application.add_handler(MessageHandler(filters.Regex("^Secret Mode$"), secret_mode_cmd))

    # Feedback
    application.add_handler(MessageHandler(filters.Regex("^Feedback$"), feedback_cmd))

    # Next/Stop
    application.add_handler(MessageHandler(filters.Regex("^Next$"), next_cmd))
    application.add_handler(MessageHandler(filters.Regex("^Stop$"), stop_cmd))

    # Leaderboard daily job
    job_queue = application.job_queue
    job_queue.run_daily(daily_leaderboard_job, time=datetime.now().replace(hour=23, minute=59, second=0))

    logger.info("Bot started.")
    application.run_polling()

if __name__ == "__main__":
    main()