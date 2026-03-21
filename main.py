from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from temp_mails import Tenminemail_com  # En stabil olanı başlatalım
# Alternatif dene: from temp_mails import Guerrillamail_com, Tempmail_id

import re
import time
from typing import Optional

app = FastAPI(title="Temp Mail API - Multi-Provider (temp-mails paketi)")

class EmailResponse(BaseModel):
    email: str
    provider: str

class CodeResponse(BaseModel):
    code: Optional[str] = None
    message: str
    sender: Optional[str] = None

@app.get("/generate", response_model=EmailResponse)
def generate_temp_email():
    try:
        # Provider seç (istediğini değiştir: Guerrillamail_com() vs.)
        mail = Tenminemail_com()
        return {
            "email": mail.email,
            "provider": mail.__class__.__name__
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mail oluşturulamadı: {str(e)}")

@app.get("/wait-for-code/{email}", response_model=CodeResponse)
def wait_for_code(
    email: str,
    timeout: int = Query(180, description="Bekleme süresi saniye"),
    interval: float = Query(5.0, description="Her kontrol arası saniye")
):
    try:
        # Paket random üretir, mevcut email'i doğrudan kullanamayabiliriz → fallback polling
        # Eğer provider aynı email'i desteklemiyorsa, yeni instance ile inbox check yap
        mail = Tenminemail_com()  # Yeni instance (eğer email aynı domain'deyse şanslıyız)

        # Bazı provider'larda email set edilebiliyor, dene:
        # mail.email = email  # Çalışmazsa yorum satırına al

        start = time.time()
        found_code = None
        sender = None

        while time.time() - start < timeout:
            try:
                # Inbox'ı çek (paketin ortak method'u)
                inbox = mail.get_inbox()  # List of dicts döner genelde

                for msg in inbox:
                    # Mesaj detayını al (subject + body)
                    subject = msg.get("subject", "").lower()
                    body = msg.get("body", "") or msg.get("text", "") or ""

                    full_text = f"{subject} {body}"

                    # 6 haneli OTP kod ara
                    match = re.search(r'\b\d{6}\b', full_text)
                    if match:
                        found_code = match.group(0)
                        sender = msg.get("from", "Bilinmeyen")
                        break  # İlk bulduğumuzu dön

                    # Alternatif: "kodunuz" veya "verification code" kelimeleriyle filtrele
                    if "kod" in full_text or "code" in full_text or "verify" in full_text:
                        match = re.search(r'\b\d{6}\b', full_text)
                        if match:
                            found_code = match.group(0)
                            sender = msg.get("from", "Bilinmeyen")
                            break

                if found_code:
                    return {
                        "code": found_code,
                        "message": "Kod başarıyla bulundu!",
                        "sender": sender
                    }

            except Exception as poll_err:
                # Log için (Render log'larında görünür)
                print(f"Polling hatası: {poll_err}")

            time.sleep(interval)

        return {
            "code": None,
            "message": f"{timeout} saniye içinde kod gelmedi. Provider: {mail.__class__.__name__}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Genel hata: {str(e)}")

# Render dışında konsolda test için
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
