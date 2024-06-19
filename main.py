import machine
import time
import boot
import neopixel
import dht
from umqtt.simple2 import MQTTClient
from config import CONFIG

np = neopixel.NeoPixel(machine.Pin(7), 1)
d = dht.DHT22(machine.Pin(4))
d_last_read = time.ticks_ms()
# binary2 = machine.Pin(0, machine.Pin.IN) # not working, not stable
power_pin = machine.Pin(2, machine.Pin.OUT)

def rgb_control(r, g, b):
    np[0] = (r, g, b)
    np.write()

def rgb_sequence(seq_list: list, delay=0.5, end_is_off=True):
    for seq in seq_list:
        rgb_control(*seq)
        time.sleep(delay)
    if end_is_off:
        rgb_control(0, 0, 0)

def read_dht(boot=False, d_last_read=d_last_read):
    print('Reading DHT')
    if boot:
        d.measure()
        d_last_read = time.ticks_ms()
        temperature = d.temperature()
        humidity = d.humidity()
        print('Temperature:', temperature)
        print('Humidity:', humidity)
        client.publish(b'homeassistant/esp8266_0001/temperature', str(temperature))
        client.publish(b'homeassistant/esp8266_0001/humidity', str(humidity))
        return temperature, humidity, d_last_read
    elif time.ticks_ms()-d_last_read < 2000:
        return d.temperature(), d.humidity(), d_last_read
    else:
        d.measure()
        d_last_read = time.ticks_ms()
        return d.temperature(), d.humidity(), d_last_read
    
def update_dht_values(prev_temperature, prev_humidity, d_last_read):
    temperature, humidity, d_last_read = read_dht(d_last_read=d_last_read)
    if temperature != prev_temperature or humidity != prev_humidity:
        print('Temperature:', temperature)
        print('Humidity:', humidity)
        client.publish(b'homeassistant/esp8266_0001/temperature', str(temperature))
        client.publish(b'homeassistant/esp8266_0001/humidity', str(humidity))
    return temperature, humidity, d_last_read

def binary_sensor_callback(p):
    print(p.value())    

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
        print('Pressing power button')
        power_pin.on()
        rgb_sequence([(220, 28, 242)])
        power_pin.off()
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
    # binary2.irq(trigger=machine.Pin.IRQ_RISING, handler=binary_sensor_callback) # not working, not stable
    subscribe(client, b'homeassistant/esp8266_0001/control')

    wlan = boot.wlan_connect()
    client.publish(config_topic, 'Wifi is connected at {}'.format(wlan.ifconfig()))
    read_dht(boot=True)
    rgb_sequence([(128, 0, 0), (0, 128, 0), (0, 0, 0)])

    print("Connected to {}".format(CONFIG['broker']))
    # Continuously checking for messages
    while True:
        print('Loop running')
        time.sleep(0.5)
        client.check_msg()
        temperature, humidity, d_last_read = update_dht_values(d.temperature(), d.humidity(), d_last_read)

        
except Exception as e:
    print('Error:', e)
