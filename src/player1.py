#!/usr/bin/env python

import argparse
import time
import asyncio
from uuid import uuid4
from numpy import random
from typing import Dict

from confluent_kafka import SerializingProducer, DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient, schema_registry_client
from confluent_kafka.schema_registry import avro
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from confluent_kafka.serialization import StringSerializer, StringDeserializer


class Message(object):
  def __init__(self, turn, grid) -> None:
    self.turn = turn
    self.grid = grid

def message_to_dict(message: Message, ctx):
  return dict(turn=message.turn, grid=message.grid)

def dict_to_message(obj: Dict, ctx):
  if obj is None:
    return None
  return Message(turn=obj['turn'], grid=obj['grid'])

def main(args):
  schema_registry_url = args.schema_registry
  bootstrap_servers = args.bootstrap_servers
  group_id = args.group
  schema_str = """
  {
    "namespace": "io.tucows.kafka.examples.avro",
    "name": "Message",
    "type": "record",
    "fields": [
      {"name": "turn", "type": "int"},
      {"name": "grid", "type": "string"}
    ]
  }
  """

  schema_registry_conf = {'url': schema_registry_url}
  schema_registry_client = SchemaRegistryClient(conf=schema_registry_conf)

  # Used for message value
  avro_serializer = AvroSerializer(schema_registry_client=schema_registry_client, schema_str=schema_str, to_dict=message_to_dict)
  # Used for message key
  string_serializer = StringSerializer('utf_8')

  producer_conf = {
    'bootstrap.servers': bootstrap_servers,
    'key.serializer': string_serializer,
    'value.serializer': avro_serializer
  }
  producer = SerializingProducer(producer_conf)

  judge_topic = 'judge-topic'
  player1_topic = 'player1-topic'

  # Used for message value
  avro_deserializer = AvroDeserializer(
      schema_registry_client=schema_registry_client, schema_str=schema_str, from_dict=dict_to_message)
  # Used for message key
  string_deserializer = StringDeserializer('utf_8')

  consumer_conf = {'bootstrap.servers': bootstrap_servers,
                   'key.deserializer': string_deserializer,
                   'value.deserializer': avro_deserializer,
                   'group.id': group_id,
                   'auto.offset.reset': "latest"}
  consumer = DeserializingConsumer(consumer_conf)
  consumer.subscribe([player1_topic])
  
  print("player1 started consuming...")

  # infinite consume
  while True:
    try:
      # SIGINT can't be handled when polling, limit to 1 second
      msg = consumer.poll(1.0)
      if msg is None:
        continue
      message = msg.value()
      key = msg.key()
      if message is not None:
        # print(f"player1 consumed message with grid={message.grid}\n")
        available_slots = []
        for i in range(len(message.grid)):
          if message.grid[i] == '0':
            available_slots.append(i)
        random_index = random.randint(0, len(available_slots))
        message.grid = message.grid[:available_slots[random_index]] + '1' + message.grid[available_slots[random_index] + 1:]

        producer.poll(0.0)
        newmessage = Message(turn=message.turn, grid=message.grid)
        # print(f"producing message with grid={newmessage.grid} and turn={newmessage.turn}\n")
        producer.produce(topic=judge_topic, key=key, value=newmessage)

    except KeyboardInterrupt:
      print("Interrupted!")
      consumer.close()
      break
  producer.flush()


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Tucows Avro Producer Kafka Example")
  parser.add_argument('-b', dest="bootstrap_servers", required=True, help="Bootstrap broker(s) (host[:port])")
  parser.add_argument('-s', dest="schema_registry", required=True, help="Schema Registry (http(s)://host[:port]")
  parser.add_argument('-t', dest='topic', default="tucows-users-example-avro", help="Topic name")
  parser.add_argument('-g', dest="group", default="player1", help="Consumer group")

  main(parser.parse_args())
