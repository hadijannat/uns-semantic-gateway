"""
UNS Semantic Gateway
A DataOps middleware that transforms legacy MQTT data into ISA-95 compliant
Unified Namespace payloads.
"""

import json
import yaml
import sys
import logging
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler
from paho.mqtt import client as mqtt_client

from src.domain.models import UNSPayload

# --- Setup Observability ---
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
log = logging.getLogger("gateway")
console = Console()

# --- Configuration ---
BROKER = "mosquitto"
PORT = 1883
CONFIG_PATH = "config/mapping.yaml"


class SemanticGateway:
    """
    Core gateway engine that:
    1. Ingests raw legacy MQTT data
    2. Contextualizes using the tag map
    3. Normalizes to ISA-95 schema
    4. Publishes to Unified Namespace
    """

    def __init__(self):
        self.tag_map = self._load_config()
        # Use Paho MQTT V2 API
        self.client = mqtt_client.Client(
            mqtt_client.CallbackAPIVersion.VERSION2,
            client_id="UNS_Gateway"
        )
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect

    def _load_config(self) -> dict:
        """Load tag mapping from YAML configuration."""
        try:
            with open(CONFIG_PATH, "r") as f:
                data = yaml.safe_load(f)
                log.info(f"📋 Loaded {len(data['tags'])} tag mappings")
                return data["tags"]
        except Exception as e:
            log.critical(f"Config Load Failed: {e}")
            sys.exit(1)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        """Callback when connected to broker."""
        if reason_code == 0:
            log.info("✅ Connected to UNS Broker")
            # Subscribe to all legacy sources found in config
            for topic in self.tag_map.keys():
                client.subscribe(topic)
                log.info(f"👂 Subscribed: [dim]{topic}[/dim]", extra={"markup": True})
        else:
            log.error(f"Connection failed with code: {reason_code}")

    def on_message(self, client, userdata, msg):
        """
        Core transformation logic:
        Legacy Data -> Contextualize -> Normalize -> Publish to UNS
        """
        try:
            legacy_topic = msg.topic

            # 1. Ingest (Parse "Messy" Legacy Data)
            # Assumption: Legacy PLC sends {"v": 12.3}
            raw_payload = json.loads(msg.payload.decode())
            raw_value = raw_payload.get("v")

            if legacy_topic in self.tag_map:
                ctx = self.tag_map[legacy_topic]

                # 2. Contextualize & Normalize (The Core Value)
                clean_packet = UNSPayload(
                    value=raw_value,
                    unit=ctx["unit"],
                    asset_id=ctx["asset_id"],
                    metadata={"description": ctx["description"]}
                )

                # 3. Publish to Unified Namespace
                target_topic = ctx["uns_topic"]
                client.publish(target_topic, clean_packet.to_json(), retain=True)

                # 4. Visualize Transformation
                self._render_transformation(
                    legacy_topic, target_topic, raw_value, clean_packet
                )

        except json.JSONDecodeError as e:
            log.warning(f"Invalid JSON from {msg.topic}: {e}")
        except Exception as e:
            log.error(f"Processing Error: {e}")

    def _render_transformation(self, src: str, dst: str, val: float, packet: UNSPayload):
        """Display before/after transformation in Rich table."""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row(
            f"[red]{src}[/red]",
            "➔",
            f"[green]{dst}[/green]",
            f"[bold cyan]{val} {packet.unit}[/bold cyan]"
        )
        console.print(table)

    def run(self):
        """Start the gateway and enter the event loop."""
        console.print("\n[bold magenta]🏭 UNS Semantic Gateway[/bold magenta]")
        console.print("[dim]Brownfield → ISA-95 → Unified Namespace[/dim]\n")

        try:
            self.client.connect(BROKER, PORT)
            log.info(f"🔌 Connecting to {BROKER}:{PORT}...")
            self.client.loop_forever()
        except KeyboardInterrupt:
            log.info("🛑 Shutting down gracefully...")
            self.client.disconnect()
        except Exception as e:
            log.critical(f"Fatal error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    gateway = SemanticGateway()
    gateway.run()
