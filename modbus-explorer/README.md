# 🔌 Modbus Explorer

[![Home Assistant Add-on](https://img.shields.io/badge/Home%20Assistant-Add--on-blue.svg?logo=home-assistant)](https://www.home-assistant.io/)
[![GitHub Release](https://img.shields.io/github/v/release/marius945/Modbus-Explorer?label=Version)](https://github.com/marius945/Modbus-Explorer/releases)
[![License](https://img.shields.io/github/license/marius945/Modbus-Explorer)](LICENSE)

Ein **Home Assistant Add-on** zum flexiblen Lesen und Schreiben von Modbus-Registern über eine benutzerfreundliche Web-Oberfläche.

---

## ✨ Funktionen

| Funktion | Beschreibung |
|----------|--------------|
| 📖 **Register lesen** | Holding, Input, Coils und Discrete Inputs |
| ✏️ **Register schreiben** | Werte in Holding Register und Coils schreiben |
| 🔍 **Bereich scannen** | Mehrere Register auf einmal auslesen |
| 🧪 **Schreibtest** | Prüfen ob ein Register beschreibbar ist |
| 🎨 **Dark Theme** | Passt perfekt zur Home Assistant Oberfläche |
| 🚀 **Ingress** | Direkt aus der HA-Sidebar erreichbar |

---

## 📦 Installation

### Schritt 1: Repository hinzufügen

1. Öffne **Home Assistant**
2. Gehe zu **Einstellungen → Add-ons → Add-on Store**
3. Klicke oben rechts auf das **Drei-Punkte-Menü** (⋮)
4. Wähle **Repositories**
5. Füge diese URL hinzu:

```
https://github.com/marius945/Modbus-Explorer
```

6. Klicke auf **Hinzufügen**

### Schritt 2: Add-on installieren

1. Suche nach **"Modbus Explorer"** im Add-on Store
2. Klicke auf **Installieren**
3. Nach der Installation: **Starten**
4. **"In Seitenleiste anzeigen"** aktivieren

---

## 🚀 Verwendung

### Verbindung herstellen

1. Öffne **Modbus Explorer** aus der Seitenleiste
2. Gib die **IP-Adresse** deines Modbus-Geräts ein
3. Setze **Port** (Standard: 502) und **Slave-ID** (Standard: 1)

### Register lesen

1. Wähle die **Register-Adresse**
2. Wähle den **Register-Typ** und **Datentyp**
3. Klicke auf **"Wert lesen"**

### Register schreiben

1. Lies zuerst den aktuellen Wert
2. Wenn das Register schreibbar ist, erscheint das Eingabefeld
3. Gib den neuen Wert ein und klicke **"Schreiben"**

### Bereich scannen

1. Gib **Start-** und **End-Adresse** ein
2. Klicke auf **"Register scannen"**
3. Klicke auf **"Bearbeiten"** um einen Wert zu ändern

---

## 📋 Register-Typen

| Typ | Lesen | Schreiben | Beschreibung |
|-----|:-----:|:---------:|--------------|
| **Holding Register** | ✅ | ✅ | Lese-/Schreibregister (Funktionscodes 3, 6, 16) |
| **Input Register** | ✅ | ❌ | Nur-Lese-Register (Funktionscode 4) |
| **Coil** | ✅ | ✅ | Lese-/Schreib-Bits (Funktionscodes 1, 5) |
| **Discrete Input** | ✅ | ❌ | Nur-Lese-Bits (Funktionscode 2) |

---

## 🔢 Datentypen

| Typ | Größe | Wertebereich |
|-----|-------|--------------|
| `uint16` | 1 Register | 0 bis 65.535 |
| `int16` | 1 Register | -32.768 bis 32.767 |
| `uint32` | 2 Register | 0 bis 4.294.967.295 |
| `int32` | 2 Register | -2.147.483.648 bis 2.147.483.647 |
| `float32` | 2 Register | Gleitkommazahl (32-Bit) |
| `uint64` | 4 Register | 0 bis 18.446.744.073.709.551.615 |
| `int64` | 4 Register | Große Ganzzahl mit Vorzeichen |
| `float64` | 4 Register | Gleitkommazahl (64-Bit) |

---

## ⚙️ Konfiguration

```yaml
default_port: 502        # Standard Modbus TCP Port
default_slave_id: 1      # Standard Modbus Slave/Unit ID
timeout: 5               # Verbindungs-Timeout in Sekunden
```

---

## 🔧 Fehlerbehebung

### Verbindung fehlgeschlagen

- ✅ Überprüfe die IP-Adresse
- ✅ Stelle sicher, dass Port 502 nicht blockiert ist
- ✅ Prüfe ob das Modbus-Gerät eingeschaltet und im Netzwerk ist

### Schreiben fehlgeschlagen

- Das Register ist möglicherweise schreibgeschützt
- Prüfe die Dokumentation deines Geräts
- Überprüfe die korrekte Slave-ID

### Falsche Werte

- Überprüfe ob der Datentyp mit der Register-Spezifikation übereinstimmt
- Manche Geräte verwenden eine andere Byte-Reihenfolge

---

## 🤝 Beitragen

Beiträge sind willkommen! Öffne gerne ein [Issue](https://github.com/marius945/Modbus-Explorer/issues) oder einen Pull Request.

---

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE) für Details.

---

<p align="center">
  <strong>Entwickelt für die Home Assistant Community</strong><br>
  <a href="https://github.com/marius945/Modbus-Explorer">GitHub</a> •
  <a href="https://github.com/marius945/Modbus-Explorer/issues">Issues</a>
</p>
