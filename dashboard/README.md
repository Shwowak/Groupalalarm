# GroupAlarm Dashboard

## Einbinden in Home Assistant

### Option A – Als eigene Dashboard-Datei (empfohlen)

1. Datei `groupalarm-dashboard.yaml` nach `config/` kopieren
2. In `configuration.yaml` eintragen:

```yaml
lovelace:
  mode: yaml
  dashboards:
    groupalarm:
      mode: yaml
      title: GroupAlarm
      icon: mdi:alarm-light
      show_in_sidebar: true
      filename: groupalarm-dashboard.yaml
```

3. HA neu starten → In der Seitenleiste erscheint "GroupAlarm"

### Option B – In bestehendes Dashboard einfügen

Inhalt aus `groupalarm-dashboard.yaml` → Abschnitt `cards:` kopieren und in dein bestehendes Dashboard einfügen.

---

## Dashboard-Inhalt

| Bereich | Beschreibung |
|---------|-------------|
| 🔴 Alarm-Banner | Roter Banner wenn Alarm aktiv, grün wenn ruhig |
| 📊 Status-Kacheln | Aktive Alarme, Historien-Zähler, Status |
| 📨 Rückmeldung | Buttons: Ja / Nein / Später direkt im Dashboard |
| ℹ️ Alarm-Details | Stichwort, Adresse, Meldung, Uhrzeit des aktuellen Alarms |
| 📋 Letzte Alarme | Tabelle der letzten 10 Alarme mit Status |

---

## Benötigte Entitäten

- `binary_sensor.groupalarm_alarm_aktiv`
- `sensor.groupalarm_aktive_alarme`
- `sensor.groupalarm_letzter_alarm`
- `sensor.groupalarm_letzte_alarme`
