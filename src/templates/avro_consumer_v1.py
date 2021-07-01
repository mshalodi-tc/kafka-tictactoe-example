#!/usr/bin/env python

import argparse
from typing import Dict

from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer


class User(object):
  def __init__(self, name, favorite_number, favorite_color) -> None:
    self.name = name
    self.favorite_number = favorite_number
    self.favorite_color = favorite_color


def dict_to_user(obj: Dict, ctx):
  if obj is None:
    return None

  return User(name=obj['name'], favorite_number=obj['favorite_number'], favorite_color=obj['favorite_color'])


def main(args):
  schema_registry_url = args.schema_registry
  bootstrap_servers = args.bootstrap_servers
  topic = args.topic
  group_id = args.group
  schema_str = """
  {
    "namespace": "io.tucows.kafka.examples.avro",
    "name": "User",
    "type": "record",
    "fields": [
      {"name": "name", "type": "string"},
      {"name": "favorite_number", "type": "int"},
      {"name": "favorite_color", "type": "string"}    ]
  }
  """

  schema_registry_conf = {'url': schema_registry_url}
  schema_registry_client = SchemaRegistryClient(conf=schema_registry_conf)

  # Used for message value
  avro_deserializer = AvroDeserializer(
      schema_registry_client=schema_registry_client, schema_str=schema_str, from_dict=dict_to_user)
  # Used for message key
  string_deserializer = StringDeserializer('utf_8')

  consumer_conf = {'bootstrap.servers': bootstrap_servers,
                   'key.deserializer': string_deserializer,
                   'value.deserializer': avro_deserializer,
                   'group.id': group_id,
                   'auto.offset.reset': "earliest"}
  consumer = DeserializingConsumer(consumer_conf)
  consumer.subscribe([topic])

  while True:
    try:
      # SIGINT can't be handled when polling, limit to 1 second
      msg = consumer.poll(1.0)
      if msg is None:
        continue
      user = msg.value()
      if user is not None:
        print(
            f"User record {msg.key()}\n\tname: {user.name}\n\tfavorite_number: {user.favorite_number}\n\tfavorite_color: {user.favorite_color}")

    except KeyboardInterrupt:
      print("Interrupted!")
      consumer.close()
      break


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
      description="Tucows Avro Consumer Kafka Example")
  parser.add_argument('-b', dest="bootstrap_servers",
                      required=True, help="Bootstrap broker(s) (host[:port])")
  parser.add_argument('-s', dest="schema_registry", required=True,
                      help="Schema Registry (http(s)://host[:port]")
  parser.add_argument('-t', dest='topic',
                      default="tucows-users-example-avro", help="Topic name")
  parser.add_argument(
      '-g', dest="group", default="avro_consumer_tucows_example", help="Consumer group")

  main(parser.parse_args())
