# 🏭 UNS Semantic Gateway

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-ISA--95-green)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![MQTT](https://img.shields.io/badge/Protocol-MQTT-purple)

A **DataOps middleware** that transforms legacy brownfield MQTT data into a clean, ISA-95 compliant **Unified Namespace**.

## The Problem

Most factories are "Brownfield" — legacy PLCs output unstructured, context-less data:

```
legacy/plc_01/register_4001 → {"v": 185.5}
```

No metadata. No semantic meaning. No interoperability.

## The Solution

A **Semantic Gateway** that:
1. **Ingests** raw legacy MQTT tags
2. **Contextualizes** using a configurable tag map
3. **Normalizes** to strict ISA-95 Pydantic schema
4. **Publishes** to the Unified Namespace

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────────────────────────┐
│   Legacy PLC    │ ──▶ │   Semantic Gateway   │ ──▶ │   Unified Namespace                 │
│   {"v": 185.5}  │     │   (Context Engine)   │     │   Acme/Berlin/Line1/Oven/Temperature│
└─────────────────┘     └──────────────────────┘     └─────────────────────────────────────┘
```

### Output Payload (ISA-95 Compliant)

```json
{
  "value": 185.5,
  "timestamp": 1703856000000,
  "quality": "Good",
  "unit": "Celsius",
  "asset_id": "OVEN-01",
  "metadata": {"description": "Main Heating Zone"}
}
```

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/hadijannat/uns-semantic-gateway.git
cd uns-semantic-gateway

# Start the entire stack
docker-compose up --build
```

You'll see the transformation in real-time:

```
legacy/plc_01/register_4001  ➔  Acme/Berlin/Extrusion/Line1/Oven/Temperature  185.5 Celsius
legacy/plc_01/register_4002  ➔  Acme/Berlin/Extrusion/Line1/Conveyor/Speed    1.25 m/s
```

## 🔧 Configuration

Edit `config/mapping.yaml` to define your tag mappings:

```yaml
tags:
  "legacy/plc_01/register_4001":
    uns_topic: "Acme/Berlin/Extrusion/Line1/Oven/Temperature"
    unit: "Celsius"
    asset_id: "OVEN-01"
    description: "Main Heating Zone"
```

## 🏗️ Architecture

```
/uns-semantic-gateway
├── src/
│   ├── main.py              # Gateway Engine
│   └── domain/
│       └── models.py        # ISA-95 Pydantic Schema
├── config/
│   ├── mapping.yaml         # Tag Database
│   └── mosquitto.conf       # Broker Config
├── tools/
│   └── simulator.py         # Legacy PLC Simulator
├── docker-compose.yml
└── Dockerfile
```

## 🔬 Verification

Use [MQTT Explorer](https://mqtt-explorer.com/) to visualize:
- **Legacy topics** (`legacy/...`) with raw `{"v": ...}` payloads
- **UNS topics** (`Acme/...`) with enriched, structured JSON

## 📈 Future Improvements

- **Sparkplug B**: Currently uses JSON for readability. A production version would utilize **Sparkplug B** payloads for bandwidth efficiency and state management (Birth/Death certificates).
- **Schema Registry**: Integrate with Confluent Schema Registry for payload evolution.
- **Metrics**: Add Prometheus metrics for observability.
- **Dead Letter Queue**: Handle unmapped tags gracefully.

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11 |
| Validation | Pydantic V2 |
| MQTT Client | Paho MQTT V2 |
| CLI Visualization | Rich |
| Infrastructure | Docker Compose |

## 📄 License

MIT
