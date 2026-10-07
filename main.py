from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()


class SentimentRequest(BaseModel):
    sentences: list[str]


# Common positive words/phrases
POSITIVE = {
    "love", "loved", "loving", "like", "liked", "great", "excellent",
    "amazing", "awesome", "wonderful", "fantastic", "good", "happy",
    "best", "perfect", "nice", "enjoy", "enjoyed", "enjoyable",
    "success", "successful", "win", "won", "beautiful", "helpful",
    "impressive", "brilliant", "thank", "thanks", "excited", "fun",
    "pleasant", "satisfied", "recommend", "recommendation", "positive"
}

# Common negative words/phrases
NEGATIVE = {
    "hate", "hated", "horrible", "terrible", "awful", "bad", "worst",
    "poor", "sad", "angry", "disappointed", "disappointing", "failure",
    "failed", "fail", "problem", "problems", "broken", "useless",
    "boring", "annoying", "annoyed", "wrong", "negative", "pain",
    "painful", "hard", "difficult", "issue", "issues", "worse",
    "unhappy", "frustrated", "frustrating", "regret", "regretted"
}

# Strong phrases
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


def sentiment(text: str) -> str:
    text_lower = text.lower()
    
    # Normalize punctuation
    clean = re.sub(r"[^a-z0-9'\s]", " ", text_lower)
    clean = re.sub(r"\s+", " ", clean).strip()

    # Check strong phrases first
    positive_score = 0
    negative_score = 0

    for phrase in POSITIVE_PHRASES:
        if phrase in clean:
            positive_score += 2

    for phrase in NEGATIVE_PHRASES:
        if phrase in clean:
            negative_score += 2

    words = clean.split()

    for word in words:
        if word in POSITIVE:
            positive_score += 1
        if word in NEGATIVE:
            negative_score += 1

    # Basic negation handling
    negations = {"not", "no", "never", "n't"}

    for i, word in enumerate(words):
        if word in negations and i + 1 < len(words):
            next_word = words[i + 1]

            if next_word in POSITIVE:
                positive_score -= 1
                negative_score += 2

            if next_word in NEGATIVE:
                negative_score -= 1
                positive_score += 2

    if positive_score > negative_score:
        return "happy"

    if negative_score > positive_score:
        return "sad"

    return "neutral"


@app.post("/sentiment")
async def analyze_sentiment(request: SentimentRequest):
    results = []

    for sentence in request.sentences:
        results.append({
            "sentence": sentence,
            "sentiment": sentiment(sentence)
        })

    return {"results": results}
