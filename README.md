# 🤖 Telegram Anonymous Chat Bot

Bot Telegram untuk chat anonymous dengan fitur lengkap dan sistem logging komprehensif untuk debugging.

## ✨ Fitur Utama

### 🔐 Chat Anonymous
- **Random Chat**: Cari partner chat secara acak
- **Pro Search**: Pencarian partner berdasarkan gender, hobi, dan usia (untuk user Pro)
- **Secret Mode**: Mode pesan rahasia yang otomatis menghapus pesan setelah dibaca

### 👤 Profile Management
- **Complete Profile**: Gender, usia, bio, foto, bahasa, hobi
- **Multi-Language**: Dukungan bahasa Indonesia dan Inggris
- **Profile Validation**: Validasi data profil sebelum chat

### 🎮 Quiz & Points System
- **Daily Quiz**: Quiz harian dengan reward poin/Pro
- **Point System**: Sistem poin yang bisa ditukar Pro
- **Leaderboard**: Papan peringkat harian

### 🛡️ Moderation & Safety
- **Content Moderation**: Filter kata kasar dan konten NSFW
- **Report System**: Sistem pelaporan user
- **Block System**: Block user yang tidak diinginkan
- **Ban System**: Sistem ban otomatis

### 👥 Group Features
- **Group Chat**: Grup anonim dengan maksimal 30 member
- **Auto Join**: Bergabung otomatis ke grup yang belum penuh
- **Group Polling**: Polling dalam grup

### 📊 Analytics & Feedback
- **User Feedback**: Rating sistem untuk partner
- **Daily Statistics**: Statistik harian untuk owner
- **Broadcast System**: Broadcast pemenang quiz

## 🔧 Setup & Installation

### 1. Install Dependencies
```bash
pip install python-telegram-bot requests
```

### 2. Konfigurasi Bot
Edit file `bot.py` dan ganti nilai berikut:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Token dari @BotFather
OWNER_ID = 123456789          # ID Telegram Anda
NSFW_API_KEY = "YOUR_MODERATECONTENT_API_KEY"  # API key ModerateContent
```

### 3. Run Bot
```bash
python3 bot.py
```

## 📝 Sistem Logging

Bot ini dilengkapi dengan sistem logging komprehensif untuk memudahkan debugging dan monitoring.

### 🎯 Jenis Log

#### 1. **User Actions** (`USER_ACTION`)
Log semua aksi user:
```
USER_ACTION | User 123456789 (@username) | START_COMMAND | User started bot
USER_ACTION | User 123456789 (@username) | PROFILE_GENDER_SET | Gender set to: Male
USER_ACTION | User 123456789 (@username) | SEARCH_PREFERENCES | Gender: Female, Hobby: Music, Age: 18-25
```

#### 2. **Feature Usage** (`FEATURE`)
Log penggunaan fitur dengan status sukses/gagal:
```
FEATURE | START_COMMAND | User 123456789 (@username) | SUCCESS | Profile complete
FEATURE | SEARCH_PRO | User 123456789 (@username) | FAILED | User not Pro
FEATURE | QUIZ | User 123456789 (@username) | SUCCESS | Quiz #1234 correct answer: Jakarta
```

#### 3. **Errors** (`ERROR`)
Log error dengan context user:
```
ERROR | User 123456789 (@username) | Database connection failed: database is locked
ERROR | System | Bot initialization failed: Invalid token
```

#### 4. **System Info** (`INFO`)
Log informasi sistem:
```
INFO | Database initialized successfully
INFO | All handlers registered successfully. Starting bot...
INFO | Daily leaderboard sent - Users: 150, Chats: 45, Reports: 3
```

### 🔍 Cara Debugging

#### 1. **Monitor Logs Real-time**
```bash
tail -f bot.log  # Jika menggunakan file log
# Atau lihat output console saat menjalankan bot
```

#### 2. **Cari Error Spesifik**
```bash
grep "ERROR" bot.log
grep "User 123456789" bot.log  # Cari log user tertentu
grep "FEATURE.*FAILED" bot.log  # Cari fitur yang gagal
```

#### 3. **Track User Journey**
```bash
grep "User 123456789" bot.log | grep "USER_ACTION"
```

### 📊 Log Examples

#### User Registration Flow:
```
INFO | Database initialized successfully
USER_ACTION | User 123456789 (@newuser) | NEW_USER_CREATED | Profile auto-created
USER_ACTION | User 123456789 (@newuser) | PROFILE_COMMAND | Started profile setup
FEATURE | PROFILE_SETUP | User 123456789 (@newuser) | SUCCESS | Gender selection started
USER_ACTION | User 123456789 (@newuser) | PROFILE_GENDER_SET | Gender set to: Male
USER_ACTION | User 123456789 (@newuser) | PROFILE_AGE_SET | Age set to: 25
USER_ACTION | User 123456789 (@newuser) | PROFILE_BIO_SET | Bio length: 50 chars
USER_ACTION | User 123456789 (@newuser) | PROFILE_PHOTO_SET | Photo ID: AgACAgEAAxkBAAIB...
USER_ACTION | User 123456789 (@newuser) | PROFILE_LANG_SET | Language set to: Indonesian
USER_ACTION | User 123456789 (@newuser) | PROFILE_COMPLETED | Hobbies: ['Music', 'Coding']
FEATURE | PROFILE_SETUP | User 123456789 (@newuser) | SUCCESS | Profile completed successfully
```

#### Chat Session Flow:
```
USER_ACTION | User 123456789 (@user1) | SEARCH_PRO_COMMAND
FEATURE | SEARCH_PRO | User 123456789 (@user1) | SUCCESS | Search options shown
USER_ACTION | User 123456789 (@user1) | SEARCH_TYPE_SELECTED | Gender search
USER_ACTION | User 123456789 (@user1) | SEARCH_GENDER_SET | Gender preference: Female
USER_ACTION | User 123456789 (@user1) | SEARCH_AGE_MIN_SET | Min age: 18
USER_ACTION | User 123456789 (@user1) | SEARCH_AGE_MAX_SET | Max age: 25, Min age: 18
INFO | Found 5 potential partners for user 123456789
INFO | Partner found with gender match: 123456789 -> 987654321 (gender: Female)
FEATURE | SEARCH_PRO | User 123456789 (@user1) | SUCCESS | Partner found: 987654321
INFO | Session created: 123456789 <-> 987654321 (secret_mode: False)
USER_ACTION | User 123456789 (@user1) | FORWARD_TEXT | Text forwarded to 987654321
USER_ACTION | User 987654321 (@user2) | FORWARD_TEXT | Text forwarded to 123456789
```

#### Error Handling:
```
USER_ACTION | User 123456789 (@user1) | PROFILE_AGE_INVALID | Invalid age: abc
ERROR | User 123456789 (@user1) | Database connection failed: database is locked
FEATURE | SEARCH_PRO | User 123456789 (@user1) | FAILED | User not Pro
USER_ACTION | User 123456789 (@user1) | MODERATION_BAD_WORDS | Bad words detected: kata kasar
```

## 🚀 Commands

### User Commands
- `/start` - Mulai bot
- `/help` - Bantuan
- `/profile` - Atur profil
- `/searchpro` - Cari partner Pro
- `/playquiz` - Main quiz
- `/redeem` - Cek poin
- `/tukarpro7` - Tukar 7 poin untuk Pro 7 hari
- `/joingroup` - Join grup
- `/next` - Cari partner baru
- `/stop` - Akhiri chat
- `/report` - Laporkan partner
- `/feedback` - Beri rating
- `/poll` - Buat polling
- `/secretmode` - Aktifkan mode rahasia

### Owner Commands
- `/ban` - Ban user
- `/unban` - Unban user
- `/grant_pro` - Berikan Pro
- `/broadcast` - Broadcast pesan
- `/adminstats` - Statistik admin

## 🛠️ Troubleshooting

### Common Issues

#### 1. **Bot tidak merespon**
- Cek log untuk error connection
- Pastikan token bot valid
- Cek koneksi internet

#### 2. **Database error**
- Cek permission file database
- Restart bot untuk reset connection
- Cek log untuk error spesifik

#### 3. **Fitur tidak berfungsi**
- Cek log `FEATURE.*FAILED`
- Pastikan user sudah complete profile
- Cek permission user (Pro vs Free)

#### 4. **Moderation tidak bekerja**
- Cek NSFW API key
- Cek log `MODERATION_*`
- Pastikan kata kasar terdaftar

### Debug Commands
```bash
# Cek syntax
python3 -m py_compile bot.py

# Cek dependencies
pip list | grep telegram

# Monitor logs
tail -f bot.log

# Cari error
grep -i error bot.log
```

## 📈 Performance Monitoring

### Key Metrics
- **User Registration**: Track `NEW_USER_CREATED`
- **Profile Completion**: Track `PROFILE_COMPLETED`
- **Chat Sessions**: Track `Session created`
- **Feature Usage**: Track `FEATURE.*SUCCESS`
- **Error Rate**: Track `ERROR` frequency

### Daily Reports
Bot akan mengirim laporan harian ke owner dengan:
- Total users
- Total chat sessions
- Report count (24h)
- Top point users

## 🔒 Security Features

- **User Privacy**: Username masking untuk privacy
- **Content Filtering**: Auto-filter konten tidak aman
- **Rate Limiting**: Built-in protection
- **Ban System**: Auto-ban untuk pelanggaran
- **Report System**: User reporting mechanism

## 📞 Support

Jika ada masalah, cek log terlebih dahulu untuk informasi detail error. Log akan membantu mengidentifikasi masalah dengan cepat dan akurat.

---

**Bot ini siap untuk production dengan sistem logging yang komprehensif! 🚀**