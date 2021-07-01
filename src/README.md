### Creating your venv

For our example, we will use a virtual python environment.
```
python3 -m venv venv
source venv/bin/activate
```

### Installing required packages

In your virtual environment. Install the packages specified in `requirements.txt`.
```
(venv) evaisman in ~/vs-code-workspace/c18e/kafka-crash-course-training-src/solution/python-clients-avro on main ● ● λ pip install -r requirements.txt
```

## Running your clients

### Producer
```
python ./avro_producer_v1.py -b localhost:9092 -s http://localhost:8081
python ./avro_producer_v2.py -b localhost:9092 -s http://localhost:8081
```

### Consumer
```
python ./avro_consumer_v1.py -b localhost:9092 -s http://localhost:8081
python ./avro_consumer_v2.py -b localhost:9092 -s http://localhost:8081
```