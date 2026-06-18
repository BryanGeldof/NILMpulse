import logging
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change_event
from .const import DOMAIN, CONF_P1_SENSOR

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    p1_sensor_id = config_entry.data.get(CONF_P1_SENSOR)
    analyzer = hass.data[DOMAIN]["analyzer"]

    unknown_sensor = NILMpulseUnknownSensor(analyzer, p1_sensor_id)
    efficiency_sensor = NILMpulseEfficiencySensor(analyzer, p1_sensor_id)

    async_add_entities([unknown_sensor, efficiency_sensor])

    # Luister live naar de P1 meter updates zonder de boel te blokkeren
    async def _async_p1_state_changed(event):
        new_state = event.data.get("new_state")
        if new_state and new_state.state not in ['unknown', 'unavailable']:
            try:
                total_power = float(new_state.state)
                # Bereken de nieuwe statistieken in de analyzer
                _, unknown_rest = analyzer.process_reading(total_power)
                
                # Push de waarden direct live naar de sensoren
                unknown_sensor.update_value(unknown_rest)
                efficiency_sensor.update_value(total_power, unknown_rest)
            except ValueError:
                pass

    async_track_state_change_event(hass, [p1_sensor_id], _async_p1_state_changed)


class NILMpulseUnknownSensor(Entity):
    def __init__(self, analyzer, p1_sensor_id):
        self._analyzer = analyzer
        self._state = 0

    @property
    def name(self): return "NILMpulse Unknown Restwaarde"
    @property
    def unique_id(self): return "nilmpulse_unknown_restwaarde"
    @property
    def state(self): return self._state
    @property
    def unit_of_measurement(self): return "W"
    @property
    def icon(self): return "mdi:help-circle-outline"
    @property
    def should_poll(self): return False

    def update_value(self, value):
        self._state = value
        self.async_write_ha_state()


class NILMpulseEfficiencySensor(Entity):
    def __init__(self, analyzer, p1_sensor_id):
        self._analyzer = analyzer
        self._state = 100

    @property
    def name(self): return "NILMpulse Deconstructie Efficiëntie"
    @property
    def unique_id(self): return "nilmpulse_deconstructie_efficiency"
    @property
    def state(self): return self._state
    @property
    def unit_of_measurement(self): return "%"
    @property
    def icon(self): return "mdi:shield-check"
    @property
    def should_poll(self): return False

    def update_value(self, total_grid, unknown_rest):
        if total_grid > 0:
            acc = 1 - (unknown_rest / (2 * total_grid))
            self._state = min(100, max(0, round(acc * 100)))
        else:
            self._state = 100
        self.async_write_ha_state()
