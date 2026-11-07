import random

# Truth: campuran romance, PDKT, hubungan, rahasia ringan, dan pertanyaan seru.
TRUTH_QUESTIONS = [
    "Siapa orang terakhir yang bikin kamu senyum-senyum sendiri saat melihat notifikasi?",
    "Pernah nggak kamu punya crush sama teman sendiri? Ceritakan sedikit kalau nyaman.",
    "Apa hal sederhana yang bisa bikin kamu langsung tertarik sama seseorang?",
    "Kamu lebih suka didekati duluan atau jadi pihak yang memulai?",
    "Pernah pura-pura biasa saja padahal sebenarnya salting? Karena apa?",
    "Menurutmu, first impression kamu tentang orang di grup ini biasanya akurat atau sering meleset?",
    "Apa green flag yang paling kamu cari dari seseorang?",
    "Apa red flag yang langsung bikin kamu kehilangan ketertarikan?",
    "Pilih mana: hubungan yang penuh kejutan atau hubungan yang tenang dan konsisten?",
    "Pernah menyimpan chat seseorang karena terlalu senang membacanya lagi?",
    "Apa lagu yang paling menggambarkan kisah cinta atau kehidupanmu sekarang?",
    "Kalau bisa mengulang satu momen bersama seseorang, momen apa yang ingin kamu ulang?",
    "Apa bentuk perhatian kecil yang paling berkesan buatmu?",
    "Pernah salah mengartikan kebaikan seseorang sebagai kode? Ceritakan singkat.",
    "Kamu tipe yang mudah jatuh cinta atau butuh waktu lama untuk yakin?",
    "Apa pengalaman paling lucu atau paling awkward saat PDKT?",
    "Kalau gebetan mengirim 'lagi apa?', jawaban jujurmu biasanya apa?",
    "Apa satu hal tentang dirimu yang biasanya tidak terlihat dari luar?",
    "Siapa di grup ini yang menurutmu paling mungkin jadi tempat curhat soal cinta?",
    "Kalau harus memilih, lebih baik mengungkapkan perasaan atau menyimpan rasa penasaran?",
    "Apa date sederhana yang menurutmu justru paling berkesan?",
    "Pernah cemburu padahal belum punya hubungan apa-apa?",
    "Apa pujian yang paling kamu ingat sampai sekarang?",
    "Kalau hidupmu jadi film romance, judulnya apa?",
    "Apa hal spontan paling seru yang pernah kamu lakukan demi seseorang?",
]

# Dare: seru dan sedikit romantis, tetapi tetap aman dan tidak memaksa
# pemain menghubungi, menyebut, atau mengungkapkan identitas orang lain.
DARE_CHALLENGES = [
    "Kirim satu emoji yang paling menggambarkan status percintaanmu sekarang. Jangan dijelaskan dulu!",
    "Buat gombalan original dalam maksimal 15 kata.",
    "Nyanyikan atau tuliskan satu baris lagu romantis yang sedang terlintas di kepala.",
    "Buat caption dating profile tentang dirimu dalam satu kalimat.",
    "Sebutkan tiga green flag yang kamu punya—percaya diri sedikit boleh!",
    "Buat pantun romantis dadakan untuk seluruh anggota grup.",
    "Ketik kalimat 'aku punya sesuatu yang mau diceritakan...' lalu lanjutkan dengan cerita lucu, bukan prank yang bikin khawatir.",
    "Ceritakan ide first date impianmu dalam tiga kalimat.",
    "Gunakan gaya bahasa penyair untuk mengatakan bahwa kamu sedang lapar.",
    "Buat pickup line paling receh yang bisa kamu pikirkan sekarang.",
    "Pilih satu lagu untuk jadi soundtrack saat kamu jatuh cinta, lalu sebutkan alasannya.",
    "Tulis pesan penyemangat untuk seseorang yang sedang berusaha move on.",
    "Deskripsikan tipe idealmu tanpa menyebut nama orang atau ciri fisik yang terlalu spesifik.",
    "Buat dialog singkat seolah-olah kamu sedang bertemu crush di lift.",
    "Kirim tiga emoji yang menggambarkan kencan impianmu.",
    "Ucapkan 'aku menghargai diriku sendiri' dengan gaya paling dramatis.",
    "Buat review bintang lima untuk dirimu sendiri sebagai calon pasangan.",
    "Ceritakan momen paling bikin salting yang aman untuk dibagikan.",
    "Buat satu kalimat rayuan yang terdengar seperti dialog film.",
    "Pilih satu anggota grup untuk diberi gelar fiktif, misalnya 'CEO paling jago bikin suasana'. Tetap sopan!",
    "Tulis bio aplikasi kencan versi lucu dalam maksimal 20 kata.",
    "Sebutkan satu kebiasaan kecil yang menurutmu romantis.",
    "Buat voice note 5 detik (atau tulis teksnya) dengan gaya penyiar radio yang sedang menyampaikan lagu cinta.",
    "Ciptakan nama couple fiktif dari dua benda di sekitarmu.",
    "Berikan satu pujian tulus kepada grup secara umum.",
]

def proses_truth_dare(pesan: str):
    """Memproses perintah Truth or Dare. Mengembalikan teks atau None."""
    if not isinstance(pesan, str):
        return None

    command = pesan.strip().lower()

    if command in ("!tod help", "!tod bantuan"):
        return (
            "🎲 TRUTH OR DARE — NASTY POTTER\n\n"
            "!tod  → pilih Truth atau Dare secara acak\n"
            "!truth → dapat pertanyaan Truth\n"
            "!dare  → dapat tantangan Dare\n\n"
            "Tema: romance, PDKT, hubungan, dan hal-hal seru. "
            "Boleh skip jika pertanyaan atau tantangannya membuatmu tidak nyaman."
        )

    if command == "!tod":
        jenis = random.choice(("truth", "dare"))
        if jenis == "truth":
            return f"💗 TRUTH TIME!\n{random.choice(TRUTH_QUESTIONS)}"
        return f"🔥 DARE TIME!\n{random.choice(DARE_CHALLENGES)}"

    if command == "!truth":
        return f"💗 TRUTH TIME!\n{random.choice(TRUTH_QUESTIONS)}"

    if command == "!dare":
        return f"🔥 DARE TIME!\n{random.choice(DARE_CHALLENGES)}"

    return None
