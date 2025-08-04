# 🐛 Debug Guide - Telegram Anonymous Chat Bot

## ✅ **Logging System Sudah Lengkap!**

Bot Anda sudah memiliki sistem logging yang sangat komprehensif. Berikut adalah panduan lengkap untuk debugging:

## 📊 **Jenis Log yang Tersedia:**

### 1. **User Actions** (`USER_ACTION`)
```
USER_ACTION | User 123456789 (@username) | START_COMMAND | User started bot
USER_ACTION | User 123456789 (@username) | PROFILE_GENDER_SET | Gender set to: Male
USER_ACTION | User 123456789 (@username) | SEARCH_PREFERENCES | Gender: Female, Hobby: Music, Age: 18-25
```

### 2. **Feature Usage** (`FEATURE`)
```
FEATURE | START_COMMAND | User 123456789 (@username) | SUCCESS | Profile complete
FEATURE | SEARCH_PRO | User 123456789 (@username) | FAILED | User not Pro
FEATURE | QUIZ | User 123456789 (@username) | SUCCESS | Quiz #1234 correct answer: Jakarta
```

### 3. **Errors** (`ERROR`)
```
ERROR | User 123456789 (@username) | Database connection failed: database is locked
ERROR | System | Bot initialization failed: Invalid token
```

### 4. **System Info** (`INFO`)
```
INFO | Database initialized successfully
INFO | All handlers registered successfully. Starting bot...
INFO | Daily leaderboard sent - Users: 150, Chats: 45, Reports: 3
```

## 🔍 **Cara Debugging Saat Testing:**

### **Step 1: Jalankan Bot**
```bash
python3 bot.py
```

### **Step 2: Monitor Logs Real-time**
Semua log akan muncul di console. Contoh output:
```
2024-08-04 13:54:00,123 - INFO - === BOT STARTING ===
2024-08-04 13:54:00,124 - INFO - Bot Token: NOT SET
2024-08-04 13:54:00,125 - INFO - Owner ID: 123456789
2024-08-04 13:54:00,126 - INFO - Database Path: bot_database.db
2024-08-04 13:54:00,127 - INFO - NSFW API Key: NOT SET
2024-08-04 13:54:00,128 - INFO - Starting bot initialization...
2024-08-04 13:54:00,129 - INFO - Database initialized successfully
2024-08-04 13:54:00,130 - INFO - Bot application created successfully
2024-08-04 13:54:00,131 - INFO - Registering command handlers...
2024-08-04 13:54:00,132 - INFO - Command handlers registered successfully
2024-08-04 13:54:00,133 - INFO - All handlers registered successfully. Starting bot...
```

### **Step 3: Test Fitur dan Monitor Logs**

#### **Contoh User Registration:**
```
USER_ACTION | User 123456789 (@newuser) | NEW_USER_CREATED | Profile auto-created
USER_ACTION | User 123456789 (@newuser) | PROFILE_COMMAND | Started profile setup
FEATURE | PROFILE_SETUP | User 123456789 (@newuser) | SUCCESS | Gender selection started
USER_ACTION | User 123456789 (@newuser) | PROFILE_GENDER_SET | Gender set to: Male
USER_ACTION | User 123456789 (@newuser) | PROFILE_AGE_SET | Age set to: 25
USER_ACTION | User 123456789 (@newuser) | PROFILE_BIO_SET | Bio length: 50 chars
USER_ACTION | User 123456789 (@newuser) | PROFILE_PHOTO_SET | Photo ID: AgACAgEAAxkBAAIB...
USER_ACTION | User 123456789 (@newuser) | PROFILE_COMPLETED | Hobbies: ['Music', 'Coding']
FEATURE | PROFILE_SETUP | User 123456789 (@newuser) | SUCCESS | Profile completed successfully
```

#### **Contoh Chat Session:**
```
USER_ACTION | User 123456789 (@user1) | SEARCH_PRO_COMMAND
FEATURE | SEARCH_PRO | User 123456789 (@user1) | SUCCESS | Search options shown
USER_ACTION | User 123456789 (@user1) | SEARCH_TYPE_SELECTED | Gender search
USER_ACTION | User 123456789 (@user1) | SEARCH_GENDER_SET | Gender preference: Female
INFO | Found 5 potential partners for user 123456789
INFO | Partner found with gender match: 123456789 -> 987654321 (gender: Female)
FEATURE | SEARCH_PRO | User 123456789 (@user1) | SUCCESS | Partner found: 987654321
INFO | Session created: 123456789 <-> 987654321 (secret_mode: False)
USER_ACTION | User 123456789 (@user1) | FORWARD_TEXT | Text forwarded to 987654321
```

#### **Contoh Error Handling:**
```
USER_ACTION | User 123456789 (@user1) | PROFILE_AGE_INVALID | Invalid age: abc
ERROR | User 123456789 (@user1) | Database connection failed: database is locked
FEATURE | SEARCH_PRO | User 123456789 (@user1) | FAILED | User not Pro
USER_ACTION | User 123456789 (@user1) | MODERATION_BAD_WORDS | Bad words detected: kata kasar
```

## 🚨 **Troubleshooting Common Issues:**

### **1. Bot Tidak Merespon**
**Cek Log:**
```
ERROR | System | Bot initialization failed: Invalid token
ERROR | System | Bot crashed: Connection timeout
```

**Solusi:**
- Pastikan `BOT_TOKEN` sudah diset dengan benar
- Cek koneksi internet
- Restart bot

### **2. Database Error**
**Cek Log:**
```
ERROR | User 123456789 (@username) | Database connection failed: database is locked
ERROR | System | Database initialization failed: permission denied
```

**Solusi:**
- Cek permission file database
- Restart bot untuk reset connection
- Hapus file database jika corrupt

### **3. Fitur Tidak Berfungsi**
**Cek Log:**
```
FEATURE | SEARCH_PRO | User 123456789 (@username) | FAILED | User not Pro
FEATURE | PROFILE_SETUP | User 123456789 (@username) | FAILED | Profile incomplete
```

**Solusi:**
- Pastikan user sudah complete profile
- Cek permission user (Pro vs Free)
- Cek konfigurasi fitur

### **4. Moderation Tidak Bekerja**
**Cek Log:**
```
ERROR | System | NSFW check failed: API key invalid
USER_ACTION | User 123456789 (@username) | MODERATION_BAD_WORDS | Bad words detected: kata kasar
```

**Solusi:**
- Cek NSFW API key
- Pastikan kata kasar terdaftar di `MODERATION_WORDS`
- Cek koneksi ke API

## 📈 **Performance Monitoring:**

### **Key Metrics to Track:**
- **User Registration**: `NEW_USER_CREATED`
- **Profile Completion**: `PROFILE_COMPLETED`
- **Chat Sessions**: `Session created`
- **Feature Usage**: `FEATURE.*SUCCESS`
- **Error Rate**: `ERROR` frequency

### **Daily Reports:**
Bot akan mengirim laporan harian ke owner dengan:
- Total users
- Total chat sessions
- Report count (24h)
- Top point users

## 🔧 **Debug Commands:**

```bash
# Cek syntax
python3 -m py_compile bot.py

# Cek dependencies
pip list | grep telegram

# Monitor logs real-time
python3 bot.py

# Cari error spesifik (jika menggunakan file log)
grep "ERROR" bot.log
grep "User 123456789" bot.log
grep "FEATURE.*FAILED" bot.log
```

## 📱 **Testing Checklist:**

### **Before Testing:**
- [ ] Update `BOT_TOKEN` dengan token yang benar
- [ ] Update `OWNER_ID` dengan ID Telegram Anda
- [ ] Update `NSFW_API_KEY` jika menggunakan moderation
- [ ] Install dependencies: `pip install -r requirements.txt`

### **During Testing:**
- [ ] Monitor console logs real-time
- [ ] Test setiap fitur satu per satu
- [ ] Cek error messages di log
- [ ] Verifikasi user journey di log

### **After Testing:**
- [ ] Review semua log untuk error
- [ ] Cek performance metrics
- [ ] Identifikasi area yang perlu improvement

## 🎯 **Tips Debugging:**

1. **Start Small**: Test fitur dasar dulu (start, profile)
2. **Follow the Logs**: Setiap aksi user akan ter-log
3. **Check Error Context**: Error log akan menunjukkan user dan detail masalah
4. **Monitor Performance**: Track fitur yang sering digunakan
5. **User Journey**: Follow user dari registration sampai chat

## 🚀 **Ready to Test!**

Bot Anda sudah siap dengan sistem logging yang sangat detail. Saat testing:

1. **Jalankan**: `python3 bot.py`
2. **Monitor**: Lihat console output
3. **Test**: Coba semua fitur di Telegram
4. **Debug**: Gunakan log untuk identifikasi masalah

**Semua aktivitas akan ter-log dengan detail, jadi Anda bisa dengan mudah melihat apa yang terjadi jika ada masalah! 🎉**