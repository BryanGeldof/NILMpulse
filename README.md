# NILMpulse

NILMpulse is a Non-Intrusive Load Monitoring (NILM) integration for Home Assistant. It disaggregates a single total power feed into individual virtual appliance entities using real-time edge detection and statistical clustering. 

The integration initializes with an empty database and builds appliance profiles dynamically based on the power changes (Delta P) captured from a smart meter or a template helper sensor.

## Core Mechanics

* **Edge Detection:** The integration processes every state change of the main power sensor to calculate the absolute step change ($\Delta P$). Looppack filtering isolates genuine appliance events from baseline electrical grid noise.
* **Transient and Shape Analysis:** Step changes are monitored over time to match positive turn-on edges with corresponding negative turn-off edges, mapping the specific duty cycle of the load.
* **Unsupervised Clustering:** Unidentified power steps are grouped into anonymous clusters based on magnitude and time characteristics. Once a specific cluster reproduces consistently, it is flagged for user identification.
* **Drift Adaptation:** Appliance profiles utilize an exponential moving average to recalculate their reference power rating. This accounts for long-term power drift caused by appliance degradation, voltage fluctuations, or scaling.
* **Power Conservation Balance:** All unattributed power consumption is aggregated into a dedicated residual entity, ensuring the total power balance matches the physical main meter reading.

## Load Classification Profiles

The decomposition engine evaluates step signatures against six core load profiles:
1. **Finite State Machines:** Multi-stage loads with pre-programmed cycles (e.g., washing machines, ovens).
2. **CC/CV Charging Profiles:** Step transitions followed by an exponential decay curve (e.g., electric vehicles, home battery systems).
3. **Continuous Base Load:** Constant static draw operating uninterrupted over a 24-hour window (e.g., network hardware, ventilation fans).
4. **Pure Resistive Step:** Rectangular power profiles with steep, symmetrical turn-on and turn-off edges (e.g., kettles, space heaters).
5. **Inductive Motor Transients:** Profiles characterized by high inrush current spikes settling into a lower stable operating state (e.g., compressors, heat pumps).
6. **Variable Modulated Loads:** High-frequency, random power fluctuations within constrained limits (e.g., television displays, dimmed lighting arrays).

## Installation

### Via HACS (Recommended)
1. Navigate to **HACS** within your Home Assistant instance.
2. Open the top-right menu (three dots) and select **Custom repositories**.
3. Paste the URL of this GitHub repository into the Repository field.
4. Select **Integration** as the category and click **Add**.
5. Search for **NILMpulse** and click **Download**.
6. Restart Home Assistant to load the component.

### Manual Installation
1. Download the latest source code release.
2. Extract and copy the `custom_components/nilmpulse/` directory into your Home Assistant `config/custom_components/` directory.
3. Restart Home Assistant.

## Configuration

NILMpulse is configured entirely via the Home Assistant user interface:

1. Navigate to **Settings** > **Devices & Services**.
2. Click **Add Integration** in the bottom right corner.
3. Search for **NILMpulse**.
4. In the configuration dialog, select your primary total active power sensor. This can be the direct export/import sensor from a physical P1 smart meter, or a calculated template helper sensor (e.g., a combined value adding grid import, solar generation, and battery state).
5. Click **Submit**.

## Generated Entities

Upon successful setup, the integration instantiates the following base entities:

* `sensor.nilmpulse_unknown_restwaarde`: Represents the residual unallocated real-time power consumption (in Watts) not currently mapped to an active cluster or base load.
* `sensor.nilmpulse_deconstructie_efficiency`: A mathematical confidence score expressed as a percentage. It measures how effectively the active load profile balances against the main meter.

When an anonymous cluster meets the repetition threshold, a native Home Assistant notification is generated. Approving and naming the cluster (e.g., "Heat Pump") registers the profile and instantiates a dedicated sensor, such as `sensor.nilmpulse_heat_pump`.

## Diagnostics and Logging

The core tracking module logs state changes under the `[NILMpulse]` prefix. To capture deep telemetry regarding edge matching and cluster generation, adjust your `configuration.yaml` debug levels:

```yaml
logger:
  default: warning
  logs:
    custom_components.nilmpulse: info
