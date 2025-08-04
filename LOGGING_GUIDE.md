# 📋 Panduan Logging Bot Telegram

## 🎯 Overview

Bot Telegram ini telah dilengkapi dengan sistem logging yang komprehensif untuk memudahkan debugging dan monitoring. Setiap fitur bot akan menghasilkan log entries yang detail untuk membantu mengidentifikasi masalah dan memantau aktivitas pengguna.

## 📁 File Log

Bot akan menghasilkan file log dengan nama `bot.log` yang berisi semua aktivitas. Format log menggunakan struktur yang mudah dibaca:

```
2025-08-04 16:58:10,218 - INFO - USER_ACTION | User 123456789 (@username) | START_COMMAND | User started bot
```

## 🔧 Fungsi Logging yang Tersedia

### 1. **log_user_action(user_id, username, action, details="")**
- Log semua aksi user untuk debugging
- Contoh: `USER_ACTION | User 123456789 (@username) | START_COMMAND | User started bot`

### 2. **log_error(error_msg, user_id=None, username=None, exception=None)**
- Log error dengan context user dan exception details
- Contoh: `ERROR | User 123456789 (@username) | Database connection failed | Exception: ConnectionError: Connection refused`

### 3. **log_feature_usage(feature, user_id, username, success=True, details="")**
- Log penggunaan fitur dengan status sukses/gagal
- Contoh: `FEATURE | PROFILE_SETUP | User 123456789 (@username) | SUCCESS | Profile completed successfully`

### 4. **log_chat_session(user_id, partner_id, action, details="")**
- Log aktivitas chat session
- Contoh: `CHAT_SESSION | User 123456789 | Partner 987654321 | SESSION_STARTED | New chat session`

### 5. **log_database_operation(operation, table, user_id=None, details="")**
- Log operasi database (debug level)
- Contoh: `DB_OP | INSERT | Table: user_profiles | User 123456789 | New user created`

### 6. **log_message_handling(message_type, user_id, username, success=True, details="")**
- Log handling pesan (text, photo, video, etc.)
- Contoh: `MESSAGE | TEXT | User 123456789 (@username) | SUCCESS | Text length: 50 chars`

### 7. **log_conversation_state(user_id, username, state, details="")**
- Log perubahan state conversation
- Contoh: `CONVERSATION | User 123456789 (@username) | State: PROFILE_AGE | Moving to age input`

### 8. **log_callback_query(user_id, username, callback_data, success=True, details="")**
- Log callback query handling
- Contoh: `CALLBACK | User 123456789 (@username) | Data: search_gender | SUCCESS | Search type selection`

### 9. **log_quiz_activity(user_id, username, action, details="")**
- Log aktivitas quiz
- Contoh: `QUIZ | User 123456789 (@username) | QUIZ_STARTED | Quiz #1234 started`

### 10. **log_pro_feature(user_id, username, feature, success=True, details="")**
- Log penggunaan fitur Pro
- Contoh: `PRO_FEATURE | User 123456789 (@username) | SEARCH_PRO | SUCCESS | Pro search completed`

### 11. **log_moderation(user_id, username, content_type, action, details="")**
- Log aktivitas moderasi konten
- Contoh: `MODERATION | User 123456789 (@username) | IMAGE | NSFW_DETECTED | File: ABC123`

## 📊 Kategori Log Entries

### 🚀 **USER_ACTION** - Aksi User
- `START_COMMAND` - User memulai bot
- `HELP_COMMAND` - User meminta bantuan
- `PROFILE_COMMAND` - User mengatur profil
- `SEARCH_PRO_COMMAND` - User mencari partner Pro
- `PLAY_QUIZ_COMMAND` - User memulai quiz
- `REPORT_COMMAND` - User melaporkan partner
- `JOIN_GROUP_COMMAND` - User join grup
- `NEXT_COMMAND` - User mencari partner baru
- `STOP_COMMAND` - User mengakhiri chat
- `FEEDBACK_COMMAND` - User memberikan feedback
- `POLL_COMMAND` - User membuat polling
- `SECRET_MODE_COMMAND` - User mengaktifkan mode rahasia

### 📝 **FEATURE** - Penggunaan Fitur
- `PROFILE_SETUP` - Setup profil
- `SEARCH_PRO` - Pencarian Pro
- `QUIZ` - Aktivitas quiz
- `REDEEM_POINTS` - Penukaran poin
- `TUKAR_PRO7` - Tukar 7 poin untuk Pro
- `JOIN_GROUP` - Join grup
- `LEAVE_GROUP` - Keluar grup
- `NEXT` - Cari partner baru
- `STOP` - Akhiri chat
- `REPORT` - Laporan user
- `BLOCK` - Block user
- `FEEDBACK` - Feedback chat
- `POLL` - Polling
- `SECRET_MODE` - Mode rahasia

### 💬 **MESSAGE** - Handling Pesan
- `TEXT` - Pesan teks
- `PHOTO` - Foto
- `VIDEO` - Video
- `VOICE` - Voice message
- `STICKER` - Sticker

### 🔄 **CONVERSATION** - State Conversation
- `PROFILE_GENDER` - Input gender
- `PROFILE_AGE` - Input usia
- `PROFILE_BIO` - Input bio
- `PROFILE_PHOTO` - Input foto
- `PROFILE_LANG` - Pilih bahasa
- `PROFILE_HOBBY` - Pilih hobi
- `SEARCH_GENDER` - Pilih gender partner
- `SEARCH_HOBBY` - Pilih hobi partner
- `SEARCH_AGE_MIN` - Input usia minimum
- `SEARCH_AGE_MAX` - Input usia maksimum

### 🎯 **CALLBACK** - Callback Query
- `search_gender` - Pilih gender search
- `search_hobby` - Pilih hobby search
- `search_gender_hobby` - Pilih gender+hobby search
- `quizpro_*` - Reward quiz Pro
- `quizpoin_*` - Reward quiz poin
- `report_*` - Laporan dengan alasan
- `block_*` - Block user
- `fb_*` - Feedback rating

### 🎮 **QUIZ** - Aktivitas Quiz
- `QUIZ_STARTED` - Quiz dimulai
- `QUIZ_ANSWERED` - Quiz dijawab
- `QUIZ_CORRECT` - Jawaban benar
- `QUIZ_WRONG` - Jawaban salah
- `QUIZ_REWARD_CLAIMED` - Hadiah diambil
- `POINT_EARNED` - Poin didapat

### ⭐ **PRO_FEATURE** - Fitur Pro
- `SEARCH_PRO` - Pencarian Pro
- `QUIZ_PRO_REWARD` - Reward Pro dari quiz
- `PRO_UPGRADE` - Upgrade ke Pro
- `PRO_EXPIRED` - Pro expired

### 🛡️ **MODERATION** - Moderasi Konten
- `USER_REPORT` - Laporan user
- `USER_BLOCK` - Block user
- `IMAGE` - Moderasi gambar
- `NSFW_DETECTED` - Konten NSFW terdeteksi
- `BAD_WORDS` - Kata kasar terdeteksi

### 💬 **CHAT_SESSION** - Session Chat
- `SESSION_STARTED` - Session dimulai
- `SESSION_ENDED` - Session berakhir
- `MESSAGE_SENT` - Pesan dikirim
- `MESSAGE_RECEIVED` - Pesan diterima

## 🔍 Cara Menggunakan Log untuk Debugging

### 1. **Monitor File Log**
```bash
# Lihat log real-time
tail -f bot.log

# Cari log untuk user tertentu
grep "User 123456789" bot.log

# Cari error
grep "ERROR" bot.log

# Cari aktivitas tertentu
grep "FEATURE.*PROFILE_SETUP" bot.log
```

### 2. **Identifikasi Masalah**
- **Error**: Cari entries dengan `ERROR` level
- **Failed Features**: Cari `FEATURE.*FAILED`
- **User Issues**: Filter berdasarkan user_id
- **Session Problems**: Cari `CHAT_SESSION` entries

### 3. **Contoh Debugging Scenarios**

#### User tidak bisa start bot:
```
grep "User 123456789.*START_COMMAND" bot.log
grep "User 123456789.*ERROR" bot.log
```

#### Profile setup gagal:
```
grep "User 123456789.*PROFILE" bot.log
grep "FEATURE.*PROFILE_SETUP.*FAILED" bot.log
```

#### Chat tidak berfungsi:
```
grep "User 123456789.*CHAT_SESSION" bot.log
grep "User 123456789.*MESSAGE" bot.log
```

#### Quiz error:
```
grep "User 123456789.*QUIZ" bot.log
grep "QUIZ.*ERROR" bot.log
```

## 📈 Monitoring Aktivitas

### Statistik Harian
- Total users aktif
- Total chat sessions
- Total reports
- Top users berdasarkan poin
- Fitur yang paling sering digunakan

### Alert Monitoring
- Error rate yang tinggi
- User yang sering di-report
- Konten NSFW yang terdeteksi
- Fitur yang sering gagal

## 🛠️ Konfigurasi Logging

Logging dapat dikonfigurasi di bagian awal `bot.py`:

```python
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', 
    level=logging.INFO,  # INFO, DEBUG, WARNING, ERROR
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()  # Output ke console juga
    ]
)
```

## ✅ Test Logging

Untuk memverifikasi sistem logging berfungsi, jalankan:

```bash
python3 test_logging_simple.py
```

Test ini akan memverifikasi semua fungsi logging dan menghasilkan contoh output.

## 📋 Kesimpulan

Dengan sistem logging yang komprehensif ini, Anda akan dapat:

1. **Debug masalah** dengan mudah menggunakan log entries yang detail
2. **Monitor aktivitas** bot secara real-time
3. **Identifikasi pola** penggunaan dan masalah yang sering terjadi
4. **Track user behavior** untuk improvement fitur
5. **Maintain bot** dengan lebih efisien

Semua aktivitas bot sekarang akan tercatat dengan detail, sehingga Anda tidak perlu lagi mengirim screenshot untuk debugging - cukup cek file `bot.log`! 🎉