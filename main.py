import machine
import time

from umqtt.simple2 import MQTTClient

from config import load_config

LED_PIN = machine.Pin(2, machine.Pin.OUT)


def error_blink(duration=10):
    for count in range(duration):
        LED_PIN.on()
        print('LED ON')
        time.sleep(0.5)
        LED_PIN.off()
        time.sleep(0.5)


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
    if message == b'ON':
        print('Turning LED ON')
        LED_PIN.on()
    elif message == b'OFF':
        print('Turning LED OFF')
        LED_PIN.off()
    else:
        print('Unknown command')

   


if __name__ == '__main__':
    CONFIG = load_config()
    

try:
    client = MQTTClient(CONFIG['client_id'], CONFIG['broker'], port=1883, user=None, password=None, keepalive=60, ssl=False)
    # led_topic = build_mqtt_topic(CONFIG['topic'], CONFIG['client_id'], 'led')
    try:
        client.connect()
    except OSError:
        print("Failed to connect to broker {}, will retry...".format(CONFIG['broker']))
        error_blink(10)
    client.set_callback(my_callback)
    subscribe(client, b'homeassistant/esp8266_0001/led')

    error_blink(3)

    print("Connected to {}".format(CONFIG['broker']))
    # Continuously checking for messages
    while True:
        # time.sleep(2)
        client.check_msg()
        print('Loop running')
except Exception as e:
    print('Error:', e)
