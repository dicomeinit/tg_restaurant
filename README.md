## Installation

_NOTE: Make sure you have python3 installed on your system_, and you have installed `pip` and `virtualenv` packages.
Require Python3.9+

1. Create virtual environment

```bash
python3 -m venv venv
```

2. Activate virtual environment

```bash
source venv/bin/activate
```

3. Install requirements

```bash
pip install -r requirements.txt
```

4. Set up the database

```bash
make setup
```

5. Run the application

```bash
./manage.py runserver
```

6. Open the browser and go to `http://127.0.0.1:8000/admin` to see the application running.


7. Login with the following credentials:
    - Username: `admin`
    - Password: `admin`


8. Insert your bot token in the `.env` file


9. Run bot with command

```bash
./bot.py
```