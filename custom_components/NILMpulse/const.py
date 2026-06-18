DOMAIN = "nilmpulse"
CONF_P1_SENSOR = "p1_total_power_sensor"

# De 6 NILM Apparaatklassen gedefinieerd voor het algoritme
CLASS_1_FSM = "State Machine (Oven/Wasmachine)"
CLASS_2_BATTERY = "CC/CV Curve (EV/Batterij)"
CLASS_3_BASELOAD = "Constante Sluipverbruikers"
CLASS_4_RESISTIVE = "Blokgolf Weerstand (Waterkoker)"
CLASS_5_INDUCTIVE = "Motor Inschakelpiek (Frigo/Warmtepomp)"
CLASS_6_NOISE = "Variabele Ruis (TV/Led)"

# Wiskundige toleranties voor Unsupervised Clustering
FLANK_THRESHOLD_WATT = 30  # Minimale sprong om als flank gezien te worden
MATCH_TOLERANCE_PERCENT = 0.08  # 8% foutmarge voor clusterherkenning
MIN_REPETITIONS_FOR_NOTIF = 3  # Aantal keer dat patroon moet voorkomen voor notificatie
