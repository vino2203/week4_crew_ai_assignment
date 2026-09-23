# Hardware Troubleshooting Manual

## Page 1

This manual covers troubleshooting steps for the SyncBox Pro hardware
appliance, our on-premise caching device used for accelerating CloudSync in
large offices.

### Power and Boot Issues

If the SyncBox Pro does not power on, check that the power LED is off (not
just dim). Try a different power outlet and the original power adapter only —
third-party adapters can under-power the device and cause silent failures.

If the device powers on but the status LED stays amber (never turns green),
this indicates the device failed its self-test. Hold the reset button for 10
seconds to trigger a safe-mode boot, then check the admin portal for a
firmware update.

## Page 2

### Network Connectivity Issues

The SyncBox Pro requires a wired Gigabit Ethernet connection; Wi-Fi is not
supported. If the device shows "No Network" in the status app:

1. Confirm the Ethernet cable is fully seated at both ends.
2. Confirm the switch port is active (check the switch's own port LED).
3. Power-cycle the SyncBox Pro (unplug 10 seconds, replug).
4. If still offline, factory reset via the recessed pinhole button (hold 15s)
   and re-run the setup wizard from the admin portal.

The device requires outbound HTTPS (443) access to `*.cloudsync-api.com`.
Corporate firewalls that block by default must allowlist this domain.

## Page 3

### Overheating and Fan Noise

The SyncBox Pro is rated for ambient temperatures up to 35°C (95°F). If the
fan runs continuously at high speed, ensure the device has at least 10cm of
clearance on all sides and is not stacked under other equipment. Persistent
overheating alerts after proper ventilation is provided may indicate a failed
fan, which is covered under the standard hardware warranty for 3 years from
purchase.

### RMA Process

To initiate a hardware return merchandise authorization (RMA), contact support
with the device serial number (found on the bottom label) and a description of
the fault. Approved RMAs receive a prepaid shipping label within 1 business
day.
