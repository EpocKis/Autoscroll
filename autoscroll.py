#!/usr/bin/env python3
"""
autoscroll.py – säker variant utan device.grab()

Lyssnar passivt på musen. Musen funkar alltid normalt.
Håll musknapp 3 + rör musen → scroll-events injiceras via ett separat uinput-device.

Kräver:
  - python-evdev   (sudo pacman -S python-evdev)
  - Användaren i gruppen 'input'  (sudo usermod -aG input $USER)
"""

import sys
import threading

try:
    from evdev import InputDevice, UInput, ecodes, list_devices
except ImportError:
    print("Fel: python-evdev saknas. Installera med: sudo pacman -S python-evdev")
    sys.exit(1)

# ── Inställningar ────────────────────────────────────────────────────────────
SCROLL_THRESHOLD = 8   # pixels per scroll-tick (lägre = känsligare)
SPEED_MULTIPLIER = 1    # ticks per threshold-crossing (höj för snabbare scroll)
# ────────────────────────────────────────────────────────────────────────────


def find_mice():
    mice = []
    for path in list_devices():
        try:
            dev = InputDevice(path)
            caps = dev.capabilities()
            has_middle = ecodes.BTN_MIDDLE in caps.get(ecodes.EV_KEY, [])
            has_rel    = ecodes.REL_X      in caps.get(ecodes.EV_REL, [])
            if has_middle and has_rel:
                mice.append(dev)
        except Exception:
            pass
    return mice


def create_scroll_device():
    """Minimalt uinput-device som bara kan skicka scroll-events."""
    rel = [ecodes.REL_WHEEL, ecodes.REL_HWHEEL]
    if hasattr(ecodes, "REL_WHEEL_HI_RES"):
        rel += [ecodes.REL_WHEEL_HI_RES, ecodes.REL_HWHEEL_HI_RES]

    return UInput(
        {ecodes.EV_REL: rel},
        name="autoscroll-injector"
    )


def handle(device, scroller):
    print(f"[+] Lyssnar på: {device.path} ({device.name})")

    active = False
    ax = 0.0
    ay = 0.0

    try:
        for ev in device.read_loop():

            # Mittenknapp – sätt aktivt läge
            if ev.type == ecodes.EV_KEY and ev.code == ecodes.BTN_MIDDLE:
                if ev.value == 1:       # nedtryckt
                    active = True
                    ax = ay = 0.0
                elif ev.value == 0:     # släppt
                    active = False
                    ax = ay = 0.0

            # Musrörelse – injicera scroll om aktiv
            elif active and ev.type == ecodes.EV_REL:
                if ev.code == ecodes.REL_Y:
                    ay += ev.value
                    ticks = int(ay / SCROLL_THRESHOLD)
                    if ticks:
                        scroller.write(ecodes.EV_REL, ecodes.REL_WHEEL, -ticks)
                        if hasattr(ecodes, "REL_WHEEL_HI_RES"):
                            scroller.write(ecodes.EV_REL, ecodes.REL_WHEEL_HI_RES, -ticks * 120)
                        scroller.syn()
                        ay -= ticks * SCROLL_THRESHOLD

                elif ev.code == ecodes.REL_X:
                    ax += ev.value
                    ticks = int(ax / SCROLL_THRESHOLD)
                    if ticks:
                        scroller.write(ecodes.EV_REL, ecodes.REL_HWHEEL, ticks)
                        if hasattr(ecodes, "REL_HWHEEL_HI_RES"):
                            scroller.write(ecodes.EV_REL, ecodes.REL_HWHEEL_HI_RES, ticks * 120)
                        scroller.syn()
                        ax -= ticks * SCROLL_THRESHOLD

    except OSError as e:
        print(f"[-] Enhet bortkopplad ({device.path}): {e}")


def main():
    mice = find_mice()
    if not mice:
        print("Ingen mus hittades.")
        print("Se till att du är i gruppen 'input': sudo usermod -aG input $USER")
        print("Logga sedan ut och in igen.")
        sys.exit(1)

    print(f"Hittade {len(mice)} musenhet(er).")
    print("Håll musknapp 3 och rör musen för att scrolla. Avsluta med Ctrl+C.\n")

    scroller = create_scroll_device()

    threads = [
        threading.Thread(target=handle, args=(m, scroller), daemon=True)
        for m in mice
    ]
    for t in threads:
        t.start()

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\nAvslutar autoscroll.")
    finally:
        scroller.close()


if __name__ == "__main__":
    main()
