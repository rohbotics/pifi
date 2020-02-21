"""
This module provides helpers for connecting LEDs
"""

def blink(led_paths, delay_on=500, delay_off=500, open=open):
    """
    Make the led(s) start a blinking animation

    led_paths should be a string path or a tuple of string paths
    delay_on is how many milliseconds the led should be on in a cycle
    delay_on is how many milliseconds the led should be off in a cycle
    """
    if led_paths is None: return
    if type(led_paths) is not tuple: led_paths = [led_paths]

    # Some basic sanity checks
    assert delay_on > 0
    assert delay_off > 0

    for led_path in led_paths:
        # Setup blinking animation on the led
        with open(led_path + '/trigger', 'w+') as led_file:
            # Use the timer module provided by the kernel, this makes it
            # so that we don't have to handle the timing of the led
            led_file.write('timer')
        with open(led_path + '/delay_on', 'w+') as led_file:
            led_file.write(str(delay_on))
        with open(led_path + '/delay_off', 'w+') as led_file:
            led_file.write(str(delay_off))

def try_blink(led_paths, delay_on=500, delay_off=500, open=open):
    try:
        blink(led_paths, delay_on=delay_on, delay_off=delay_off, open=open)
    except:
        print("Error starting LED blink animation")


def off(led_paths, open=open):
    """
    Turn the led(s) the leds off, canceling any blinking

    led_paths should be a string path or a tuple of string paths
    """
    if led_paths is None: return
    if type(led_paths) is not tuple: led_paths = [led_paths]

    for led_path in led_paths:
        # Writing the brightness to 0 stops any other kernel system
        # that is driving the led, so this will also the stop the blinking
        # that is driven by the timer module
        with open(led_path + '/brightness', 'w+') as led_file:
            led_file.write('0')

def on(led_paths, open=open):
    """
    Turn the led(s) the leds on, canceling any blinking

    led_paths should be a string path or a tuple of string paths
    """
    if led_paths is None: return
    if type(led_paths) is not tuple: led_paths = [led_paths]

    for led_path in led_paths:
        # Writing the brightness to 0 stops any other kernel system
        # that is driving the led, so this will the stop the blinking
        # that is driven by the timer module
        with open(led_path + '/brightness', 'w+') as led_file:
            led_file.write('0')
        # Write 255 to brightness to turn the led on
        with open(led_path + '/brightness', 'w+') as led_file:
            led_file.write('255')
