import logging
import voltuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .analyzer import PeakSenseClusterAnalyzer

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # Initialiseer de analyzer
    analyzer = PeakSenseClusterAnalyzer(hass)
    hass.data[DOMAIN]["analyzer"] = analyzer

    # ---- 1. SERVICE REGISTRATIE (BOOST MODUS) ----
    async def start_boost(call: ServiceCall):
        analyzer.set_boost_mode(True)
        hass.components.persistent_notification.create(
            title="🚀 NILMpulse: Boost-modus Actief",
            message="De snelle leermodus staat aan voor 60 minuten. Elk apparaat dat je nu aan/uit zet, triggert direct een melding!",
            notification_id="nilmpulse_boost_status"
        )
        
        # Automatisch stoppen na 1 uur (60 minuten = 3600 seconden)
        async def auto_stop_boost(_):
            analyzer.set_boost_mode(False)
            _LOGGER.info("[NILMpulse] Boost-modus automatisch beëindigd na 60 minuten.")
        
        from homeassistant.helpers.event import async_call_later
        async_call_later(hass, 3600, auto_stop_boost)

    async def stop_boost(call: ServiceCall):
        analyzer.set_boost_mode(False)
        _LOGGER.info("[NILMpulse] Boost-modus handmatig uitgeschakeld.")

    hass.services.async_register(DOMAIN, "start_boost_mode", start_boost)
    hass.services.async_register(DOMAIN, "stop_boost_mode", stop_boost)


    # ---- 2. EVENT LISTENER (INTERACTIEVE GSM PUSHNOTIFICATIE) ----
    async def handle_notification_action(event):
        action = event.data.get("action", "")
        
        if action.startswith("NILMPULSE_LABEL_"):
            cluster_id = action.replace("NILMPULSE_LABEL_", "")
            # Pak de tekst die de gebruiker heeft ingetypt op zijn gsm
            user_response = event.data.get("text_input", "").strip()
            
            if user_response:
                _LOGGER.info(f"[NILMpulse] GSM Input ontvangen voor {cluster_id}: {user_response}")
                
                # Voeg het apparaat toe aan de bekende apparatenlijst
                analyzer.registered_appliances[user_response] = {
                    "mean_watt": analyzer.temporary_clusters[cluster_id]["mean_watt"],
                    "active": False
                }
                
                # Ruim het tijdelijke cluster op
                if cluster_id in analyzer.temporary_clusters:
                    del analyzer.temporary_clusters[cluster_id]

                # Update de sensoren in Home Assistant direct live
                await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # Luister wereldwijd naar acties vanuit de mobiele app
    hass.bus.async_listen("mobile_app_notification_action", handle_notification_action)

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Netjes opruimen bij het verwijderen/herstarten van de integratie
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop("analyzer", None)
    return unload_ok
