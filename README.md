# Tic Tac Toe simple application
this is a simple application runs using kafka to simulate playing tic-tac-toe

To run it:
    1. install docker
    2. open terminal and go to repository root directory 
    3. docker compose up -d
    4. go to http://localhost:8080 and create three new topics ['player1-topic', 'player2-topic', 'judge-topic']
    5. cd src
    6. python -m venv venv
    7. open 3 terminals
    8. for each one of them
        ⋅⋅1. cd venv/Scripts *
        ⋅⋅2. activate
        ⋅⋅3. cd ../..
        - pip install -r requirements.txt
        - first terminal
            - python ./player1.py -b localhost:9092 -s http://localhost:8081
        - second terminal
            - python ./player2.py -b localhost:9092 -s http://localhost:8081
        - third terminal
            - python ./judge.py -b localhost:9092 -s http://localhost:8081
        - make sure you run player1 then player2 then judge
    - gg