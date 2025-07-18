# 🤖 AI Commands Reference

Complete guide to using the Bitrix24 AI Assistant with natural language commands in Serbian and English.

## 📋 Individual AI Commands

### **Calendar Management**
```serbian
"Dodaj sastanak sutra u 14h"
"Pomeri moj sastanak za ponedeljak u 10h"
"Obriši sve događaje za sredu"
"Pronađi mi slobodan termin za 2 sata"
```

```english
"Add meeting tomorrow at 2pm"
"Move my meeting to Monday at 10am"
"Delete all events for Wednesday"
"Find me a free 2-hour slot"
```

### **Schedule Analysis**
```serbian
"Kako mi izgleda sledeća nedelja?"
"Kada je moj sledeći sastanak?"
"Koliko imam slobodnog vremena danas?"
"Šta imam zakazano za sutra?"
```

```english
"How does my next week look?"
"When is my next meeting?"
"How much free time do I have today?"
"What do I have scheduled for tomorrow?"
```

### **Smart Recommendations**
```serbian
"Predloži mi najbolje termine za sastanke"
"Optimizuj mi raspored za sledeću nedelju"
"Preporuči mi kada da zakazujem važne sastanke"
```

```english
"Suggest the best meeting times"
"Optimize my schedule for next week"
"Recommend when to schedule important meetings"
```

## 👥 Team AI Commands

### **Team Scheduling**
```serbian
"Zakaži timski sastanak za sutra u 10h za sav tim"
"Pronađi najbolji termin za sve članove tima"
"Zakaži brainstorming sesiju sa marketing timom"
```

```english
"Schedule team meeting tomorrow at 10am for whole team"
"Find the best time slot for all team members"
"Schedule brainstorming session with marketing team"
```

### **Bulk Operations**
```serbian
"Pomeri sve događaje tima za ponedeljak"
"Obriši sve sastanke za sredu"
"Ažuriraj prioritete za sve projekte"
```

```english
"Move all team events to Monday"
"Delete all meetings for Wednesday"
"Update priorities for all projects"
```

### **Team Analysis**
```serbian
"Analiziraj raspored celog tima za sledeću nedelju"
"Proveri konflikte u rasporedu tima"
"Optimizuj workload za ceo tim"
"Balansiranje radnog vremena"
```

```english
"Analyze entire team schedule for next week"
"Check conflicts in team schedule"
"Optimize workload for entire team"
"Balance working hours"
```

## 🎯 Command Patterns

### **Time Expressions**
- **Relative**: sutra, prekosutra, sledeća nedelja, za 2 dana
- **Absolute**: 25. jul, ponedeljak, 15:30, 14h
- **Duration**: 2 sata, 30 minuta, ceo dan, pola sata

### **Event Types**
- **Meetings**: sastanak, meeting, call, poziv
- **Tasks**: zadatak, task, posao, aktivnost  
- **Deadlines**: deadline, rok, krajnji termin
- **Reminders**: podsetnik, reminder, napomena

### **Team References**
- **Specific**: Milan, Ana, marketing tim, development tim
- **Generic**: sav tim, ceo tim, svi, grupa, članovi

## ⚙️ Advanced Features

### **Conditional Commands**
```serbian
"Ako nema konflikata, zakaži sastanak u 14h"
"Pomeri sastanak samo ako je moguće u jutarnjim satima"
"Dodaj podsetnik osim ako već postoji"
```

### **Batch Processing**
```serbian
"Za sve projekte: dodaj podsetnik za deadline"
"Za sav tim: pomeri sastanke za sat vremena ranije"
"Za sledeću nedelju: oslobodi petak posle 15h"
```

### **Smart Filtering**
```serbian
"Prikaži samo važne događaje"
"Sakrij sve podsetnike"
"Filtriraj po timu development"
```

## 🔍 Response Types

### **Success Responses**
- Event created successfully
- Schedule updated
- Team notification sent
- Conflicts resolved

### **Clarification Requests**
- "Which team members should I include?"
- "What priority should I set?"
- "Should I send notifications?"

### **Error Handling**
- Time slot not available
- Team member not found
- Invalid date format
- Permission denied

## 💡 Best Practices

### **Clear Commands**
- Be specific with times and dates
- Mention all required attendees
- Specify duration when needed
- Include priority levels

### **Team Commands**
- Always specify which team members
- Use clear meeting titles
- Set realistic durations
- Consider time zones

### **Follow-up Actions**
- Confirm important changes
- Check for conflicts after bulk operations
- Verify team availability
- Set appropriate reminders

## 🛠️ API Integration

### **Command Processing**
```http
POST /api/ai/chat
{
  "message": "Zakaži sastanak sutra u 14h",
  "user_id": 1,
  "context": "calendar"
}
```

### **Team Commands**
```http
POST /api/calendar/team/ai-command
{
  "command": "Zakaži timski sastanak za sutra",
  "user_id": 1,
  "team_members": [1, 2, 3, 4]
}
```

---

*For technical implementation details, see [API Documentation](http://localhost:8000/docs)*
*For troubleshooting, see [FAQ](FAQ.md)*