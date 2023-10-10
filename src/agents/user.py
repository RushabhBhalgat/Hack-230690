import os
import json

import dotenv
from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low

from messages.basic import ConvertRequest, ConvertResponse, Error, Notification

# Load environment variables
dotenv.load_dotenv()

USER_AGENT_SEED = os.getenv("USER_AGENT_SEED", "user agent secret phrase")

# Create user agent
user_agent = Agent(
    name="user",
    seed=USER_AGENT_SEED,
    port=8003,
    endpoint=["http://127.0.0.1:8003/submit"],
)

# Ensure the agent has enough funds
fund_agent_if_low(user_agent.wallet.address())

# Address of exchange and notify agents
EXCHANGE_AGENT_ADDRESS = os.getenv("EXCHANGE_AGENT_ADDRESS")

NOTIFY_AGENT_ADDRESS = os.getenv("NOTIFY_AGENT_ADDRESS")

assert (
    EXCHANGE_AGENT_ADDRESS is not None
), "Need EXCHANGE_AGENT_ADDRESS, please check README file"

assert (
    NOTIFY_AGENT_ADDRESS is not None
), "Need NOTIFY_AGENT_ADDRESS, please check README file"

# Create a protocol for conversion requests and notifications
user_agent_convert_protocol = Protocol("Convert")
user_agent_notify_protocol = Protocol("Notify")

# Function to read the user preferences from "data.json" file
async def update_user_preference(ctx: Context, force=False):
    try:
        with open("data.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        ctx.logger.error("data.json not found. Skipping update.")
        return False
    except Exception as e:
        ctx.logger.error(f"Error in opening data.json : {e}")

    # check if data has been updated
    if data["hasChanged"] or force:
        ctx.logger.info("Updating internal state")
        ctx.storage.set("base", data["base"])
        ctx.storage.set("target", data["target"])
        ctx.storage.set("name", data["name"])
        ctx.storage.set("email", data["email"])
        data["hasChanged"] = False
        with open("data.json", "w") as file:
            json.dump(data, file)
        return True
    return False

# Function to initialize the storage on startup
@user_agent.on_event("startup")
async def initialize_storage(ctx: Context):
    # try to get user's preferences from data.json
    status = await update_user_preference(ctx, force=True)
    if status:
        return
    # else set default values
    ctx.storage.set("base", "INR")
    default_targets = {
        "USD": (1 / 85, 1 / 84),
        "EUR": (1 / 90, 1 / 85),
        "CAD": (1 / 58, 1 / 55),
    }
    ctx.storage.set("target", default_targets)
    ctx.storage.set("name", "Username")
    ctx.storage.set("email", "default.email@gmail.com")

# Timed function that will send a conversion request to exchange agent every 10 minutes
@user_agent_convert_protocol.on_interval(600, messages=ConvertRequest)
async def get_currency_conversion_rates(ctx: Context):
    # get updated user preferences
    await update_user_preference(ctx)

    ctx.logger.info(f"Request sent to Exchange agent({EXCHANGE_AGENT_ADDRESS[:15]}...)")
    await ctx.send(
        EXCHANGE_AGENT_ADDRESS,
        ConvertRequest(
            base_currency=ctx.storage.get("base"),
            target_currencies=list(ctx.storage.get("target").keys()),
        ),
    )

# Function to handle conversion response from exchange agent
@user_agent_convert_protocol.on_message(model=ConvertResponse)
async def handle_response(ctx: Context, sender: str, msg: ConvertResponse):
    ctx.logger.info(f"Received response from Exchange({sender[:15]}...)")
    thresholds = ctx.storage.get("target")
    notification = []
    for currency, rate in msg.rates.items():
        if rate <= thresholds[currency][0]:
            ctx.logger.critical(
                f"Rate for {currency} is {rate}. Sending alert to user."
            )
            notification.append((currency, rate, thresholds[currency][0]))
        elif rate >= thresholds[currency][1]:
            ctx.logger.critical(
                f"Rate for {currency} is {rate}. Sending alert to user."
            )
            notification.append((currency, rate, thresholds[currency][1]))
    if notification:
        await ctx.send(
            NOTIFY_AGENT_ADDRESS,
            Notification(
                name=ctx.storage.get("name"),
                email=ctx.storage.get("email"),
                base_cur=ctx.storage.get("base"),
                notif=notification,
            ),
        )

# Function to handle error from exchange agent
@user_agent_convert_protocol.on_message(model=Error)
async def handle_error(ctx: Context, sender: str, msg: Error):
    ctx.logger.error(f"Received Error from Exchange({sender[:15]}...): {msg.error}")

# Include protocols with the agent
user_agent.include(user_agent_convert_protocol)
user_agent.include(user_agent_notify_protocol)
