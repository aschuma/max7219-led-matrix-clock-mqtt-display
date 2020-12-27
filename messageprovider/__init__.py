import json

import paho.mqtt.client as mqtt

import ttldict


class MessageProvider:
    
    def __init__(self, mqtt_config):
        self.ttl_cache = ttldict.TTLOrderedDict(60 * 3)
        self.config = mqtt_config
        self.client = None
    
    def loop_start(self):
        def mqtt_on_connect(cl, userdata, flags, rc):
            cl.subscribe("display/#")
        
        def mqtt_on_message(cl, userdata, msg):
            raw = msg.payload.decode("utf-8", "ignore")
            self.ttl_cache[msg.topic] = json.loads(raw)
        
        self.client = mqtt.Client()
        self.client.on_connect = mqtt_on_connect
        self.client.on_message = mqtt_on_message
        self.client.username_pw_set(
            username=self.config.mqtt_server['username'],
            password=self.config.mqtt_server['password'])
        self.client.connect(
            self.config.mqtt_server['ip_address'],
            self.config.mqtt_server['port'], 60)
        self.client.loop_start()
    
    def loop_stop(self):
        if self.client is not None:
            self.client.loop_stop()
            self.client = None
    
    def messages(self):
        sorted_sensor_json_obj_list = sorted(
            [pair[1] for pair in self.ttl_cache.items()],
            key=lambda json_object: json_object["weight"])
        return [self._format(json_obj) for json_obj in sorted_sensor_json_obj_list]
    
    @staticmethod
    def _format(json_obj):
        return "" + str(json_obj["name"]) + " " + str(json_obj["value"]) + "" + str(json_obj["unit"])
