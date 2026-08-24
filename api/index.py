from flask import Flask, request, abort
import random

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    ImageMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    MemberJoinedEvent
)

app = Flask(__name__)

# Konfigurasi Token & Secret LINE
CHANNEL_ACCESS_TOKEN = '0ItZ8oKmmMOnK36rH/rfvejjbk747FPnnduh+ut53jovviD4hDaD5IHd3VKqvZNessFKvT+6G3MtJ5ykXL7yX3LqSOdJHJBDco8Q0t5/VJwFJqs0QwwPLKSneZPM9A8IIpxlfatETqvdFLEcLElYmgdB04t89/1O/w1cDnyilFU='
CHANNEL_SECRET = '3e144619ae7414a083b43427f5ed2b53'

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# Database Sederhana di Memory
user_points = {}
SAWNASTY_IMAGE_URL = "https://link-gambar-anda.com/sawnasty-welcome.jpg"

# Route Root agar Vercel & LINE Verify tidak Timeout (Error 404/500)
@app.route("/", methods=['GET'])
def home():
    return "Bot status: Active", 200

# Endpoint Webhook untuk LINE
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK', 200

# Event: Member Baru Bergabung di Grup
@app.event_handler(MemberJoinedEvent)
def handle_member_joined(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        reply_text = (
            "Selamat datang di grup Sawnasty! 🦅\n"
            "Jaga sikap atau Nasty bakal tindak tegas Nih!\n\n"
            "Ketik !help untuk melihat menu perintah."
        )
        
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    ImageMessage(original_content_url=SAWNASTY_IMAGE_URL, preview_image_url=SAWNASTY_IMAGE_URL),
                    TextMessage(text=reply_text)
                ]
            )
        )

# Event: Pesan Teks Masuk
@app.event_handler(MessageEvent, message_content_type=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text.strip()
    user_message_lower = user_message.lower()
    
    # Tambah poin keaktifan
    user_points[user_id] = user_points.get(user_id, 0) + 1
    reply_messages = []

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # 0. Menu Help
        if user_message_lower in ["!help", "!menu"]:
            help_text = (
                "📜 MENU PERINTAH SAUNASTY BOT 📜\n\n"
                "🎮 *GAME & HIBURAN*\n"
                "• !tebak [1-5] : Tebak angka (+10 PTS jika benar)\n"
                "• !dadu : Adu angka dadu lawan Aeto (+5 PTS jika menang)\n"
                "• !tanya [pertanyaan] : Tanya ramalan Ya/Tidak ke Aeto\n\n"
                "👤 *INFORMASI & PROFIL*\n"
                "• !profil : Cek profil LINE & total PTS kamu\n"
                "• !top : Lihat 5 member paling aktif\n"
                "• !admin : Informasi kontak admin\n\n"
                "📢 *FITUR GRUP*\n"
                "• !getcall / !panggil : Panggil semua member di grup"
            )
            reply_messages.append(TextMessage(text=help_text))

        # 1. Profil Admin
        elif user_message_lower == "!admin":
            reply_messages.append(TextMessage(text="👑 ADMIN SAWNASTY 👑\nNama: Admin Sawnasty\nStatus: Active\nContact: @charmingbanget_"))

        # 2. Game Tebak Angka
        elif user_message_lower.startswith("!tebak"):
            parts = user_message.split()
            if len(parts) > 1 and parts[1].isdigit():
                tebakan = int(parts[1])
                angka_rahasia = random.randint(1, 5)
                if tebakan == angka_rahasia:
                    user_points[user_id] += 10
                    reply_messages.append(TextMessage(text=f"🎯 BENAR! Angkanya adalah {angka_rahasia}. Kamu dapat +10 poin!"))
                else:
                    reply_messages.append(TextMessage(text=f"❌ SALAH! Angkanya adalah {angka_rahasia}. Coba lagi sob!"))
            else:
                reply_messages.append(TextMessage(text="Ketik: !tebak [1-5]\nContoh: !tebak 3"))

        # 3. Ramalan Ya/Tidak
        elif user_message_lower.startswith("!tanya"):
            jawaban_list = ["Ya, pasti!", "Gak mungkin, mimpi kamu.", "Kelihatannya iya.", "Tidak sama sekali.", "Bisa jadi sih."]
            reply_messages.append(TextMessage(text=f"🔮 Aeto berkata: {random.choice(jawaban_list)}"))

        # 4. Panggil Member Grup
        elif user_message_lower in ["!getcall", "!panggil"]:
            reply_messages.append(TextMessage(text="📢 PERHATIAN SEMUA MEMBER SAWNASTY! 📢\nAda panggilan darurat di grup! Kumpul sekarang! 🔥"))

        # 5. Cek Profil Pengirim
        elif user_message_lower == "!profil":
            try:
                profile = line_bot_api.get_profile(user_id)
                reply_messages.append(TextMessage(text=f"👤 PROFIL KAMU\nNama LINE: {profile.display_name}\nStatus: {profile.status_message or '-'}\nTotal Poin Keaktifan: {user_points[user_id]} PTS"))
            except Exception:
                reply_messages.append(TextMessage(text="Gagal mengambil data profil."))

        # 6. Respon Chat Otomatis
        elif "sad" in user_message_lower:
            reply_messages.append(TextMessage(text="Hidup memang kadang tidak adil, jadi gausah sad sob."))

        # 7. Leaderboard
        elif user_message_lower == "!top":
            sorted_points = sorted(user_points.items(), key=lambda item: item[1], reverse=True)[:5]
            lb_text = "🏆 LEADERBOARD MEMBER TERAKTIF 🏆\n"
            for rank, (uid, pts) in enumerate(sorted_points, start=1):
                try:
                    p = line_bot_api.get_profile(uid)
                    name = p.display_name
                except Exception:
                    name = uid[:6]
                lb_text += f"{rank}. {name} - {pts} PTS\n"
            reply_messages.append(TextMessage(text=lb_text))

        # 8. Mini RPG Dadu
        elif user_message_lower == "!dadu":
            dadu_user = random.randint(1, 6)
            dadu_bot = random.randint(1, 6)
            
            if dadu_user > dadu_bot:
                hasil = "🎉 Kamu Menang melawan Aeto!"
                user_points[user_id] += 5
            elif dadu_user < dadu_bot:
                hasil = "SKOR! Aeto Menang!"
            else:
                hasil = "🤝 Seri!"

            reply_messages.append(TextMessage(text=f"🎲 DADU BATTLE 🎲\nDadu Kamu: {dadu_user}\nDadu Aeto: {dadu_bot}\n\nHasil: {hasil}"))

        # Kirim Balasan Pesan
        if reply_messages:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=reply_messages
                )
            )
