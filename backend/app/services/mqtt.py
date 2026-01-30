"""MQTT Service for communication with Raspberry Pi IoT devices."""

import json
import logging
import ssl
import threading
from typing import Callable, Optional, Any
from datetime import datetime

import paho.mqtt.client as mqtt

from app.config import get_settings
from app.services.websocket import manager as ws_manager

logger = logging.getLogger(__name__)
settings = get_settings()


class MQTTService:
    """MQTT Client service for subscribing to IoT device messages."""
    
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.connected: bool = False
        self._message_handlers: dict[str, list[Callable]] = {}
        self._thread: Optional[threading.Thread] = None
    
    def connect(self) -> bool:
        """Connect to the MQTT broker."""
        if not settings.MQTT_ENABLED:
            logger.info("MQTT is disabled in settings")
            return False
        
        try:
            # Create MQTT client with protocol v5
            self.client = mqtt.Client(
                client_id=settings.MQTT_CLIENT_ID,
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2
            )
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # Set authentication if provided
            if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
                self.client.username_pw_set(
                    settings.MQTT_USERNAME,
                    settings.MQTT_PASSWORD
                )
            
            # Configure TLS if enabled
            if settings.MQTT_USE_TLS:
                self._configure_tls()
            
            # Connect to broker
            tls_status = "TLS" if settings.MQTT_USE_TLS else "non-TLS"
            logger.info(
                f"Connecting to MQTT broker at "
                f"{settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT} ({tls_status})"
            )
            self.client.connect(
                settings.MQTT_BROKER_HOST,
                settings.MQTT_BROKER_PORT,
                keepalive=60
            )
            
            # Start the loop in a background thread
            self.client.loop_start()
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def _configure_tls(self):
        """Configure TLS settings for secure connection."""
        try:
            # Create SSL context
            ssl_context = ssl.create_default_context()
            
            # Load CA certificate if provided
            if settings.MQTT_CA_CERT:
                ssl_context.load_verify_locations(settings.MQTT_CA_CERT)
                logger.info(f"Loaded CA certificate: {settings.MQTT_CA_CERT}")
            
            # Load client certificate and key if provided (mutual TLS)
            if settings.MQTT_CLIENT_CERT and settings.MQTT_CLIENT_KEY:
                ssl_context.load_cert_chain(
                    certfile=settings.MQTT_CLIENT_CERT,
                    keyfile=settings.MQTT_CLIENT_KEY
                )
                logger.info("Loaded client certificate for mutual TLS")
            
            # Set hostname verification
            if settings.MQTT_TLS_INSECURE:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                logger.warning("TLS hostname verification disabled (insecure)")
            
            # Apply TLS configuration
            self.client.tls_set_context(ssl_context)
            logger.info("TLS configuration applied successfully")
            
        except Exception as e:
            logger.error(f"Failed to configure TLS: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from the MQTT broker."""
        if self.client:
            logger.info("Disconnecting from MQTT broker")
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            self.client = None
    
    def _on_connect(self, client, userdata, flags, reason_code, properties):
        """Callback when connected to MQTT broker."""
        if reason_code == 0:
            self.connected = True
            logger.info("Connected to MQTT broker successfully")
            
            # Subscribe to all topics under the prefix
            topic = f"{settings.MQTT_TOPIC_PREFIX}/#"
            client.subscribe(topic)
            logger.info(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker: {reason_code}")
    
    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        """Callback when disconnected from MQTT broker."""
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker: {reason_code}")
    
    def _on_message(self, client, userdata, msg):
        """Callback when a message is received."""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            logger.debug(f"Received message on {topic}: {payload}")
            
            # Parse JSON payload
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                data = {"raw": payload}
            
            # Add metadata
            message = {
                "topic": topic,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            # Call registered handlers for this topic
            self._dispatch_message(topic, message)
            
            # Broadcast to WebSocket clients
            self._broadcast_to_websocket(message)
            
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def _dispatch_message(self, topic: str, message: dict):
        """Dispatch message to registered handlers."""
        # Check exact topic match
        if topic in self._message_handlers:
            for handler in self._message_handlers[topic]:
                try:
                    handler(message)
                except Exception as e:
                    logger.error(f"Error in message handler: {e}")
        
        # Check wildcard matches (e.g., "autobox/sensor/#")
        for pattern, handlers in self._message_handlers.items():
            if self._topic_matches(pattern, topic):
                for handler in handlers:
                    try:
                        handler(message)
                    except Exception as e:
                        logger.error(f"Error in message handler: {e}")
    
    def _topic_matches(self, pattern: str, topic: str) -> bool:
        """Check if a topic matches a pattern with wildcards."""
        if pattern == topic:
            return False  # Already handled in exact match
        
        pattern_parts = pattern.split('/')
        topic_parts = topic.split('/')
        
        for i, part in enumerate(pattern_parts):
            if part == '#':
                return True  # Multi-level wildcard matches everything after
            if part == '+':
                continue  # Single-level wildcard matches any single level
            if i >= len(topic_parts) or part != topic_parts[i]:
                return False
        
        return len(pattern_parts) == len(topic_parts)
    
    def _broadcast_to_websocket(self, message: dict):
        """Broadcast MQTT message to WebSocket clients."""
        import asyncio
        
        try:
            # Create async task to broadcast
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                ws_manager.broadcast({
                    "type": "mqtt_message",
                    "payload": message
                })
            )
            loop.close()
        except Exception as e:
            logger.debug(f"Could not broadcast to WebSocket: {e}")
    
    def publish(self, topic: str, payload: Any, qos: int = 0, retain: bool = False) -> bool:
        """Publish a message to the MQTT broker."""
        if not self.client or not self.connected:
            logger.warning("Cannot publish: not connected to MQTT broker")
            return False
        
        try:
            # Convert payload to JSON string if it's a dict
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            
            full_topic = f"server_msg/{topic}"
            result = self.client.publish(full_topic, payload, qos=qos, retain=retain)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published to {full_topic}: {payload}")
                return True
            else:
                logger.error(f"Failed to publish message: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing MQTT message: {e}")
            return False
    
    def subscribe(self, topic: str, handler: Callable[[dict], None]):
        """Register a handler for a specific topic."""
        full_topic = f"{settings.MQTT_TOPIC_PREFIX}/{topic}"
        
        if full_topic not in self._message_handlers:
            self._message_handlers[full_topic] = []
        
        self._message_handlers[full_topic].append(handler)
        logger.info(f"Registered handler for topic: {full_topic}")
    
    def unsubscribe(self, topic: str, handler: Callable[[dict], None]):
        """Remove a handler for a specific topic."""
        full_topic = f"{settings.MQTT_TOPIC_PREFIX}/{topic}"
        
        if full_topic in self._message_handlers:
            if handler in self._message_handlers[full_topic]:
                self._message_handlers[full_topic].remove(handler)
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to MQTT broker."""
        return self.connected


# Global MQTT service instance
mqtt_service = MQTTService()


# Example message handlers
def handle_sensor_data(message: dict):
    """Handle sensor data from IoT devices."""
    logger.info(f"Sensor data received: {message}")
    
    # Store sensor data in database
    try:
        from app.database import SessionLocal
        from app.models.vehicle import SensorStatus
        
        data = message.get("data", {})
        if not data:
            return
        
        vehicle_id = data.get("vehicle_id", "AGV-001")
        
        db = SessionLocal()
        try:
            # Handle individual sensor update
            if "sensor_name" in data:
                sensor = db.query(SensorStatus).filter(
                    SensorStatus.vehicle_id == vehicle_id,
                    SensorStatus.sensor_name == data["sensor_name"]
                ).first()
                
                if sensor:
                    sensor.status = data.get("status", "ok")
                    sensor.value = data.get("value")
                    sensor.health = data.get("health", 100)
                    sensor.data = data.get("data")
                else:
                    sensor = SensorStatus(
                        vehicle_id=vehicle_id,
                        sensor_name=data["sensor_name"],
                        sensor_type=data.get("sensor_type"),
                        status=data.get("status", "ok"),
                        value=data.get("value"),
                        health=data.get("health", 100),
                        data=data.get("data")
                    )
                    db.add(sensor)
                
                db.commit()
                logger.info(f"Sensor status updated: {vehicle_id}/{data['sensor_name']}")
            
            # Handle bulk sensor update (multiple sensors in one message)
            elif "sensors" in data:
                for sensor_data in data["sensors"]:
                    sensor = db.query(SensorStatus).filter(
                        SensorStatus.vehicle_id == vehicle_id,
                        SensorStatus.sensor_name == sensor_data["name"]
                    ).first()
                    
                    if sensor:
                        sensor.status = sensor_data.get("status", "ok")
                        sensor.value = sensor_data.get("value")
                        sensor.health = sensor_data.get("health", 100)
                    else:
                        sensor = SensorStatus(
                            vehicle_id=vehicle_id,
                            sensor_name=sensor_data["name"],
                            sensor_type=sensor_data.get("type"),
                            status=sensor_data.get("status", "ok"),
                            value=sensor_data.get("value"),
                            health=sensor_data.get("health", 100)
                        )
                        db.add(sensor)
                
                db.commit()
                logger.info(f"Bulk sensor status updated for: {vehicle_id}")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error storing sensor data: {e}")


def handle_vehicle_position(message: dict):
    """Handle vehicle position updates from IoT devices."""
    logger.info(f"Vehicle position received: {message}")
    
    # Store vehicle position in database
    try:
        from app.database import SessionLocal
        from app.models.vehicle import VehiclePosition
        
        data = message.get("data", {})
        if not data:
            return
        
        vehicle_id = data.get("vehicle_id", "AGV-001")
        
        db = SessionLocal()
        try:
            # Find existing position record or create new one
            position = db.query(VehiclePosition).filter(
                VehiclePosition.vehicle_id == vehicle_id
            ).first()
            
            if position:
                position.x = data.get("x", position.x)
                position.y = data.get("y", position.y)
                position.angle = data.get("angle", position.angle)
                position.speed = data.get("speed", position.speed)
                position.battery = data.get("battery", position.battery)
                position.mode = data.get("mode", position.mode)
            else:
                position = VehiclePosition(
                    vehicle_id=vehicle_id,
                    x=data.get("x", 0),
                    y=data.get("y", 0),
                    angle=data.get("angle", 0),
                    speed=data.get("speed", 0),
                    battery=data.get("battery", 100),
                    mode=data.get("mode", "IDLE")
                )
                db.add(position)
            
            db.commit()
            logger.info(f"Vehicle position updated: {vehicle_id} at ({position.x}, {position.y})")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error storing vehicle position: {e}")


def handle_device_status(message: dict):
    """Handle device status updates."""
    logger.info(f"Device status update: {message}")
    
    # Store device status in database
    try:
        from app.database import SessionLocal
        from app.models.device import DeviceStatus, OperationStatus
        
        data = message.get("data", {})
        if not data:
            return
        
        device_id = data.get("device_id")
        if not device_id:
            return
        
        db = SessionLocal()
        try:
            device = db.query(DeviceStatus).filter(
                DeviceStatus.device_id == device_id
            ).first()
            
            if device:
                device.battery_level = data.get("battery_level", device.battery_level)
                device.is_connected = data.get("is_connected", device.is_connected)
                device.cpu_temperature = data.get("cpu_temperature")
                device.location = data.get("location")
                if "operation_status" in data:
                    device.operation_status = OperationStatus(data["operation_status"])
            else:
                device = DeviceStatus(
                    device_id=device_id,
                    battery_level=data.get("battery_level", 0),
                    is_connected=data.get("is_connected", True),
                    cpu_temperature=data.get("cpu_temperature"),
                    location=data.get("location"),
                    operation_status=OperationStatus(data.get("operation_status", "STOP"))
                )
                db.add(device)
            
            db.commit()
            logger.info(f"Device status updated: {device_id}")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error storing device status: {e}")


def handle_alert_notification(message: dict):
    """Handle alert notifications from devices."""
    logger.info(f"Alert notification: {message}")
    
    # Create alert record in database
    try:
        from app.database import SessionLocal
        from app.models.alert import Alert, AlertSeverity
        
        data = message.get("data", {})
        if not data:
            return
        
        db = SessionLocal()
        try:
            alert = Alert(
                alert_type=data.get("alert_type", "system"),
                severity=AlertSeverity(data.get("severity", "info")),
                title=data.get("title", "시스템 알림"),
                message=data.get("message", ""),
                source_type=data.get("source_type"),
                source_id=data.get("source_id")
            )
            db.add(alert)
            db.commit()
            logger.info(f"Alert created: {alert.alert_id}")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error creating alert: {e}")


# Register default handlers
def register_default_handlers():
    """Register default message handlers."""
    mqtt_service.subscribe("sensor/#", handle_sensor_data)
    mqtt_service.subscribe("vehicle/position", handle_vehicle_position)
    mqtt_service.subscribe("vehicle/#", handle_vehicle_position)
    mqtt_service.subscribe("device/status", handle_device_status)
    mqtt_service.subscribe("alert/#", handle_alert_notification)
