"""
# https://python-evdev.readthedocs.io/en/latest/
# https://gamepad-tester.com/
# https://www.phind.com/search?cache=114b6e96-f2f4-4b50-a01c-0553601ec28b
# https://strategywiki.org/wiki/The_Legend_of_Zelda:_Breath_of_the_Wild/Controls
# /home/$USERNAME/.local/share/Cemu/graphicPacks/downloadedGraphicPacks/BreathOfTheWild/Mods/CameraSensitivity/

# INSTRUCTIONS
# NOTE this program needs to be run as root
# requires `xprop | grep WM_CLASS` for setup and optional `xdotool` to auto move cursor to window.
# also consider using xdotool as a mouse movement fallback in case you get stuck: `xdotool mousemove_relative -- x y`
# you can get a list of device names by setting the debugging variable to `True`
# NOTE if using steam controller make sure steam is open and desktop configuration is set to generic xbox 360 pad
# program reads mouse inputs and uses value of input to scale to joystick movement amount
# mouse buttons are mapped to the keyboard, so use cemu bindings to map actions to keys you wont normally use
# by mapping 0,large_mouse_movement to 0,32768
# crank controller sensitivity in game so that large joystick movements result in very rapid turning
# LoZ BotW cemu camera settings mod: cam_sens=3x, add_move_sens=3x, add_vert_move_sens=0.5x
# recommend setting in game camera reset/home to extra mouse button or keyboard key

# TODO how did I set [Y|X]-Rotation[-|+] in the cemu controls menu?
# create virt cont then pass through real cont inputs to it 1:1?
"""
import random
from select import select
import signal
import subprocess
import time

import evdev


# CONFIG VARIABLES
debugging: bool = False
auto_move_lock_cursor_to_window: bool = False
controller_name: str = "Microsoft X-Box 360 pad 0"
mouse_name: str = "Logitech G602"
max_mouse_speed: int = 100  # 100 is based off highest value I could get waving the mouse around
keyboard_name: str = "Keychron Keychron K2 Pro"
# TODO mouse_grab_key
wm_class: str = "cemu"  # NOTE run `xprop | grep WM_CLASS` on window you want to focus on
# USERS SHOULD AVOID EDITING ANYTHING BELOW THIS LINE IF THEY AREN'T FAMILIAR WITH PYTHON


# FUNCTIONS
def sig_handler(sig, frame):
    if sig == signal.SIGINT:
        try:
            print("\nexiting...")
            mouse.ungrab()
            print("released mouse")
        except OSError as e:
            print("Error releasing mouse (mouse wasn't grabbed?):", e)
        finally:
            print("clean exit")
            exit(0)


signal.signal(signal.SIGINT, sig_handler)


def accel_curve(mouse_val: int, axis: str):
    """Possible mouse acceleration equations
    # y = 320 * x for mouse 0-100 controller 0-32000
    # y = 250 * x + 6000
    # y = 4 * x^2
    # y = 32000 * sin(0.01*x)
    # y = 3000 * sin(0.007 * x) + 10000
    # scalar: float = mouse_val / max_mouse_speed
    # return 0 + int(scalar * (32000 - 0))  # 0 is placeholder for dead zone
    """
    if abs(mouse_val) > max_mouse_speed:  # cap max mouse speed
        mouse_val = ((mouse_val > 0) - (mouse_val < 0)) * max_mouse_speed
    if axis == "X":
        # return 320 * mouse_val
        return ((mouse_val > 0) - (mouse_val < 0)) * ((250 * abs(mouse_val)) + 5000)
    elif axis == "Y":
        return ((mouse_val > 0) - (mouse_val < 0)) * ((250 * abs(mouse_val)) + 5000)


def handle_mouse_btn(event):  # TODO scroll wheel
    if event.code == evdev.ecodes.BTN_LEFT:
        virt_key.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_I, event.value)
        virt_key.syn()
    elif event.code == evdev.ecodes.BTN_RIGHT:
        virt_key.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_O, event.value)
        virt_key.syn()
    elif event.code == evdev.ecodes.BTN_MIDDLE:
        virt_key.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_L, event.value)
        virt_key.syn()
    elif event.code == evdev.ecodes.BTN_SIDE:
        virt_key.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_U, event.value)
        virt_key.syn()
    elif event.code == evdev.ecodes.BTN_EXTRA:
        virt_key.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_J, event.value)
        virt_key.syn()


def toggle_mouse_grab():
    global mouse_grabbed
    if mouse_grabbed:
        mouse.ungrab()
        mouse_grabbed = False
        if debugging:
            print("mouse released")
    elif not mouse_grabbed:
        mouse.grab()
        mouse_grabbed = True
        if debugging:
            print("mouse grabbed")


# START PROGRAM
for d in [evdev.InputDevice(path) for path in evdev.list_devices()]:
    if debugging:
        print(d.path, d.name)
        print(d.capabilities(verbose=True), end="\n\n")

    # if d.name == controller_name:  # TODO old remove later
    #     print("controller found")
    #     controller = evdev.InputDevice(d.path)
    if d.name == mouse_name:
        print("mouse found")
        mouse = evdev.InputDevice(d.path)
    if d.name == keyboard_name:
        print("keyboard found")
        keyboard = evdev.InputDevice(d.path)

devices = {dev.fd: dev for dev in [mouse, keyboard]}  # so select can read multiple inputs

# TODO do we need to use a virtual controller? can we create on then just store it in code so users don't need a controller plugged in?
print("creating virtual controller for mouse movement")
# virt_cont = evdev.UInput.from_device(controller, name="virtual_controller")  # old method
controller_mapping_dict: dict = {1: {304, 305, 307, 308, 310, 311, 314, 315, 316, 317, 318},
                                 3: {(3, evdev.AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
                                     (1, evdev.AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
                                     (2, evdev.AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
                                     (5, evdev.AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
                                     (16, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
                                     (4, evdev.AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0)),
                                     (17, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
                                     (0, evdev.AbsInfo(value=0, min=-32767, max=32767, fuzz=16, flat=128, resolution=0))}}
virt_cont = evdev.UInput(events=controller_mapping_dict, name="virtual_controller")

print("creating virtual keyboard for mouse buttons")
virt_key = evdev.UInput.from_device(keyboard, name="virtual_keyboard")

mouse_grabbed: bool = False
if auto_move_lock_cursor_to_window:
    print("auto moving mouse to window")  # TODO error handle no xdotool
    subprocess.run(f"xdotool search --onlyvisible --classname {wm_class} mousemove --window %1 20 50", shell=True)
    print("grabbing mouse")
    mouse.grab()
    mouse_grabbed = True

# speed: int = 0
print("starting main program")
while True:
    try:
        r, _, _ = select(devices, [], [], 0.05)
        if r:
            for fd in r:
                for event in devices[fd].read():
                    if debugging and event.type != evdev.ecodes.EV_SYN:
                        print(evdev.categorize(event))
                        print(event.type, event.code, event.value, end="\n\n")

                    if event.type == evdev.ecodes.EV_KEY:
                        if event.code == evdev.ecodes.KEY_ESC and event.value == 0:  # handle esc as special case
                            toggle_mouse_grab()
                        elif mouse_grabbed:
                            handle_mouse_btn(event)

                    if event.type == evdev.ecodes.EV_REL and mouse_grabbed:
                        # if abs(event.value) > speed:  # NOTE used to find max mouse speed
                        #     speed = abs(event.value)
                        #     with open("./speed.txt", "a") as f:
                        #         f.write(f"{speed}\n")
                        if event.code == evdev.ecodes.REL_X:
                            virt_cont.write(evdev.ecodes.EV_ABS, evdev.ecodes.ABS_RX, accel_curve(event.value, "X"))
                            virt_cont.syn()

                        elif event.code == evdev.ecodes.REL_Y:
                            virt_cont.write(evdev.ecodes.EV_ABS, evdev.ecodes.ABS_RY, accel_curve(event.value, "Y"))
                            virt_cont.syn()
        else:  # add timer that sends 0 to camera to stop it from drifting
            virt_cont.write(evdev.ecodes.EV_ABS, evdev.ecodes.ABS_RX, 0)
            virt_cont.write(evdev.ecodes.EV_ABS, evdev.ecodes.ABS_RY, 0)
            virt_cont.syn()

    except Exception as e:
        print("unknown error", e)
