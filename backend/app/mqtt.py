import asyncio
import json
import logging

from app.config import get_settings
from app.schemas import AlertPayload

logger = logging.getLogger(__name__)


async def start_mqtt_listener(process_alert_fn) -> None:
    """
    Subscribe to MQTT broker and process messages through the same
    logic as the REST POST /api/alert endpoint.

    Activated only when MQTT_BROKER_URL is set.
    """
    settings = get_settings()
    if not settings.mqtt_broker_url:
        logger.info("MQTT_BROKER_URL not set — MQTT listener disabled.")
        return

    try:
        import aiomqtt  # type: ignore
    except ImportError:
        logger.warning("aiomqtt not installed — MQTT support unavailable.")
        return

    from app.database import AsyncSessionLocal

    logger.info(
        "Connecting to MQTT broker %s:%s, topic: %s",
        settings.mqtt_broker_url,
        settings.mqtt_port,
        settings.mqtt_topic,
    )

    reconnect_interval = 5  # seconds

    while True:
        try:
            async with aiomqtt.Client(
                hostname=settings.mqtt_broker_url,
                port=settings.mqtt_port,
            ) as client:
                await client.subscribe(settings.mqtt_topic)
                logger.info("MQTT subscribed to %s", settings.mqtt_topic)
                async for message in client.messages:
                    try:
                        raw = json.loads(message.payload.decode())
                        payload = AlertPayload(**raw)
                        async with AsyncSessionLocal() as db:
                            await process_alert_fn(payload, db)
                    except Exception as exc:
                        logger.error("MQTT message processing error: %s", exc)
        except Exception as exc:
            logger.error(
                "MQTT connection error: %s. Retrying in %ds…",
                exc,
                reconnect_interval,
            )
            await asyncio.sleep(reconnect_interval)
