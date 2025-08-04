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
    format='%(asctime)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Enhanced logging functions for debugging
def log_user_action(user_id, username, action, details=""):
    """Log semua aksi user untuk debugging"""
    logger.info(f"USER_ACTION | User {user_id} (@{username}) | {action} | {details}")

def log_error(error_msg, user_id=None, username=None, exception=None):
    """Log error dengan context user dan exception details"""
    user_info = f"User {user_id} (@{username})" if user_id else "System"
    error_details = f"{error_msg}"
    if exception:
        error_details += f" | Exception: {type(exception).__name__}: {str(exception)}"
    logger.error(f"ERROR | {user_info} | {error_details}")

def log_feature_usage(feature, user_id, username, success=True, details=""):
    """Log penggunaan fitur"""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"FEATURE | {feature} | User {user_id} (@{username}) | {status} | {details}")

def log_chat_session(user_id, partner_id, action, details=""):
    """Log chat session activities"""
    logger.info(f"CHAT_SESSION | User {user_id} | Partner {partner_id} | {action} | {details}")

def log_database_operation(operation, table, user_id=None, details=""):
    """Log database operations"""
    user_info = f" | User {user_id}" if user_id else ""
    logger.debug(f"DB_OP | {operation} | Table: {table}{user_info} | {details}")

def log_message_handling(message_type, user_id, username, success=True, details=""):
    """Log message handling (text, photo, video, etc.)"""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"MESSAGE | {message_type} | User {user_id} (@{username}) | {status} | {details}")

def log_conversation_state(user_id, username, state, details=""):
    """Log conversation state changes"""
    logger.info(f"CONVERSATION | User {user_id} (@{username}) | State: {state} | {details}")

def log_callback_query(user_id, username, callback_data, success=True, details=""):
    """Log callback query handling"""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"CALLBACK | User {user_id} (@{username}) | Data: {callback_data} | {status} | {details}")

def log_quiz_activity(user_id, username, action, details=""):
    """Log quiz-related activities"""
    logger.info(f"QUIZ | User {user_id} (@{username}) | {action} | {details}")

def log_pro_feature(user_id, username, feature, success=True, details=""):
    """Log pro feature usage"""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"PRO_FEATURE | User {user_id} (@{username}) | {feature} | {status} | {details}")

def log_moderation(user_id, username, content_type, action, details=""):
    """Log content moderation activities"""
    logger.info(f"MODERATION | User {user_id} (@{username}) | {content_type} | {action} | {details}")

def log_bot_startup():
    """Log bot startup information"""
    logger.info("=== BOT STARTUP LOG ===")
    logger.info(f"Bot Token Status: {'CONFIGURED' if BOT_TOKEN != 'YOUR_BOT_TOKEN' else 'NOT CONFIGURED'}")
    logger.info(f"Owner ID: {OWNER_ID}")
    logger.info(f"Database Path: {DB_PATH}")
    logger.info(f"NSFW API Status: {'CONFIGURED' if NSFW_API_KEY != 'YOUR_MODERATECONTENT_API_KEY' else 'NOT CONFIGURED'}")
    logger.info(f"Pro Week Price: {PRO_WEEK_PRICE}")
    logger.info(f"Pro Month Price: {PRO_MONTH_PRICE}")
    logger.info(f"Quiz Limit Winners: {QUIZ_LIMIT_WINNERS}")
    logger.info("=== STARTUP LOG COMPLETE ===")

def log_handler_registration(handler_type, handler_name):
    """Log handler registration"""
    logger.info(f"HANDLER_REG | {handler_type} | {handler_name}")

def log_partner_search(user_id, username, search_type, preferences, result):
    """Log partner search attempts"""
    logger.info(f"PARTNER_SEARCH | User {user_id} (@{username}) | Type: {search_type} | Prefs: {preferences} | Result: {result}")

def log_session_management(user_id, partner_id, action, session_type="normal"):
    """Log session management activities"""
    logger.info(f"SESSION_MGMT | User {user_id} | Partner {partner_id} | Action: {action} | Type: {session_type}")

def log_points_transaction(user_id, username, transaction_type, amount, balance_after):
    """Log points transactions"""
    logger.info(f"POINTS_TXN | User {user_id} (@{username}) | Type: {transaction_type} | Amount: {amount} | Balance: {balance_after}")

def log_pro_subscription(user_id, username, subscription_type, duration_days, expires_at):
    """Log pro subscription changes"""
    logger.info(f"PRO_SUB | User {user_id} (@{username}) | Type: {subscription_type} | Duration: {duration_days} days | Expires: {datetime.fromtimestamp(expires_at)}")

def log_group_activity(user_id, username, group_id, action, member_count=None):
    """Log group chat activities"""
    member_info = f" | Members: {member_count}" if member_count else ""
    logger.info(f"GROUP_ACTIVITY | User {user_id} (@{username}) | Group #{group_id} | Action: {action}{member_info}")

def log_poll_creation(user_id, username, poll_id, question, options_count):
    """Log poll creation"""
    logger.info(f"POLL_CREATE | User {user_id} (@{username}) | Poll #{poll_id} | Q: {question} | Options: {options_count}")

def log_feedback_submission(user_id, username, partner_id, rating, comment=""):
    """Log feedback submissions"""
    comment_info = f" | Comment: {comment}" if comment else ""
    logger.info(f"FEEDBACK_SUB | User {user_id} (@{username}) | Partner {partner_id} | Rating: {rating} stars{comment_info}")

def log_report_submission(user_id, username, reported_id, reason):
    """Log report submissions"""
    logger.info(f"REPORT_SUB | User {user_id} (@{username}) | Reported {reported_id} | Reason: {reason}")

def log_block_action(user_id, username, blocked_id, action_type):
    """Log user blocking actions"""
    logger.info(f"BLOCK_ACTION | User {user_id} (@{username}) | Blocked {blocked_id} | Type: {action_type}")

def log_secret_mode(user_id, username, action, enabled=True):
    """Log secret mode activities"""
    status = "ENABLED" if enabled else "DISABLED"
    logger.info(f"SECRET_MODE | User {user_id} (@{username}) | Action: {action} | Status: {status}")

def log_media_processing(user_id, username, media_type, file_id, file_size=None, processing_time=None):
    """Log media processing activities"""
    size_info = f" | Size: {file_size}" if file_size else ""
    time_info = f" | Time: {processing_time}ms" if processing_time else ""
    logger.info(f"MEDIA_PROC | User {user_id} (@{username}) | Type: {media_type} | File: {file_id}{size_info}{time_info}")

def log_api_call(api_name, success=True, response_time=None, error_msg=None):
    """Log external API calls"""
    status = "SUCCESS" if success else "FAILED"
    time_info = f" | Time: {response_time}ms" if response_time else ""
    error_info = f" | Error: {error_msg}" if error_msg else ""
    logger.info(f"API_CALL | {api_name} | {status}{time_info}{error_info}")

def log_performance_metric(metric_name, value, unit=""):
    """Log performance metrics"""
    unit_info = f" {unit}" if unit else ""
    logger.info(f"PERFORMANCE | {metric_name}: {value}{unit_info}")

def log_security_event(event_type, user_id=None, username=None, details=""):
    """Log security-related events"""
    user_info = f" | User {user_id} (@{username})" if user_id else ""
    logger.warning(f"SECURITY | {event_type}{user_info} | {details}")

def log_system_health(component, status, details=""):
    """Log system health information"""
    logger.info(f"HEALTH | {component} | {status} | {details}")

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
    try:
        conn = sqlite3.connect(DB_PATH)
        log_database_operation("CONNECT", "database", details="Connection established")
        return conn
    except Exception as e:
        log_error(f"Database connection failed: {e}", exception=e)
        raise

def init_db():
    try:
        log_database_operation("INIT", "database", details="Starting database initialization")
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
        logger.info("Database initialized successfully")
    except Exception as e:
        log_error(f"Database initialization failed: {e}")
        raise

# ========== Decorator ==========
def check_ban_status(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        username = update.effective_user.username
        try:
            with db() as conn:
                c = conn.cursor()
                c.execute("SELECT is_banned, banned_until FROM user_profiles WHERE user_id=?", (user_id,))
                row = c.fetchone()
                if row and row[0]:
                    banned_until = row[1]
                    if banned_until > int(time.time()):
                        log_user_action(user_id, username, "BANNED_USER_ATTEMPT", f"Banned until {datetime.fromtimestamp(banned_until)}")
                        await update.message.reply_text("🚫 Kamu di-ban hingga " + datetime.fromtimestamp(banned_until).strftime("%Y-%m-%d %H:%M"))
                        return
                    else:
                        c.execute("UPDATE user_profiles SET is_banned=0, banned_until=0 WHERE user_id=?", (user_id,))
                        conn.commit()
                        log_user_action(user_id, username, "BAN_EXPIRED", "Ban automatically removed")
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            log_error(f"Ban check failed: {e}", user_id, username)
            return await func(update, context, *args, **kwargs)
    return wrapper

def owner_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        username = update.effective_user.username
        if user_id != OWNER_ID:
            log_user_action(user_id, username, "UNAUTHORIZED_OWNER_ACCESS", f"Attempted to use owner command")
            await update.message.reply_text("❌ Hanya owner yang bisa menggunakan perintah ini.")
            return
        log_user_action(user_id, username, "OWNER_COMMAND", f"Executing owner command: {func.__name__}")
        return await func(update, context, *args, **kwargs)
    return wrapper

def auto_update_profile(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        try:
            with db() as conn:
                c = conn.cursor()
                c.execute("SELECT user_id FROM user_profiles WHERE user_id=?", (user.id,))
                if not c.fetchone():
                    c.execute("INSERT INTO user_profiles (user_id, username) VALUES (?,?)", (user.id, user.username))
                    log_user_action(user.id, user.username, "NEW_USER_CREATED", "Profile auto-created")
                else:
                    c.execute("UPDATE user_profiles SET username=? WHERE user_id=?", (user.username, user.id))
                    log_user_action(user.id, user.username, "USERNAME_UPDATED", f"Username updated to {user.username}")
                conn.commit()
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            log_error(f"Auto update profile failed: {e}", user.id, user.username)
            return await func(update, context, *args, **kwargs)
    return wrapper

# ========== Helper ==========
def is_pro(user_id):
    try:
        with db() as conn:
            c = conn.cursor()
            c.execute("SELECT pro_expires_at FROM user_profiles WHERE user_id=?", (user_id,))
            row = c.fetchone()
            is_pro_user = bool(row and row[0] and row[0] > int(time.time()))
            logger.debug(f"Pro check for user {user_id}: {is_pro_user}")
            return is_pro_user
    except Exception as e:
        log_error(f"Pro check failed: {e}", user_id)
        return False

def get_profile(user_id):
    try:
        with db() as conn:
            c = conn.cursor()
            c.execute("""SELECT gender, age, bio, photo_id, hobbies, points FROM user_profiles WHERE user_id=?""", (user_id,))
            row = c.fetchone()
            if row:
                data = dict(zip(["gender", "age", "bio", "photo_id", "hobbies", "points"], row))
                data["hobbies"] = data["hobbies"].split(",") if data["hobbies"] else []
                logger.debug(f"Profile retrieved for user {user_id}")
                return data
            logger.debug(f"No profile found for user {user_id}")
            return {}
    except Exception as e:
        log_error(f"Get profile failed: {e}", user_id)
        return {}

def profile_complete(user_id):
    try:
        profile = get_profile(user_id)
        is_complete = all([profile.get("gender"), profile.get("age"), profile.get("bio"), profile.get("photo_id")])
        logger.debug(f"Profile completeness check for user {user_id}: {is_complete}")
        return is_complete
    except Exception as e:
        log_error(f"Profile completeness check failed: {e}", user_id)
        return False

def is_in_chat(user_id):
    try:
        with db() as conn:
            c = conn.cursor()
            c.execute("SELECT partner_id FROM sessions WHERE user_id=?", (user_id,))
            in_chat = c.fetchone() is not None
            logger.debug(f"Chat status check for user {user_id}: {in_chat}")
            return in_chat
    except Exception as e:
        log_error(f"Chat status check failed: {e}", user_id)
        return False

def is_blocked(user_id, target_id):
    try:
        with db() as conn:
            c = conn.cursor()
            c.execute("SELECT 1 FROM block_list WHERE user_id=? AND blocked_id=?", (user_id, target_id))
            is_blocked_user = c.fetchone() is not None
            logger.debug(f"Block check: user {user_id} blocked {target_id}: {is_blocked_user}")
            return is_blocked_user
    except Exception as e:
        log_error(f"Block check failed: {e}", user_id)
        return False

def mask_username(username):
    try:
        if not username:
            masked = "User" + "".join(random.choices("0123456789", k=4))
        elif len(username) <= 4:
            masked = username[0] + "**" + username[-1]
        else:
            masked = username[:2] + "*"*(len(username)-3) + username[-1]
        logger.debug(f"Username masked: {username} -> {masked}")
        return masked
    except Exception as e:
        log_error(f"Username masking failed: {e}")
        return "User****"

def add_session(user_id, partner_id, secret_mode=False):
    try:
        now = int(time.time())
        with db() as conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO sessions (user_id, partner_id, started_at, secret_mode) VALUES (?,?,?,?)", (user_id, partner_id, now, int(secret_mode)))
            c.execute("INSERT OR REPLACE INTO sessions (user_id, partner_id, started_at, secret_mode) VALUES (?,?,?,?)", (partner_id, user_id, now, int(secret_mode)))
            conn.commit()
        
        # Get usernames for logging
        c.execute("SELECT user_id, username FROM user_profiles WHERE user_id IN (?, ?)", (user_id, partner_id))
        usernames = {row[0]: row[1] for row in c.fetchall()}
        user1_username = usernames.get(user_id, "unknown")
        user2_username = usernames.get(partner_id, "unknown")
        
        session_type = "SECRET" if secret_mode else "NORMAL"
        log_session_management(user_id, partner_id, "CREATED", session_type)
        logger.info(f"Session created: {user_id} (@{user1_username}) <-> {partner_id} (@{user2_username}) (secret_mode: {secret_mode})")
    except Exception as e:
        log_error(f"Add session failed: {e}", user_id)

def end_session(user_id):
    try:
        with db() as conn:
            c = conn.cursor()
            c.execute("SELECT partner_id FROM sessions WHERE user_id=?", (user_id,))
            row = c.fetchone()
            if row:
                partner_id = row[0]
                c.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
                c.execute("DELETE FROM sessions WHERE user_id=?", (partner_id,))
                conn.commit()
                
                # Get usernames for logging
                c.execute("SELECT user_id, username FROM user_profiles WHERE user_id IN (?, ?)", (user_id, partner_id))
                usernames = {row[0]: row[1] for row in c.fetchall()}
                user1_username = usernames.get(user_id, "unknown")
                user2_username = usernames.get(partner_id, "unknown")
                
                log_session_management(user_id, partner_id, "ENDED", "NORMAL")
                logger.info(f"Session ended: {user_id} (@{user1_username}) <-> {partner_id} (@{user2_username})")
                return partner_id
        logger.debug(f"No active session found for user {user_id}")
        return None
    except Exception as e:
        log_error(f"End session failed: {e}", user_id)
        return None

def find_partner(user_id, gender_pref=None, hobby_pref=None, age_min=None, age_max=None):
    try:
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
            
            # Get user info for logging
            c.execute("SELECT username FROM user_profiles WHERE user_id=?", (user_id,))
            user_row = c.fetchone()
            username = user_row[0] if user_row else "unknown"
            
            preferences = f"Gender: {gender_pref}, Hobby: {hobby_pref}, Age: {age_min}-{age_max}" if any([gender_pref, hobby_pref, age_min, age_max]) else "Random"
            log_partner_search(user_id, username, "PRO_SEARCH" if any([gender_pref, hobby_pref, age_min, age_max]) else "RANDOM", preferences, f"Found {len(partners)} candidates")
            
            # Prioritas: gender + hobi
            if hobby_pref:
                for pid, hobbies_str in partners:
                    if pid in block_ids: continue
                    hobbies = hobbies_str.split(",") if hobbies_str else []
                    if hobby_pref in hobbies:
                        log_partner_search(user_id, username, "HOBBY_MATCH", f"Hobby: {hobby_pref}", f"Matched with {pid}")
                        return pid
                # Fallback: gender saja
                for pid, hobbies_str in partners:
                    if pid in block_ids: continue
                    log_partner_search(user_id, username, "GENDER_MATCH", f"Gender: {gender_pref}", f"Matched with {pid}")
                    return pid
                log_partner_search(user_id, username, "NO_MATCH", preferences, "No suitable partner found")
                return None
            else:
                for pid, hobbies_str in partners:
                    if pid in block_ids: continue
                    log_partner_search(user_id, username, "RANDOM_MATCH", "Random", f"Matched with {pid}")
                    return pid
                log_partner_search(user_id, username, "NO_MATCH", "Random", "No available partners")
                return None
    except Exception as e:
        log_error(f"Find partner failed: {e}", user_id)
        return None

# ========== Command Handler ==========
@check_ban_status
@auto_update_profile
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "START_COMMAND", "User started bot")
    
    try:
        if not profile_complete(user_id):
            log_feature_usage("PROFILE_INCOMPLETE", user_id, username, False, "Profile not complete")
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Lengkapi Profil", callback_data="complete_profile")],
                [InlineKeyboardButton("Lanjutkan & Cari Acak", callback_data="skip_profile")]
            ])
            await update.message.reply_text(
                "👋 Selamat datang di Anonymous Chat!\nProfilmu belum lengkap.",
                reply_markup=keyboard
            )
            return
        
        log_feature_usage("START_COMMAND", user_id, username, True, "Profile complete")
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
    except Exception as e:
        log_error(f"Start command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

@check_ban_status
@auto_update_profile
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "HELP_COMMAND")
    
    try:
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
        log_feature_usage("HELP_COMMAND", user_id, username, True)
    except Exception as e:
        log_error(f"Help command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

# ========== Profile Conversation ==========
@check_ban_status
@auto_update_profile
async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "PROFILE_COMMAND", "Started profile setup")
    
    try:
        await update.message.reply_text(
            "📝 Gender? (Pilih salah satu)",
            reply_markup=ReplyKeyboardMarkup([GENDERS], one_time_keyboard=True, resize_keyboard=True)
        )
        log_feature_usage("PROFILE_SETUP", user_id, username, True, "Gender selection started")
        return PROFILE_GENDER
    except Exception as e:
        log_error(f"Profile command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END

async def profile_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    gender = update.message.text
    
    try:
        if gender not in GENDERS:
            log_user_action(user_id, username, "PROFILE_GENDER_INVALID", f"Invalid gender: {gender}")
            await update.message.reply_text("Gender tidak valid. Ulangi.")
            return PROFILE_GENDER
        
        context.user_data['gender'] = gender
        log_user_action(user_id, username, "PROFILE_GENDER_SET", f"Gender set to: {gender}")
        log_conversation_state(user_id, username, "PROFILE_AGE", "Moving to age input")
        await update.message.reply_text("Usia kamu?")
        return PROFILE_AGE
    except Exception as e:
        log_error(f"Profile gender step failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END

async def profile_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    try:
        age = int(update.message.text)
        context.user_data['age'] = age
        log_user_action(user_id, username, "PROFILE_AGE_SET", f"Age set to: {age}")
        log_conversation_state(user_id, username, "PROFILE_BIO", "Moving to bio input")
        await update.message.reply_text("Bio singkat kamu?")
        return PROFILE_BIO
    except ValueError:
        log_user_action(user_id, username, "PROFILE_AGE_INVALID", f"Invalid age: {update.message.text}")
        await update.message.reply_text("Usia harus angka. Ulangi.")
        return PROFILE_AGE
    except Exception as e:
        log_error(f"Profile age step failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END

async def profile_bio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    bio = update.message.text
    
    try:
        context.user_data['bio'] = bio
        log_user_action(user_id, username, "PROFILE_BIO_SET", f"Bio length: {len(bio)} chars")
        log_conversation_state(user_id, username, "PROFILE_PHOTO", "Moving to photo input")
        await update.message.reply_text("Kirim foto profil kamu.")
        return PROFILE_PHOTO
    except Exception as e:
        log_error(f"Profile bio step failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END

async def profile_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    try:
        photo = update.message.photo[-1]
        photo_id = photo.file_id
        context.user_data['photo_id'] = photo_id
        log_user_action(user_id, username, "PROFILE_PHOTO_SET", f"Photo ID: {photo_id}")
        log_conversation_state(user_id, username, "PROFILE_LANG", "Moving to language selection")
        await update.message.reply_text("Pilih bahasa botmu.",
            reply_markup=ReplyKeyboardMarkup([LANGS], one_time_keyboard=True, resize_keyboard=True))
        return PROFILE_LANG
    except Exception as e:
        log_error(f"Profile photo step failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END

async def profile_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    lang = update.message.text
    
    try:
        if lang not in LANGS:
            log_user_action(user_id, username, "PROFILE_LANG_INVALID", f"Invalid language: {lang}")
            await update.message.reply_text("Bahasa tidak valid. Ulangi.")
            return PROFILE_LANG
        
        context.user_data['language'] = lang
        log_user_action(user_id, username, "PROFILE_LANG_SET", f"Language set to: {lang}")
        log_conversation_state(user_id, username, "PROFILE_HOBBY", "Moving to hobby selection")
        await update.message.reply_text("Pilih hobi kamu (bisa lebih dari satu, pisahkan dengan koma).\nContoh: Music, Coding",
            reply_markup=ReplyKeyboardMarkup([HOBBIES], one_time_keyboard=True, resize_keyboard=True))
        return PROFILE_HOBBY
    except Exception as e:
        log_error(f"Profile language step failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END

async def profile_hobby(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    try:
        hobbies = update.message.text
        hobby_list = [h.strip() for h in hobbies.split(",") if h.strip() in HOBBIES]
        
        with db() as conn:
            c = conn.cursor()
            c.execute("UPDATE user_profiles SET gender=?, age=?, bio=?, photo_id=?, language=?, hobbies=? WHERE user_id=?",
                      (context.user_data['gender'], context.user_data['age'], context.user_data['bio'], context.user_data['photo_id'], context.user_data['language'], ",".join(hobby_list), user_id))
            conn.commit()
        
        log_user_action(user_id, username, "PROFILE_COMPLETED", f"Hobbies: {hobby_list}")
        log_feature_usage("PROFILE_SETUP", user_id, username, True, "Profile completed successfully")
        await update.message.reply_text("✅ Profil kamu telah diperbarui!", reply_markup=MAIN_MENU)
        return ConversationHandler.END
    except Exception as e:
        log_error(f"Profile hobby step failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END

async def profile_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "PROFILE_CANCELLED")
    
    try:
        await update.message.reply_text("Profil batal diatur.", reply_markup=MAIN_MENU)
        return ConversationHandler.END
    except Exception as e:
        log_error(f"Profile cancel failed: {e}", user_id, username)
        return ConversationHandler.END

# ========== Search Pro Conversation ==========
@check_ban_status
@auto_update_profile
async def search_pro_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "SEARCH_PRO_COMMAND")
    
    try:
        if not is_pro(user_id):
            log_feature_usage("SEARCH_PRO", user_id, username, False, "User not Pro")
            await update.message.reply_text("🚫 Fitur ini hanya untuk Pro. Silakan /upgrade dulu.", reply_markup=MAIN_MENU)
            return
        if not profile_complete(user_id):
            log_feature_usage("SEARCH_PRO", user_id, username, False, "Profile incomplete")
            await update.message.reply_text("Profil belum lengkap. /profile dulu.", reply_markup=MAIN_MENU)
            return
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Gender", callback_data="search_gender"),
             InlineKeyboardButton("Hobi", callback_data="search_hobby"),
             InlineKeyboardButton("Gender & Hobi", callback_data="search_gender_hobby")]
        ])
        await update.message.reply_text("Pilih tipe pencarian partner:", reply_markup=keyboard)
        log_feature_usage("SEARCH_PRO", user_id, username, True, "Search options shown")
        return SEARCH_TYPE
    except Exception as e:
        log_error(f"Search pro command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END

async def search_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username
    search_type = query.data
    
    try:
        await query.answer()
        log_callback_query(user_id, username, search_type, True, "Search type selection")
        
        if search_type == "search_gender":
            log_user_action(user_id, username, "SEARCH_TYPE_SELECTED", "Gender search")
            await query.edit_message_text("Gender partner yang kamu cari?", reply_markup=ReplyKeyboardMarkup([GENDERS], one_time_keyboard=True, resize_keyboard=True))
            context.user_data['search_mode'] = "gender"
            log_conversation_state(user_id, username, "SEARCH_GENDER", "Gender selection started")
            return SEARCH_GENDER
        elif search_type == "search_hobby":
            log_user_action(user_id, username, "SEARCH_TYPE_SELECTED", "Hobby search")
            await query.edit_message_text("Hobi partner yang kamu cari?", reply_markup=ReplyKeyboardMarkup([HOBBIES], one_time_keyboard=True, resize_keyboard=True))
            context.user_data['search_mode'] = "hobby"
            log_conversation_state(user_id, username, "SEARCH_HOBBY", "Hobby selection started")
            return SEARCH_HOBBY
        elif search_type == "search_gender_hobby":
            log_user_action(user_id, username, "SEARCH_TYPE_SELECTED", "Gender & Hobby search")
            await query.edit_message_text("Gender partner yang kamu cari?", reply_markup=ReplyKeyboardMarkup([GENDERS], one_time_keyboard=True, resize_keyboard=True))
            context.user_data['search_mode'] = "gender_hobby"
            log_conversation_state(user_id, username, "SEARCH_GENDER", "Gender selection started for gender+hobby search")
            return SEARCH_GENDER
    except Exception as e:
        log_error(f"Search type callback failed: {e}", user_id, username)
        await query.edit_message_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END

async def search_gender_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    gender_pref = update.message.text
    
    try:
        context.user_data['gender_pref'] = gender_pref
        log_user_action(user_id, username, "SEARCH_GENDER_SET", f"Gender preference: {gender_pref}")
        
        if context.user_data.get('search_mode') == "gender_hobby":
            log_conversation_state(user_id, username, "SEARCH_HOBBY", "Moving to hobby selection for gender+hobby search")
            await update.message.reply_text("Hobi partner yang kamu cari?", reply_markup=ReplyKeyboardMarkup([HOBBIES], one_time_keyboard=True, resize_keyboard=True))
            return SEARCH_HOBBY
        else:
            log_conversation_state(user_id, username, "SEARCH_AGE_MIN", "Moving to age minimum input")
            await update.message.reply_text("Umur minimum partner?")
            return SEARCH_AGE_MIN
    except Exception as e:
        log_error(f"Search gender step failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END

async def search_hobby_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    hobby_pref = update.message.text
    
    try:
        context.user_data['hobby_pref'] = hobby_pref
        log_user_action(user_id, username, "SEARCH_HOBBY_SET", f"Hobby preference: {hobby_pref}")
        
        log_conversation_state(user_id, username, "SEARCH_AGE_MIN", "Moving to age minimum input")
        await update.message.reply_text("Umur minimum partner?")
        return SEARCH_AGE_MIN
    except Exception as e:
        log_error(f"Search hobby step failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END

async def search_age_min_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    try:
        age_min = int(update.message.text)
        context.user_data['age_min'] = age_min
        log_user_action(user_id, username, "SEARCH_AGE_MIN_SET", f"Min age: {age_min}")
        log_conversation_state(user_id, username, "SEARCH_AGE_MAX", "Moving to age maximum input")
        await update.message.reply_text("Umur maksimum partner?")
        return SEARCH_AGE_MAX
    except ValueError:
        log_user_action(user_id, username, "SEARCH_AGE_INVALID", f"Invalid age: {update.message.text}")
        await update.message.reply_text("Umur harus angka.")
        return SEARCH_AGE_MIN
    except Exception as e:
        log_error(f"Search age min step failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END

async def search_age_max_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    try:
        age_max = int(update.message.text)
        context.user_data['age_max'] = age_max
        
        gender_pref = context.user_data.get('gender_pref')
        hobby_pref = context.user_data.get('hobby_pref')
        age_min = context.user_data['age_min']
        
        log_user_action(user_id, username, "SEARCH_AGE_MAX_SET", f"Max age: {age_max}, Min age: {age_min}")
        log_user_action(user_id, username, "SEARCH_PREFERENCES", f"Gender: {gender_pref}, Hobby: {hobby_pref}, Age: {age_min}-{age_max}")
        
        partner_id = find_partner(user_id, gender_pref, hobby_pref, age_min, age_max)
        if partner_id:
            add_session(user_id, partner_id)
            log_feature_usage("SEARCH_PRO", user_id, username, True, f"Partner found: {partner_id}")
            await update.message.reply_text("✅ Partner ditemukan! Mulai ngobrol.", reply_markup=CHAT_MENU)
            await context.bot.send_message(partner_id, "✅ Partner ditemukan! Mulai ngobrol.", reply_markup=CHAT_MENU)
        else:
            log_feature_usage("SEARCH_PRO", user_id, username, False, "No partner found")
            await update.message.reply_text("😔 Partner sesuai kriteria belum ditemukan.", reply_markup=MAIN_MENU)
        return ConversationHandler.END
    except ValueError:
        log_user_action(user_id, username, "SEARCH_AGE_INVALID", f"Invalid age: {update.message.text}")
        await update.message.reply_text("Umur harus angka.")
        return SEARCH_AGE_MAX
    except Exception as e:
        log_error(f"Search age max step failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
        return ConversationHandler.END

# ========== Quiz/Permainan ==========
async def play_quiz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "PLAY_QUIZ_COMMAND")
    
    try:
        # Pilih quiz random
        quiz_id = random.randint(1000, 9999)
        q_data = random.choice(QUIZ_QUESTIONS)
        current_quiz[quiz_id] = {"question": q_data["q"], "answer": q_data["a"].lower(), "winners": []}
        context.user_data['quiz_id'] = quiz_id
        context.bot_data['quiz_id'] = quiz_id
        
        log_feature_usage("QUIZ", user_id, username, True, f"Quiz #{quiz_id} started: {q_data['q']}")
        await update.message.reply_text(f"Quiz #{quiz_id} : {q_data['q']}\nJawab dengan /answer <jawaban>")
    except Exception as e:
        log_error(f"Play quiz command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

async def answer_quiz_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    try:
        if 'quiz_id' not in context.user_data:
            log_user_action(user_id, username, "QUIZ_ANSWER_NO_ACTIVE", "No active quiz")
            await update.message.reply_text("Tidak ada quiz aktif yang kamu ikuti.")
            return
        
        quiz_id = context.user_data['quiz_id']
        answer = ' '.join(update.message.text.split()[1:]).lower()
        quiz = current_quiz.get(quiz_id)
        
        if not quiz:
            log_user_action(user_id, username, "QUIZ_ANSWER_INVALID", f"Quiz #{quiz_id} not active")
            await update.message.reply_text("Quiz tidak aktif.")
            return
        
        if user_id in quiz["winners"]:
            log_user_action(user_id, username, "QUIZ_ANSWER_ALREADY_WON", f"Already won quiz #{quiz_id}")
            await update.message.reply_text("Kamu sudah menang di quiz ini.")
            return
        
        if len(quiz["winners"]) >= QUIZ_LIMIT_WINNERS:
            log_user_action(user_id, username, "QUIZ_ANSWER_LIMIT_REACHED", f"Quiz #{quiz_id} limit reached")
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
            
            log_feature_usage("QUIZ", user_id, username, True, f"Quiz #{quiz_id} correct answer: {answer}")
            await update.message.reply_text("Selamat! Pilih hadiahmu:", reply_markup=keyboard)
            
            # Broadcast pemenang dengan username sensor
            winners_masked = [mask_username(username)]
            await context.bot.send_message(OWNER_ID, f"🎉 Pemenang Quiz #{quiz_id}: {winners_masked}")
        else:
            log_user_action(user_id, username, "QUIZ_ANSWER_WRONG", f"Quiz #{quiz_id} wrong answer: {answer}")
            await update.message.reply_text("Jawaban salah.")
    except Exception as e:
        log_error(f"Answer quiz command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

async def quiz_reward_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username
    quiz_id = int(query.data.split("_")[1])
    
    try:
        await query.answer()
        log_callback_query(user_id, username, query.data, True, f"Quiz reward selection for quiz #{quiz_id}")
        
        if query.data.startswith("quizpro_"):
            expires_at = int(time.time()) + 86400
            with db() as conn:
                c = conn.cursor()
                c.execute("UPDATE user_profiles SET pro_expires_at=? WHERE user_id=?", (expires_at, user_id))
                c.execute("UPDATE quiz_winners SET prize=? WHERE quiz_id=? AND user_id=?", ("pro", quiz_id, user_id))
                conn.commit()
            
            # Enhanced logging
            log_pro_subscription(user_id, username, "QUIZ_REWARD", 1, expires_at)
            log_feature_usage("QUIZ_REWARD", user_id, username, True, f"Quiz #{quiz_id} Pro reward claimed")
            log_pro_feature(user_id, username, "QUIZ_PRO_REWARD", True, f"Pro activated for 1 day from quiz #{quiz_id}")
            await query.edit_message_text("✅ Pro aktif 1 hari!")
        elif query.data.startswith("quizpoin_"):
            with db() as conn:
                c = conn.cursor()
                c.execute("SELECT points FROM user_profiles WHERE user_id=?", (user_id,))
                current_points = c.fetchone()[0]
                c.execute("UPDATE user_profiles SET points=points+1 WHERE user_id=?", (user_id,))
                c.execute("UPDATE quiz_winners SET prize=? WHERE quiz_id=? AND user_id=?", ("poin", quiz_id, user_id))
                conn.commit()
            
            # Enhanced logging
            log_points_transaction(user_id, username, "QUIZ_REWARD", 1, current_points + 1)
            log_feature_usage("QUIZ_REWARD", user_id, username, True, f"Quiz #{quiz_id} Point reward claimed")
            log_quiz_activity(user_id, username, "POINT_EARNED", f"1 point earned from quiz #{quiz_id}")
            await query.edit_message_text("✅ Kamu dapat 1 poin! Bisa ditukar Pro nanti.")
    except Exception as e:
        log_error(f"Quiz reward callback failed: {e}", user_id, username)
        await query.edit_message_text("❌ Terjadi kesalahan. Silakan coba lagi.")

# ========== Poin Tukar Pro ==========
async def redeem_points_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "REDEEM_POINTS_COMMAND")
    
    try:
        with db() as conn:
            c = conn.cursor()
            c.execute("SELECT points FROM user_profiles WHERE user_id=?", (user_id,))
            row = c.fetchone()
            points = row[0] if row else 0
        
        log_feature_usage("REDEEM_POINTS", user_id, username, True, f"Current points: {points}")
        await update.message.reply_text(f"Poinmu: {points}\nTukar 7 poin untuk Pro 7 hari? /tukarpro7")
    except Exception as e:
        log_error(f"Redeem points command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

async def tukarpro7_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "TUKAR_PRO7_COMMAND")
    
    try:
        with db() as conn:
            c = conn.cursor()
            c.execute("SELECT points FROM user_profiles WHERE user_id=?", (user_id,))
            row = c.fetchone()
            points = row[0] if row else 0
            
            if points >= 7:
                expires_at = int(time.time()) + 7*86400
                c.execute("UPDATE user_profiles SET pro_expires_at=?, points=points-7 WHERE user_id=?", (expires_at, user_id))
                conn.commit()
                
                # Enhanced logging
                log_points_transaction(user_id, username, "EXCHANGE_PRO7", -7, points - 7)
                log_pro_subscription(user_id, username, "POINTS_EXCHANGE", 7, expires_at)
                log_feature_usage("TUKAR_PRO7", user_id, username, True, f"Exchanged 7 points for Pro 7 days")
                await update.message.reply_text("✅ Pro aktif 7 hari!")
            else:
                log_feature_usage("TUKAR_PRO7", user_id, username, False, f"Insufficient points: {points}/7")
                await update.message.reply_text("Poinmu belum cukup.")
    except Exception as e:
        log_error(f"Tukar pro7 command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

# ========== Block User ==========
async def report_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "REPORT_COMMAND")
    
    try:
        with db() as conn:
            c = conn.cursor()
            c.execute("SELECT partner_id FROM sessions WHERE user_id=?", (user_id,))
            row = c.fetchone()
            if not row:
                log_user_action(user_id, username, "REPORT_NO_PARTNER", "No active chat partner")
                await update.message.reply_text("Kamu tidak sedang chat siapapun.")
                return
            partner_id = row[0]
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(reason, callback_data=f"report_{reason}") for reason in REPORT_REASONS],
            [InlineKeyboardButton("Block User", callback_data=f"block_{partner_id}")]
        ])
        await update.message.reply_text("Pilih alasan report atau block:", reply_markup=keyboard)
        log_feature_usage("REPORT", user_id, username, True, f"Report options shown for partner {partner_id}")
    except Exception as e:
        log_error(f"Report command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

async def report_reason_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username
    
    try:
        await query.answer()
        log_callback_query(user_id, username, query.data, True, "Report/block action")
        
        if query.data.startswith("report_"):
            reason = query.data.replace("report_", "")
            with db() as conn:
                c = conn.cursor()
                c.execute("SELECT partner_id FROM sessions WHERE user_id=?", (user_id,))
                row = c.fetchone()
                if not row:
                    log_user_action(user_id, username, "REPORT_CALLBACK_NO_PARTNER", "No active chat partner")
                    await query.edit_message_text("Kamu tidak sedang chat siapapun.")
                    return
                reported_id = row[0]
                c.execute("INSERT INTO reports (reporter_id, reported_id, reason, timestamp) VALUES (?,?,?,?)",
                          (user_id, reported_id, reason, int(time.time())))
                conn.commit()
            
            log_report_submission(user_id, username, reported_id, reason)
            log_feature_usage("REPORT", user_id, username, True, f"Reported user {reported_id} for reason: {reason}")
            log_moderation(user_id, username, "USER_REPORT", "REPORTED", f"Reported user {reported_id} for {reason}")
            await query.edit_message_text("✅ Laporan terkirim ke Owner. Terima kasih.")
            await context.bot.send_message(OWNER_ID, f"🚩 Report: {mask_username(username)} melaporkan {mask_username('')} Alasan: {reason}")
        elif query.data.startswith("block_"):
            blocked_id = int(query.data.split("_")[1])
            with db() as conn:
                c = conn.cursor()
                c.execute("INSERT OR IGNORE INTO block_list (user_id, blocked_id) VALUES (?,?)", (user_id, blocked_id))
                conn.commit()
            
            log_block_action(user_id, username, blocked_id, "BLOCKED")
            log_feature_usage("BLOCK", user_id, username, True, f"Blocked user {blocked_id}")
            log_moderation(user_id, username, "USER_BLOCK", "BLOCKED", f"Blocked user {blocked_id}")
            await query.edit_message_text("✅ User diblok. Kamu tidak akan match dengan user ini lagi.")
    except Exception as e:
        log_error(f"Report reason callback failed: {e}", user_id, username)
        await query.edit_message_text("❌ Terjadi kesalahan. Silakan coba lagi.")

# ========== Group Chat ==========
async def join_group_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "JOIN_GROUP_COMMAND")
    
    try:
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
                
                log_group_activity(user_id, username, gid, "JOINED", len(members))
                log_feature_usage("JOIN_GROUP", user_id, username, True, f"Joined existing group #{gid}")
                await update.message.reply_text(f"✅ Bergabung ke grup #{gid}. Mulai ngobrol!", reply_markup=GROUP_MENU)
            else:
                # Buat group baru
                c.execute("INSERT INTO groups (members, started_at) VALUES (?,?)", (str(user_id), int(time.time())))
                gid = c.lastrowid
                conn.commit()
                
                log_group_activity(user_id, username, gid, "CREATED", 1)
                log_feature_usage("JOIN_GROUP", user_id, username, True, f"Created new group #{gid}")
                await update.message.reply_text(f"✅ Grup #{gid} dibuat. Tunggu member lain...", reply_markup=GROUP_MENU)
    except Exception as e:
        log_error(f"Join group command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

async def leave_group_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "LEAVE_GROUP_COMMAND")
    
    try:
        with db() as conn:
            c = conn.cursor()
            c.execute("SELECT group_id, members FROM groups WHERE members LIKE ?", (f"%{user_id}%",))
            row = c.fetchone()
            if row:
                gid, members_str = row
                members = [mid for mid in members_str.split(",") if mid != str(user_id)]
                c.execute("UPDATE groups SET members=? WHERE group_id=?", (",".join(members), gid))
                conn.commit()
                
                log_group_activity(user_id, username, gid, "LEFT", len(members))
                log_feature_usage("LEAVE_GROUP", user_id, username, True, f"Left group #{gid}")
                await update.message.reply_text(f"Kamu keluar dari grup #{gid}.", reply_markup=MAIN_MENU)
            else:
                log_user_action(user_id, username, "LEAVE_GROUP_NOT_IN_GROUP", "Not in any group")
                await update.message.reply_text("Kamu tidak sedang di grup.")
    except Exception as e:
        log_error(f"Leave group command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

# ========== Moderasi Gambar ==========
def is_nsfw(file_url):
    try:
        start_time = time.time()
        # Pakai ModerateContent API
        resp = requests.get(NSFW_API_URL, params={"key": NSFW_API_KEY, "url": file_url})
        response_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
        
        if resp.ok:
            js = resp.json()
            rating = js.get("rating_label")
            is_nsfw_content = rating and rating != "everyone"
            log_api_call("ModerateContent_NSFW", True, response_time, f"Rating: {rating}")
            logger.debug(f"NSFW check for {file_url}: {rating} -> {is_nsfw_content}")
            return is_nsfw_content
        else:
            log_api_call("ModerateContent_NSFW", False, response_time, f"HTTP {resp.status_code}")
            logger.warning(f"NSFW API request failed: {resp.status_code}")
            return False
    except Exception as e:
        log_api_call("ModerateContent_NSFW", False, None, str(e))
        log_error(f"NSFW check failed: {e}")
        return False

# ========== Forward Message (Media, Moderasi, Rahasia) ==========
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    try:
        with db() as conn:
            c = conn.cursor()
            c.execute("SELECT partner_id, secret_mode FROM sessions WHERE user_id=?", (user_id,))
            row = c.fetchone()
            if not row:
                log_user_action(user_id, username, "FORWARD_NO_PARTNER", "No active chat partner")
                await update.message.reply_text("Kamu belum terhubung dengan siapapun. Cari partner dulu.", reply_markup=MAIN_MENU)
                return
            partner_id, secret_mode = row
        
        # Moderasi kata kasar
        if hasattr(update.message, "text") and update.message.text:
            if any(word.lower() in update.message.text.lower() for word in MODERATION_WORDS):
                log_user_action(user_id, username, "MODERATION_BAD_WORDS", f"Bad words detected: {update.message.text}")
                await update.message.reply_text("⚠️ Kata kasar terdeteksi! Jangan diulang.")
                await context.bot.send_message(OWNER_ID, f"⚠️ Kata kasar oleh {mask_username(username)}: {update.message.text}")
                return
        
        # Moderasi gambar
        if update.message.photo:
            start_time = time.time()
            file_id = update.message.photo[-1].file_id
            file_size = update.message.photo[-1].file_size
            file_url = await context.bot.get_file(file_id)
            processing_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            
            log_media_processing(user_id, username, "PHOTO", file_id, file_size, processing_time)
            log_message_handling("PHOTO", user_id, username, True, f"Photo received, file_id: {file_id}")
            
            if is_nsfw(file_url.file_path):
                log_moderation(user_id, username, "IMAGE", "NSFW_DETECTED", f"File: {file_id}")
                await update.message.reply_text("🚫 Gambar tidak aman (NSFW).")
                await context.bot.send_message(OWNER_ID, f"NSFW image by {mask_username(username)}")
                return
            
            await context.bot.send_photo(partner_id, file_id, caption=update.message.caption)
            if secret_mode:
                await context.bot.delete_message(partner_id, update.message.message_id)
            log_user_action(user_id, username, "FORWARD_PHOTO", f"Photo forwarded to {partner_id}")
            
        elif update.message.video:
            start_time = time.time()
            file_id = update.message.video.file_id
            file_size = update.message.video.file_size
            processing_time = int((time.time() - start_time) * 1000)
            
            log_media_processing(user_id, username, "VIDEO", file_id, file_size, processing_time)
            log_message_handling("VIDEO", user_id, username, True, f"Video file_id: {file_id}")
            await context.bot.send_video(partner_id, file_id, caption=update.message.caption)
            if secret_mode:
                await context.bot.delete_message(partner_id, update.message.message_id)
            log_user_action(user_id, username, "FORWARD_VIDEO", f"Video forwarded to {partner_id}")
            
        elif update.message.voice:
            start_time = time.time()
            file_id = update.message.voice.file_id
            file_size = update.message.voice.file_size
            processing_time = int((time.time() - start_time) * 1000)
            
            log_media_processing(user_id, username, "VOICE", file_id, file_size, processing_time)
            log_message_handling("VOICE", user_id, username, True, f"Voice file_id: {file_id}")
            await context.bot.send_voice(partner_id, file_id)
            if secret_mode:
                await context.bot.delete_message(partner_id, update.message.message_id)
            log_user_action(user_id, username, "FORWARD_VOICE", f"Voice forwarded to {partner_id}")
            
        elif update.message.sticker:
            log_message_handling("STICKER", user_id, username, True, f"Sticker file_id: {update.message.sticker.file_id}")
            await context.bot.send_sticker(partner_id, update.message.sticker.file_id)
            log_user_action(user_id, username, "FORWARD_STICKER", f"Sticker forwarded to {partner_id}")
            
        elif update.message.text:
            log_message_handling("TEXT", user_id, username, True, f"Text length: {len(update.message.text)} chars")
            await context.bot.send_message(partner_id, update.message.text)
            if secret_mode:
                await context.bot.delete_message(partner_id, update.message.message_id)
            log_user_action(user_id, username, "FORWARD_TEXT", f"Text forwarded to {partner_id}")
            
    except Exception as e:
        log_error(f"Forward message failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan saat mengirim pesan.")

# ========== Next & Stop ==========
@check_ban_status
@auto_update_profile
async def next_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "NEXT_COMMAND")
    
    try:
        partner_id = end_session(user_id)
        if partner_id:
            log_feature_usage("NEXT", user_id, username, True, f"Ended session with {partner_id}")
            await update.message.reply_text("Partner diakhiri. Mencari partner baru...", reply_markup=MAIN_MENU)
            await context.bot.send_message(partner_id, "Partner mengakhiri chat. Kamu kembali ke menu.", reply_markup=MAIN_MENU)
            await start(update, context)
        else:
            log_user_action(user_id, username, "NEXT_NO_SESSION", "No active session")
            await update.message.reply_text("Kamu tidak sedang dalam chat.")
    except Exception as e:
        log_error(f"Next command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

@check_ban_status
@auto_update_profile
async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "STOP_COMMAND")
    
    try:
        partner_id = end_session(user_id)
        if partner_id:
            log_feature_usage("STOP", user_id, username, True, f"Ended session with {partner_id}")
            await update.message.reply_text("Chat diakhiri.", reply_markup=MAIN_MENU)
            await context.bot.send_message(partner_id, "Partner mengakhiri chat. Kamu kembali ke menu.", reply_markup=MAIN_MENU)
        else:
            log_user_action(user_id, username, "STOP_NO_SESSION", "No active session")
            await update.message.reply_text("Kamu tidak sedang dalam chat.")
    except Exception as e:
        log_error(f"Stop command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

# ========== Feedback ==========
async def feedback_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "FEEDBACK_COMMAND")
    
    try:
        with db() as conn:
            c = conn.cursor()
            c.execute("SELECT partner_id FROM sessions WHERE user_id=?", (user_id,))
            row = c.fetchone()
            if not row:
                log_user_action(user_id, username, "FEEDBACK_NO_PARTNER", "No active chat partner")
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
        log_feature_usage("FEEDBACK", user_id, username, True, f"Feedback options shown for partner {partner_id}")
    except Exception as e:
        log_error(f"Feedback command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

async def feedback_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username
    rating = int(query.data.split("_")[1])
    
    try:
        await query.answer()
        log_callback_query(user_id, username, query.data, True, f"Feedback rating: {rating} stars")
        
        with db() as conn:
            c = conn.cursor()
            c.execute("SELECT partner_id FROM sessions WHERE user_id=?", (user_id,))
            row = c.fetchone()
            partner_id = row[0] if row else None
            c.execute("INSERT INTO feedback (user_id, partner_id, rating, comment, timestamp) VALUES (?,?,?,?,?)",
                      (user_id, partner_id, rating, "", int(time.time())))
            conn.commit()
        
        log_feedback_submission(user_id, username, partner_id, rating)
        log_feature_usage("FEEDBACK", user_id, username, True, f"Rating {rating} stars for partner {partner_id}")
        log_user_action(user_id, username, "FEEDBACK_SUBMITTED", f"Rating: {rating} stars, Partner: {partner_id}")
        await query.edit_message_text("Terima kasih atas feedbackmu!")
    except Exception as e:
        log_error(f"Feedback callback failed: {e}", user_id, username)
        await query.edit_message_text("❌ Terjadi kesalahan. Silakan coba lagi.")

# ========== Poll ==========
async def poll_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "POLL_COMMAND")
    
    try:
        await update.message.reply_text("Kirim pertanyaan polling (opsi pisahkan dengan koma):\nContoh: Apakah kamu suka fitur baru?,Ya,Tidak")
        log_feature_usage("POLL", user_id, username, True, "Poll creation started")
    except Exception as e:
        log_error(f"Poll command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

async def poll_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    try:
        parts = update.message.text.split(",")
        if len(parts) < 2:
            log_user_action(user_id, username, "POLL_INVALID_FORMAT", f"Invalid format: {update.message.text}")
            await update.message.reply_text("Format salah.")
            return
        
        question = parts[0]
        options = parts[1:]
        poll_msg = await update.message.reply_poll(question, options, is_anonymous=True)
        
        with db() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO polls (question, options, responses, created_at) VALUES (?,?,?,?)",
                      (question, ",".join(options), "", int(time.time())))
            poll_id = c.lastrowid
            conn.commit()
        
        log_poll_creation(user_id, username, poll_id, question, len(options))
        log_feature_usage("POLL", user_id, username, True, f"Poll created: {question} with {len(options)} options")
    except Exception as e:
        log_error(f"Poll message failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

# ========== Secret Mode ==========
async def secret_mode_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    log_user_action(user_id, username, "SECRET_MODE_COMMAND")
    
    try:
        with db() as conn:
            c = conn.cursor()
            c.execute("UPDATE sessions SET secret_mode=1 WHERE user_id=?", (user_id,))
            conn.commit()
        
        log_secret_mode(user_id, username, "ACTIVATED", True)
        log_feature_usage("SECRET_MODE", user_id, username, True, "Secret mode activated")
        await update.message.reply_text("Mode rahasia aktif. Pesanmu akan dihapus otomatis setelah dibaca.")
    except Exception as e:
        log_error(f"Secret mode command failed: {e}", user_id, username)
        await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")

# ========== Leaderboard & Broadcast ==========
async def daily_leaderboard_job(context: ContextTypes.DEFAULT_TYPE):
    try:
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
        
        logger.info(f"Daily leaderboard sent - Users: {user_count}, Chats: {chat_count}, Reports: {report_count}")
    except Exception as e:
        log_error(f"Daily leaderboard job failed: {e}")

def broadcast_quiz_winners(context: ContextTypes.DEFAULT_TYPE, quiz_id):
    try:
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
        
        success_count = 0
        for uid in user_ids:
            try:
                context.bot.send_message(uid, msg)
                success_count += 1
            except Exception:
                continue
        
        logger.info(f"Quiz winners broadcast completed - Quiz #{quiz_id}, Winners: {len(winners)}, Success: {success_count}/{len(user_ids)}")
    except Exception as e:
        log_error(f"Broadcast quiz winners failed: {e}")

# ========== Handler Registrasi ==========
def main():
    try:
        log_bot_startup()
        logger.info("Starting bot initialization...")
        init_db()
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("Bot application created successfully")

        # Command
        logger.info("Registering command handlers...")
        application.add_handler(CommandHandler("start", start))
        log_handler_registration("COMMAND", "start")
        application.add_handler(CommandHandler("help", help_cmd))
        log_handler_registration("COMMAND", "help")
        application.add_handler(CommandHandler("profile", profile_cmd))
        log_handler_registration("COMMAND", "profile")
        application.add_handler(CommandHandler("upgrade", help_cmd)) # implementasi payment bisa tambah
        log_handler_registration("COMMAND", "upgrade")
        application.add_handler(CommandHandler("search", start))
        log_handler_registration("COMMAND", "search")
        application.add_handler(CommandHandler("searchpro", search_pro_cmd))
        log_handler_registration("COMMAND", "searchpro")
        application.add_handler(CommandHandler("playquiz", play_quiz_cmd))
        log_handler_registration("COMMAND", "playquiz")
        application.add_handler(CommandHandler("answer", answer_quiz_cmd))
        log_handler_registration("COMMAND", "answer")
        application.add_handler(CommandHandler("tukarpro7", tukarpro7_cmd))
        log_handler_registration("COMMAND", "tukarpro7")
        application.add_handler(CommandHandler("redeem", redeem_points_cmd))
        log_handler_registration("COMMAND", "redeem")
        application.add_handler(CommandHandler("joingroup", join_group_cmd))
        log_handler_registration("COMMAND", "joingroup")
        application.add_handler(CommandHandler("leavegroup", leave_group_cmd))
        log_handler_registration("COMMAND", "leavegroup")
        application.add_handler(CommandHandler("next", next_cmd))
        log_handler_registration("COMMAND", "next")
        application.add_handler(CommandHandler("stop", stop_cmd))
        log_handler_registration("COMMAND", "stop")
        application.add_handler(CommandHandler("report", report_cmd))
        log_handler_registration("COMMAND", "report")
        application.add_handler(CommandHandler("feedback", feedback_cmd))
        log_handler_registration("COMMAND", "feedback")
        application.add_handler(CommandHandler("poll", poll_cmd))
        log_handler_registration("COMMAND", "poll")
        application.add_handler(CommandHandler("secretmode", secret_mode_cmd))
        log_handler_registration("COMMAND", "secretmode")
        logger.info("Command handlers registered successfully")
        
        # Profile Conversation
        logger.info("Registering profile conversation handler...")
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
        log_handler_registration("CONVERSATION", "profile")
        logger.info("Profile conversation handler registered successfully")

        # Search Pro Conversation
        logger.info("Registering search pro conversation handler...")
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
        log_handler_registration("CONVERSATION", "search_pro")
        logger.info("Search pro conversation handler registered successfully")

        # Quiz reward
        logger.info("Registering quiz reward callback handler...")
        application.add_handler(CallbackQueryHandler(quiz_reward_callback, pattern=r"^quiz(pro|poin)_"))
        log_handler_registration("CALLBACK", "quiz_reward")

        # Report & block
        logger.info("Registering report and block callback handlers...")
        application.add_handler(CallbackQueryHandler(report_reason_callback, pattern=r"^(report_|block_)"))
        log_handler_registration("CALLBACK", "report_block")

        # Feedback
        logger.info("Registering feedback callback handler...")
        application.add_handler(CallbackQueryHandler(feedback_callback, pattern=r"^fb_"))
        log_handler_registration("CALLBACK", "feedback")

        # Polling
        logger.info("Registering polling message handlers...")
        application.add_handler(MessageHandler(filters.Regex("^Poll$"), poll_cmd))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, poll_message))
        log_handler_registration("MESSAGE", "poll")

        # Forward message (media, teks, voice dsb)
        logger.info("Registering forward message handler...")
        application.add_handler(MessageHandler(
            filters.ALL & ~filters.COMMAND, forward_message
        ))
        log_handler_registration("MESSAGE", "forward")

        # Group chat
        logger.info("Registering group chat handlers...")
        application.add_handler(MessageHandler(filters.Regex("^Join Group$"), join_group_cmd))
        application.add_handler(MessageHandler(filters.Regex("^Leave Group$"), leave_group_cmd))
        log_handler_registration("MESSAGE", "group_chat")

        # Secret mode
        logger.info("Registering secret mode handler...")
        application.add_handler(MessageHandler(filters.Regex("^Secret Mode$"), secret_mode_cmd))
        log_handler_registration("MESSAGE", "secret_mode")

        # Feedback
        logger.info("Registering feedback button handler...")
        application.add_handler(MessageHandler(filters.Regex("^Feedback$"), feedback_cmd))
        log_handler_registration("MESSAGE", "feedback_button")

        # Next/Stop
        logger.info("Registering next/stop button handlers...")
        application.add_handler(MessageHandler(filters.Regex("^Next$"), next_cmd))
        application.add_handler(MessageHandler(filters.Regex("^Stop$"), stop_cmd))
        log_handler_registration("MESSAGE", "next_stop")

        # Leaderboard daily job
        logger.info("Setting up daily leaderboard job...")
        job_queue = application.job_queue
        job_queue.run_daily(daily_leaderboard_job, time=datetime.now().replace(hour=23, minute=59, second=0))
        logger.info("Daily leaderboard job scheduled successfully")

        logger.info("All handlers registered successfully. Starting bot...")
        log_system_health("Bot", "READY", "All handlers registered and job queue configured")
        logger.info("=== BOT READY TO START POLLING ===")
        application.run_polling()
        
    except Exception as e:
        log_error(f"Bot initialization failed: {e}")
        raise

if __name__ == "__main__":
    try:
        logger.info("=== BOT STARTING ===")
        log_system_health("Startup", "INITIATED", "Bot startup sequence started")
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
        log_system_health("Shutdown", "GRACEFUL", "Bot stopped by user interrupt")
    except Exception as e:
        log_error(f"Bot crashed: {e}")
        log_system_health("Shutdown", "CRASH", f"Bot crashed with error: {e}")
        raise