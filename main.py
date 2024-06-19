import machine
import time
import boot
import neopixel

from umqtt.simple2 import MQTTClient

from config import CONFIG

LED_PIN = machine.Pin(2, machine.Pin.OUT)

np = neopixel.NeoPixel(machine.Pin(7), 1)

def rgb_control(r, g, b):
    np[0] = (r, g, b)
    np.write()

def rgb_sequence(seq_list: list, delay=0.5, end_is_off=True):
    for seq in seq_list:
        rgb_control(*seq)
        time.sleep(delay)
    if end_is_off:
        rgb_control(0, 0, 0)

def build_mqtt_topic(*args):
    """Join topic components with a '/' delimeters and encode as bytes

    The umqtt library expects topic to be byte encoded

    Arguments:
        *args {string} -- String to be added to topic

    Returns:
        [bytearray] -- byte encoded mqtt topic
    """
    topic = '/'.join(args)
    return topic.encode('utf-8')

# Subcribe to MQTT topics
def subscribe(client, topic):
    client.subscribe(topic)
    print('Subscribe to topic:', topic)

def my_callback(topic, message):
    # Perform desired actions based on the subscribed topic and response
    print('Received message on topic:', topic)
    print('Response:', message)
    # Check the content of the received message
    if message == b'TOGGLE':
        print('Turning LED ON')
        rgb_sequence([(220, 28, 242)])
        LED_PIN.on()
        time.sleep(0.5)
        LED_PIN.off()
    else:
        print('Unknown command')

   


if __name__ == '__main__':
    CONFIG
    

try:
    client = MQTTClient(CONFIG['client_id'], CONFIG['broker'], port=1883, user=None, password=None, keepalive=60, ssl=False)
    config_topic = b'homeassistant/esp8266_0001/config'
    try:
        client.connect()
    except OSError:
        print("Failed to connect to broker {}, will retry...".format(CONFIG['broker']))
        rgb_sequence([(128, 0, 0), (0, 0, 0)], end_is_off=False)
    client.set_callback(my_callback)
    subscribe(client, b'homeassistant/esp8266_0001/control')

    wlan = boot.wlan_connect()
    client.publish(config_topic, 'Wifi is connected at {}'.format(wlan.ifconfig()))
    rgb_sequence([(128, 0, 0), (0, 128, 0), (0, 0, 0)])

    print("Connected to {}".format(CONFIG['broker']))
    # Continuously checking for messages
    while True:
        # time.sleep(2)
        client.check_msg()
        print('Loop running')
except Exception as e:
    print('Error:', e)
