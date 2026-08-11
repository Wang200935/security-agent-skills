// wifi_bypass.c — linker wrapper to bypass ieee80211_raw_frame_sanity_check
// Include this in your Arduino sketch directory alongside the .ino file
//
// This wrapper tells the linker to globally replace calls to
// ieee80211_raw_frame_sanity_check() with __wrap_ieee80211_raw_frame_sanity_check(),
// which always returns 0 (success). This allows sending ANY 802.11 frame type,
// including deauth (0xC0) and disassociation (0xA0), which the ESP-IDF
// normally blocks.
//
// Prerequisite: ld_flags must contain -Wl,--wrap=ieee80211_raw_frame_sanity_check
// For Arduino IDE: edit ~/Library/Arduino15/packages/esp32/tools/esp32-libs/<ver>/flags/ld_flags

#include <stdbool.h>
#include <stdint.h>

int __wrap_ieee80211_raw_frame_sanity_check(
    int ifx,
    const void *buffer,
    int len,
    bool auto_seq
) {
    // Suppress unused-parameter warnings
    (void)ifx;
    (void)buffer;
    (void)len;
    (void)auto_seq;

    // Always return 0 — everything is "OK"
    return 0;
}