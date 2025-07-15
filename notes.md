## Notes 15/07/2025

- If the user isn't registered. The default behavior is to not let them in. And that's already implemented by the device's creators.
- zk.disable_device() .enable_device() .poweroff() and .resatrt() do not work. We have no real way of intercepting attendances AS they happen. Only after the fact..

- FOUND WORKAROUND: set "Retard de serrure de porte (s)" setting to 0
- this will effectively make the device NEVER open the door on its own (IMPORTANT: THIS WILL RENDER THE DEVICE USELESS WHEN THE SCRIPT IS NOT ACTIVE)