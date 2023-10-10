from uagents import Bureau
from agents.exchange import exchange_agent
from agents.user import user_agent
from agents.notify import notify_agent

def main():
    # Create a Bureau instance
    bureau = Bureau(endpoint="http://127.0.0.1:8000/submit", port=8000)

    # Add Exchange agent to Bureau
    exchange_address = exchange_agent.address
    print(f"Adding Exchange agent to Bureau: {exchange_address}")
    bureau.add(exchange_agent)

    # Add Notify agent to Bureau
    notify_address = notify_agent.address
    print(f"Adding Notify agent to Bureau: {notify_address}")
    bureau.add(notify_agent)

    # Add User agent to Bureau
    user_address = user_agent.address
    print(f"Adding User agent to Bureau: {user_address}")
    bureau.add(user_agent)

    # Run the Bureau
    bureau.run()

if __name__ == "__main__":
    main()








