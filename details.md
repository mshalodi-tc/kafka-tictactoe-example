# Solution
This folder contains the solutions for all exercises

## Bringing up your environment

### Starting your containers

Starting the containers will provide you with your own local kafka cluster, a schema registry instance, a connect instance (to be used in future), a AKHQ (GUI).

Zookeeper is exposed as `localhost:2181`
Kafka is exposed as `localhost:9092`
To access the kafka gui visit [http://localhost:8080/](http://localhost:8080/). 
To access schema registry rest api visit [http://localhost:8081/subjects/](http://localhost:8081/subjects/). Docs here: https://docs.confluent.io/platform/current/schema-registry/develop/api.html
To access connects rest api visit [http://localhost:8083/](http://localhost:8083/). Docs here: https://docs.confluent.io/platform/current/connect/references/restapi.html

```
evaisman in ~/vs-code-workspace/c18e/kafka-crash-course-training-src/solution on main ● ● λ docker compose up -d
[+] Running 6/6
 ⠿ Network solution_default     Created                                                                                                3.9s
 ⠿ Container solution_zoo1_1    Started                                                                                                3.3s
 ⠿ Container solution_kafka1_1  Started                                                                                                6.9s
 ⠿ Container schema-registry    Started                                                                                               10.7s
 ⠿ Container connect            Started                                                                                               14.5s
 ⠿ Container solution_akhq_1    Started                                                                                               18.1s
```

### Running your application

For details on how to run applicaton, navigate to your desired folder and follow those instructions.

### Kafka CLI Tools

You can exec into the Kafka broker container and run the Kafka command line tools.

Start a shell in the broker container:
```
evaisman in ~/vs-code-workspace/c18e/kafka-crash-course-training-src/solution on main ● ● λ docker compose exec kafka1 bash
bash-5.1# 
```

List topics (Note: test-topic was created when the demo scripts were run)
```
bash-5.1# kafka-topics.sh --bootstrap-server localhost:9092 --list
__consumer_offsets
_schemas
docker-connect-configs
docker-connect-offsets
docker-connect-status
```

Create a new topic
```
bash-5.1# kafka-topics.sh --bootstrap-server localhost:9092 --create --topic mytopic
Created topic mytopic.
bash-5.1# kafka-topics.sh --bootstrap-server localhost:9092 --list
__consumer_offsets
_schemas
docker-connect-configs
docker-connect-offsets
docker-connect-status
mytopic
```

Delete a topic
```
bash-5.1# kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic mytopic
bash-5.1# kafka-topics.sh --bootstrap-server localhost:9092 --list
__consumer_offsets
_schemas
docker-connect-configs
docker-connect-offsets
docker-connect-status
```