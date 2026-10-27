"""Werewolf: Desa Terkutuk untuk bot LINE Nasty Potter.

State disimpan di werewolf_state.json. Pemanggilan dari index.py:
proses_game(chat_id, user_id, pesan, get_nama, kirim_pesan, kirim_pribadi)
"""
import json
import os
import random
import threading
import time
from collections import Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "werewolf_state.json")
NIGHT_SECONDS = 45
DAY_SECONDS = 60
VOTE_SECONDS = 30
MIN_PLAYERS = 3
MAX_PLAYERS = 15

_LOCK = threading.RLock()
_GAMES = {}
_TIMERS = {}
_CALLBACKS = {}  # chat_id -> {group: callable, private: callable}

ROLE_INFO = {
    "werewolf": "🐺 WEREWOLF — saat malam, gunakan !ww kill Nama untuk memilih korban. Menangkan permainan dengan menyamai atau melebihi jumlah warga hidup.",
    "seer": "🔮 PERAMAL — saat malam, gunakan !ww see Nama untuk memeriksa apakah pemain itu Werewolf. Hasil dikirim secara pribadi.",
    "doctor": "🩺 DOKTER — saat malam, gunakan !ww heal Nama untuk melindungi satu pemain dari serangan malam.",
    "villager": "🧑‍🌾 WARGA — diskusikan petunjuk dan gunakan !ww vote Nama saat fase voting untuk mengusir tersangka.",
}


def _load():
    global _GAMES
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        _GAMES = data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        _GAMES = {}


def _save():
    temp = STATE_FILE + ".tmp"
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(_GAMES, f, ensure_ascii=False, indent=2)
    os.replace(temp, STATE_FILE)


_load()


def _cancel_timer(chat_id):
    timer = _TIMERS.pop(str(chat_id), None)
    if timer:
        timer.cancel()


def _send_group(chat_id, text):
    callback = _CALLBACKS.get(str(chat_id), {}).get("group")
    if callback:
        try:
            callback(str(chat_id), text)
        except Exception as exc:
            print(f"[Werewolf] Gagal mengirim pesan grup: {exc}")


def _send_private(chat_id, user_id, text):
    callback = _CALLBACKS.get(str(chat_id), {}).get("private")
    if callback:
        try:
            callback(str(user_id), text)
        except Exception as exc:
            print(f"[Werewolf] Gagal mengirim role/pesan pribadi: {exc}")


def _schedule(chat_id, seconds):
    chat_id = str(chat_id)
    _cancel_timer(chat_id)
    game = _GAMES.get(chat_id)
    if not game or game.get("status") != "active":
        return
    game["deadline"] = time.time() + seconds
    _save()
    timer = threading.Timer(seconds, _timer_advance, args=(chat_id,))
    timer.daemon = True
    _TIMERS[chat_id] = timer
    timer.start()


def _timer_advance(chat_id):
    with _LOCK:
        _TIMERS.pop(str(chat_id), None)
        message = _advance(str(chat_id), timed_out=True)
    if message:
        _send_group(chat_id, message)


def _alive_players(game):
    return {uid: p for uid, p in game["players"].items() if p.get("alive", True)}


def _name_for(game, uid):
    return game.get("players", {}).get(uid, {}).get("name", f"Pemain {uid[:5]}")


def _find_player(game, name):
    target = name.strip().lstrip("@").casefold()
    if not target:
        return None
    matches = []
    for uid, player in game.get("players", {}).items():
        if player.get("name", "").casefold() == target:
            matches.append(uid)
    if len(matches) == 1:
        return matches[0]
    # Allow unique partial name, but reject ambiguous matches.
    matches = [uid for uid, p in game.get("players", {}).items() if target in p.get("name", "").casefold()]
    return matches[0] if len(matches) == 1 else None


def _winner(game):
    alive = _alive_players(game)
    wolves = sum(1 for p in alive.values() if p["role"] == "werewolf")
    others = len(alive) - wolves
    if wolves == 0:
        return "WARGA", "Semua Werewolf telah tersingkir! Desa selamat."
    if wolves >= others:
        return "WEREWOLF", "Jumlah Werewolf menyamai atau melebihi pemain lain yang masih hidup. Desa jatuh ke tangan Werewolf!"
    return None, None


def _end_game(chat_id, reason):
    game = _GAMES[chat_id]
    _cancel_timer(chat_id)
    lines = [f"🏁 GAME WEREWOLF SELESAI — {reason}", "", "Identitas pemain:"]
    for uid, p in game["players"].items():
        mark = "💀" if not p.get("alive", True) else "🟢"
        role_name = p["role"].replace("werewolf", "Werewolf").replace("seer", "Peramal").replace("doctor", "Dokter").replace("villager", "Warga")
        lines.append(f"{mark} {p['name']} — {role_name}")
    lines.append("\nKetik !ww join untuk ikut permainan berikutnya.")
    game["status"] = "finished"
    game["phase"] = "finished"
    game["deadline"] = None
    _save()
    return "\n".join(lines)


def _begin_day(chat_id, game, intro=""):
    game["phase"] = "day"
    game["votes"] = {}
    game["deadline"] = None
    _save()
    _schedule(chat_id, DAY_SECONDS)
    alive = _alive_players(game)
    names = ", ".join(p["name"] for p in alive.values())
    prefix = (intro + "\n\n") if intro else ""
    return (f"{prefix}☀️ HARI KE-{game['round']} DIMULAI!\n"
            f"Pemain hidup: {names}\n\nDiskusikan siapa yang mencurigakan. "
            f"Fase diskusi berlangsung {DAY_SECONDS} detik, lalu voting dimulai otomatis.")


def _begin_night(chat_id, game):
    game["phase"] = "night"
    game["night_actions"] = {"kill_votes": {}, "heal": None, "see": None}
    game["votes"] = {}
    game["round"] = int(game.get("round", 1))
    _save()
    _schedule(chat_id, NIGHT_SECONDS)
    alive = _alive_players(game)
    return (f"🌙 MALAM KE-{game['round']} TIBA! Semua pemain memilih aksi role masing-masing.\n"
            f"Aksi malam berlangsung {NIGHT_SECONDS} detik. Gunakan command role secara pribadi di grup; "
            "jangan tulis aksi jika kamu bukan role yang sesuai.")


def _resolve_night(chat_id, game):
    actions = game.get("night_actions", {})
    alive = _alive_players(game)
    saved = actions.get("heal")
    # Setiap Werewolf memberikan suara korban. Target terbanyak dipilih;
    # jika seri, serangan gagal dan tidak ada korban.
    kill_votes = actions.get("kill_votes", {})
    if not isinstance(kill_votes, dict):
        kill_votes = {}
    # Kompatibilitas dengan state lama yang hanya menyimpan satu target.
    legacy_target = actions.get("kill")
    valid_votes = [target for wolf_id, target in kill_votes.items()
                   if wolf_id in alive and alive[wolf_id].get("role") == "werewolf"
                   and target in alive and target != wolf_id]
    if not valid_votes and legacy_target in alive:
        valid_votes = [legacy_target]
    counts = Counter(valid_votes)
    victim = None
    if counts:
        top_count = max(counts.values())
        leaders = [target for target, count in counts.items() if count == top_count]
        if len(leaders) == 1:
            victim = leaders[0]
    intro = "🌅 PAGI TIBA!"
    if victim and victim != saved:
        alive[victim]["alive"] = False
        intro += f"\n💀 {alive[victim]['name']} ditemukan tewas saat malam!"
    elif victim and victim == saved:
        intro += "\n🩺 Serangan malam berhasil digagalkan dokter. Tidak ada korban!"
    elif counts and len([t for t, c in counts.items() if c == max(counts.values())]) > 1:
        intro += "\n🐺 Suara Werewolf seri. Tidak ada korban malam ini."
    else:
        intro += "\nTidak ada korban malam ini."
    _save()
    winner, reason = _winner(game)
    if winner:
        return _end_game(chat_id, f"{winner} MENANG! {reason}")
    return _begin_day(chat_id, game, intro)


def _resolve_vote(chat_id, game):
    alive = _alive_players(game)
    votes = {uid: target for uid, target in game.get("votes", {}).items()
             if uid in alive and target in alive and uid != target}
    counts = Counter(votes.values())
    if not counts:
        intro = "⚖️ Voting selesai, tetapi tidak ada suara yang sah. Tidak ada pemain yang diusir."
    else:
        highest = max(counts.values())
        leaders = [uid for uid, count in counts.items() if count == highest]
        if len(leaders) != 1:
            intro = "⚖️ Hasil voting seri. Tidak ada pemain yang diusir."
        else:
            target = leaders[0]
            game["players"][target]["alive"] = False
            role = game["players"][target]["role"]
            role_name = {"werewolf": "Werewolf", "seer": "Peramal", "doctor": "Dokter", "villager": "Warga"}[role]
            intro = f"🗳️ {game['players'][target]['name']} diusir oleh warga. Role-nya adalah {role_name}."
    _save()
    winner, reason = _winner(game)
    if winner:
        return _end_game(chat_id, f"{winner} MENANG! {reason}")
    game["round"] = int(game.get("round", 1)) + 1
    return intro + "\n\n" + _begin_night(chat_id, game)


def _advance(chat_id, timed_out=False):
    game = _GAMES.get(str(chat_id))
    if not game or game.get("status") != "active":
        return None
    phase = game.get("phase")
    if phase == "night":
        return _resolve_night(str(chat_id), game)
    if phase == "day":
        game["phase"] = "vote"
        game["votes"] = {}
        _save()
        _schedule(str(chat_id), VOTE_SECONDS)
        names = ", ".join(p["name"] for p in _alive_players(game).values())
        return (f"🗳️ FASE VOTING DIMULAI! ({VOTE_SECONDS} detik)\nPemain hidup: {names}\n"
                "Pilih tersangka dengan !ww vote Nama. Suara terbanyak akan diusir.")
    if phase == "vote":
        return _resolve_vote(str(chat_id), game)
    return None


def _maybe_finish_night(chat_id, game):
    alive = _alive_players(game)
    actions = game.get("night_actions", {})
    wolves_alive = [uid for uid, p in alive.items() if p.get("role") == "werewolf"]
    kill_votes = actions.get("kill_votes", {})
    if not isinstance(kill_votes, dict):
        kill_votes = {}
    wolves_done = all(uid in kill_votes for uid in wolves_alive)
    seer_alive = any(p.get("role") == "seer" for p in alive.values())
    doctor_alive = any(p.get("role") == "doctor" for p in alive.values())
    seer_done = not seer_alive or actions.get("see") is not None
    doctor_done = not doctor_alive or actions.get("heal") is not None
    if wolves_done and seer_done and doctor_done:
        _cancel_timer(chat_id)
        return _resolve_night(chat_id, game)
    return None


def _werewolf_count(player_count):
    """Jumlah Werewolf bertambah bertahap agar game besar tetap seimbang."""
    if player_count <= 5:
        return 1
    if player_count <= 8:
        return 2
    if player_count <= 12:
        return 3
    return 4


def _help_text():
    return (
        "🐺 WEREWOLF: DESA TERKUTUK\n\n"
        "!ww join — ikut lobby\n!ww leave — keluar dari lobby\n!ww start — mulai (3–15 pemain)\n"
        "!ww status — cek fase dan pemain hidup\n!ww role — kirim ulang role secara pribadi\n"
        "!ww kill Nama — aksi Werewolf saat malam\n!ww heal Nama — aksi Dokter saat malam\n"
        "!ww see Nama — aksi Peramal saat malam\n!ww vote Nama — voting saat fase voting\n"
        "!ww stop — hentikan game (siapa pun boleh menghentikan; gunakan hanya jika perlu)\n\n"
        f"Pemain: {MIN_PLAYERS}–{MAX_PLAYERS}. Werewolf bertambah sesuai jumlah pemain.\n"
        f"Durasi otomatis: malam {NIGHT_SECONDS} dtk, diskusi {DAY_SECONDS} dtk, voting {VOTE_SECONDS} dtk."
    )


def proses_game(chat_id, user_id, pesan, get_nama, kirim_pesan=None, kirim_pribadi=None):
    """Memproses command Werewolf. Return string untuk dibalas di chat, atau None."""
    raw = (pesan or "").strip()
    if not raw.lower().startswith("!ww"):
        return None
    chat_id, user_id = str(chat_id), str(user_id)
    if kirim_pesan or kirim_pribadi:
        _CALLBACKS[chat_id] = {"group": kirim_pesan, "private": kirim_pribadi}
    parts = raw.split(maxsplit=2)
    sub = parts[1].lower() if len(parts) > 1 else "help"
    arg = parts[2].strip() if len(parts) > 2 else ""

    with _LOCK:
        game = _GAMES.get(chat_id)
        # Restore a timer after a process restart when an active game is next used.
        if game and game.get("status") == "active" and chat_id not in _TIMERS:
            remaining = max(5, float(game.get("deadline") or time.time()) - time.time())
            _schedule(chat_id, remaining)

        if sub in ("help", "menu"):
            return _help_text()

        if sub == "join":
            if game and game.get("status") == "active":
                return "⚠️ Game sudah dimulai. Tunggu sampai game selesai."
            if not game or game.get("status") == "finished":
                game = {"status": "lobby", "phase": "lobby", "players": {}, "round": 1,
                        "night_actions": {}, "votes": {}, "deadline": None}
                _GAMES[chat_id] = game
            if user_id in game["players"]:
                return f"⚠️ {game['players'][user_id]['name']}, kamu sudah masuk lobby."
            if len(game["players"]) >= MAX_PLAYERS:
                return f"❌ Lobby penuh. Maksimal {MAX_PLAYERS} pemain."
            try:
                name = get_nama(user_id)
            except Exception:
                name = f"Pemain {user_id[:5]}"
            game["players"][user_id] = {"name": str(name), "role": None, "alive": True}
            _save()
            names = ", ".join(p["name"] for p in game["players"].values())
            return (f"✅ {name} bergabung ke Werewolf! ({len(game['players'])}/{MAX_PLAYERS})\n"
                    f"Pemain: {names}\nKetik !ww start untuk mulai saat sudah ada 3–15 pemain.")

        if sub == "leave":
            if not game or game.get("status") != "lobby":
                return "Tidak ada lobby yang bisa kamu tinggalkan. Game yang sudah dimulai tidak bisa ditinggalkan."
            if user_id not in game["players"]:
                return "Kamu belum bergabung ke lobby."
            name = game["players"].pop(user_id)["name"]
            if not game["players"]:
                _GAMES.pop(chat_id, None)
            _save()
            return f"👋 {name} keluar dari lobby."

        if sub == "start":
            if game and game.get("status") == "active":
                return "⚠️ Werewolf sedang berjalan!"
            if not game or len(game.get("players", {})) < MIN_PLAYERS:
                count = len(game.get("players", {})) if game else 0
                return f"❌ Minimal {MIN_PLAYERS} pemain. Saat ini baru {count}. Ketik !ww join untuk masuk."
            if len(game["players"]) > MAX_PLAYERS:
                return f"❌ Maksimal {MAX_PLAYERS} pemain."
            player_ids = list(game["players"].keys())
            player_count = len(player_ids)
            wolf_count = _werewolf_count(player_count)
            roles = ["werewolf"] * wolf_count + ["seer"]
            if player_count >= 4:
                roles.append("doctor")
            while len(roles) < player_count:
                roles.append("villager")
            random.shuffle(roles)
            for uid, role in zip(player_ids, roles):
                game["players"][uid]["role"] = role
                game["players"][uid]["alive"] = True
                _send_private(chat_id, uid, "🐺 WEREWOLF: DESA TERKUTUK\nRole rahasiamu:\n" + ROLE_INFO[role] + "\n\nCommand: !ww kill Nama / !ww heal Nama / !ww see Nama / !ww vote Nama sesuai role dan fase.")
            game["status"] = "active"
            game["phase"] = "night"
            game["round"] = 1
            game["night_actions"] = {"kill_votes": {}, "heal": None, "see": None}
            game["votes"] = {}
            _save()
            _schedule(chat_id, NIGHT_SECONDS)
            return (f"🐺 WEREWOLF: DESA TERKUTUK DIMULAI!\nPemain: {len(player_ids)}\n"
                    "Role rahasia sudah dikirim melalui chat pribadi bot. Cek pesan pribadi dari bot.\n"
                    f"🌙 MALAM KE-1 dimulai ({NIGHT_SECONDS} detik). Gunakan aksi sesuai role.\n"
                    "Ketik !ww status untuk melihat status permainan.")

        if sub == "stop":
            if not game or game.get("status") not in ("lobby", "active"):
                return "Tidak ada game Werewolf yang sedang berjalan."
            _cancel_timer(chat_id)
            game["status"] = "finished"
            game["phase"] = "finished"
            game["deadline"] = None
            _save()
            return "🛑 Game Werewolf dihentikan. Ketik !ww join untuk membuat lobby baru."

        if sub == "status":
            if not game:
                return "Belum ada lobby. Ketik !ww join untuk membuat atau bergabung ke lobby."
            names = []
            for p in game["players"].values():
                names.append(("🟢 " if p.get("alive", True) else "💀 ") + p["name"])
            if game.get("status") == "active":
                remaining = max(0, int((game.get("deadline") or time.time()) - time.time()))
                return (f"🐺 STATUS WEREWOLF\nFase: {game['phase'].upper()}\nRonde: {game.get('round', 1)}\n"
                        f"Sisa waktu: sekitar {remaining} detik\nPemain: " + ", ".join(names))
            return f"🐺 LOBBY WEREWOLF ({len(game['players'])}/{MAX_PLAYERS})\n" + (", ".join(names) or "Belum ada pemain")

        if sub == "role":
            if not game or user_id not in game.get("players", {}):
                return "Kamu tidak terdaftar di game ini."
            role = game["players"][user_id].get("role")
            if not role:
                return "Role belum dibagikan. Game belum dimulai."
            _send_private(chat_id, user_id, "🔐 Role rahasiamu: " + ROLE_INFO[role])
            return "🔐 Role dikirim ulang melalui chat pribadi bot. Cek DM dari bot, jangan bocorkan role kamu!"

        if not game or game.get("status") != "active":
            return "Game belum dimulai. Ketik !ww join, lalu !ww start jika sudah ada 3–15 pemain."
        if user_id not in game["players"]:
            return "Kamu bukan pemain di game ini. Game sudah dimulai, jadi kamu tidak bisa bergabung di ronde berjalan."
        player = game["players"][user_id]
        if not player.get("alive", True):
            return "💀 Kamu sudah tereliminasi dan tidak bisa menggunakan aksi atau voting."

        if sub in ("kill", "heal", "see"):
            if game.get("phase") != "night":
                return "Aksi role hanya bisa digunakan saat fase malam. Tunggu malam berikutnya."
            required_role = {"kill": "werewolf", "heal": "doctor", "see": "seer"}[sub]
            if player.get("role") != required_role:
                return "❌ Role kamu tidak bisa menggunakan aksi tersebut."
            target = _find_player(game, arg)
            if not target:
                return "Nama target tidak ditemukan atau namanya ambigu. Gunakan nama LINE yang tepat."
            if target not in _alive_players(game):
                return "Target sudah tereliminasi. Pilih pemain yang masih hidup."
            if target == user_id and sub in ("kill", "see"):
                return "Kamu tidak bisa memilih dirimu sendiri untuk aksi ini."
            if sub == "kill":
                game.setdefault("night_actions", {}).setdefault("kill_votes", {})[user_id] = target
            else:
                game["night_actions"][sub] = target
            _save()
            if sub == "see":
                result = "🐺 TARGET ADALAH WEREWOLF!" if game["players"][target]["role"] == "werewolf" else "✅ Target bukan Werewolf."
                _send_private(chat_id, user_id, f"🔮 HASIL PERAMAL\n{_name_for(game, target)}: {result}")
                confirmation = "🔮 Pemeriksaan selesai. Hasil dikirim secara pribadi."
            else:
                confirmation = {"kill": "🐺 Pilihan korban dicatat.", "heal": "🩺 Pilihan perlindungan dicatat."}[sub]
            advance_message = _maybe_finish_night(chat_id, game)
            if advance_message:
                _send_group(chat_id, advance_message)
                return confirmation + "\nSemua aksi malam sudah masuk; fase berikutnya dimulai otomatis."
            return confirmation

        if sub == "vote":
            if game.get("phase") != "vote":
                return "Voting belum dibuka. Tunggu bot memulai fase voting otomatis."
            target = _find_player(game, arg)
            if not target:
                return "Nama target tidak ditemukan atau namanya ambigu. Gunakan nama LINE yang tepat."
            if target not in _alive_players(game):
                return "Target sudah tereliminasi. Pilih pemain yang masih hidup."
            if target == user_id:
                return "Kamu tidak bisa memilih dirimu sendiri."
            game["votes"][user_id] = target
            _save()
            alive = _alive_players(game)
            if len(game["votes"]) >= len(alive):
                _cancel_timer(chat_id)
                result = _resolve_vote(chat_id, game)
                _send_group(chat_id, result)
                return f"🗳️ Suara kamu untuk {_name_for(game, target)} sudah dicatat. Semua pemain hidup sudah memilih; hasil diumumkan di grup."
            return f"🗳️ Suara kamu untuk {_name_for(game, target)} sudah dicatat secara rahasia."

        return _help_text()
