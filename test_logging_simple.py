#!/usr/bin/env python3
"""
Test script untuk memverifikasi sistem logging bot
"""

import logging
import time
from datetime import datetime

# Setup logging seperti di bot.py
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    handlers=[
        logging.FileHandler('test_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Fungsi logging yang sama seperti di bot.py
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

def test_all_logging_functions():
    """Test semua fungsi logging"""
    print("🧪 Testing semua fungsi logging...")
    print("=" * 50)
    
    # Test data
    user_id = 123456789
    username = "testuser"
    partner_id = 987654321
    
    # 1. Test log_user_action
    print("1. Testing log_user_action...")
    log_user_action(user_id, username, "START_COMMAND", "User started bot")
    log_user_action(user_id, username, "HELP_COMMAND")
    log_user_action(user_id, username, "PROFILE_COMMAND", "Started profile setup")
    
    # 2. Test log_error
    print("2. Testing log_error...")
    try:
        raise ValueError("Test error message")
    except Exception as e:
        log_error("Test error occurred", user_id, username, e)
    
    # 3. Test log_feature_usage
    print("3. Testing log_feature_usage...")
    log_feature_usage("PROFILE_SETUP", user_id, username, True, "Profile completed successfully")
    log_feature_usage("SEARCH_PRO", user_id, username, False, "User not Pro")
    
    # 4. Test log_chat_session
    print("4. Testing log_chat_session...")
    log_chat_session(user_id, partner_id, "SESSION_STARTED", "New chat session")
    log_chat_session(user_id, partner_id, "MESSAGE_SENT", "Text message sent")
    
    # 5. Test log_message_handling
    print("5. Testing log_message_handling...")
    log_message_handling("TEXT", user_id, username, True, "Text length: 50 chars")
    log_message_handling("PHOTO", user_id, username, True, "Photo ID: ABC123")
    log_message_handling("VIDEO", user_id, username, False, "File too large")
    
    # 6. Test log_conversation_state
    print("6. Testing log_conversation_state...")
    log_conversation_state(user_id, username, "PROFILE_GENDER", "Moving to gender input")
    log_conversation_state(user_id, username, "PROFILE_AGE", "Moving to age input")
    
    # 7. Test log_callback_query
    print("7. Testing log_callback_query...")
    log_callback_query(user_id, username, "search_gender", True, "Search type selection")
    log_callback_query(user_id, username, "quizpro_123", True, "Quiz reward claimed")
    
    # 8. Test log_quiz_activity
    print("8. Testing log_quiz_activity...")
    log_quiz_activity(user_id, username, "QUIZ_STARTED", "Quiz #1234 started")
    log_quiz_activity(user_id, username, "QUIZ_CORRECT", "Correct answer: 5 points earned")
    
    # 9. Test log_pro_feature
    print("9. Testing log_pro_feature...")
    log_pro_feature(user_id, username, "SEARCH_PRO", True, "Pro search completed")
    log_pro_feature(user_id, username, "QUIZ_PRO_REWARD", True, "Pro reward claimed")
    
    # 10. Test log_moderation
    print("10. Testing log_moderation...")
    log_moderation(user_id, username, "IMAGE", "NSFW_DETECTED", "File: ABC123")
    log_moderation(user_id, username, "TEXT", "BAD_WORDS", "Kata kasar terdeteksi")
    
    print("=" * 50)
    print("✅ Semua fungsi logging berhasil ditest!")
    print("📁 Log file: test_bot.log")
    print("📊 Cek file log untuk melihat output detail")

def simulate_bot_workflow():
    """Simulasi workflow bot untuk testing logging"""
    print("\n🤖 Simulasi workflow bot...")
    print("=" * 50)
    
    user_id = 123456789
    username = "demo_user"
    partner_id = 987654321
    
    # Simulasi user journey
    log_user_action(user_id, username, "START_COMMAND", "User started bot")
    log_feature_usage("START_COMMAND", user_id, username, True, "Profile complete")
    
    # Profile setup
    log_user_action(user_id, username, "PROFILE_COMMAND", "Started profile setup")
    log_conversation_state(user_id, username, "PROFILE_GENDER", "Gender selection started")
    log_user_action(user_id, username, "PROFILE_GENDER_SET", "Gender set to: Male")
    
    log_conversation_state(user_id, username, "PROFILE_AGE", "Age input started")
    log_user_action(user_id, username, "PROFILE_AGE_SET", "Age set to: 25")
    
    log_user_action(user_id, username, "PROFILE_BIO_SET", "Bio length: 100 chars")
    log_user_action(user_id, username, "PROFILE_PHOTO_SET", "Photo ID: PHOTO123")
    log_user_action(user_id, username, "PROFILE_LANG_SET", "Language set to: Indonesian")
    log_user_action(user_id, username, "PROFILE_COMPLETED", "Hobbies: Music, Gaming")
    log_feature_usage("PROFILE_SETUP", user_id, username, True, "Profile completed successfully")
    
    # Search partner
    log_user_action(user_id, username, "SEARCH_PRO_COMMAND")
    log_feature_usage("SEARCH_PRO", user_id, username, True, "Search options shown")
    log_callback_query(user_id, username, "search_gender", True, "Gender search selected")
    log_user_action(user_id, username, "SEARCH_GENDER_SET", "Gender preference: Female")
    
    # Chat session
    log_chat_session(user_id, partner_id, "SESSION_STARTED", "New chat session")
    log_message_handling("TEXT", user_id, username, True, "Text length: 30 chars")
    log_chat_session(user_id, partner_id, "MESSAGE_SENT", "Text message sent")
    
    # Quiz
    log_user_action(user_id, username, "PLAY_QUIZ_COMMAND")
    log_quiz_activity(user_id, username, "QUIZ_STARTED", "Quiz #5678 started")
    log_quiz_activity(user_id, username, "QUIZ_CORRECT", "Correct answer: 10 points earned")
    log_callback_query(user_id, username, "quizpoin_5678", True, "Points reward claimed")
    
    # Report
    log_user_action(user_id, username, "REPORT_COMMAND")
    log_callback_query(user_id, username, "report_spam", True, "Report submitted")
    log_moderation(user_id, username, "USER_REPORT", "SPAM", "User reported for spam")
    
    print("✅ Workflow simulation completed!")
    print("📁 Check test_bot.log for detailed logs")

if __name__ == "__main__":
    print("🚀 Starting Logging Test...")
    print(f"⏰ Timestamp: {datetime.now()}")
    print()
    
    # Test semua fungsi logging
    test_all_logging_functions()
    
    # Simulasi workflow bot
    simulate_bot_workflow()
    
    print("\n🎉 Logging test completed successfully!")
    print("📋 Next steps:")
    print("1. Check test_bot.log file for detailed logs")
    print("2. Run your actual bot with: python3 bot.py")
    print("3. Monitor bot.log for real bot activity")
    print("4. Use LOGGING_GUIDE.md for debugging tips")