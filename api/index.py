import os
import random
from datetime import datetime, timedelta
from flask import Flask, request, abort
from sambung_kata import proses_sambung_kata
from tarot_game import proses_tarot
from whitelist_admin import cek_izin_admin



from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage,
    FlexMessage,
    FlexContainer
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    MemberJoinedEvent
)

app = Flask(__name__)

# 1. Token & Secret LINE (Disarankan menggunakan Environment Variables)
CHANNEL_ACCESS_TOKEN = os.getenv(
    "LINE_CHANNEL_ACCESS_TOKEN",
    "ahyfh8AWxAywi+kMmsrtAmyLjqaO7bNF+xkd1647BSl9+N/t8cmgD3pvXlw8fZBCssFKvT+6G3MtJ5ykXL7yX3LqSOdJHJBDco8Q0t5/VJxWvfrddzFFFqy+SbpYMXiQ2Nouux6adOw3LJXwa+bR0gdB04t89/1O/w1cDnyilFU="
)
CHANNEL_SECRET = os.getenv(
    "LINE_CHANNEL_SECRET",
    "2a0bdf110f1cb36d25d5bc972a6722e9"
)

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


# Database Sederhana di Memory
user_points = {}  # {user_id: points}
user_status = {}  # {user_id: {"status": "off", "alasan": "...", "waktu_off": ...}}

# Database Game Quiz
quiz_state = {
    "is_active": False,
    "players": set(),
    "current_question_index": 0,
    "questions": [
         {"q": "Monumen Nasional (Monas) terletak di kota apa?", "a": "jakarta"},
        {"q": "Candi Borobudur peninggalan dari agama apa?", "a": ["buddha","budha"]},
        {"q": "Berapa hasil dari 12 x 12?", "a": "144"},
        {"q": "Ibu kota dari negara Jepang adalah?", "a": "tokyo"},
        {"q": "Hewan darat terbesar di dunia adalah?", "a": "gajah"},
        {"q": "Siapakah proklamator kemerdekaan Indonesia selain Moh. Hatta?", "a": ["soekarno"]},
        {"q": "Planet terdekat dari matahari adalah?", "a": "merkurius"},
        {"q": "Mata uang negara Inggris adalah?", "a": "poundsterling"},
        {"q": "Lagu kebangsaan Indonesia adalah?", "a": "indonesia raya"},
        {"q": "Benua terbesar di dunia adalah benua?", "a": "asia"},
        {"q": "Alat musik petik khas NTT adalah?", "a": "sasando"},
        {"q": "Penemu bola lampu adalah Thomas Alva...?", "a": "edison"},
        {"q": "Jumlah provinsi di Indonesia saat ini adalah?", "a": "38"},
        {"q": "Candi Prambanan dibangun untuk menyembah dewa apa dalam agama Hindu?", "a": "siwa"},
        {"q": "Unsur kimia dengan simbol 'O' adalah?", "a": "oksigen"},
        {"q": "Samudra terbesar di dunia adalah samudra?", "a": "pasifik"},
        {"q": "Berapa hasil dari 15 + 25 x 2?", "a": "65"},
        {"q": "Ibu kota negara Prancis adalah?", "a": "paris"},
        {"q": "Mamalia laut terbesar di dunia adalah?", "a": "paus biru"},
        {"q": "Sila pertama Pancasila dilambangkan dengan simbol?", "a": "bintang"},
        {"q": "Negara yang dijuluki sebagai Negeri Tirai Bambu adalah?", "a": ["cina","china"]},
        {"q": "Senjata tradisional khas Jawa Barat adalah?", "a": "kujang"},
        {"q": "Organ tubuh manusia yang berfungsi memompa darah adalah?", "a": "jantung"},
        {"q": "Sungai terpanjang di Indonesia adalah sungai?", "a": "kapuas"},
        {"q": "Bahasa resmi negara Australia adalah bahasa?", "a": "inggris"},
        {"q": "Penemu pesawat terbang adalah Wright...?", "a": "bersaudara"},
        {"q": "Bahan bakar untuk pesawat terbang disebut?", "a": "avtur"},
        {"q": "Garis khayal yang membagi bumi menjadi dua bagian utara dan selatan adalah?", "a": "khatulistiwa"},
        {"q": "Kota yang dijuluki sebagai Kota Hujan di Indonesia adalah?", "a": "bogor"},
        {"q": "Siapa penulis novel Laskar Pelangi?", "a": "andrea hirata"},
        {"q": "Berapa jumlah kaki pada seekor laba-laba?", "a": "8"},
        {"q": "Gas yang dihirup manusia saat bernapas adalah?", "a": "oksigen"},
        {"q": "Gas yang dikeluarkan manusia saat menghembuskan napas adalah?", "a": "karbondioksida"},
        {"q": "Mata uang negara Thailand adalah?", "a": "baht"},
        {"q": "Ibu kota dari negara Australia adalah?", "a": "canberra"},
        {"q": "Tari Pendet berasal dari daerah?", "a": "bali"},
        {"q": "Ibu kota Provinsi Jawa Tengah adalah?", "a": "semarang"},
        {"q": "Gunung tertinggi di pulau Jawa adalah gunung?", "a": "semeru"},
        {"q": "Zat hijau daun pada tumbuhan disebut?", "a": "klorofil"},
        {"q": "Rumah adat khas Papua disebut?", "a": "honai"},
        {"q": "Berapa hasil akar kuadrat dari 81?", "a": "9"},
        {"q": "Satelit alami bumi adalah?", "a": "bulan"},
        {"q": "Candi pemandian kuno atau candi Hindu terbesar di Indonesia adalah?", "a": "prambanan"},
        {"q": "Kota tempat lahirnya Pancasila atau tempat pengasingan Soekarno di NTT adalah?", "a": "ende"},
        {"q": "Mata uang negara Malaysia adalah?", "a": "ringgit"},
        {"q": "Ibu kota dari negara Korea Selatan adalah?", "a": "seoul"},
        {"q": "Alat untuk mengukur suhu tubuh adalah?", "a": "termometer"},
        {"q": "Bapak Pendidikan Nasional Indonesia adalah?", "a": ["ki hadjar dewantara","ki hajar dewantara"]},
        {"q": "Hari Kemerdekaan Indonesia diperingati setiap bulan?", "a": "agustus"},
        {"q": "Sumpah Pemuda dibacakan pada tahun 19...?", "a": "28"},
        {"q": "Hewan yang memiliki kemampuan mengubah warna kulitnya adalah?", "a": "bunglon"},
        {"q": "Unsur kimia dengan simbol 'Au' adalah?", "a": "emas"},
        {"q": "Pencipta lagu Indonesia Raya adalah W.R. ...?", "a": "soepratman"},
        {"q": "Ibu kota dari negara Jerman adalah?", "a": "berlin"},
        {"q": "Proses pembuatan makanan pada tumbuhan hijau disebut?", "a": "fotosintesis"},
        {"q": "Senjata khas suku Dayak adalah?", "a": "mandau"},
        {"q": "Planet terbesar di tata surya kita adalah?", "a": ["yupiter","jupiter"]},
        {"q": "Berapa sudut siku-siku dalam derajat?", "a": "90"},
        {"q": "Tari Saman berasal dari provinsi?", "a": "aceh"},
        {"q": "Ibu kota dari negara Italia adalah?", "a": "roma"},
        {"q": "Negara terkecil di dunia adalah?", "a": "vatikan"},
        {"q": "Hewan yang hidup di dua alam (darat dan air) disebut?", "a": "amfibi"},
        {"q": "Rumah adat khas Sumatra Barat adalah rumah?", "a": "gadang"},
        {"q": "Mata uang negara Jepang adalah?", "a": "yen"},
        {"q": "Bumi berputar pada porosnya disebut?", "a": "rotasi"},
        {"q": "Pergerakan bumi mengelilingi matahari disebut?", "a": "revolusi"},
        {"q": "Patung Merlion merupakan ikon dari negara?", "a": ["singapura","singapore"]},
        {"q": "Gudeg adalah makanan khas dari kota?", "a": "yogyakarta"},
        {"q": "Berapa jumlah pemain dalam satu tim sepak bola di lapangan?", "a": "11"},
        {"q": "Alat musik angklung berasal dari provinsi?", "a": "jawa barat"},
        {"q": "Vitamin yang banyak terkandung dalam buah jeruk adalah vitamin?", "a": "c"},
        {"q": "Danau terbesar di Indonesia adalah danau?", "a": "toba"},
        {"q": "Siapa presiden pertama Republik Indonesia?", "a": ["soekarno","sukarno"]},
        {"q": "Siapa wakil presiden pertama Republik Indonesia?", "a": ["mohammad hatta","muh hatta"]},
        {"q": "Ibu kota negara Arab Saudi adalah?", "a": "riyadh"},
        {"q": "Hewan pemakan daging disebut?", "a": "karnivora"},
        {"q": "Hewan pemakan tumbuhan disebut?", "a": "herbivora"},
        {"q": "Hewan pemakan segala disebut?", "a": "omnivora"},
        {"q": "Mata uang negara Amerika Serikat adalah?", "a": "dollar"},
        {"q": "Berapa hasil dari 50 / 2 + 10?", "a": "35"},
        {"q": "Ibu kota dari provinsi Jawa Timur adalah?", "a": "surabaya"},
        {"q": "Senjata tradisional suku Aborigin adalah?", "a": "bumerang"},
        {"q": "Kota terluat di ujung barat Indonesia adalah?", "a": "sabang"},
        {"q": "Kota di ujung timur Indonesia adalah?", "a": "merauke"},
        {"q": "Lagu daerah 'Ampar Ampar Pisang' berasal dari Kalimantan...?", "a": "selatan"},
        {"q": "Penemu telepon adalah Alexander Graham...?", "a": "bell"},
        {"q": "Ibu kota dari negara Mesir adalah?", "a": "kairo"},
        {"q": "Monumen Menara Eiffel terletak di negara?", "a": "prancis"},
        {"q": "Pahlawan wanita yang memperjuangkan hak perempuan Indonesia adalah R.A. ...?", "a": "kartini"},
        {"q": "Alat untuk mengukur gempa bumi disebut?", "a": "seismograf"},
        {"q": "Batu batuan cair yang keluar dari gunung berapi disebut?", "a": "lava"},
        {"q": "Samudra tersempit di dunia adalah samudra?", "a": "arktik"},
        {"q": "Senyawa kimia air memiliki rumus?", "a": "h2o"},
        {"q": "Ibu kota dari provinsi Jawa Barat adalah?", "a": "bandung"},
        {"q": "Candi Muaro Jambi terletak di provinsi?", "a": "jambi"},
        {"q": "Peristiwa perubahan wujud zat dari padat menjadi gas disebut?", "a": "menyublim"},
        {"q": "Jumlah warna dalam pelangi dasar adalah?", "a": "7"},
        {"q": "Simbol sila ke-5 Pancasila adalah padi dan...?", "a": "kapas"},
        {"q": "Pakaian adat khas Jawa untuk pria yang dipasang di kepala disebut?", "a": "blangkon"},
        {"q": "Seni melipat kertas dari Jepang disebut?", "a": "origami"}

    ]
}

# 2. URL Gambar Wajib Direct Link (SSL/HTTPS)
SAWNASTY_IMAGE_URL = "https://via.placeholder.com/1040x1040.png?text=Satpam+Nasty" 

@app.route("/", methods=["GET"])
def home():
    return "Nasty Potter Bot is Online! 🧙‍♂️🔥"

@app.route("/callback", methods=["GET", "POST"])
def callback():
    if request.method == "GET":
        return "Webhook endpoint is active!", 200

    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    if not signature:
        return 'OK', 200

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        app.logger.error(f"Callback Error: {e}")
        return 'OK', 200

    return 'OK', 200

# --- WELCOME MESSAGE ---
@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    if event.reply_token in ["00000000000000000000000000000000", "ffffffffffffffffffffffffffffffff"]:
        return

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        reply_text = "Welcome Manizzz, yang ganteng gk welcome! 🦅\nJaga sikap atau Nasty bakal tindak tegas nih!\nKetik !help untuk melihat menu perintah."
        
        messages_to_send = [TextMessage(text=reply_text)]
        if SAWNASTY_IMAGE_URL.startswith(""):
            messages_to_send.insert(0, ImageMessage(original_content_url=SAWNASTY_IMAGE_URL, preview_image_url=SAWNASTY_IMAGE_URL))

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=messages_to_send
            )
        )

# --- FUNGSI PENGOLAH PESAN TULISAN ---
@handler.add(MessageEvent, TextMessageContent)
def handle_message(event):
    if event.reply_token in ["00000000000000000000000000000000", "ffffffffffffffffffffffffffffffff"]:
        return

    user_id = event.source.user_id
    user_message = event.message.text.strip()
    user_message_lower = user_message.lower()
    print(f"User ID LINE: {user_id}")
    print("" \
    "abc")

    
    # Penambahan poin keaktifan per chat
    user_points[user_id] = user_points.get(user_id, 0) + 1
    reply_messages = []

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        group_id = getattr(event.source, 'group_id', None)

        def get_user_name(uid):
            if group_id:
                try:
                    return line_bot_api.get_group_member_profile(
                        group_id, uid
                    ).display_name
                except Exception:
                    pass

            try:
                return line_bot_api.get_profile(uid).display_name
            except Exception:
                return f"User ({uid[:5]})"

        # --- WHITELIST PERINTAH ADMIN ---
        pesan_penolakan = cek_izin_admin(
            user_id=user_id,
            pesan=user_message,
            get_nama=get_user_name
        )

        if pesan_penolakan is not None:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=pesan_penolakan)]
                )
            )
            return


        # --- DETEKSI MENTION USER OFF ---
        if hasattr(event.message, 'mention') and event.message.mention:
            for mentionee in event.message.mention.mentionees:
                target_uid = getattr(mentionee, 'user_id', None)
                if target_uid and target_uid in user_status and user_status[target_uid].get("status") == "off":
                    target_name = get_user_name(target_uid)
                    alasan = user_status[target_uid].get("alasan", "-")
                    waktu_off = user_status[target_uid].get("waktu_off")
                    
                    durasi_str = ""
                    if waktu_off:
                        selisih = datetime.now() - waktu_off
                        total_detik = int(selisih.total_seconds())
                        jam, sisa = divmod(total_detik, 3600)
                        menit, detik = divmod(sisa, 60)
                        if jam > 0:
                            durasi_str = f"{jam} jam {menit} menit"
                        elif menit > 0:
                            durasi_str = f"{menit} menit"
                        else:
                            durasi_str = f"{detik} detik"
                    
                    teks_durasi = f"\n⏱️ Durasi OFF: {durasi_str}" if durasi_str else ""
                    reply_messages.append(TextMessage(
                        text=f"🔴 *INFORMASI STATUS*\nUser **{target_name}** sedang **OFF**.\n📝 Alasan: {alasan}{teks_durasi}"
                    ))

        # --- STATUS OFF & AUTOMATIC ON ---
        if user_id in user_status and user_status[user_id].get("status") == "off":
            if not user_message_lower.startswith("!off"):
                user_name = get_user_name(user_id)
                waktu_off = user_status[user_id].get("waktu_off")
                durasi_str = ""
                if waktu_off:
                    selisih = datetime.now() - waktu_off
                    total_detik = int(selisih.total_seconds())
                    jam, sisa = divmod(total_detik, 3600)
                    menit, detik = divmod(sisa, 60)
                    if jam > 0:
                        durasi_str = f"{jam} jam {menit} menit"
                    elif menit > 0:
                        durasi_str = f"{menit} menit"
                    else:
                        durasi_str = f"{detik} detik"

                del user_status[user_id]
                teks_durasi = f" (Kamu OFF selama {durasi_str})" if durasi_str else ""
                reply_messages.append(TextMessage(text=f"🟢 Welcome back {user_name}! Status kamu otomatis kembali *ON*{teks_durasi}."))

        if user_message_lower.startswith("!off"):
            alasan = user_message[4:].strip()
            if alasan:
                user_name = get_user_name(user_id)
                user_status[user_id] = {
                    "status": "off", 
                    "alasan": alasan, 
                    "waktu_off": datetime.now()
                }
                reply_messages.append(TextMessage(text=f"🔴 Status {user_name} sekarang *OFF*.\nAlasan: {alasan}\n\n*Catatan:* Ketik pesan apapun untuk otomatis ON."))
            else:
                reply_messages.append(TextMessage(text="Ketik: !off [alasan kamu]\nContoh: !off Mau tidur dulu bro"))

        # --- PERSONA SATPAM ---
        elif "bot" in user_message_lower:
            bot_responses = [
                "Sembarangan manggil bot! Gue Nasty, SATPAM resmi yang jaga ketertiban di grup ini! 👮‍♂️🔥",
                "Heh! Panggil yang sopan dikit kek, gue ini Satpam Nasty yang lagi tugas jaga pos! 🚨",
                "Siapa yang panggil-panggil bot?! Ada yang bikin ulah di grup ini? Lapor ke Nasty sekarang! 👮‍♂️⚡",
                "Bot bot bot... Muka garang gini dipanggil bot! Panggil Pak Satpam Nasty! 🦅🔥",
                "Hadir! Ada razia apa nih? Oh cuma panggil-panggil doang. Jangan buat keonaran ya! 👮‍♂️",
                "Nasty di sini! Mau lapor kejadian atau cuma mau ngajak ronda? ☕👮‍♂️",
                "Gue bukan sekadar bot biasa, gue Satpam Nasty penjaga kedamaian grup ini! 🛡️✨",
                "Panggil bot lagi gue tilang poin lu! Panggil Pak Nasty biar kerenan dikit! 🚨👮‍♂️",
                "Mata gue memantau chat kalian 24 jam! Jangan panggil-panggil kalau nggak penting! 🦅👀"

            ]
            reply_messages.append(TextMessage(text=random.choice(bot_responses)))

        elif user_message_lower in ["!siapa", "!siapanasty"]:
            reply_messages.append(TextMessage(
                text="Gue Nasty Potter! Satpam jaga di grup ini. Tugas gue memantau kalian agar gak bikin ulah. Ada masalah? Ketik !lapor."
            ))

        # --- FITUR GAME QUIZ ---
        elif user_message_lower == "!join":
            user_name = get_user_name(user_id)
            if user_id in quiz_state["players"]:
                reply_messages.append(TextMessage(text=f"⚠️ {user_name}, kamu sudah terdaftar di game quiz!"))
            else:
                quiz_state["players"].add(user_id)
                reply_messages.append(TextMessage(text=f"✅ {user_name} berhasil bergabung ke Quiz!\nTotal Pemain: {len(quiz_state['players'])} orang.\nKetik !mulai jika siap."))

        elif user_message_lower == "!mulai":
            if quiz_state["is_active"]:
                reply_messages.append(TextMessage(text="⚠️ Game quiz sedang berjalan!"))
            elif len(quiz_state["players"]) == 0:
                reply_messages.append(TextMessage(text="❌ Belum ada pemain! Ketik !join terlebih dahulu untuk bergabung."))
            else:
                quiz_state["is_active"] = True
                quiz_state["current_question_index"] = 0
                random.shuffle(quiz_state["questions"])
                q = quiz_state["questions"][0]["q"]
                reply_messages.append(TextMessage(text=f"🎮 *GAME QUIZ DIMULAI!* 🎮\n\nPertanyaan 1:\n{q}\n\nJawab langsung di chat ini!"))

        elif user_message_lower in ["!next", "!lanjut"]:
            if not quiz_state["is_active"]:
                reply_messages.append(TextMessage(text="❌ Game quiz belum dimulai. Ketik !join lalu !mulai."))
            else:
                quiz_state["current_question_index"] += 1
                if quiz_state["current_question_index"] < len(quiz_state["questions"]):
                    idx = quiz_state["current_question_index"]
                    q = quiz_state["questions"][idx]["q"]
                    reply_messages.append(TextMessage(text=f"❓ Pertanyaan {idx + 1}:\n{q}"))
                else:
                    quiz_state["is_active"] = False
                    quiz_state["players"].clear()
                    reply_messages.append(TextMessage(text="🎉 *GAME QUIZ SELESAI!* 🎉\nSemua pertanyaan telah dijawab. Terima kasih sudah bermain!"))

        elif user_message_lower in ["!stopquiz", "!berakhir"]:
            if quiz_state["is_active"] or len(quiz_state["players"]) > 0:
                quiz_state["is_active"] = False
                quiz_state["players"].clear()
                quiz_state["current_question_index"] = 0
                reply_messages.append(TextMessage(text="🛑 Game quiz telah dihentikan secara paksa."))
            else:
                reply_messages.append(TextMessage(text="Sesi quiz sedang tidak aktif."))

        # Deteksi Jawaban Quiz
        elif quiz_state["is_active"] and user_id in quiz_state["players"]:
            idx = quiz_state["current_question_index"]
            kunci_jawaban = quiz_state["questions"][idx]["a"]

            if isinstance(kunci_jawaban, list):
                is_correct = user_message_lower in [k.lower() for k in kunci_jawaban]
            else:
                is_correct = user_message_lower == kunci_jawaban.lower()

            if is_correct:
                user_name = get_user_name(user_id)
                user_points[user_id] = user_points.get(user_id, 0) + 10
                
                quiz_state["current_question_index"] += 1
                if quiz_state["current_question_index"] < len(quiz_state["questions"]):
                    next_idx = quiz_state["current_question_index"]
                    next_q = quiz_state["questions"][next_idx]["q"]
                    reply_messages.append(TextMessage(
                        text=f"🎉 *BENAR!* Jawaban oleh {user_name} tepat! (+10 PTS)\n\n❓ Pertanyaan {next_idx + 1}:\n{next_q}"
                    ))
                else:
                    quiz_state["is_active"] = False
                    quiz_state["players"].clear()
                    reply_messages.append(TextMessage(
                        text=f"🎉 *BENAR!* Jawaban oleh {user_name} tepat! (+10 PTS)\n\n🏆 *QUIZ SELESAI!* Semua pertanyaan telah dijawab!"
                    ))

        # --- COMMAND REGULER ---
        if not reply_messages:
            if user_message_lower.startswith("!lapor"):
                aduan = user_message[6:].strip()
                if aduan:
                    reply_messages.append(TextMessage(
                        text=f"📝 *LAPORAN DITERIMA SATPAM NASTY*\n\nLaporan: '{aduan}'\n\nTenang, laporan sudah dicatat di buku piket."
                    ))
                else:
                    reply_messages.append(TextMessage(text="Ketik: !lapor [keluhan kamu]\nContoh: !lapor grup sepi banget nih"))

            elif user_message_lower in ["!help", "!menu"]:
                help_text = (
                     "🚨 POS JAGA SATPAM NASTY 🚨\n"
                    "Ketik perintah di bawah untuk berinteraksi:\n\n"
                    "🎯 *GAME QUIZ*\n"
                    "• !join : Bergabung ke sesi quiz\n"
                    "• !mulai : Memulai pertanyaan quiz\n"
                    "• !next : Lanjut ke pertanyaan berikutnya\n"
                    "• !stopquiz : Menghentikan sesi quiz\n\n"
                    "🎮 *GAME & HIBURAN*\n"
                    "• !sambungkata create : Memulai game sambung kata  (+PTS)\n"
                    "• !tarot : Memulai game Tarot\n"
                    "• !tanya [pertanyaan] : Tanya ramalan Ya/Tidak ke Nasty\n\n"
                    "👮‍♂️ *STATUS & POS SATPAM*\n"
                    "• !off [alasan] : Set status kamu sedang off/sibuk\n"
                    "• !lapor [aduan] : Kirim laporan/keluhan warga ke pos jaga\n"
                    "• !siapa : Cek siapa identitas Satpam Nasty sebenarnya\n\n"
                    "👤 *INFORMASI & PROFIL*\n"
                    "• !profil : Cek profil LINE & total PTS keaktifan kamu\n"
                    "• !top : Lihat 5 warga paling aktif di grup\n"
                    "• !admin : Kontak Komandan / Admin utama"

                )
                reply_messages.append(TextMessage(text=help_text))

            elif user_message_lower == "!admin":
                reply_messages.append(TextMessage(text="👑 ADMIN SAWNASTY 👑\nNama: Owen Pembaik\nStatus: Active\nContact: line.me/ti/p/~charmingbanget_"))

            elif user_message_lower.startswith("!tanya"):
                jawaban_list = ["Ya, pasti!", "Gak mungkin, mimpi kamu.", "Kelihatannya iya.", "Tidak sama sekali.", "Bisa jadi sih."]
                reply_messages.append(TextMessage(text=f"🔮 Nasty berkata: {random.choice(jawaban_list)}"))

            elif user_message_lower in ["!getcall", "!panggil","@all"]:
                reply_messages.append(TextMessage(text="📢 PERHATIAN SEMUA MEMBER! 📢\nAda panggilan darurat di grup!"))

            elif user_message_lower == "!profil":
                user_name = get_user_name(user_id)
                st = "OFF" if (user_id in user_status and user_status[user_id]["status"] == "off") else "ON"
                reply_messages.append(TextMessage(text=f"👤 PROFIL KAMU\nNama LINE: {user_name}\nStatus: {st}\nTotal Poin Keaktifan: {user_points.get(user_id, 0)} PTS"))

            elif user_message_lower == "!top":
                sorted_points = sorted(
                    user_points.items(),
                    key=lambda item: item[1],
                    reverse=True
                )[:5]

                lb_text = "🏆 LEADERBOARD MEMBER TERAKTIF 🏆\\n\\n"

                if not sorted_points:
                    lb_text += "Belum ada data keaktifan member."
                else:
                    for rank, (uid, pts) in enumerate(sorted_points, start=1):
                        name = get_user_name(uid)
                        lb_text += f"{rank}. {name} - {pts} PTS\\n"

                reply_messages.append(TextMessage(text=lb_text))

            # --- FITUR JODOH SAWNASTY (FLEX MESSAGE) ---\n            elif user_message_lower in ["!jodoh", "!jodohku", "!match"]:
                user_name = get_user_name(user_id)

                # 1. Ambil semua ID user yang pernah interaksi/terdata (selain diri sendiri)
                available_members = [uid for uid in user_points.keys() if uid != user_id]

                # 2. Jika ada member lain di data, pilih acak. Jika tidak ada, gunakan default fallback
                if available_members:
                    partner_uid = random.choice(available_members)
                    partner_name = get_user_name(partner_uid)
                else:
                    # Fallback kalau belum ada member lain yang pernah chat di grup
                    partner_candidates = ["Siti Ronda", "Nabila Pos Jaga", "Gwen Sawnasty", "Luna Phoenix"]
                    partner_name = random.choice(partner_candidates)
                
                kecocokan = random.randint(30, 100)
                future_days = random.randint(300, 3650)
                tgl_nikah = (datetime.now() + timedelta(days=future_days)).strftime("%d-%m-%Y")
                lokasi_first_date = random.choice(["Pos Ronda Sawnasty", "Kantor Satpam", "Kantin Grup", "Warkop Aceng","Bioskop","Cafe Romatis","Pantai","Gedung DPR","RSJ"])
                kekayaan = random.choice(["Rp 100 Ribu","Rp 500 Ribu","Rp 1 Juta","Rp 10 Ribu","Rp 10 Juta", "Rp 50 Juta", "Rp 1 Miliar"])

                flex_contents = {
                    "type": "bubble",
                    "header": {
                        "type": "box",
                        "layout": "vertical",
                        "backgroundColor": "#1A1A1A",
                        "contents": [
                            {"type": "text", "text": "🦅 MATCHMAKER SAWNASTY 🦅", "weight": "bold", "color": "#E63946", "size": "sm", "align": "center"},
                            {"type": "text", "text": "TAKDIR SATPAM NASTY", "weight": "bold", "color": "#FFD700", "size": "lg", "align": "center", "margin": "xs"}
                        ]
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "backgroundColor": "#111111",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "margin": "md",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {"type": "text", "text": "👤 USER", "color": "#AAAAAA", "size": "xs", "align": "center"},
                                            {"type": "text", "text": str(user_name), "color": "#FFFFFF", "weight": "bold", "size": "sm", "align": "center", "wrap": True}
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {"type": "text", "text": f"{kecocokan}%", "color": "#FFD700", "weight": "bold", "size": "xl", "align": "center"},
                                            {"type": "text", "text": "MATCH", "color": "#E63946", "weight": "bold", "size": "xxs", "align": "center"}
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {"type": "text", "text": "❤️ JODOH", "color": "#AAAAAA", "size": "xs", "align": "center"},
                                            {"type": "text", "text": str(partner_name), "color": "#FFFFFF", "weight": "bold", "size": "sm", "align": "center", "wrap": True}
                                        ]
                                    }
                                ]
                            },
                            {"type": "separator", "margin": "lg", "color": "#333333"},
                            {
                                "type": "box",
                                "layout": "vertical",
                                "margin": "lg",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "contents": [
                                            {"type": "text", "text": "📅 Tgl Nikah", "color": "#AAAAAA", "size": "xs", "flex": 2},
                                            {"type": "text", "text": str(tgl_nikah), "color": "#FFFFFF", "size": "xs", "flex": 3, "align": "right"}
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "contents": [
                                            {"type": "text", "text": "📍 First Date", "color": "#AAAAAA", "size": "xs", "flex": 2},
                                            {"type": "text", "text": str(lokasi_first_date), "color": "#FFFFFF", "size": "xs", "flex": 3, "align": "right"}
                                        ]
                                    },
                                    {
                                        "type": "box",
                                        "layout": "baseline",
                                        "contents": [
                                            {"type": "text", "text": "💰 Kekayaan", "color": "#AAAAAA", "size": "xs", "flex": 2},
                                            {"type": "text", "text": str(kekayaan), "color": "#FFFFFF", "size": "xs", "flex": 3, "align": "right"}
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
                
                try:
                    container_obj = FlexContainer.from_dict(flex_contents)
                    reply_messages.append(FlexMessage(alt_text="Hasil Ramalan Jodoh", contents=container_obj))
                except Exception as err:
                    fallback_text = (
                        f"🦅 *RAMALAN JODOH SAWNASTY* 🦅\n\n"
                        f"👤 User: {user_name}\n"
                        f"❤️ Jodoh: {partner_name}\n"
                        f"🔥 Kecocokan: {kecocokan}%\n"
                        f"📅 Tgl Nikah: {tgl_nikah}\n"
                        f"📍 First Date: {lokasi_first_date}\n"
                        f"💰 Kekayaan: {kekayaan}"
                    )
                    reply_messages.append(TextMessage(text=fallback_text))
                    
        # --- INTEGRASI GAME TAROT ---
        if not reply_messages:
            balasan_tarot = proses_tarot(
                chat_id=group_id or user_id,
                user_id=user_id,
                pesan=user_message,
                get_nama=get_user_name
            )

            if balasan_tarot is not None:
                reply_messages.append(TextMessage(text=balasan_tarot))

        # --- INTEGRASI GAME SAMBUNG KATA ---
        if not reply_messages:
            chat_id = group_id or user_id

            balasan_sambung_kata = proses_sambung_kata(
                chat_id=chat_id,
                user_id=user_id,
                pesan=user_message,
                get_nama=get_user_name
            )

            if balasan_sambung_kata is not None:
                reply_messages.append(
                    TextMessage(text=balasan_sambung_kata)
                )

        # Kirim Balasan jika ada pesan dalam array
        if reply_messages:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=reply_messages[:5]  # Maksimal LINE hanya memperbolehkan 5 pesan per balasan
                )
            )

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
