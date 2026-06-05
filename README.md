# GroupAlarm Home Assistant Integration

Custom Integration für [GroupAlarm](https://www.groupalarm.com) in Home Assistant.

## Funktionen

- 🚨 **Alarme empfangen** – Neue Alarme werden als HA-Events gefeuert
- 📊 **Status abfragen** – Sensoren für aktive Alarmanzahl und letzten Alarm
- ✅ **Rückmeldungen senden** – Service `groupalarm.send_feedback` (ja/nein/später)

---

## Installation via HACS (empfohlen)

1. **HACS öffnen** → Integrationen
2. Oben rechts: **⋮ → Benutzerdefiniertes Repository**
3. URL: `https://github.com/rittelj/groupalarm-ha` · Kategorie: **Integration**
4. **Hinzufügen** → in der Liste **GroupAlarm** suchen → Herunterladen
5. Home Assistant neu starten

## Installation manuell

1. Ordner `custom_components/groupalarm/` nach `config/custom_components/groupalarm/` kopieren
2. HA neu starten

---

## Konfiguration

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen → GroupAlarm**
2. Ausfüllen:
   - **API-Key**: app.groupalarm.com → Einstellungen → API-Token
   - **Organisations-ID**: Zahl aus der GroupAlarm-URL oder den Einstellungen
   - **Abfrageintervall**: Standard 30 Sekunden (empfohlen: 10–30 s)

---

## Sensoren

| Entität | Beschreibung |
|---------|-------------|
| `sensor.groupalarm_aktive_alarme` | Anzahl aktiver Alarme |
| `sensor.groupalarm_letzter_alarm` | Stichwort des letzten Alarms |
| `binary_sensor.groupalarm_alarm_aktiv` | `on` wenn Alarm aktiv |

## Events

| Event | Beschreibung |
|-------|-------------|
| `groupalarm_alarm_received` | Neuer Alarm eingegangen |
| `groupalarm_alarm_closed` | Alarm geschlossen |

### Event-Daten (`groupalarm_alarm_received`)
```yaml
alarm_id: 12345
keyword: "THL Klein"
message: "Türöffnung"
address: "Musterstraße 1, 12345 Musterstadt"
created_at: "2024-01-01T12:00:00Z"
organization_id: 678
```

---

## Services

### `groupalarm.send_feedback`
```yaml
service: groupalarm.send_feedback
data:
  alarm_id: 12345
  feedback: "yes"  # yes | no | later
```

---

## Automation-Beispiele

### Benachrichtigung bei Alarm
```yaml
automation:
  - alias: "GroupAlarm Benachrichtigung"
    trigger:
      - platform: event
        event_type: groupalarm_alarm_received
    action:
      - service: notify.mobile_app_dein_handy
        data:
          title: "🚨 {{ trigger.event.data.keyword }}"
          message: "📍 {{ trigger.event.data.address }}"
```

### Automatisch Rückmeldung senden
```yaml
automation:
  - alias: "GroupAlarm Auto-Rückmeldung"
    trigger:
      - platform: event
        event_type: groupalarm_alarm_received
    action:
      - service: groupalarm.send_feedback
        data:
          alarm_id: "{{ trigger.event.data.alarm_id }}"
          feedback: "yes"
```

### Licht rot bei Alarm
```yaml
automation:
  - alias: "Alarm-Licht"
    trigger:
      - platform: state
        entity_id: binary_sensor.groupalarm_alarm_aktiv
        to: "on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.wohnzimmer
        data:
          color_name: red
          brightness: 255
```
