import logging
from homeassistant.helpers.entity import Entity
from .const import DOMAIN, CONF_P1_SENSOR
from .analyzer import PeakSenseClusterAnalyzer

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    p1_sensor_id = config_entry.data.get(CONF_P1_SENSOR)
    
    # Initialiseer de overkoepelende AI engine in de HASS datastructuur
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
        
    analyzer = PeakSenseClusterAnalyzer(hass)
    hass.data[DOMAIN]["analyzer"] = analyzer

    # Voeg de standaard basissensoren toe
    entities = [
        PeakSenseUnknownSensor(analyzer, p1_sensor_id),
        PeakSenseEfficiencySensor(analyzer, p1_sensor_id)
    ]
    async_add_entities(entities, update_before_add=True)

class PeakSenseUnknownSensor(Entity):
    def __init__(self, analyzer, p1_sensor_id):
        self._analyzer = analyzer
        self._p1_sensor_id = p1_sensor_id
        self._state = 0

    @property
    def name(self): return "PeakSense Unknown Restwaarde"
    @property
    def unique_id(self): return "peaksense_unknown_restwaarde"
    @property
    def state(self): return self._state
    @property
    def unit_of_measurement(self): return "W"
    @property
    def icon(self): return "mdi:help-circle-outline"

    async def async_update(self):
        # Haal de live waarde op van de gekoppelde P1-meter
        p1_state = self.hass.states.get(self._p1_sensor_id)
        if p1_state and p1_state.state not in ['unknown', 'unavailable']:
            total_power = float(p1_state.state)
            _, unknown_rest = self._analyzer.process_reading(total_power)
            self._state = unknown_rest

class PeakSenseEfficiencySensor(Entity):
    def __init__(self, analyzer, p1_sensor_id):
        self._analyzer = analyzer
        self._p1_sensor_id = p1_sensor_id
        self._state = 100

    @property
    def name(self): return "PeakSense Deconstructie Efficiëntie"
    @property
    def unique_id(self): return "peaksense_deconstructie_efficiency"
    @property
    def state(self): return self._state
    @property
    def unit_of_measurement(self): return "%"
    @property
    def icon(self): return "mdi:shield-check"

    async def async_update(self):
        p1_state = self.hass.states.get(self._p1_sensor_id)
        if p1_state and p1_state.state not in ['unknown', 'unavailable']:
            total_grid = float(p1_state.state)
            if total_grid > 0:
                acc = 1 - (self._analyzer.temporary_clusters.get("unknown", {}).get("mean_watt", 0) / (2 * total_grid))
                self._state = min(100, max(0, round(acc * 100)))
