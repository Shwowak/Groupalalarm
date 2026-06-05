"""Constants for the GroupAlarm integration."""

DOMAIN = "groupalarm"

# Config entries
CONF_API_KEY = "api_key"
CONF_ORGANIZATION_ID = "organization_id"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_SCAN_INTERVAL = 30  # seconds

# API
API_BASE_URL = "https://app.groupalarm.com/api/v1"
API_TIMEOUT = 10

# Events
EVENT_ALARM_RECEIVED = f"{DOMAIN}_alarm_received"
EVENT_ALARM_CLOSED = f"{DOMAIN}_alarm_closed"

# Platforms
PLATFORMS = ["sensor", "binary_sensor"]

# Alarm states
ALARM_STATE_ACTIVE = "active"
ALARM_STATE_CLOSED = "closed"
ALARM_STATE_UNKNOWN = "unknown"

# Services
SERVICE_SEND_FEEDBACK = "send_feedback"
ATTR_ALARM_ID = "alarm_id"
ATTR_FEEDBACK = "feedback"

# Feedback values
FEEDBACK_YES = "yes"
FEEDBACK_NO = "no"
FEEDBACK_LATER = "later"
