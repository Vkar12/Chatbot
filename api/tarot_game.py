# tarot_game.py — game tarot lucu untuk bot LINE
# Hubungkan dari index.py dengan: from tarot_game import proses_tarot
# Data poin, kartu harian, koleksi, dan kuis disimpan otomatis di tarot_data.db.

import random
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).with_name("tarot_data.db")
QUIZ_SECONDS = 30
DAILY_POINTS = 10
QUIZ_POINTS = 15

KARTU = [
    {"nama": "The Fool", "ramalan": "Ada awal baru di depan mata. Jangan impulsif checkout jam 2 pagi.", "cinta": "Jangan menganggap view story sebagai lamaran.", "nasihat": "Berani mencoba itu bagus; baca syarat dan ketentuan juga bagus."},
    {"nama": "The Magician", "ramalan": "Kamu punya modal untuk mulai. Tinggal jangan kebanyakan buka tab.", "cinta": "Pesona boleh, komunikasi tetap perlu.", "nasihat": "Gunakan kemampuanmu, bukan alasanmu."},
    {"nama": "The High Priestess", "ramalan": "Pikirkan semuanya dengan tenang. Jangan semua dijadikan teori konspirasi.", "cinta": "Kalau dia membingungkan, tanyakan baik-baik; jangan menyewa detektif.", "nasihat": "Dengarkan intuisi, lalu cek fakta."},
    {"nama": "The Empress", "ramalan": "Waktunya merawat diri. Minum air juga termasuk glow up.", "cinta": "Kamu layak dihargai tanpa harus menjadi badut emosional.", "nasihat": "Rawat dirimu seperti playlist favorit."},
    {"nama": "The Emperor", "ramalan": "Susun rencana sebelum bertindak. Spreadsheet tidak pernah mengkhianati—biasanya.", "cinta": "Batasan sehat lebih menarik daripada tarik-ulur.", "nasihat": "Tegas boleh, keras kepala jangan."},
    {"nama": "The Lovers", "ramalan": "Sebuah pilihan meminta perhatian. Jangan lempar koin untuk keputusan penting.", "cinta": "Chemistry itu seru; konsistensi juga penting.", "nasihat": "Pilih yang sejalan dengan nilai dan kebutuhanmu."},
    {"nama": "The Chariot", "ramalan": "Gas boleh, tapi lihat jalan. Semangat tanpa arah cuma bikin capek.", "cinta": "Kalau ingin dekat, tunjukkan lewat tindakan yang jelas.", "nasihat": "Fokus satu langkah sebelum sepuluh langkah berikutnya."},
    {"nama": "Strength", "ramalan": "Kekuatan hari ini adalah menahan diri dari membalas chat dengan paragraf 12 halaman.", "cinta": "Jujur dan tenang lebih kuat daripada tes rahasia.", "nasihat": "Lembut bukan berarti lemah."},
    {"nama": "The Hermit", "ramalan": "Kamu mungkin butuh waktu sendiri. Mode pesawat bukan kejahatan.", "cinta": "Jangan menghilang tanpa kabar kalau orang lain menunggu kejelasan.", "nasihat": "Ambil jeda, lalu kembali dengan pikiran jernih."},
    {"nama": "Wheel of Fortune", "ramalan": "Situasi bisa berubah. Semoga yang berubah cuma rencana, bukan password Wi-Fi.", "cinta": "Jangan menggantungkan semuanya pada timing; komunikasi tetap berperan.", "nasihat": "Fleksibel menghadapi hal yang tidak bisa kamu kendalikan."},
    {"nama": "Justice", "ramalan": "Hari ini semesta menyarankan kejujuran. Mulailah dengan mengakui kamu belum baca pesan tadi.", "cinta": "Hubungan sehat butuh kejelasan dan tanggung jawab dua arah.", "nasihat": "Pertimbangkan fakta sebelum mengambil kesimpulan."},
    {"nama": "The Hanged Man", "ramalan": "Coba lihat masalah dari sisi lain. Kecuali saldo, itu perlu tindakan nyata.", "cinta": "Menunggu boleh, tetapi jangan menunda hidup demi ketidakpastian.", "nasihat": "Jeda bisa membantu menemukan perspektif baru."},
    {"nama": "Death", "ramalan": "Satu bab mungkin perlu ditutup agar bab baru dimulai. Ini bukan ramalan kematian sungguhan.", "cinta": "Melepas pola tidak sehat bisa menjadi awal yang baik.", "nasihat": "Perubahan bisa membuka pilihan baru."},
    {"nama": "Temperance", "ramalan": "Jaga keseimbangan. Jangan produktif 14 jam lalu rebahan 14 hari.", "cinta": "Hubungan perlu usaha seimbang, bukan satu orang jadi customer service.", "nasihat": "Cari ritme yang bisa kamu pertahankan."},
    {"nama": "The Devil", "ramalan": "Ada kebiasaan yang sulit dilepas. Kalau ini soal diskon, semoga keranjangmu kuat.", "cinta": "Jangan salah mengira obsesi sebagai kasih sayang.", "nasihat": "Kenali kebiasaan yang menguras energi."},
    {"nama": "The Tower", "ramalan": "Rencana bisa berubah. Backup tugas dulu sebelum semesta ikut campur.", "cinta": "Jangan bikin kesimpulan hanya dari satu chat.", "nasihat": "Saat keadaan berubah, susun ulang langkah."},
    {"nama": "The Star", "ramalan": "Ada ruang untuk berharap. Tapi tetap kirim lamaran, jangan cuma manifesting.", "cinta": "Harapan baik, komunikasi langsung lebih baik.", "nasihat": "Rayakan kemajuan kecil yang sudah kamu buat."},
    {"nama": "The Moon", "ramalan": "Jangan buru-buru percaya asumsi. Otakmu kadang penulis fanfiction.", "cinta": "Sinyal campur aduk bukan bukti cinta rahasia.", "nasihat": "Pisahkan fakta, dugaan, dan overthinking."},
    {"nama": "The Sun", "ramalan": "Cari hal kecil yang bikin senang. Kalau ketemu uang di saku, itu plot twist positif.", "cinta": "Nikmati hubungan yang membuatmu aman menjadi diri sendiri.", "nasihat": "Bagikan energi baik tanpa memaksakan diri selalu ceria."},
    {"nama": "Judgement", "ramalan": "Saatnya evaluasi pilihan. Tidak semua keputusan lama harus dipertahankan demi gengsi.", "cinta": "Percakapan jujur bisa memperjelas arah hubungan.", "nasihat": "Belajar dari masa lalu tanpa tinggal di sana."},
    {"nama": "The World", "ramalan": "Satu tahap hampir selesai. Silakan bangga dulu sebelum mencari masalah baru.", "cinta": "Hubungan yang baik memberi ruang untuk tumbuh bersama.", "nasihat": "Akui pencapaianmu, sekecil apa pun."},
]

QUIZ = [
    {"q": "Kartu yang melambangkan harapan dan optimisme adalah...", "opts": {"A": "The Tower", "B": "The Star", "C": "The Devil"}, "a": "B", "why": "The Star melambangkan harapan dan pemulihan."},
    {"q": "Kartu perubahan mendadak dan runtuhnya rencana adalah...", "opts": {"A": "The Tower", "B": "The Sun", "C": "The Empress"}, "a": "A", "why": "The Tower melambangkan guncangan atau perubahan besar."},
    {"q": "Kartu yang berkaitan dengan keceriaan dan kejelasan adalah...", "opts": {"A": "The Moon", "B": "Death", "C": "The Sun"}, "a": "C", "why": "The Sun diasosiasikan dengan kehangatan dan kejelasan."},
    {"q": "Kartu tentang ketidakpastian dan asumsi adalah...", "opts": {"A": "The Moon", "B": "Justice", "C": "The Chariot"}, "a": "A", "why": "The Moon mengingatkan kita membedakan fakta dan overthinking."},
    {"q": "Kartu yang berkaitan dengan pilihan dan hubungan adalah...", "opts": {"A": "The Hermit", "B": "The Lovers", "C": "The World"}, "a": "B", "why": "The Lovers berkaitan dengan hubungan, pilihan, dan keselarasan."},
]


def _db():
    return sqlite3.connect(DB_PATH, timeout=10)


def _init_db():
    with _db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            chat_id TEXT, user_id TEXT, points INTEGER DEFAULT 0,
            last_daily TEXT, collection TEXT DEFAULT '',
            PRIMARY KEY(chat_id, user_id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS quizzes (
            chat_id TEXT PRIMARY KEY, qindex INTEGER, answer TEXT, expires REAL)""")


_init_db()


def _today():
    return time.strftime("%Y-%m-%d", time.localtime())


def _user(chat_id, user_id):
    with _db() as c:
        c.execute("INSERT OR IGNORE INTO users(chat_id,user_id) VALUES(?,?)", (str(chat_id), str(user_id)))
        row = c.execute("SELECT points,last_daily,collection FROM users WHERE chat_id=? AND user_id=?",
                        (str(chat_id), str(user_id))).fetchone()
    return {"points": row[0], "daily": row[1], "collection": row[2]}


def _points(chat_id, user_id, amount):
    _user(chat_id, user_id)
    with _db() as c:
        c.execute("UPDATE users SET points=points+? WHERE chat_id=? AND user_id=?",
                  (amount, str(chat_id), str(user_id)))


def _add_card(chat_id, user_id, name):
    user = _user(chat_id, user_id)
    cards = user["collection"].split(",") if user["collection"] else []
    new = name not in cards
    if new:
        cards.append(name)
    with _db() as c:
        c.execute("UPDATE users SET collection=? WHERE chat_id=? AND user_id=?",
                  (",".join(cards), str(chat_id), str(user_id)))
    return new


def _fmt(card, title="🃏 KARTU TAROT"):
    return (f"{title}: {card['nama'].upper()}\n\n"
            f"🔮 Ramalan: {card['ramalan']}\n"
            f"💘 Cinta: {card['cinta']}\n"
            f"🧭 Pesan: {card['nasihat']}\n\n"
            "Catatan: bacaan simbolis untuk hiburan, bukan kepastian masa depan.")


def _draw(chat_id, user_id, daily=False, love=False):
    user = _user(chat_id, user_id)
    if daily and user["daily"] == _today():
        return "🌞 Kamu sudah mengambil kartu harian hari ini. Besok balik lagi, wahai pencari takdir."
    card = random.choice(KARTU)
    if daily:
        with _db() as c:
            c.execute("UPDATE users SET last_daily=? WHERE chat_id=? AND user_id=?",
                      (_today(), str(chat_id), str(user_id)))
        _points(chat_id, user_id, DAILY_POINTS)
        new = _add_card(chat_id, user_id, card["nama"])
        return _fmt(card, "🌞 DAILY CARD") + f"\n\n✨ +{DAILY_POINTS} Oracle Points" + (
            "\n🗂️ Kartu baru masuk koleksi!" if new else "\n🗂️ Kartu ini sudah ada di koleksi.")
    if love:
        return "💘 LOVE ORACLE\n\n" + _fmt(card, "💞 KARTU CINTA") + (
            "\n\nSemesta tidak bisa memastikan perasaan orang lain—komunikasi tetap juaranya.")
    return _fmt(card)


def _start_quiz(chat_id):
    qi = random.randrange(len(QUIZ))
    q = QUIZ[qi]
    with _db() as c:
        c.execute("INSERT OR REPLACE INTO quizzes(chat_id,qindex,answer,expires) VALUES(?,?,?,?)",
                  (str(chat_id), qi, q["a"], time.time() + QUIZ_SECONDS))
    return ("🔮 ORACLE QUIZ\n\n" + q["q"] + "\n\n" +
            "\n".join(f"{k}. {v}" for k, v in q["opts"].items()) +
            f"\n\nKetik !tarot answer A/B/C.\n⏱️ Batas waktu {QUIZ_SECONDS} detik.")


def _answer_quiz(chat_id, user_id, choice):
    with _db() as c:
        row = c.execute("SELECT qindex,answer,expires FROM quizzes WHERE chat_id=?", (str(chat_id),)).fetchone()
        if not row:
            return "🔮 Belum ada kuis aktif. Ketik !tarot quiz."
        qi, answer, expires = row
        if time.time() > expires:
            c.execute("DELETE FROM quizzes WHERE chat_id=?", (str(chat_id),))
            return "⏰ Waktu kuis habis! Semesta sudah pindah ke sesi berikutnya."
        if choice not in ("A", "B", "C"):
            return "Pilih A, B, atau C. Jangan jawab pakai telepati dulu."
        if choice != answer:
            return "❌ Belum tepat. Poin aman, harga diri bisa dipulihkan. Coba kuis berikutnya!"
        c.execute("DELETE FROM quizzes WHERE chat_id=?", (str(chat_id),))
    _points(chat_id, user_id, QUIZ_POINTS)
    return f"✅ BENAR! +{QUIZ_POINTS} Oracle Points.\n{QUIZ[qi]['why']}"


def _rank(points):
    if points >= 300:
        return "✨ Supreme Delulu Oracle"
    if points >= 150:
        return "👑 Certified Oracle"
    if points >= 50:
        return "🌙 Reader of the Moon"
    return "🔮 Oracle Magang"


def proses_tarot(chat_id, user_id, pesan, get_nama=None):
    """Return teks balasan untuk command tarot, atau None jika bukan command tarot."""
    chat_id, user_id = str(chat_id or user_id), str(user_id)
    command = " ".join((pesan or "").strip().lower().split())

    if command in ("!tarot", "!tarot help", "!tarot bantuan"):
        return (
            "🔮 THE GROUP ORACLE\nRamalan lucu, kartu misterius, dan keputusan hidup yang perlu ditinjau.\n\n"
            "!tarot draw — ambil kartu acak\n"
            "!tarot daily — kartu harian (+10 poin, sekali sehari)\n"
            "!tarot love — bacaan bertema cinta\n"
            "!tarot crush — bacaan simbolis tentang gebetan\n"
            "!tarot group — ramalan lucu grup\n"
            "!tarot quiz — mulai kuis\n"
            "!tarot answer A — jawab kuis\n"
            "!tarot points — cek poin dan gelar\n"
            "!tarot leaderboard — peringkat grup\n"
            "!tarot collection — koleksi kartu\n"
            "!tarot help — aturan\n\n"
            "Kuis berlangsung 30 detik. Jawaban benar +15 poin. Kartu harian +10 poin sekali sehari.\n"
            "Tarot ini untuk hiburan dan refleksi, bukan kepastian masa depan."
        )

    if command == "!tarot draw":
        return _draw(chat_id, user_id)
    if command == "!tarot daily":
        return _draw(chat_id, user_id, daily=True)
    if command in ("!tarot love", "!tarot crush"):
        return _draw(chat_id, user_id, love=True)
    if command == "!tarot group":
        jokes = [
            "Seseorang akan bilang 'aku cuma mau nanya' lalu memulai rapat 87 pesan.",
            "Ada yang membaca chat dari tadi tapi membalas saat topik sudah pindah tiga kali.",
            "Energi grup hari ini: 20% informasi, 80% stiker.",
            "Satu drama kecil berpotensi menjadi trilogi. Siapkan camilan.",
            "Semesta menyarankan admin istirahat. Notifikasi tidak dibayar lembur.",
        ]
        return f"🌪️ GROUP PROPHECY: {random.choice(KARTU)['nama'].upper()}\n\n{random.choice(jokes)}\n\nIni ramalan hiburan, bukan tuduhan kepada anggota tertentu."
    if command == "!tarot quiz":
        return _start_quiz(chat_id)
    if command.startswith("!tarot answer"):
        parts = command.split()
        if len(parts) != 3:
            return "Format: !tarot answer A (atau B/C)."
        return _answer_quiz(chat_id, user_id, parts[2].upper())
    if command == "!tarot points":
        user = _user(chat_id, user_id)
        return f"🏅 Oracle Points: {user['points']}\nGelar: {_rank(user['points'])}"
    if command == "!tarot leaderboard":
        with _db() as c:
            rows = c.execute(
                "SELECT user_id,points FROM users WHERE chat_id=? ORDER BY points DESC,user_id LIMIT 10",
                (chat_id,)
            ).fetchall()
        if not rows:
            return "🔮 ORACLE LEADERBOARD\nBelum ada skor. Ambil kartu atau ikuti kuis dulu!"

        lines = ["🏆 ORACLE LEADERBOARD", "✨ 10 Oracle dengan poin tertinggi ✨"]
        for i, (uid, pts) in enumerate(rows, 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
            nama = None
            if get_nama:
                try:
                    nama = get_nama(uid)
                except Exception:
                    nama = None
            if not nama or nama == uid or str(nama).startswith("User ("):
                # Fallback bila LINE gagal memberikan nama profil
                nama = f"Member {str(uid)[-4:]}"
            lines.append(f"{medal} {nama} — {pts} poin")
        lines.append("\n💡 Mainkan !tarot daily atau !tarot quiz untuk menambah poin.")
        return "\n".join(lines)
    if command == "!tarot collection":
        user = _user(chat_id, user_id)
        cards = user["collection"].split(",") if user["collection"] else []
        if not cards:
            return "🗂️ Koleksimu masih kosong. Ketik !tarot daily untuk mengambil kartu pertamamu."
        return "🗂️ KOLEKSI KARTU\n" + "\n".join(f"• {name}" for name in cards)
    if command.startswith("!tarot"):
        return "Command tidak dikenal. Ketik !tarot untuk melihat menu."
    return None
