#!/usr/bin/env python

import argparse
import time
from uuid import uuid4
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

def check_win(grid):
  return grid[0]==grid[1] and grid[1]==grid[2] and grid[0]!='0' or grid[3]==grid[4] and grid[4]==grid[5] and grid[3]!='0' or grid[6]==grid[7] and grid[7]==grid[8] and grid[6]!='0' or grid[0]==grid[3] and grid[3]==grid[6] and grid[0]!='0' or grid[0]==grid[3] and grid[3]==grid[6] and grid[0]!='0' or grid[1]==grid[4] and grid[4]==grid[7] and grid[1]!='0' or grid[2]==grid[5] and grid[5]==grid[8] and grid[2]!='0' or grid[0]==grid[4] and grid[4]==grid[8] and grid[0]!='0' or grid[2]==grid[4] and grid[4]==grid[6] and grid[2]!='0'

def check_end(grid):
  return grid[0]!='0' and grid[1]!='0' and grid[2]!='0' and grid[3]!='0' and grid[4]!='0' and grid[5]!='0' and grid[6]!='0' and grid[7]!='0' and grid[8]!='0'

def grididize(grid):
  result = ''
  for i in range(3):
    result = f"{result}{grid[i*3:i*3+3]}\n"
  return result


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


  # Used for message value
  avro_deserializer = AvroDeserializer(
      schema_registry_client=schema_registry_client, schema_str=schema_str, from_dict=dict_to_message)
  # Used for message key
  string_deserializer = StringDeserializer('utf_8')

  judge_topic = 'judge-topic'
  player1_topic = 'player1-topic'
  player2_topic = 'player2-topic'

  consumer_conf = {'bootstrap.servers': bootstrap_servers,
                   'key.deserializer': string_deserializer,
                   'value.deserializer': avro_deserializer,
                   'group.id': group_id,
                   'auto.offset.reset': "latest"}
  consumer = DeserializingConsumer(consumer_conf)
  consumer.subscribe([judge_topic])

  # initial message produce
  producer.poll(0.0)
  print("judge producing initial message\n")
  producer.produce(topic=player1_topic, key=str(uuid4()), value=Message(turn=1, grid="000000000"))

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
        print(f"player {message.turn} played and grid = \n{grididize(message.grid)}\n")
        is_win = check_win(message.grid)
        if is_win:
          print(f"player {message.turn} won!\n")
          break
        is_end = check_end(message.grid)
        if is_end:
          print(f"game ends with no win.")
          break
          
        producer.poll(0.0)
        message.turn = 2 - message.turn + 1
        newmessage = Message(turn=message.turn, grid=message.grid)
        if message.turn==1:
          producer.produce(topic=player1_topic, key=key, value=newmessage)
        else:
          producer.produce(topic=player2_topic, key=key, value=newmessage)

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
  parser.add_argument('-g', dest="group", default="judge", help="Consumer group")

  main(parser.parse_args())
