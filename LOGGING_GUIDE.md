# 📝 Bot Logging System Guide

## 🎯 **Overview**
Bot Telegram Anda sudah dilengkapi dengan sistem logging yang komprehensif untuk memudahkan debugging dan monitoring. Semua aktivitas bot akan dicatat dalam file `bot.log` dengan format yang terstruktur.

## 📁 **File Log**
- **File**: `bot.log` (dibuat otomatis saat bot berjalan)
- **Format**: Timestamp - Level - Category | Details
- **Level**: INFO, ERROR, DEBUG

## 🔍 **Kategori Log yang Tersedia**

### 1. **USER_ACTION** - Aksi User
```
USER_ACTION | User 123456789 (@username) | START_COMMAND | User started bot
USER_ACTION | User 123456789 (@username) | PROFILE_COMMAND | Started profile setup
USER_ACTION | User 123456789 (@username) | SEARCH_PRO_COMMAND | Searching for Pro partner
```

### 2. **FEATURE** - Penggunaan Fitur
```
FEATURE | PROFILE_SETUP | User 123456789 (@username) | SUCCESS | Profile completed successfully
FEATURE | SEARCH_PRO | User 123456789 (@username) | FAILED | User not Pro
FEATURE | QUIZ_PLAY | User 123456789 (@username) | SUCCESS | Quiz completed, earned 50 points
```

### 3. **MESSAGE** - Penanganan Pesan
```
MESSAGE | TEXT | User 123456789 (@username) | SUCCESS | Text message forwarded
MESSAGE | PHOTO | User 123456789 (@username) | SUCCESS | Photo processed and sent
MESSAGE | VIDEO | User 123456789 (@username) | FAILED | Video too large
```

### 4. **QUIZ** - Aktivitas Quiz
```
QUIZ | User 123456789 (@username) | QUIZ_STARTED | Quiz ID: Q123
QUIZ | User 123456789 (@username) | QUIZ_ANSWERED | Correct answer, +10 points
QUIZ | User 123456789 (@username) | QUIZ_COMPLETED | Total score: 85/100
```

### 5. **PRO_FEATURE** - Fitur Pro
```
PRO_FEATURE | User 123456789 (@username) | PRO_SEARCH | SUCCESS | Found 3 Pro partners
PRO_FEATURE | User 123456789 (@username) | PRO_UPGRADE | FAILED | Payment failed
```

### 6. **MODERATION** - Moderasi Konten
```
MODERATION | User 123456789 (@username) | TEXT | BAD_WORDS_DETECTED | Kata kasar: anjing
MODERATION | User 123456789 (@username) | IMAGE | NSFW_DETECTED | File: PHOTO123
```

### 7. **MEDIA_PROC** - Pemrosesan Media
```
MEDIA_PROC | User 123456789 (@username) | Type: PHOTO | File: PHOTO123 | Size: 1024000 bytes | Time: 150ms
MEDIA_PROC | User 123456789 (@username) | Type: VIDEO | File: VIDEO456 | Size: 5242880 bytes | Time: 800ms
```

### 8. **HEALTH** - Status Sistem
```
HEALTH | Database | CONNECTED | SQLite connection established
HEALTH | API | RESPONDING | NSFW API response time: 200ms
HEALTH | Bot | READY | All handlers registered successfully
```

### 9. **ERROR** - Error dan Exception
```
ERROR | User 123456789 (@username) | Database connection failed | Exception: sqlite3.OperationalError: no such table
ERROR | System | Bot initialization failed | Exception: ValueError: Invalid token
```

## 🚀 **Cara Menggunakan Log untuk Debugging**

### **1. Melihat Log Real-time**
```bash
# Melihat log secara real-time
tail -f bot.log

# Melihat 50 baris terakhir
tail -n 50 bot.log

# Mencari log user tertentu
grep "User 123456789" bot.log

# Mencari error saja
grep "ERROR" bot.log
```

### **2. Debugging Masalah Umum**

#### **User tidak bisa start bot:**
```bash
grep "START_COMMAND" bot.log
grep "ERROR.*start" bot.log
```

#### **Pro search tidak berfungsi:**
```bash
grep "SEARCH_PRO" bot.log
grep "PRO_FEATURE.*FAILED" bot.log
```

#### **Media tidak terkirim:**
```bash
grep "MEDIA_PROC.*FAILED" bot.log
grep "MESSAGE.*VIDEO.*FAILED" bot.log
```

#### **Quiz error:**
```bash
grep "QUIZ.*ERROR" bot.log
grep "QUIZ.*FAILED" bot.log
```

### **3. Monitoring Performa**
```bash
# Melihat response time media processing
grep "MEDIA_PROC.*Time:" bot.log

# Melihat API response time
grep "API.*RESPONDING" bot.log

# Melihat database operations
grep "Database" bot.log
```

## 📊 **Contoh Log Skenario Lengkap**

### **Skenario 1: User Baru Setup Profile**
```
2025-08-04 17:47:48,051 - INFO - USER_ACTION | User 123456789 (@newuser) | START_COMMAND | User started bot
2025-08-04 17:47:48,051 - INFO - FEATURE | PROFILE_INCOMPLETE | User 123456789 (@newuser) | FAILED | Profile not complete
2025-08-04 17:47:48,051 - INFO - USER_ACTION | User 123456789 (@newuser) | PROFILE_COMMAND | Started profile setup
2025-08-04 17:47:48,051 - INFO - CONVERSATION | User 123456789 (@newuser) | State: PROFILE_GENDER | Gender selection started
2025-08-04 17:47:48,051 - INFO - USER_ACTION | User 123456789 (@newuser) | PROFILE_GENDER_SET | Gender set to: Male
2025-08-04 17:47:48,051 - INFO - USER_ACTION | User 123456789 (@newuser) | PROFILE_AGE_SET | Age set to: 25
2025-08-04 17:47:48,051 - INFO - USER_ACTION | User 123456789 (@newuser) | PROFILE_COMPLETED | Profile setup finished
2025-08-04 17:47:48,051 - INFO - FEATURE | PROFILE_SETUP | User 123456789 (@newuser) | SUCCESS | Profile completed successfully
```

### **Skenario 2: User Kirim Media**
```
2025-08-04 17:47:48,051 - INFO - USER_ACTION | User 123456789 (@user) | FORWARD_PHOTO | Photo sent to partner
2025-08-04 17:47:48,051 - INFO - MEDIA_PROC | User 123456789 (@user) | Type: PHOTO | File: PHOTO123 | Size: 1024000 bytes | Time: 150ms
2025-08-04 17:47:48,051 - INFO - MESSAGE | PHOTO | User 123456789 (@user) | SUCCESS | Photo processed and sent
```

### **Skenario 3: Error Handling**
```
2025-08-04 17:47:48,051 - INFO - USER_ACTION | User 123456789 (@user) | SEARCH_PRO_COMMAND | Searching for Pro partner
2025-08-04 17:47:48,051 - INFO - FEATURE | SEARCH_PRO | User 123456789 (@user) | FAILED | User not Pro
2025-08-04 17:47:48,051 - ERROR | User 123456789 (@user) | Pro search failed: User not Pro
```

## 🔧 **Tips Debugging**

### **1. Identifikasi Masalah**
- Cari log dengan status `FAILED`
- Perhatikan timestamp untuk urutan kejadian
- Cek user ID dan username untuk tracking

### **2. Analisis Error**
- Error log akan menunjukkan exception type dan message
- Cek apakah error terjadi di database, API, atau bot logic
- Perhatikan context user untuk reproduksi masalah

### **3. Monitoring Performa**
- Response time media processing (ideal < 500ms)
- API response time (ideal < 1000ms)
- Database operation success rate

### **4. Security Monitoring**
- Moderation logs untuk konten tidak aman
- User report logs
- Ban/unban activities

## 📱 **Contoh Debugging Telegram Bot**

Ketika user melaporkan masalah di Telegram, Anda bisa:

1. **Minta user ID mereka** (dari `/start` command)
2. **Cari log user tersebut:**
   ```bash
   grep "User 123456789" bot.log | tail -20
   ```
3. **Analisis urutan kejadian** berdasarkan timestamp
4. **Identifikasi error** yang terjadi
5. **Reproduksi masalah** berdasarkan log

## ✅ **Keuntungan Sistem Logging Ini**

1. **Real-time monitoring** - Semua aktivitas tercatat
2. **Structured format** - Mudah dibaca dan dianalisis
3. **User tracking** - Bisa track per user
4. **Performance monitoring** - Response time dan error rate
5. **Security audit** - Moderation dan report logs
6. **Debugging friendly** - Error context lengkap

## 🎯 **Kesimpulan**

Bot Anda sudah siap untuk debugging! Dengan sistem logging yang komprehensif ini, Anda bisa:

- ✅ **Monitor semua aktivitas user** secara real-time
- ✅ **Debug masalah** dengan mudah menggunakan log
- ✅ **Track performa** bot dan API
- ✅ **Monitor keamanan** dan moderasi
- ✅ **Analisis penggunaan fitur** untuk improvement

Sekarang Anda bisa test bot di Telegram dan jika ada masalah, tinggal cek log file untuk debugging! 🚀