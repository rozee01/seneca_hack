from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline


sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

app = FastAPI()

class TweetRequest(BaseModel):
    tweet: str

@app.post("/predict")
def predict_sentiment(request: TweetRequest):
    result = sentiment_pipeline(request.text[:512])[0]
    return {"label": result['label'], "score": result['score']}
