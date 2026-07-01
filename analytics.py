from collections import Counter
from statistics import mean


class Analytics:

    def __init__(self):

        self.total_questions = 0
        self.cache_hits = 0
        self.groq_calls = 0
        self.fallbacks = 0

        self.response_times = []

        self.topics = Counter()

    def question(self):

        self.total_questions += 1

    def cache_hit(self):

        self.cache_hits += 1

    def groq_call(self):

        self.groq_calls += 1

    def fallback(self):

        self.fallbacks += 1

    def response_time(self, seconds: float):

        self.response_times.append(seconds)

    def topic(self, topic: str):

        if topic:
            self.topics[topic] += 1

    def stats(self):

        return {
            "questions": self.total_questions,
            "cache_hits": self.cache_hits,
            "groq_calls": self.groq_calls,
            "fallbacks": self.fallbacks,
            "average_response": (
                round(mean(self.response_times), 2)
                if self.response_times
                else 0
            ),
            "top_topics": self.topics.most_common(10)
        }


analytics = Analytics()