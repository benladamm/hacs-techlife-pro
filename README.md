# HACS TechLife Pro

Custom Component for Home Assistant to control TechLife Pro LED strips via MQTT.

## Features
- On/Off Control
- Brightness Control (Approximate)
- Discovery via MQTT

## DNS Redirection (REQUIRED)
To use this component, you MUST redirect the traffic from the LED strip to your local MQTT broker. The device tries to connect to `cloud.techlifepro.com` (or sometimes `clim8.techlifepro.com`).

### How to Redirect
1. **Identify the domain**: Check your DNS logs (e.g., Pi-hole, AdGuard Home) to see what domain the device requests. Common domains: `cloud.techlifepro.com`.
2. **Configure DNS**: Add a DNS record in your router or DNS server (like Pi-hole) to point that domain to the IP address of your Home Assistant instance (or wherever your MQTT broker is running).
3. **MQTT Broker**: Ensure your MQTT broker handles anonymous connections or that you have configured the integration if the device supports auth (usually they don't, they just connect).
4. **Validation**: Check your MQTT broker logs. You should see a connection from the device and it subscribing to `dev_sub_{MAC}` and publishing to `dev_pub_{MAC}`.

## Installation
1. Install via HACS (Custom Repository).
2. Restart Home Assistant.
3. Go to Settings -> Integrations -> Add Integration -> TechLife Pro.
