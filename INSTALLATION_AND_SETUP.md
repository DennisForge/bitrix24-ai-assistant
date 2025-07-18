# 🛠️ Vodič za Instalaciju i Podešavanje

Kompletni vodič za instalaciju i podešavanje Bitrix24 AI Asistent-a.

## 📋 Sistemske Potrebe

### **Minimalne Potrebe**
- **Operativni Sistem**: Windows 10+, macOS 12+, ili Linux Ubuntu 20.04+
- **Python**: Verzija 3.8 ili novija
- **RAM**: 2GB minimum (4GB preporučeno)
- **Disk**: 1GB slobodnog prostora
- **Internet**: Stabilna konekcija za AI funkcionalnosti

### **Preporučeno**
- **RAM**: 4GB ili više
- **CPU**: 2+ cores
- **SSD**: Za bolje performanse
- **Docker**: Za lakše deployment

## 🚀 Metod 1: Brza Instalacija sa Docker-om (Preporučeno)

### **Korak 1: Instaliraj Docker**
```bash
# Windows/Mac: Preuzmite Docker Desktop sa https://docker.com
# Ubuntu:
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER
```

### **Korak 2: Kloniraj Repozitorijum**
```bash
git clone https://github.com/yourusername/bitrix24-ai-assistant.git
cd bitrix24-ai-assistant
```

### **Korak 3: Konfiguriši Environment (Opciono)**
```bash
# Kopiraj template
cp .env.example .env

# Edituj sa svojim API ključevima (opciono za demo)
nano .env
```

### **Korak 4: Pokreni Aplikaciju**
```bash
# Pokreni sve servise
docker-compose up -d

# Proveri status
docker-compose ps

# Prikaži logove
docker-compose logs -f
```

### **Korak 5: Testiraj Instalaciju**
- **Web Interfejs**: http://localhost:8000/calendar
- **API Dokumentacija**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

🎉 **Gotovo! Vaš AI Asistent je spreman za korišćenje!**

---

## 🐍 Metod 2: Lokalna Python Instalacija

### **Korak 1: Proveri Python Verziju**
```bash
python --version  # Mora biti 3.8+
# ili
python3 --version
```

### **Korak 2: Kloniraj Repozitorijum**
```bash
git clone https://github.com/yourusername/bitrix24-ai-assistant.git
cd bitrix24-ai-assistant
```

### **Korak 3: Kreiraj Virtualno Okruženje**
```bash
# Kreiraj virtualno okruženje
python -m venv venv

# Aktiviraj virtualno okruženje
# Na macOS/Linux:
source venv/bin/activate

# Na Windows:
venv\Scripts\activate

# Potvrdi aktivaciju (trebalo bi videti (venv) u terminal-u)
which python
```

### **Korak 4: Instaliraj Dependencies**
```bash
# Ažuriraj pip
pip install --upgrade pip

# Instaliraj sve potrebne pakete
pip install -r requirements.txt

# Proveri instalaciju
pip list
```

### **Korak 5: Konfiguriši Environment**
```bash
# Kopiraj template
cp .env.example .env

# Edituj configuration
nano .env  # ili bilo koji text editor
```

### **Korak 6: Inicijalizuj Bazu Podataka**
```bash
# Baza će se automatski kreirati pri prvom pokretanju
python -c "
from app.core.database import init_db
import asyncio
asyncio.run(init_db())
print('Baza podataka uspešno inicijalizovana!')
"
```

### **Korak 7: Pokreni Aplikaciju**
```bash
# Pokreni development server
python main.py

# Trebali biste videti poruke poput:
# "Starting Bitrix24 AI Assistant..."
# "Application started successfully!"
# "Uvicorn running on http://0.0.0.0:8000"
```

### **Korak 8: Testiraj Instalaciju**
- **Web Interfejs**: http://localhost:8000/calendar
- **API Dokumentacija**: http://localhost:8000/docs

---

## 🔑 Konfiguracija Environment Varijabli

### **Osnovne Postavke (.env fajl)**
```env
# Osnovno okruženje
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# Database (SQLite za development)
DATABASE_URL=sqlite:///calendar.db

# AI Konfiguracija
OPENAI_API_KEY=your_openai_api_key_here
AI_MODEL=gpt-4
AI_MAX_TOKENS=1000
AI_TEMPERATURE=0.7

# Email Konfiguracija (opciono)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
SMTP_USE_TLS=True

# Bitrix24 Integracija (opciono)
BITRIX24_DOMAIN=your_company.bitrix24.com
BITRIX24_API_KEY=your_bitrix24_api_key
BITRIX24_USER_ID=1

# Server Konfiguracija
HOST=0.0.0.0
PORT=8000
WORKERS=1
RELOAD=True

# Bezbednost
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
ALLOWED_HOSTS=localhost,127.0.0.1

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Scheduller
SCHEDULER_ENABLED=True
NOTIFICATION_INTERVAL=300
```

### **Kako Dobiti API Ključeve**

#### **OpenAI API Ključ**
1. Idite na https://platform.openai.com/api-keys
2. Kliknite "Create new secret key"
3. Kopirajte ključ i dodajte u .env
4. Dodajte kredit na nalog (~$5 je dovoljno)

#### **Gmail App Password**
1. Omogućite 2-faktorsku autentifikaciju
2. Idite na Google Account Settings
3. Security → App passwords
4. Generiši app password
5. Koristite ovaj password u .env

#### **Bitrix24 API Ključ**
1. Logujte se u vaš Bitrix24
2. Applications → Developer resources
3. Other → Inbound webhook
4. Kopirajte webhook URL i API ključ

---

## 🗄️ Konfiguracija Baze Podataka

### **SQLite (Default - Development)**
```env
DATABASE_URL=sqlite:///calendar.db
```

### **PostgreSQL (Production)**
```bash
# Instaliraj PostgreSQL
sudo apt install postgresql postgresql-contrib

# Kreiraj bazu i korisnika
sudo -u postgres psql
CREATE DATABASE bitrix24_ai;
CREATE USER bitrix24_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE bitrix24_ai TO bitrix24_user;
\q

# Ažuriraj .env
DATABASE_URL=postgresql://bitrix24_user:your_password@localhost/bitrix24_ai
```

### **MySQL (Production)**
```bash
# Instaliraj MySQL
sudo apt install mysql-server

# Kreiraj bazu
mysql -u root -p
CREATE DATABASE bitrix24_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bitrix24_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON bitrix24_ai.* TO 'bitrix24_user'@'localhost';
FLUSH PRIVILEGES;
exit;

# Ažuriraj .env
DATABASE_URL=mysql://bitrix24_user:your_password@localhost/bitrix24_ai
```

---

## 🔧 Dodatna Podešavanja

### **SSL/HTTPS Konfiguracija**
```bash
# Za produkciju sa nginx
sudo apt install nginx certbot python3-certbot-nginx

# Konfiguriši nginx
sudo nano /etc/nginx/sites-available/bitrix24-ai-assistant

# Sadržaj:
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Aktiviraj konfiguraciju
sudo ln -s /etc/nginx/sites-available/bitrix24-ai-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Dobij SSL sertifikat
sudo certbot --nginx -d your-domain.com
```

### **Systemd Service (Linux)**
```bash
# Kreiraj service fajl
sudo nano /etc/systemd/system/bitrix24-ai-assistant.service

# Sadržaj:
[Unit]
Description=Bitrix24 AI Assistant
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/bitrix24-ai-assistant
Environment=PATH=/path/to/bitrix24-ai-assistant/venv/bin
ExecStart=/path/to/bitrix24-ai-assistant/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target

# Aktiviraj service
sudo systemctl daemon-reload
sudo systemctl enable bitrix24-ai-assistant
sudo systemctl start bitrix24-ai-assistant
```

### **Firewall Konfiguracija**
```bash
# Ubuntu UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# CentOS firewalld
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

---

## 🧪 Verifikacija Instalacije

### **Osnovni Testovi**
```bash
# Test server health
curl http://localhost:8000/health

# Test API
curl http://localhost:8000/docs

# Test baze podataka
curl http://localhost:8000/api/calendar/events

# Očekivani odgovor:
{
  "status": "healthy",
  "timestamp": "2025-07-19T12:00:00Z",
  "database": "connected",
  "ai_service": "ready"
}
```

### **Test AI Funkcionalnosti**
```bash
# Test AI chat (zahteva OpenAI API ključ)
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Zdravo, kako si?"}'
```

### **Test Email Funkcionalnosti**
```bash
# Test email (zahteva SMTP konfiguraciju)
curl -X POST http://localhost:8000/notifications/test-email \
  -H "Content-Type: application/json"
```

---

## 🛠️ Česti Problemi i Rešenja

### **Problem: Port 8000 je zauzet**
```bash
# Pronađi proces koji koristi port
lsof -i :8000

# Ubij proces
kill -9 <PID>

# Ili koristi drugi port
HOST=0.0.0.0 PORT=8001 python main.py
```

### **Problem: Python verzija je preniska**
```bash
# Ubuntu - instaliraj noviji Python
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv

# Koristi specifičnu verziju
python3.11 -m venv venv
```

### **Problem: Permission denied na Linux**
```bash
# Daj dozvole
chmod +x main.py

# Ili pokreni sa python
python main.py
```

### **Problem: Cannot connect to database**
```bash
# SQLite - proveri dozvole
ls -la calendar.db
chmod 664 calendar.db

# PostgreSQL - proveri connection
pg_isready -h localhost -p 5432
```

### **Problem: OpenAI API errors**
```bash
# Proveri API ključ
echo $OPENAI_API_KEY

# Test API ključ
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

---

## 📊 Monitoring i Logiranje

### **Log Files**
```bash
# Kreiraj log direktorij
mkdir logs

# Pokreni sa logiranjem
python main.py > logs/app.log 2>&1 &

# Prati logove
tail -f logs/app.log
```

### **Health Monitoring**
```bash
# Automatski health check
#!/bin/bash
while true; do
  if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "$(date): Service is healthy"
  else
    echo "$(date): Service is down! Restarting..."
    systemctl restart bitrix24-ai-assistant
  fi
  sleep 60
done
```

---

## 🚀 Finalizacija

### **Production Checklist**
- [ ] Environment varijable konfigurisane
- [ ] Produkcijski database postavljen
- [ ] SSL sertifikati instalirani
- [ ] Firewall konfigurisan
- [ ] Backup strategija implementirana
- [ ] Monitoring podešen
- [ ] Documentation ažurirana

### **Testiranje Pre Produkcije**
```bash
# Pokreni sve testove
python -m pytest tests/

# Test performansi
ab -n 100 -c 10 http://localhost:8000/

# Security scan
bandit -r app/
```

### **Backup Strategija**
```bash
# Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# SQLite backup
cp calendar.db $BACKUP_DIR/calendar_$DATE.db

# PostgreSQL backup
pg_dump bitrix24_ai > $BACKUP_DIR/bitrix24_ai_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

---

## 🎉 Čestitamo!

Vaš Bitrix24 AI Asistent je uspešno instaliran i konfigurisan! 🚀

### **Sledeći Koraci:**
1. **Testiraj osnovne funkcionalnosti**
2. **Dodaj timske članove**
3. **Konfiguriši AI API ključ za punu funkcionalnost**
4. **Postaviti backup rutinu**
5. **Počni koristiti AI komande!**

### **Prva AI Komanda za Test:**
```
"Dodaj sastanak sutra u 14h sa razvoj timom"
```

**Potrebna pomoć?** Pogledaj [FAQ](FAQ.md) ili [Korisnički Vodič](USER_GUIDE.md).

---

*Poslednje ažuriranje: 19. jul 2025.*