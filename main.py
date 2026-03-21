# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from temp_mails import Tenminemail_com  # En stabil provider'lardan biri
# Alternatifler: Guerrillamail_com, Tempmail_id, Byom_de, Dropmail_me vs.
# Tam liste: pip show temp-mails sonrası docs veya kaynak koduna bak

import re
import time
from typing import Optional

app = FastAPI(title="Temp Mail API - Multi Provider (temp-mails paketi)")

class EmailResponse(BaseModel):
    email: str
    provider: str

class CodeResponse(BaseModel):
    code: Optional[str] = None
    message: str
    from_email: Optional[str] = None

@app.get("/generate", response_model=EmailResponse)
def generate_temp_email():
    try:
        # İstediğin provider'ı seç (Tenminemail_com çok hızlı ve stabil)
        mail = Tenminemail_com()  # veya Guerrillamail_com() dene eğer bu yavaşlarsa
        return {
            "email": mail.email,
            "provider": mail.__class__.__name__
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mail oluşturulamadı: {str(e)}")

@app.get("/wait-for-code/{email}", response_model=CodeResponse)
def wait_for_verification_code(email: str, timeout: int = 180, poll_interval: float = 4.0):
    try:
        # Mevcut mail objesini yeniden oluştur (paket state tutmuyor, her seferinde yeni instance)
        # Not: Bazı provider'larda email'i constructor'a verebiliyorsun, ama genelde random üretir
        # Bu yüzden polling için provider'ı yeniden başlatıyoruz (eğer destekliyorsa)
        mail = Tenminemail_com()  # Eğer aynı email'i desteklemiyorsa → farklı provider dene

        # Eğer provider email'i kabul etmiyorsa (çoğu random üretir), hata verebilir
        # Alternatif: mail.email = email  # bazı provider'larda çalışır, deneme yanılma

        start_time = time.time()
        old_inbox_len = len(mail.get_inbox()) if hasattr(mail, 'get_inbox') else 0

        while time.time() - start_time < timeout:
            try:
                inbox = mail.get_inbox()
                new_messages = inbox[old_inbox_len:] if old_inbox_len > 0 else inbox

                for msg in new_messages:
                    # Mesaj içeriğini al
                    content = mail.get_mail_content(message_id=msg.get("id"))
                    body = content.get("body", "") or content.get("text", "")
                    subject = content.get("subject", "")

                    full_text = f"{subject} {body}".lower()

                    # 6 haneli kod ara (en yaygın OTP)
                    code_match = re.search(r'\b\d{6}\b', full_text)
                    if code_match:
                        return {
                            "code": code_match.group(0),
                            "message": "Kod bulundu!",
                            "from_email": msg.get("from")
                        }

                    # Alternatif pattern'lar ekleyebilirsin
                    # code_match = re.search(r'(?:kod|code|verify|onay).*?([a-z0-9]{8})', full_text, re.I)

                old_inbox_len = len(inbox)
            except Exception as inner_e:
                print(f"Polling hatası: {inner_e}")  # log için

            time.sleep(poll_interval)

        return {"code": None, "message": f"{timeout} saniye içinde kod gelmedi."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hata: {str(e)}")

# Konsol testi için (Render dışında dene)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
