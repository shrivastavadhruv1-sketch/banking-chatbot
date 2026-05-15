import unittest

from chatbot import BankingChatbot


class BankingChatbotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = BankingChatbot(customer_name="Alex", balance=5000.0)

    def test_returns_balance_intent(self) -> None:
        response = self.bot.respond("Can you share my balance?")
        self.assertEqual(response.intent, "balance")
        self.assertIn("₹5,000.00", response.message)

    def test_returns_offer_intent(self) -> None:
        response = self.bot.respond("Any personalized offers for me?")
        self.assertEqual(response.intent, "personalized_offer")
        self.assertIn("pre-approved", response.message)

    def test_returns_fraud_alert_intent(self) -> None:
        response = self.bot.respond("I think there is a suspicious transaction")
        self.assertEqual(response.intent, "fraud_alert")
        self.assertIn("block your card", response.message)


if __name__ == "__main__":
    unittest.main()
