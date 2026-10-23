# sambung_kata.py
import time
import random
from wordfreq import zipf_frequency

game_sessions = {}
WAKTU_GILIRAN = 30
NYAWA_AWAL = 3
BATAS_KATA_VALID = 3.0
PANJANG_KATA_MAKS = 24

# Kata awal dipilih acak setiap kali permainan dimulai.
KATA_AWAL = [
    "apel", "awan", "ayam", "buku", "bola", "bunga", "cinta",
    "daun", "dapur", "gajah", "garam", "hujan", "ikan", "jalan",
    "kertas", "kursi", "lampu", "laut", "meja", "mobil", "nasi",
    "pintu", "radio", "rumah", "sapu", "sepatu", "susu", "taman",
    "topi", "ular"
]


def pemain_aktif(session):
    """Daftar pemain yang masih memiliki nyawa, sesuai urutan join."""
    return [
        uid for uid in session["players"]
        if session["lives"].get(uid, 0) > 0
    ]


def cari_pemain_berikutnya(session, user_id):
    """Cari pemain hidup berikutnya berdasarkan urutan join."""
    players = session["players"]
    if not players or user_id not in players:
        return None

    index_sekarang = players.index(user_id)
    for langkah in range(1, len(players) + 1):
        calon = players[(index_sekarang + langkah) % len(players)]
        if session["lives"].get(calon, 0) > 0:
            return calon
    return None


def kata_valid(kata):
    """
    Saringan kosakata bahasa Indonesia menggunakan wordfreq.
    Ini lebih ketat, tetapi tetap bukan kamus resmi/daftar kata eksak.
    """
    kata = kata.lower().strip()

    # Satu kata saja, huruf alfabet, panjang masuk akal.
    if not kata.isalpha() or len(kata) < 2 or len(kata) > PANJANG_KATA_MAKS:
        return False

    # Tolak rangkaian huruf tidak wajar: 5 konsonan berurutan.
    vokal = set("aiueo")
    rentetan_konsonan = 0
    for huruf in kata:
        if huruf not in vokal:
            rentetan_konsonan += 1
            if rentetan_konsonan >= 5:
                return False
        else:
            rentetan_konsonan = 0

    # Ambang dinaikkan agar hanya kata yang cukup dikenal yang lolos.
    return zipf_frequency(kata, "id") >= BATAS_KATA_VALID


def mulai_giliran(session, user_id):
    session["current_player"] = user_id
    session["turn_started_at"] = time.monotonic()


def selesai_jika_satu_pemain(session, get_nama, hasil=""):
    aktif = pemain_aktif(session)
    if len(aktif) <= 1:
        game_sessions.pop(session["chat_id"], None)
        if aktif:
            return (hasil + "\n\n🏆 Pemenang: " + get_nama(aktif[0]) + "!").strip()
        return (hasil + "\n\nGame selesai tanpa pemenang.").strip()
    return None


def format_pemberitahuan_giliran(session, pemain, get_nama):
    """Ringkasan yang ditampilkan setiap kali giliran berpindah."""
    nyawa = session["lives"].get(pemain, 0)
    hati = "❤️" * max(0, nyawa)
    kata_terakhir = session["current_word"].upper()
    huruf_berikutnya = kata_terakhir[-1].upper()
    return (
        f"\n\n 📝 Kata Terakhir: {kata_terakhir}"
        f"\n 🎯 Giliran: {get_nama(pemain)} {hati}"
        f"\n ⏱️ {WAKTU_GILIRAN} detik"
        f"\n ➡️ Jawab dengan kata yang diawali huruf {huruf_berikutnya}"
    )


def lanjutkan_giliran(session, user_id, get_nama, hasil):
    """Majukan giliran; sudden death aktif ketika tersisa tepat dua pemain."""
    pemenang = selesai_jika_satu_pemain(session, get_nama, hasil)
    if pemenang is not None:
        return pemenang

    aktif = pemain_aktif(session)
    if len(aktif) == 2 and not session["sudden_death"]:
        session["sudden_death"] = True
        hasil += "\n\n⚡ SUDDEN DEATH AKTIF! Tersisa 2 pemain. Satu kesalahan atau kehabisan waktu langsung tereliminasi."

    berikutnya = cari_pemain_berikutnya(session, user_id)
    if berikutnya is None:
        game_sessions.pop(session["chat_id"], None)
        return hasil + "\nGame selesai tanpa pemenang."

    mulai_giliran(session, berikutnya)
    return hasil + format_pemberitahuan_giliran(session, berikutnya, get_nama)


def proses_sambung_kata(chat_id, user_id, pesan, get_nama):
    pesan = pesan.strip()
    pesan_lower = pesan.lower()
    session = game_sessions.get(chat_id)

    # Membuat room baru
    if pesan_lower == "!sambungkata create":
        game_sessions[chat_id] = {
            "chat_id": chat_id,
            "status": "waiting",
            "players": [],
            "lives": {},
            "current_word": None,
            "used_words": set(),
            "word_count": 0,
            "sudden_death": False,
            "current_player": None,
            "turn_started_at": None,
        }
        return (
            "🎮 ROOM SAMBUNG KATA DIBUAT!\n\n"
            "❤️ Setiap pemain mendapat 3 nyawa.\n"
            "⏳ Waktu setiap giliran: 30 detik.\n"
            "🔁 Kata yang sudah dipakai tidak boleh diulang.\n"
            "📚 Hanya kata bahasa Indonesia yang bermakna dan cukup dikenal yang diterima.\n\n"
            "Perintah:\n"
            "• !sambungkata join — bergabung\n"
            "• !sambungkata start — mulai\n"
            "• !sambungkata status — cek status\n"
            "• !sambungkata stop — hentikan game"
        )

    if not session:
        if pesan_lower.startswith("!sambungkata"):
            return "⚠️ Belum ada room. Ketik !sambungkata create."
        return None

    # Bergabung. Urutan masuk menentukan urutan giliran.
    if pesan_lower == "!sambungkata join":
        if session["status"] != "waiting":
            return "⚠️ Game sudah dimulai; pemain baru tidak bisa bergabung."
        if user_id in session["players"]:
            return "Kamu sudah bergabung."
        session["players"].append(user_id)
        session["lives"][user_id] = NYAWA_AWAL
        nomor = len(session["players"])
        return (
            f"✅ {get_nama(user_id)} bergabung di urutan ke-{nomor}!\n"
            f"Nyawa: {NYAWA_AWAL} ❤️\n"
            f"Total pemain: {len(session['players'])}"
        )

    if pesan_lower == "!sambungkata start":
        if session["status"] != "waiting":
            return "⚠️ Game sudah dimulai."
        if len(session["players"]) < 2:
            return "⚠️ Minimal 2 pemain harus bergabung."
        session["status"] = "playing"
        kata_awal = random.choice(KATA_AWAL)
        session["current_word"] = kata_awal
        session["used_words"] = {kata_awal}
        session["word_count"] = 0
        session["sudden_death"] = len(pemain_aktif(session)) == 2
        pemain_pertama = pemain_aktif(session)[0]
        mulai_giliran(session, pemain_pertama)
        teks = (
            "🚀 SAMBUNG KATA DIMULAI!\n\n"
            f"Kata awal: {kata_awal.upper()}\n"
            f"Kata berikutnya harus diawali huruf {kata_awal[-1].upper()}.\n"
            f"Kata awal {kata_awal.upper()} juga dianggap sudah dipakai.\n\n"
            f"🎯 Giliran pertama: {get_nama(pemain_pertama)}\n"
            f"⏳ Waktu menjawab: {WAKTU_GILIRAN} detik.\n"
            "❤️ Setiap pemain punya 3 nyawa."
        )
        if session["sudden_death"]:
            teks += "\n\n⚡ SUDDEN DEATH AKTIF karena hanya ada 2 pemain!"
        teks += format_pemberitahuan_giliran(session, pemain_pertama, get_nama)
        return teks

    if pesan_lower == "!sambungkata stop":
        game_sessions.pop(chat_id, None)
        return "🛑 Game Sambung Kata dihentikan."

    if pesan_lower == "!sambungkata status":
        baris = ["📊 STATUS SAMBUNG KATA"]
        for uid in session["players"]:
            nyawa = session["lives"].get(uid, 0)
            status_pemain = "tereliminasi" if nyawa <= 0 else f"{nyawa} ❤️"
            baris.append(f"- {get_nama(uid)}: {status_pemain}")
        if session["status"] == "playing":
            pemain = session.get("current_player")
            if pemain:
                sisa = max(0, WAKTU_GILIRAN - int(
                    time.monotonic() - session["turn_started_at"]
                ))
                baris.extend([
                    f"Kata terakhir: {session['current_word'].upper()}",
                    f"Giliran: {get_nama(pemain)}",
                    f"Sisa waktu: {sisa} detik",
                    f"Sudden death: {'AKTIF' if session['sudden_death'] else 'belum aktif'}",
                ])
        return "\n".join(baris)

    if pesan_lower.startswith("!sambungkata"):
        return (
            "Perintah Sambung Kata:\n"
            "!sambungkata create\n!sambungkata join\n"
            "!sambungkata start\n!sambungkata status\n!sambungkata stop"
        )

    if session["status"] != "playing":
        return None

    aktif = pemain_aktif(session)
    if len(aktif) <= 1:
        return selesai_jika_satu_pemain(session, get_nama)

    pemain_sekarang = session["current_player"]
    sekarang = time.monotonic()

    # Pemeriksaan waktu dilakukan saat bot menerima pesan berikutnya.
    # Jika sudah lewat 30 detik, giliran dianggap gagal.
    if sekarang - session["turn_started_at"] >= WAKTU_GILIRAN:
        nama = get_nama(pemain_sekarang)
        if session["sudden_death"]:
            session["lives"][pemain_sekarang] = 0
            hasil = f"⏰ Waktu {nama} habis saat SUDDEN DEATH. Langsung tereliminasi! 💀"
        else:
            session["lives"][pemain_sekarang] -= 1
            nyawa = session["lives"][pemain_sekarang]
            hasil = f"⏰ Waktu {nama} habis!"
            if nyawa <= 0:
                hasil += "\n💀 Nyawa habis, tereliminasi!"
            else:
                hasil += f"\nSisa nyawa: {nyawa} ❤️"
        return lanjutkan_giliran(session, pemain_sekarang, get_nama, hasil)

    # Pemain lain tidak boleh menjawab sebelum gilirannya.
    if user_id != pemain_sekarang:
        return f"⏳ Belum giliran kamu!\n🎯 Sekarang giliran {get_nama(pemain_sekarang)}."

    kata = pesan_lower
    kata_lama = session["current_word"]
    alasan_salah = None

    if not kata.isalpha() or len(kata) < 2:
        alasan_salah = "Jawaban harus satu kata saja, hanya huruf, minimal 2 huruf."
    elif kata in session["used_words"]:
        alasan_salah = f"Kata '{kata}' sudah pernah dipakai. Kata tidak boleh berulang."
    elif kata[0] != kata_lama[-1]:
        alasan_salah = f"Kata harus diawali huruf {kata_lama[-1].upper()}."
    elif not kata_valid(kata):
        alasan_salah = (
            f"Kata '{kata}' tidak dikenali sebagai kata bahasa Indonesia yang cukup umum. "
            "Gunakan kata yang memiliki arti; jangan gunakan kata asal, singkatan, nama pengguna, atau rangkaian huruf."
        )

    if alasan_salah:
        if session["sudden_death"]:
            session["lives"][user_id] = 0
            hasil = (
                f"❌ Jawaban {get_nama(user_id)} salah!\n{alasan_salah}\n"
                "⚡ Karena SUDDEN DEATH, kamu langsung tereliminasi! 💀"
            )
        else:
            session["lives"][user_id] -= 1
            nyawa = session["lives"][user_id]
            hasil = f"❌ Jawaban {get_nama(user_id)} salah!\n{alasan_salah}"
            if nyawa <= 0:
                hasil += "\n💀 Nyawa habis, kamu tereliminasi!"
            else:
                hasil += f"\nSisa nyawa: {nyawa} ❤️"
        return lanjutkan_giliran(session, user_id, get_nama, hasil)

    # Jawaban valid
    session["current_word"] = kata
    session["used_words"].add(kata)
    session["word_count"] += 1
    hasil = (
        f"✅ {kata.upper()} benar!\n"
        f"Kata selanjutnya harus diawali huruf {kata[-1].upper()}."
    )
    return lanjutkan_giliran(session, user_id, get_nama, hasil)
