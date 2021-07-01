# Tic Tac Toe simple application
this is a simple application runs using kafka to simulate playing tic-tac-toe

To run it:
    - install docker
    - open terminal and go to repository root directory 
    - docker compose up -d
    - go to http://localhost:8080 and create three new topics ['player1-topic', 'player2-topic', 'judge-topic']
    - cd src
    - python -m venv venv
    - open 3 terminals
    - for each one of them
        - cd venv/Scripts
        - activate
        - cd ../..
        - pip install -r requirements.txt
        - first terminal
            - python ./player1.py -b localhost:9092 -s http://localhost:8081
        - second terminal
            - python ./player2.py -b localhost:9092 -s http://localhost:8081
        - third terminal
            - python ./judge.py -b localhost:9092 -s http://localhost:8081
        - make sure you run player1 then player2 then judge
    - gg