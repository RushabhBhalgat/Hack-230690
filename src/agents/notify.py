import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

import dotenv
from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low

from messages.basic import Notification
from utils.email_utils import send_template_email

# Load environment variables
dotenv.load_dotenv()

# Create notify agent
NOTIFY_AGENT_SEED = os.getenv("NOTIFY_AGENT_SEED", "notify agent secret phrase")

notify_agent = Agent(
    name="notify",
    seed=NOTIFY_AGENT_SEED,
    port=8002,
    endpoint=["http://127.0.0.1:8002/submit"],
)

# Ensure the agent has enough funds
fund_agent_if_low(notify_agent.wallet.address())

# Function to handle sending email
async def send_email(ctx: Context, name: str, to: str, subject: str, msg: Notification):
    fromaddr = os.getenv("EMAIL")
    password = os.getenv("APP_PASSWORD")

    if not fromaddr or not password:
        return False, "Email credentials not found"

    message = MIMEMultipart()
    message["To"] = f"{name} <{to}>"
    message["From"] = fromaddr
    message["Subject"] = subject

    message.attach(MIMEText(generate_body(msg), "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo("Gmail")
        server.starttls()
        server.login(fromaddr, password)
        server.sendmail(fromaddr, to, message.as_string())

        server.quit()
    except Exception as e:
        return False, str(e)

    return True, "Email sent"

# Function to generate the mail body from the template
def generate_body(msg: Notification):
    alerts = []
    for n in msg.notif:
        tmp = {}
        tmp["target_cur"] = n[0]
        tmp["current_rate"] = n[1]
        tmp["threshold"] = n[2]
        tmp["type"] = "Max" if n[1] > n[2] else "Min"
        alerts.append(tmp)
    context = {
        "name": msg.name,
        "ismultiple": len(msg.notif) > 1,
        "alerts": alerts,
        "base_cur": msg.base_cur,
    }
    body = send_template_email(**context)
    return body

# Create a protocol for notifications
notify_protocol = Protocol("Notify")

# Function to handle incoming notifications requests
@notify_protocol.on_message(model=Notification)
async def handle_notification(ctx: Context, sender: str, msg: Notification):
    ctx.logger.info(f"Received notification from user({sender[:20]}):\n{msg}")
    success, data = await send_email(
        ctx, msg.name, msg.email, "Currency Conversion", msg
    )
    if success:
        ctx.logger.info("Email sent successfully")
    else:
        ctx.logger.error(f"Error sending email: {data}")

# Include protocol with the agent
notify_agent.include(notify_protocol)
