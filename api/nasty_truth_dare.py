import random

# 50 Pertanyaan Truth (Romance, PDKT, Hubungan & Seru-Seruan Santai)
TRUTH_QUESTIONS = [
    "Siapa orang terakhir yang bikin kamu senyum-senyum sendiri pas lihat HP?",
    "Pernah enggak salting (salah tingkah) parah karena chat dari seseorang? Siapa orangnya?",
    "Apa hal paling memalukan yang pernah kamu lakuin demi menarik perhatian gebetan?",
    "Kalau harus balikan sama mantan, pilih mantan yang mana atau mending jomblo selamanya?",
    "Suka mendekati duluan atau lebih suka didekati duluan?",
    "Apa first impression (kesan pertama) kamu tentang orang yang ada di urutan atas chat kamu sekarang?",
    "Sebutkan satu green flag (sifat baik) yang wajib ada di diri calon pasangan kamu.",
    "Apa red flag (sifat buruk) yang paling bikin kamu langsung ilfil?",
    "Pernah enggak menyimpan foto seseorang diam-diam di galeri HP?",
    "Apa gombalan paling receh tapi ampuh yang pernah kamu dengar atau pakai?",
    "Kalau lagi suka sama orang, tipe yang berani nyatain atau mending memendam dalam diam?",
    "Pernah salah kirim chat (salah kamar) yang bikin malu banget? Ceritakan singkat!",
    "Lagu apa yang paling pas buat menggambarkan kehidupan percintaan kamu sekarang?",
    "Apa hal kecil dari lawan jenis yang bikin kamu langsung merasa tertarik?",
    "Pernah cemburu nggak jelas sama orang yang statusnya bukan siapa-siapa kamu?",
    "Sebutkan satu hal tentang dirimu yang jarang diketahui oleh orang lain.",
    "Kalau gebetan tiba-tiba nanya 'lagi apa?', balasan jujur kamu biasanya apa?",
    "Apa julukan atau panggilan sayang teraneh yang pernah kamu dengar atau pakai?",
    "Pernah enggak pura-pura sibuk biar enggak dibalas chat dari orang tertentu?",
    "Apa mimpi atau khayalan teraneh yang pernah kamu alami tentang seseorang?",
    "Pilih pacar yang humoris tapi cuek, atau serius tapi perhatian banget?",
    "Apa pujian paling berkesan yang pernah kamu dapat dari seseorang?",
    "Kalau hidupmu dijadikan film romantis, kira-kira apa judulnya?",
    "Pernah menyesal enggak karena nolak orang yang suka sama kamu?",
    "Siapa orang di grup ini yang menurut kamu paling jago bikin suasana cair?",
    "Pernah enggak kepikiran buat stalking akun media sosial mantan pakai akun bodong?",
    "Berapa lama waktu terlama kamu pernah menyukai seseorang secara diam-diam (backstreet/crush)?",
    "Apa ketakutan terbesar kamu dalam membangun sebuah hubungan?",
    "Pernah enggak kamu pura-pura menyukai hobi tertentu demi bisa ngobrol sama gebetan?",
    "Kalau diberi kesempatan kencan impian (first date), kamu ingin pergi ke mana?",
    "Apa pengalaman PDKT paling konyol yang pernah kamu alami?",
    "Siapa orang yang paling sering kamu cari saat lagi butuh tempat curhat?",
    "Pernah enggak ketahuan bohong sama orang tua atau teman dekat? Soal apa?",
    "Apa kebiasaan buruk kamu saat lagi emosi atau stres?",
    "Kalau boleh bertukar kehidupan sehari sama anggota grup ini, kamu pilih siapa?",
    "Hal paling kekanak-kanakan apa yang masih sering kamu lakukan sampai sekarang?",
    "Apa kebohongan paling halus yang pernah kamu gunakan untuk membatalkan janji ketemu?",
    "Pernah enggak merasa insecure sama penampilan sendiri? Bagian apa yang paling sering bikin insecure?",
    "Siapa tokoh kartun atau karakter fiktif yang pernah jadi crush masa kecil kamu?",
    "Apa moment paling awkward (canggung) saat pertama kali ketemu seseorang?",
    "Pernah enggak pura-pura paham suatu topik cuma biar enggak kelihatan ketinggalan jaman?",
    "Apa janji ke diri sendiri yang paling sering kamu langgar?",
    "Kalau kamu punya kesempatan minta maaf ke satu orang di masa lalu, ke siapa dan kenapa?",
    "Apa barang teraneh yang pernah kamu beli secara impulsif karena lapar mata?",
    "Pernah enggak baper sama perhatian orang lain padahal dia anggap biasa aja?",
    "Sebutkan satu kebiasaan kamu pas tidur yang jarang orang lain tahu!",
    "Pernah enggak tidak sengaja merusak barang orang lain tapi pura-pura tidak tahu?",
    "Apa hal paling nekat yang pernah kamu lakukan demi teman atau pasangan?",
    "Kalau kamu bisa mengubah satu keputusan di masa lalu, keputusan apa itu?",
    "Sebutkan satu pesan tulus yang ingin kamu sampaikan untuk diri kamu di masa depan!"
]

# 50 Tantangan Dare (Simpel, Lucu, Romantis, dan Aman)
DARE_CHALLENGES = [
    "Kirim satu emoji yang paling menggambarkan status percintaan kamu sekarang di chat.",
    "Buat gombalan maut dalam waktu 10 detik dan ketik di chat.",
    "Ketik 'Aku mau ngaku sesuatu...' tapi setelah itu bilang 'Tapi boong wkwk'.",
    "Kirim chat random ke kontak ke-5 di chat kamu pakai stiker lucu doang.",
    "Nyanyikan atau tuliskan satu baris lagu romantis dengan gaya paling dramatis.",
    "Buat pantun singkat tentang cinta secara dadakan.",
    "Ubah nama tampilan (display name) kamu jadi 'Calon Pacarnya [Nama Bebas]' selama 10 menit.",
    "Kirim foto objek warna pink yang ada di dekat kamu sekarang.",
    "Tulis bio aplikasi kencan (dating app) versi paling lucu dan lebay.",
    "Kirim pesan suara (voice note) atau ketik dengan gaya alay: 'Aku lapar tapi boong'.",
    "Kirim 3 emoji yang mendeskripsikan tipe pacar idaman kamu.",
    "Sebutkan 3 kelebihan/pujian untuk diri sendiri dengan penuh percaya diri.",
    "Kirim stiker atau meme paling gaje yang ada di HP kamu.",
    "Berikan satu pujian tulus untuk orang yang ada di urutan chat teratas kamu.",
    "Chat gebetan atau teman kamu pakai bahasa baku/keraton (contoh: 'Duhai kisanak, sedang apakah dirimu?').",
    "Tulis review bintang 1 sampai 5 untuk dirimu sendiri sebagai teman/pasangan.",
    "Ceritakan mimpi buruk paling konyol yang pernah kamu alami dalam 2 kalimat.",
    "Tiru suara hewan peliharaan (kucing/anjing/ayam) lalu ketik suaranya di chat.",
    "Pilih satu orang di grup untuk diberi gelar fiktif yang lucu (contoh: 'CEO Suka Ngaret').",
    "Jangan pakai huruf 'A' di setiap balasan chat kamu selama 3 pertanyaan ke depan.",
    "Kirim GIF atau gambar meme kucing/hewan lucu ke chat.",
    "Ketik nama kamu pakai siku tangan kamu, lalu kirim hasilnya tanpa edited!",
    "Buat satu kalimat rayuan receh yang bikin orang lain geleng-geleng kepala.",
    "Kirim emoji muka nangis 😭 sebanyak 5 kali berturut-turut tanpa alasan.",
    "Ucapkan terima kasih kepada diri sendiri karena sudah bertahan sampai hari ini dengan gaya puitis.",
    "Gunakan gaya bahasa penyair atau pujangga untuk mengatakan bahwa kamu mau pergi mandi/makan.",
    "Buat pesan singkat berisi ajakan kencan halusinasi ke karakter fiktif pilihanmu.",
    "Sebutkan 3 benda di sekitar kamu lalu buat cerita pendek yang menghubungkan ketiganya.",
    "Ketik kalimat 'Aku adalah master dalam bidang...' lalu lanjutkan dengan keahlian paling konyol.",
    "Berikan ucapan selamat pagi/malam paling manis untuk seluruh anggota di grup.",
    "Ganti foto profil kamu dengan foto objek acak di sekitar kamu selama 5 menit.",
    "Kirim satu kalimat penuh dengan emoji tanpa menggunakan kata-kata sama sekali.",
    "Buat nama panggung keren versi kamu jika seandainya kamu jadi penyanyi dangdut.",
    "Ceritakan pengalaman paling konyol waktu zaman sekolah dalam 3 kalimat.",
    "Ketik teks pujian setinggi langit untuk makanan terakhir yang kamu makan.",
    "Kirim pesan rahasia menggunakan bahasa isyarat emoji dan minta orang lain menebaknya.",
    "Tulis slogan singkat yang unik untuk menggambarkan kepribadian kamu.",
    "Ketik kalimat tanpa spasi sama sekali sepanjang 15 kata!",
    "Tiru gaya bicara komentator bola saat menceritakan aktivitas sederhana yang lagi kamu lakukan.",
    "Sebutkan judul lagu yang menurut kamu judulnya paling unik atau aneh.",
    "Kirim meme yang menurut kamu paling relate sama kehidupan kamu minggu ini.",
    "Tulis pesan motivasi singkat seolah-olah kamu adalah seorang motivator terkenal.",
    "Buat tebak-tebakan receh di chat dan tunggu sampai ada yang menjawab.",
    "Ketik balasan chat berikutnya menggunakan CAPS LOCK (huruf kapital semua) seolah lagi marah.",
    "Ceritakan plot film favoritmu tapi jelaskan dengan cara yang sangat buruk/konyol.",
    "Buat janji konyol yang harus kamu tepati dalam kurun waktu 24 jam ke depan.",
    "Sebutkan 3 kata pertama yang terlintas di pikiranmu saat melihat foto profil orang di atas kamu.",
    "Tulis pesan singkat seolah-olah kamu sedang diwawancarai oleh media terkenal.",
    "Ketik permintaan maaf secara melamun/dramatis kepada HP kamu karena sering dijatuhkan.",
    "Kirim pesan salam keikutsertaan penuh semangat untuk ronde permainan berikutnya!"
]

def proses_truth_dare(pesan: str):
    """Memproses perintah Truth or Dare. Mengembalikan teks balasan atau None."""
    if not isinstance(pesan, str):
        return None

    command = pesan.strip().lower()

    if command in ("!tod help", "!tod bantuan", "!tod menu"):
        return (
            "🎲 TRUTH OR DARE — NASTY POTTER\n\n"
            "!tod    → Pilih Truth atau Dare secara acak\n"
            "!truth  → Dapat pertanyaan Truth (50 Pertanyaan)\n"
            "!dare   → Dapat tantangan Dare (50 Tantangan)\n\n"
            "Tema: Romance, PDKT, hubungan, dan hal-hal seru santai. "
            "Boleh di-skip jika membuat tidak nyaman."
        )

    if command == "!tod":
        jenis = random.choice(("truth", "dare"))
        if jenis == "truth":
            return "💗 TRUTH TIME!\n" + random.choice(TRUTH_QUESTIONS)
        return "🔥 DARE TIME!\n" + random.choice(DARE_CHALLENGES)

    if command == "!truth":
        return "💗 TRUTH TIME!\n" + random.choice(TRUTH_QUESTIONS)

    if command == "!dare":
        return "🔥 DARE TIME!\n" + random.choice(DARE_CHALLENGES)

    return None