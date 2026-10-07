from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re

app = FastAPI()

# Allow requests from the TDS evaluator / any website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SentimentRequest(BaseModel):
    sentences: list[str]


# Positive words
POSITIVE = {
    "love", "loved", "loving", "like", "liked",
    "great", "excellent", "amazing", "awesome",
    "wonderful", "fantastic", "good", "happy",
    "best", "perfect", "nice", "enjoy", "enjoyed",
    "success", "successful", "win", "won",
    "beautiful", "helpful", "impressive", "brilliant",
    "thank", "thanks", "excited", "fun",
    "pleasant", "satisfied", "recommend",
    "recommendation", "positive"
}


# Negative words
NEGATIVE = {
    "hate", "hated", "horrible", "terrible", "awful",
    "bad", "worst", "poor", "sad", "angry",
    "disappointed", "disappointing", "failure",
    "failed", "fail", "problem", "problems",
    "broken", "useless", "boring", "annoying",
    "annoyed", "wrong", "negative", "pain",
    "painful", "hard", "difficult", "issue",
    "issues", "worse", "unhappy", "frustrated",
    "frustrating", "regret", "regretted"
}


# Strong positive phrases
POSITIVE_PHRASES = {
    "very good",
    "really good",
    "very happy",
    "really happy",
    "highly recommend",
    "love this",
    "love it",
    "works great",
    "works perfectly",
    "well done",
    "thank you"
}


# Strong negative phrases
NEGATIVE_PHRASES = {
    "very bad",
    "really bad",
    "very sad",
    "really sad",
    "very disappointed",
    "really disappointed",
    "not good",
    "not happy",
    "doesn't work",
    "does not work",
    "doesnt work",
    "worst ever",
    "waste of money"
}


def get_sentiment(text: str) -> str:

    text = text.lower()

    # Remove punctuation
    text = re.sub(r"[^a-z0-9'\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    positive_score = 0
    negative_score = 0

    # Check positive phrases
    for phrase in POSITIVE_PHRASES:
        if phrase in text:
            positive_score += 2

    # Check negative phrases
    for phrase in NEGATIVE_PHRASES:
        if phrase in text:
            negative_score += 2

    # Check individual words
    words = text.split()

    for word in words:

        if word in POSITIVE:
            positive_score += 1

        if word in NEGATIVE:
            negative_score += 1

    # Basic negation handling
    negations = {"not", "no", "never"}

    for i, word in enumerate(words):

        if word in negations and i + 1 < len(words):

            next_word = words[i + 1]

            if next_word in POSITIVE:
                positive_score -= 1
                negative_score += 2

            elif next_word in NEGATIVE:
                negative_score -= 1
                positive_score += 2

    # Final decision
    if positive_score > negative_score:
        return "happy"

    elif negative_score > positive_score:
        return "sad"

    else:
        return "neutral"


@app.post("/sentiment")
async def analyze_sentiment(request: SentimentRequest):

    results = []

    for sentence in request.sentences:

        results.append({
            "sentence": sentence,
            "sentiment": get_sentiment(sentence)
        })

    return {
        "results": results
    }