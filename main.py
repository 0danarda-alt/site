from fastapi import FastAPI, Query
import requests
import time
import re
from typing import Optional

app = FastAPI(title="SharkLasers Temp Mail API (Guerrilla Backend)")

API_URL = "https://api.guerrillamail.com/ajax.php"

def api_call(params: dict):
    resp = requests.get(API_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

@app.get("/generate")
def generate_sharklasers_email():
    # Yeni session başlat + random email al
    data = api_call({"f": "get_email_address"})
    sid_token = data["sid_token"]
    
    # Domain'i sharklasers.com yap (random prefix ile)
    set_data = api_call({
        "f": "set_email_address",
        "sid_token": sid_token,
        "email_user": "",  # boş = random prefix
        "domain": "sharklasers.com"
    })
    
    return {
        "email": set_data.get("email_addr", "Hata"),
        "sid_token": sid_token  # polling için client tarafında veya session'da tut
    }

@app.get("/wait-for-code")
def wait_for_verification_code(
    sid_token: str = Query(..., description="generate endpoint'inden aldığın sid_token"),
    timeout: int = Query(180, description="Bekleme süresi (saniye)"),
    interval: float = Query(5.0, description="Her kontrol arası")
):
    start = time.time()
    seen_ids = set()

    while time.time() - start < timeout:
        inbox = api_call({"f": "check_email", "sid_token": sid_token})
        mails = inbox.get("list", [])

        for mail in mails:
            mail_id = mail["mail_id"]
            if mail_id in seen_ids:
                continue
            seen_ids.add(mail_id)

            # Tam içeriği çek
            content = api_call({"f": "fetch_email", "sid_token": sid_token, "email_id": mail_id})
            mail_body = content.get("mail", {}).get("mail_body", "")
            subject = content.get("mail", {}).get("mail_subject", "")

            full_text = (subject + " " + mail_body).lower()

            # 6 haneli kod ara (OTP için en yaygın)
            match = re.search(r'\b\d{6}\b', full_text)
            if match:
                return {
                    "code": match.group(0),
                    "from": mail.get("mail_from"),
                    "subject": subject,
                    "message": "Kod başarıyla bulundu!"
                }

        time.sleep(interval)

    return {"code": None, "message": f"{timeout} sn içinde kod gelmedi. Inbox boş veya gecikme var."}

# Render dışında test için
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
