from pymongo import MongoClient
import paho.mqtt.client as mqtt


class MqttClient:
    def __init__(self, host, port, username, password, topic):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.topic = topic
        self.client = mqtt.Client()
        self.client.username_pw_set(username=self.username, password=self.password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc) + "\n")
        self.client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload) + "\n")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnection.")

    def run(self):
        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()
    
    def publish(self, message):
        self.client.publish(self.topic, message)

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()
    
    def __del__(self):
        self.disconnect()


def test_mqtt_client():
    client = MqttClient(host='localhost', port=1883, username='username', password='password', topic='test')
    client.run()
    #Subscribe to the topic house and publish a message to the topic house
    while True:
        message = input('Enter message: ')
        if client.client.is_connected():
            client.publish(message)
        if message == 'exit':
            break

if __name__ == '__main__':
    test_mqtt_client()



