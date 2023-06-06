# mouse_2_joystick
Python script that converts mouse movements to joystick movements via evdev

## INSTRUCTIONS
NOTE this program needs to be run as root
requires `xprop | grep WM_CLASS` for setup and optional `xdotool` to auto move cursor to window.
also consider using xdotool as a mouse movement fallback in case you get stuck: `xdotool mousemove_relative -- x y`
you can get a list of device names by setting the debugging variable to `True`
NOTE if using steam controller make sure steam is open and desktop configuration is set to generic xbox 360 pad
program reads mouse inputs and uses value of input to scale to joystick movement amount
mouse buttons are mapped to the keyboard, so use cemu bindings to map actions to keys you wont normally use
by mapping 0,large_mouse_movement to 0,32768
crank controller sensitivity in game so that large joystick movements result in very rapid turning
LoZ BotW cemu camera settings mod: cam_sens=3x, add_move_sens=3x, add_vert_move_sens=0.5x
recommend setting in game camera reset/home to extra mouse button or keyboard key

TODO how did I set [Y|X]-Rotation[-|+] in the cemu controls menu?
create virt cont then pass through real cont inputs to it 1:1?
