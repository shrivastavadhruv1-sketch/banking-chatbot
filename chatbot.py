import re
from dataclasses import dataclass


@dataclass
class ChatbotResponse:
    intent: str
    message: str


class BankingChatbot:
    def __init__(self, customer_name: str = "Customer", balance: float = 12500.75) -> None:
        self.customer_name = customer_name
        self.balance = balance

    def respond(self, user_message: str) -> ChatbotResponse:
        normalized = user_message.lower().strip()
        words = set(re.findall(r"[a-z']+", normalized))

        if {"hello", "hi", "hey"} & words:
            return ChatbotResponse(
                intent="greeting",
                message=f"Hello {self.customer_name}! I can help with balance, personalized offers, and fraud alerts.",
            )

        if "balance" in normalized:
            return ChatbotResponse(
                intent="balance",
                message=f"Your current available balance is ₹{self.balance:,.2f}.",
            )

        if any(term in normalized for term in ["offer", "offers", "deal", "card", "loan"]):
            return ChatbotResponse(
                intent="personalized_offer",
                message=(
                    "Based on your profile, you are pre-approved for a low-interest personal loan "
                    "and 5% cashback on online purchases."
                ),
            )

        if any(term in normalized for term in ["fraud", "suspicious", "unauthorized", "alert"]):
            return ChatbotResponse(
                intent="fraud_alert",
                message=(
                    "I can help secure your account. Please confirm if you want to temporarily block your card "
                    "and report suspicious activity."
                ),
            )

        return ChatbotResponse(
            intent="fallback",
            message=(
                "I didn’t fully understand that. Please ask about your balance, personalized offers, or fraud alerts."
            ),
        )


def main() -> None:
    bot = BankingChatbot(customer_name="Dhruv")
    print("Banking Chatbot: type 'exit' to end the chat.")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Banking Chatbot: Thanks for chatting. Stay safe!")
            break
        response = bot.respond(user_input)
        print(f"Banking Chatbot: {response.message}")


if __name__ == "__main__":
    main()
