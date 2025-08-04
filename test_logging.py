#!/usr/bin/env python3
"""
Test script untuk memverifikasi fungsi logging bot
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

# Copy logging functions dari bot.py
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

def log_message_handling(message_type, user_id, username, success=True, details=""):
    """Log message handling (text, photo, video, etc.)"""
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"MESSAGE | {message_type} | User {user_id} (@{username}) | {status} | {details}")

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

def log_media_processing(user_id, username, media_type, file_id, file_size=None, processing_time=None):
    """Log media processing activities"""
    size_info = f" | Size: {file_size} bytes" if file_size else ""
    time_info = f" | Time: {processing_time}ms" if processing_time else ""
    logger.info(f"MEDIA_PROC | User {user_id} (@{username}) | Type: {media_type} | File: {file_id}{size_info}{time_info}")

def log_system_health(component, status, details=""):
    """Log system health status"""
    logger.info(f"HEALTH | {component} | {status} | {details}")

# Test data
user_id = 123456789
username = "testuser"
partner_id = 987654321

print("🧪 Testing Bot Logging Functions...")
print("=" * 50)

# Test 1: User actions
print("1. Testing user actions...")
log_user_action(user_id, username, "START_COMMAND", "User started bot")
log_user_action(user_id, username, "PROFILE_COMMAND", "Started profile setup")
log_user_action(user_id, username, "SEARCH_PRO_COMMAND", "Searching for Pro partner")

# Test 2: Feature usage
print("\n2. Testing feature usage...")
log_feature_usage("PROFILE_SETUP", user_id, username, True, "Profile completed successfully")
log_feature_usage("SEARCH_PRO", user_id, username, False, "User not Pro")
log_feature_usage("QUIZ_PLAY", user_id, username, True, "Quiz completed, earned 50 points")

# Test 3: Message handling
print("\n3. Testing message handling...")
log_message_handling("TEXT", user_id, username, True, "Text message forwarded")
log_message_handling("PHOTO", user_id, username, True, "Photo processed and sent")
log_message_handling("VIDEO", user_id, username, False, "Video too large")

# Test 4: Quiz activities
print("\n4. Testing quiz activities...")
log_quiz_activity(user_id, username, "QUIZ_STARTED", "Quiz ID: Q123")
log_quiz_activity(user_id, username, "QUIZ_ANSWERED", "Correct answer, +10 points")
log_quiz_activity(user_id, username, "QUIZ_COMPLETED", "Total score: 85/100")

# Test 5: Pro features
print("\n5. Testing Pro features...")
log_pro_feature(user_id, username, "PRO_SEARCH", True, "Found 3 Pro partners")
log_pro_feature(user_id, username, "PRO_UPGRADE", False, "Payment failed")

# Test 6: Moderation
print("\n6. Testing moderation...")
log_moderation(user_id, username, "TEXT", "BAD_WORDS_DETECTED", "Kata kasar: anjing")
log_moderation(user_id, username, "IMAGE", "NSFW_DETECTED", "File: PHOTO123")

# Test 7: Media processing
print("\n7. Testing media processing...")
log_media_processing(user_id, username, "PHOTO", "PHOTO123", 1024000, 150)
log_media_processing(user_id, username, "VIDEO", "VIDEO456", 5242880, 800)

# Test 8: System health
print("\n8. Testing system health...")
log_system_health("Database", "CONNECTED", "SQLite connection established")
log_system_health("API", "RESPONDING", "NSFW API response time: 200ms")
log_system_health("Bot", "READY", "All handlers registered successfully")

# Test 9: Error logging
print("\n9. Testing error logging...")
try:
    # Simulate an error
    raise ValueError("Test error for logging")
except Exception as e:
    log_error("Test error occurred", user_id, username, e)

print("\n" + "=" * 50)
print("✅ All logging tests completed!")
print("📝 Check 'test_bot.log' file for detailed logs")
print("🔍 Logs will show timestamps, user actions, and system status")