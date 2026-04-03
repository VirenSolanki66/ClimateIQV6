def generate_alerts(temp, humidity, wind, aqi):
    """
    Generate smart weather alerts based on current conditions.
    Returns list of (type, message) tuples.
    type can be: 'error', 'warning', 'info'
    """
    alerts = []

    # Temperature alerts
    if temp > 42:
        alerts.append(("error", "🔥 Extreme Heatwave! Stay indoors, drink lots of water, avoid direct sun."))
    elif temp > 37:
        alerts.append(("warning", "🌡️ High Temperature Alert! Limit outdoor activities, stay hydrated."))
    elif temp < 0:
        alerts.append(("error", "🧊 Freezing Conditions! Risk of ice and frostbite. Cover exposed skin."))
    elif temp < 10:
        alerts.append(("warning", "❄️ Cold Weather Alert! Wear warm clothing and limit exposure."))

    # Humidity alerts
    if humidity > 85:
        alerts.append(("warning", "💧 Very High Humidity! Risk of fungal infections and heat exhaustion."))
    elif humidity < 20:
        alerts.append(("info", "🏜️ Very Low Humidity! Risk of dehydration and dry skin."))

    # Wind alerts
    if wind > 20:
        alerts.append(("error", "🌀 Severe Wind! Risk of structural damage. Stay indoors."))
    elif wind > 12:
        alerts.append(("warning", "🌪️ Strong Wind Alert! Avoid outdoor activities and loose objects."))

    # AQI alerts
    if aqi >= 5:
        alerts.append(("error", "☠️ Hazardous Air Quality! Avoid ALL outdoor exposure. Wear N95 mask."))
    elif aqi == 4:
        alerts.append(("warning", "😷 Poor Air Quality! Wear a mask outdoors. Sensitive groups stay inside."))
    elif aqi == 3:
        alerts.append(("info", "😐 Moderate Air Quality. Sensitive groups should limit outdoor time."))

    # Combo condition
    if temp > 35 and humidity > 70:
        alerts.append(("error", "🌡️💧 Heat Index Danger! Feels much hotter due to humidity. Risk of heat stroke."))

    return alerts
