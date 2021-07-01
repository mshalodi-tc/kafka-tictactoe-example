#!/usr/bin/env python

import argparse
import time
from uuid import uuid4

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient, schema_registry_client
from confluent_kafka.schema_registry import avro
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer
from faker import Faker


class User(object):
  def __init__(self, name, favorite_number, favorite_color, address) -> None:
    self.name = name
    self.favorite_number = favorite_number
    self.favorite_color = favorite_color
    self.address = address


def user_to_dict(user: User, ctx):
  return dict(name=user.name, favorite_number=user.favorite_number, favorite_color=user.favorite_color, address=user.address)


def delivery_report(err, msg):
  if err is not None:
    print(f"Delivery failed for User record {msg.key()}: {err}")
    return
  print(
      f"User record {msg.key()} successfully produced to {msg.topic()} [{msg.partition()}] at offset {msg.offset()} in {msg.latency()} seconds")


def main(args):
  schema_registry_url = args.schema_registry
  bootstrap_servers = args.bootstrap_servers
  topic = args.topic
  fake = Faker()
  schema_str = """
  {
    "namespace": "io.tucows.kafka.examples.avro",
    "name": "User",
    "type": "record",
    "fields": [
      {"name": "name", "type": "string"},
      {"name": "favorite_number", "type": "int"},
      {"name": "favorite_color", "type": "string"},
      {"name": "address", "type": "string", "default": ""}
    ]
  }
  """

  schema_registry_conf = {'url': schema_registry_url}
  schema_registry_client = SchemaRegistryClient(conf=schema_registry_conf)

  # Used for message value
  avro_serializer = AvroSerializer(
      schema_registry_client=schema_registry_client, schema_str=schema_str, to_dict=user_to_dict)
  # Used for message key
  string_serializer = StringSerializer('utf_8')

  producer_conf = {'bootstrap.servers': bootstrap_servers,
                   'key.serializer': string_serializer,
                   'value.serializer': avro_serializer}
  producer = SerializingProducer(producer_conf)
  print(f"Producing user records to topic {topic}. ^C to exit.")
  try:
    while True:
      # serve on_delivery callbacks from previous calls to produce
      producer.poll(0.0)
      user_name = fake.name()
      user_address = fake.address()
      user_favorite_number = fake.pyint()
      user_favorite_color = fake.color_name()
      user = User(name=user_name, address=user_address,
                  favorite_color=user_favorite_color, favorite_number=user_favorite_number)

      producer.produce(topic=topic, key=str(uuid4()),
                       value=user, on_delivery=delivery_report)
      time.sleep(1)
  except KeyboardInterrupt:
    print("Interrupted!")
  print("\nFlushing records...")
  producer.flush()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(
      description="Tucows Avro Producer Kafka Example")
  parser.add_argument('-b', dest="bootstrap_servers",
                      required=True, help="Bootstrap broker(s) (host[:port])")
  parser.add_argument('-s', dest="schema_registry", required=True,
                      help="Schema Registry (http(s)://host[:port]")
  parser.add_argument('-t', dest='topic',
                      default="tucows-users-example-avro", help="Topic name")

  main(parser.parse_args())
