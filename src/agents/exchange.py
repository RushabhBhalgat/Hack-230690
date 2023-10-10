import os
import requests
from typing import List

import dotenv
from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low

from messages.basic import ConvertRequest, ConvertResponse, Error

# Load environment variables
dotenv.load_dotenv()

# Configuration for Currency API
BASE_URL = "https://api.currencyapi.com/v3/latest"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

assert ACCESS_TOKEN is not None, "ACCESS_TOKEN not found in environment variables"

# Create exchange agent
EXCHANGE_AGENT_SEED = os.getenv("EXCHANGE_AGENT_SEED", "exchange agent secret phrase")

exchange_agent = Agent(
    name="exchange",
    seed=EXCHANGE_AGENT_SEED,
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"],
)

# Ensure the agent has enough funds
fund_agent_if_low(exchange_agent.wallet.address())

# Function to handle API call for exchange rates
async def get_exchange_rates(base_currency: str, target_currencies: List[str]):
    url = f'{BASE_URL}?apikey={ACCESS_TOKEN}&currencies={"%2C".join(target_currencies)}&base_currency={base_currency}'

    res = requests.get(url)
    if res.status_code == 200:
        exchange_rates = {}
        response_data = res.json()
        for symbol in response_data["data"].keys():
            exchange_rates[symbol] = response_data["data"][symbol]["value"]
        return True, exchange_rates
    else:
        error_message = res.json()["message"]
        return False, error_message

# Create a protocol for conversion requests
exchange_agent_protocol = Protocol("Convert")

# Function to handle incoming conversion requests
@exchange_agent_protocol.on_message(
    model=ConvertRequest, replies={ConvertResponse, Error}
)
async def handle_request(ctx: Context, sender: str, msg: ConvertRequest):
    ctx.logger.info(f"Received request from user({sender[:20]}):\n{msg}")
    success, data = await get_exchange_rates(msg.base_currency, msg.target_currencies)
    if success:
        await ctx.send(
            sender,
            ConvertResponse(rates=data),
        )
    else:
        ctx.logger.error(f"Error: {data}")
        await ctx.send(
            sender,
            Error(error=data),
        )

# Include the protocol with the agent
exchange_agent.include(exchange_agent_protocol)
