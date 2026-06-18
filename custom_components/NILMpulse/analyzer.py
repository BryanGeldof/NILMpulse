import logging
import math
import time
from .const import MATCH_TOLERANCE_PERCENT, MIN_REPETITIONS_FOR_NOTIF

_LOGGER = logging.getLogger(__name__)

class PeakSenseClusterAnalyzer:
    def __init__(self, hass):
        self.hass = hass
        self.last_total_power = None
        self.baseload = 150  # Dynamische startwaarde voor sluipverbruik
        self.temporary_clusters = {} # Slaat anonieme patronen op
        self.registered_appliances = {} # Door gebruiker gelabelde apparaten
        
    def process_reading(self, current_total):
        if self.last_total_power is None:
            self.last_total_power = current_total
            return 0, current_total

        # 1. Bereken de wiskundige Flank (Delta P)
        delta_p = current_total - self.last_total_power
        self.last_total_power = current_total

        # Automatische baseload bijstelling via Moving Average
        if current_total < self.baseload:
            self.baseload = round(0.95 * self.baseload + 0.05 * current_total)

        # 2. Controleer actieve bekende apparaten via eliminatie
        active_isolated_wattage = 0
        for name, app in self.registered_appliances.items():
            if app["active"]:
                # Correctie: == in plaats van ===
                if delta_p <= -(app["mean_watt"] * (1 - MATCH_TOLERANCE_PERCENT)) and delta_p >= -(app["mean_watt"] * (1 + MATCH_TOLERANCE_PERCENT)):
                    app["active"] = False
                    _LOGGER.info(f"[NILMpulse] Apparaat uitgeschakeld: {name}")
                else:
                    active_isolated_wattage += app["mean_watt"]
            else:
                # Inschakeldetectie
                if delta_p >= (app["mean_watt"] * (1 - MATCH_TOLERANCE_PERCENT)) and delta_p <= (app["mean_watt"] * (1 + MATCH_TOLERANCE_PERCENT)):
                    app["active"] = True
                    active_isolated_wattage += app["mean_watt"]
                    _LOGGER.info(f"[NILMpulse] Apparaat ingeschakeld: {name}")

        # 3. Bereken de resterende onbekende waarde (Unknown restpost)
        unknown_rest = max(0, current_total - active_isolated_wattage - self.baseload)

        # 4. UNSUPERVISED CLUSTERING: Analyseer onbekende flanken
        if delta_p > 50 and unknown_rest > 0:
            self._analyze_unknown_flank(delta_p)

        return active_isolated_wattage, unknown_rest

    def _analyze_unknown_flank(self, flank_value):
        match_found = False
        
        for cluster_id, data in self.temporary_clusters.items():
            if math.isclose(flank_value, data["mean_watt"], rel_tol=MATCH_TOLERANCE_PERCENT):
                data["count"] += 1
                data["mean_watt"] = round(0.9 * data["mean_watt"] + 0.1 * flank_value)
                match_found = True
                
                _LOGGER.info(f"[NILMpulse] Cluster {cluster_id} herhaald! Teller: {data['count']}, Gemiddelde: {data['mean_watt']}W")
                
                if data["count"] == MIN_REPETITIONS_FOR_NOTIF and not data["notified"]:
                    data["notified"] = True
                    self._trigger_hass_notification(cluster_id, data["mean_watt"])
                break

        if not match_found:
            new_id = f"cluster_{int(time.time())}_{round(flank_value)}"
            self.temporary_clusters[new_id] = {
                "mean_watt": flank_value,
                "count": 1,
                "notified": False,
                "timestamp": time.time()
            }
            _LOGGER.info(f"[NILMpulse] Nieuw anoniem patroon gedetecteerd: +{flank_value}W (ID: {new_id})")

    def _trigger_hass_notification(self, cluster_id, wattage):
        self.hass.components.persistent_notification.create(
            title="🤖 NILMpulse AI: Nieuw Apparaat!",
            message=(
                f"Ik heb een structureel terugkerend patroon ontdekt van circa **{wattage}W**.<br><br>"
                f"Is dit een specifiek apparaat zoals een Waterkoker of Frigo?<br>"
                f"Ga naar de integratie-instellingen om dit apparaat een naam te geven."
            ),
            notification_id=f"nilmpulse_{cluster_id}"
        )
