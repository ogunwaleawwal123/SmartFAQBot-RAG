TOPICS = {
    "vpn": [
        "vpn",
        "virtual private network",
        "ip",
        "ip address",
        "login history"
    ],
    "payout": [
        "payout",
        "withdraw",
        "withdrawal",
        "profit split",
        "profit",
        "payment"
    ],
    "drawdown": [
        "drawdown",
        "daily drawdown",
        "max drawdown",
        "loss limit",
        "equity"
    ],
    "challenge": [
        "challenge",
        "evaluation",
        "phase 1",
        "phase 2"
    ],
    "funded": [
        "funded",
        "funded account",
        "live account"
    ],
    "news": [
        "news",
        "high impact",
        "red folder",
        "economic news"
    ],
    "copy_trading": [
        "copy trading",
        "copier",
        "trade copier"
    ],
    "ea": [
        "ea",
        "expert advisor",
        "robot",
        "bot"
    ],
    "kyc": [
        "kyc",
        "identity",
        "verification",
        "verify"
    ]
}


def detect_topic(text: str) -> str | None:

    text = text.lower()

    for topic, keywords in TOPICS.items():

        for keyword in keywords:

            if keyword in text:
                return topic

    return None