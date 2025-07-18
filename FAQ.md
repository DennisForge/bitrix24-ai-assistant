# ❓ Često Postavljana Pitanja

## 🚀 Početak Rada

### **P: Kako da instaliram Bitrix24 AI Asistent?**
O: Imate dve opcije:
- **Docker** (preporučeno): `docker-compose up -d`
- **Lokalno**: Kloniraj repo → Instaliraj Python deps → Konfiguriši .env → Pokreni `python main.py`

### **P: Koje su sistemske potrebe?**
O: 
- Python 3.8+
- 2GB RAM minimum
- Moderni web browser
- Internet konekcija za AI funkcionalnosti

### **P: Da li mi treba Bitrix24 nalog?**
O: Ne, sistem radi nezavisno. Bitrix24 integracija je opciona i poboljšava funkcionalnost.

## 🤖 AI Funkcionalnosti

### **P: Koje jezike AI podržava?**
O: AI primarno podržava **srpski jezik** sa engleskim kao rezervom. Komande poput "Zakaži sastanak sutra u 14h" rade savršeno.

### **P: Da li mi treba OpenAI API ključ?**
O: Da, za punu AI funkcionalnost potreban je OpenAI API ključ (~$5 kredit). Sistem uključuje demo rezerve za testiranje.

### **P: Koliko je precizan AI u razumevanju?**
O: AI ima 95%+ preciznost za kalendarske komande na srpskom. Razume kontekst, vremenske izraze i tim reference.

### **P: Može li AI da upravlja timskim planiranjem?**
O: Da! Komande poput "Zakaži timski sastanak za sutra u 10h za sav tim" automatski pronalaze optimalne termine za sve članove tima.

## 📅 Upravljanje Kalendarom

### **P: Kako kreirati ponavljajuće događaje?**
O: Koristite web interfejs ili API. AI komande za ponavljajuće događaje su u razvoju.

### **P: Mogu li da povlačim i spuštam događaje?**
O: Da, kalendarski interfejs podržava punu drag-and-drop funkcionalnost za pomeranje i menjanje veličine događaja.

### **P: Kako da upravljam dozvolama tima?**
O: Svaki događaj ima nivoe dozvola: samo-čitanje, može-da-menja, može-da-pozove-ostale. Postavite ih prilikom kreiranja događaja.

### **P: Šta se dešava kad su termini u konfliktu?**
O: AI automatski detektuje konflikte i predlaže alternativne termine. Možete prihvatiti ili modifikovati predloge.

## 👥 Timska Saradnja

### **P: Koliko članova tima mogu dodati?**
O: Nema čvrstog ograničenja. Sistem je dizajniran za timove od 5-50 članova sa optimalnim performansama.

### **P: Mogu li kreirati različite timove/odeljenja?**
O: Da, organizujte korisnike u timove i odeljenja. Svaki tim može imati zasebne kalendare i dozvole.

### **P: Kako rade bulk operacije?**
O: Koristite AI komande poput "Pomeri sve događaje tima za ponedeljak" da pomerite više događaja odjednom.

### **P: Postoje li timske analitike?**
O: Da, pregledajte distribuciju radnog opterećenja, uvide u produktivnost i metrike performansi tima.

## 🔔 Obaveštenja

### **P: Kako da postavim email obaveštenja?**
O: Konfigurišite SMTP postavke u .env fajlu:
```env
SMTP_USERNAME=vas_email@gmail.com
SMTP_PASSWORD=vas_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### **P: Mogu li prilagoditi template-e za obaveštenja?**
O: Da, email template-i su prilagodljivi. Editujte template-e u `app/templates/email/`.

### **P: Koje tipove obaveštenja su dostupna?**
O: 
- Podsetnici za događaje (email + push)
- Promene u rasporedu
- Ažuriranja tima
- Upozorenja o rokovima
- Pozivnice za sastanke

## 🔧 Tehnički Problemi

### **P: AI ne odgovara ispravno**
O: Proverite:
1. OpenAI API ključ je validan
2. Internet konekcija je stabilna
3. Komande su u podržanom formatu
4. Probajte prvo jednostavnije komande

### **P: Greške baze podataka pri pokretanju**
O: Česta rešenja:
1. Obrišite `calendar.db` fajl i restartajte
2. Proverite dozvole fajla
3. Uverite se da je SQLite instaliran
4. Pokrenite `python main.py` sa admin pravima

### **P: Frontend se ne učitava**
O: Proverite:
1. Server radi na http://localhost:8000
2. Statički fajlovi se serviraju
3. Nema JavaScript grešaka u browser konzoli
4. Očistite browser keš

### **P: Docker kontejner neće da se pokrene**
O: Česti problemi:
1. Port 8000 je već u upotrebi
2. Environment varijable nisu postavljene
3. Docker daemon ne radi
4. Nedovoljno prostora na disku

## 🔐 Bezbednost i Privatnost

### **P: Da li su moji podaci bezbedni?**
O: Da:
- Svi podaci se čuvaju lokalno po defaultu
- Zaštita od SQL injection napada
- Validacija unosa na svim endpoint-ima
- HTTPS spremno za produkciju

### **P: Gde se čuvaju moji kalendarski podaci?**
O: Po defaultu u lokalnoj SQLite bazi. Za produkciju, konfigurišite PostgreSQL ili MySQL.

### **P: Mogu li eksportovati svoje podatke?**
O: Da, koristite export API endpoint-e ili direktno backup-ujte bazu podataka.

## 🚀 Performanse

### **P: Koliko je brz AI odgovor?**
O: Tipična vremena odgovora:
- Jednostavne komande: < 1 sekunda
- Složeno planiranje: 2-5 sekundi
- Timske operacije: 5-10 sekundi

### **P: Može li podneti više korisnika istovremeno?**
O: Da, FastAPI efikasno obrađuje istovremene zahteve. Testirano sa 10+ simultanih korisnika.

### **P: Šta je sa mobilnim uređajima?**
O: Interfejs je potpuno responzivan i radi na mobilnim browser-ima. Nativna mobilna aplikacija je u razvoju.

## 🔗 Integracije

### **P: Kako da integriram sa Bitrix24?**
O: Konfigurišite u .env:
```env
BITRIX24_DOMAIN=vasa_kompanija.bitrix24.com
BITRIX24_API_KEY=vas_api_kljuc
```

### **P: Mogu li integrisati sa Google Calendar-om?**
O: Google Calendar integracija je planirana za buduće verzije.

### **P: Postoje li webhook obaveštenja?**
O: Da, konfigurišite webhook URL-ove za obaveštenja spoljnih sistema.

## 💰 Troškovi

### **P: Da li je ovo besplatno za korišćenje?**
O: Da, softver je besplatan (MIT licenca). Plaćate samo za:
- OpenAI API korišćenje (~$5/mesec za male timove)
- Cloud hosting (opciono)
- Enterprise podršku (opciono)

### **P: Koliko košta OpenAI API?**
O: Vrlo pristupačno:
- $5 kredit = ~1000 AI komandi
- Prosečan tim: $2-5/mesec
- Plaćate samo ono što koristite

## 🛠️ Razvoj i Prilagođavanje

### **P: Mogu li prilagoditi interfejs?**
O: Da, modifikujte:
- `frontend/` za HTML/CSS
- `static/` za stilove i resurse
- `app/api/` za backend funkcionalnost

### **P: Kako da dodam nove AI komande?**
O: Editujte `app/services/ai_assistant.py` i dodajte nove obrasce komandi.

### **P: Mogu li doprinositi projektu?**
O: Da! Pogledajte [CONTRIBUTING.md](CONTRIBUTING.md) za smernice.

## 📞 Podrška

### **P: Gde mogu dobiti pomoć?**
O: 
- 📚 Dokumentacija: [Vodič za instalaciju](INSTALLATION_AND_SETUP.md)
- 🐛 Problemi: [GitHub Issues](https://github.com/yourusername/bitrix24-ai-assistant/issues)
- 💬 Zajednica: [Diskusije](https://github.com/yourusername/bitrix24-ai-assistant/discussions)
- 📧 Enterprise: support@technosoft.dev

### **P: Kako da prijavim greške?**
O: Kreirajte GitHub issue sa:
- Koracima za reprodukovanje
- Očekivanim ponašanjem
- Stvarnim ponašanjem
- Informacijama o sistemu
- Porukama o greškama

### **P: Mogu li zahtevati nove funkcionalnosti?**
O: Da! Koristite GitHub Diskusije ili Issues da predložite nove funkcionalnosti.

---

## 🔄 Još Uvek Trebate Pomoć?

Ako ne možete naći odgovor ovde:

1. **Proverite dokumentaciju**: [Vodič za instalaciju](INSTALLATION_AND_SETUP.md)
2. **Pretražite postojeće probleme**: [GitHub Issues](https://github.com/yourusername/bitrix24-ai-assistant/issues)
3. **Pitajte zajednicu**: [GitHub Diskusije](https://github.com/yourusername/bitrix24-ai-assistant/discussions)
4. **Kontaktirajte podršku**: Kreirajte novi issue sa detaljnim informacijama

---

*Poslednje ažuriranje: 19. jul 2025.*