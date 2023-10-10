
# Currency Exchange Monitor & Alert Agent

Created the Currency Exchange Monitor and Alert Agent with GUI using uAgent library, a tool that:

a) Allows users to select their base currency and one or more foreign currencies they wish to monitor.

b) Connects to a currency exchange API to fetch real-time exchange rates.

c) Lets users set thresholds for alerts (e.g., notify me if 1 USD becomes more than 82.60 INR or less
than 82.55 EUR).

d) Sends an alert/notification to the user when the exchange rate crosses the thresholds they've set.






## Installation

Download this repository by running

```bash
git clone https://github.com/RushabhBhalgat/Hack-230690.git
```
First we need to install all the necessary libraries to run the program.

```
pip install -r requirements.txt
```

Now, create a .env file in src folder to store all the API keys and other user data which are:

```
ACCESS_TOKEN=
EMAIL=
APP_PASSWORD=
EXCHANGE_AGENT_SEED=
NOTIFY_AGENT_SEED=
USER_AGENT_SEED=
EXCHANGE_AGENT_ADDRESS=
NOTIFY_AGENT_ADDRESS=
```
you can get the API key from https://currencyapi.com/

Now run the main.py file

Hack-230690
