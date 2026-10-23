# whitelist_admin.py
"""
Modul whitelist admin untuk bot LINE.

Fitur:
- Whitelist admin disimpan di whitelist_admin.json.
- !whitelist       : meminta akses admin.
- !requestlist     : owner melihat permintaan.
- !acc USER_ID     : owner menyetujui permintaan.
- !tolak USER_ID   : owner menolak permintaan.
- !adminlist       : melihat daftar admin (owner/admin).
- cek_izin_admin() : memblokir perintah moderasi dari non-admin.

PENTING:
Modul ini tidak otomatis berjalan hanya karena file ada.
Aplikasi utama harus mengimpor dan memanggil process_whitelist_command()
serta cek_izin_admin() dari handler pesan. LINE Messaging API resmi juga
tidak menyediakan tindakan kick anggota atau invite anggota grup secara umum;
modul ini hanya mengatur izin/perintah, bukan melakukan kick/invite.
"""

import json
from pathlib import Path

# Ganti dengan LINE user ID milik OWNER bot.
OWNER_USER_ID = "Uee4e5e6bdabbd9e9e169dc499ad07093"

# File data dibuat di folder yang sama dengan modul ini.
DATA_FILE = Path(__file__).with_name("whitelist_admin.json")

# Perintah yang dibatasi untuk admin whitelist.
MODERATION_COMMANDS = {
    "!inv",
    "!invite",
    "!kick",
    "!keluarkan",
}

def _default_data():
    return {
        "admins": [OWNER_USER_ID],
        "pending": []
    }

def _load_data():
    """Membaca data whitelist; membuat data awal jika file belum ada."""
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Format data whitelist tidak valid")
        data.setdefault("admins", [OWNER_USER_ID])
        data.setdefault("pending", [])
        if OWNER_USER_ID not in data["admins"]:
            data["admins"].append(OWNER_USER_ID)
        return data
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        data = _default_data()
        _save_data(data)
        return data

def _save_data(data):
    """Menyimpan whitelist dan permintaan agar tetap ada setelah restart."""
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def boleh_kelola_grup(user_id):
    """True jika user merupakan owner atau admin whitelist."""
    if not user_id:
        return False
    data = _load_data()
    return user_id in data["admins"]

def perintah_admin(pesan):
    """True jika pesan diawali perintah moderasi yang dibatasi."""
    if not pesan or not pesan.strip():
        return False
    command = pesan.strip().split(maxsplit=1)[0].lower()
    return command in MODERATION_COMMANDS

def cek_izin_admin(user_id, pesan, get_nama=None):
    """
    Return pesan penolakan untuk perintah moderasi oleh non-admin.
    Return None jika bukan perintah moderasi atau user diizinkan.
    """
    if not perintah_admin(pesan) or boleh_kelola_grup(user_id):
        return None

    nama = "Kamu"
    if get_nama:
        try:
            nama = get_nama(user_id) or "Kamu"
        except Exception:
            pass

    return (
        f"⛔ Akses ditolak, {nama}!\n"
        "Perintah !inv dan !kick hanya boleh digunakan admin whitelist."
    )

def process_whitelist_command(user_id, pesan):
    """
    Memproses perintah whitelist dan mengembalikan teks balasan,
    atau None jika pesan bukan perintah whitelist.
    Panggil fungsi ini dari handler pesan utama.
    """
    if not user_id or not pesan:
        return None

    parts = pesan.strip().split()
    if not parts:
        return None

    command = parts[0].lower()
    data = _load_data()
    is_owner = user_id == OWNER_USER_ID
    is_admin = user_id in data["admins"]

    if command == "!whitelist":
        if is_admin:
            return "✅ Kamu sudah terdaftar sebagai admin whitelist."
        if user_id in data["pending"]:
            return "⏳ Permintaan whitelist kamu masih menunggu persetujuan owner."
        data["pending"].append(user_id)
        _save_data(data)
        return (
            "📨 Permintaan whitelist sudah dikirim ke sistem.\n"
            "Tunggu owner menyetujui permintaan kamu."
        )

    if command == "!requestlist":
        if not is_owner:
            return "⛔ Hanya owner yang boleh melihat permintaan whitelist."
        if not data["pending"]:
            return "📭 Belum ada permintaan whitelist."
        return "📋 Permintaan whitelist:\n" + "\n".join(
            f"{i}. {uid}" for i, uid in enumerate(data["pending"], start=1)
        ) + "\n\nSetujui dengan: !acc USER_ID\nTolak dengan: !tolak USER_ID"

    if command == "!acc":
        if not is_owner:
            return "⛔ Hanya owner yang boleh menyetujui admin."
        if len(parts) != 2:
            return "Format: !acc USER_ID"
        target_id = parts[1]
        if target_id == OWNER_USER_ID:
            return "ℹ️ User tersebut adalah owner."
        if target_id in data["admins"]:
            return "ℹ️ User tersebut sudah menjadi admin."
        if target_id not in data["pending"]:
            return "⚠️ ID tersebut tidak ada dalam daftar permintaan."
        data["pending"].remove(target_id)
        data["admins"].append(target_id)
        _save_data(data)
        return f"✅ Permintaan disetujui. {target_id} sekarang menjadi admin whitelist."

    if command == "!tolak":
        if not is_owner:
            return "⛔ Hanya owner yang boleh menolak permintaan admin."
        if len(parts) != 2:
            return "Format: !tolak USER_ID"
        target_id = parts[1]
        if target_id not in data["pending"]:
            return "⚠️ ID tersebut tidak ada dalam daftar permintaan."
        data["pending"].remove(target_id)
        _save_data(data)
        return f"❌ Permintaan whitelist {target_id} ditolak."

    if command == "!adminlist":
        if not is_admin:
            return "⛔ Hanya admin whitelist yang boleh melihat daftar admin."
        return "👑 Daftar admin whitelist:\n" + "\n".join(
            f"{i}. {uid}" for i, uid in enumerate(data["admins"], start=1)
        )

    if command == "!unadmin":
        if not is_owner:
            return "⛔ Hanya owner yang boleh mencabut akses admin."
        if len(parts) != 2:
            return "Format: !unadmin USER_ID"
        target_id = parts[1]
        if target_id == OWNER_USER_ID:
            return "⛔ Akses owner tidak dapat dicabut melalui perintah ini."
        if target_id not in data["admins"]:
            return "⚠️ User tersebut bukan admin whitelist."
        data["admins"].remove(target_id)
        _save_data(data)
        return f"✅ Akses admin {target_id} sudah dicabut."

    return None
