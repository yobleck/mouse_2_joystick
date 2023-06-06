# testing file for reading info from inputs
import evdev


for d in [evdev.InputDevice(path) for path in evdev.list_devices()]:
    print(d.path, d.name)
    if d.name == "Logitech G602":  # virtual_controller  Logitech G602  Microsoft X-Box 360 pad 0
        virt = evdev.InputDevice(d.path)

for event in virt.read_loop():
    if event.type != evdev.ecodes.EV_SYN:
        print(evdev.categorize(event))
        print(event.type, event.code, event.value, end="\n\n")
        # print(dir(event))


# OLD CODE AND TESTING CODE STORAGE
# speed: int = 0
# while True:
#     try:
#         time.sleep(0.1)  # adjust this?
#         for event in mouse.read():
#             if event_type == evdev.ecodes.EV_KEY:
#                 print(event.type, event.code, event.value, end="\n\n")
#             if event.type != evdev.ecodes.EV_SYN:
#                 print(evdev.categorize(event))
#                 print(event.type, event.code, event.value, end="\n\n")
#                 # print(dir(event))
#             if event.type == evdev.ecodes.EV_REL:
#                 # if abs(event.value) > speed:
#                 #     speed = abs(event.value)
#                 #     with open("./speed.txt", "a") as f:
#                 #         f.write(f"{speed}\n")
#                 if event.code == evdev.ecodes.REL_X:
#                     # for x in range(8):
#                     # NOTE if values are too close together they get merged into one event
#                     virt.write(evdev.ecodes.EV_ABS, evdev.ecodes.ABS_RX, accel_curve(event.value) + random.randrange(0, 50, 5))
#                     # ((event.value > 0) - (event.value < 0)) * 30000 + random.randrange(0, 50, 5))
#                     virt.syn()

#                 elif event.code == evdev.ecodes.REL_Y:
#                     # for y in range(8):
#                     virt.write(evdev.ecodes.EV_ABS, evdev.ecodes.ABS_RY, accel_curve(event.value) + random.randrange(0, 50, 5))
#                     virt.syn()

#     except BlockingIOError as e:
#         print("no input")
#         virt.write(evdev.ecodes.EV_ABS, evdev.ecodes.ABS_RX, 0)
#         virt.syn()
#         virt.write(evdev.ecodes.EV_ABS, evdev.ecodes.ABS_RY, 0)
#         virt.syn()

# mouse.grab()
# time.sleep(5)
# mouse.ungrab()
# exit()
# print(dir(evdev.ecodes))
# print(dir(controller))
# print(controller.name, controller.info)
# print(controller.capabilities(verbose=True))
# print()
# print(mouse.capabilities(verbose=True))
# print()
# print(virt.name)
# print(dir(virt))
# print(virt.capabilities(verbose=True))
# print()
# virt.write(evdev.ecodes.EV_ABS, evdev.ecodes.ABS_RX, 1000)
# virt.write(evdev.ecodes.EV_KEY, evdev.ecodes.BTN_THUMB, 1)
# for d in [evdev.InputDevice(path) for path in evdev.list_devices()]:
#     print(d.path, d.name)

# map real controller to virtual controller 1:1
# for event in controller.read_loop():
#     if event.type != evdev.ecodes.EV_SYN:
#         print(evdev.categorize(event))
#         print(event.type, event.code, event.value, end="\n\n")
#         # print(dir(event))
#     virt.write(event.type, event.code, event.value)

# handle no input and reading when there is input
# use number of inputs from mouse to determine number of inputs to controller to combat negative acceleration?
# while True:
#     try:
#         time.sleep(0.1)
#         for event in controller.read():
#             print(evdev.categorize(event))
#             print(event.type, event.code, event.value)
#     except BlockingIOError as e:
#         print("no input")