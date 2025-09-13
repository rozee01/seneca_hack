import pandas as pd
import time
from transformers import pipeline

# -----------------------------
# 1. Charger le dataset
# -----------------------------
# Suppose ton dataset est un CSV avec une colonne "text" contenant les tweets
df = pd.read_csv("NBADataset.csv")

# On prend un sample de 2000 tweets pour tester (modifiable)
tweets = df["text"].dropna().sample(2000, random_state=42).tolist()

# -----------------------------
# 2. Définir les modèles candidats
# -----------------------------
models = {
    "roberta-base-sentiment": "cardiffnlp/twitter-roberta-base-sentiment",
   # "bertweet-sentiment": "finiteautomata/bertweet-base-sentiment-analysis",
    #"xlm-roberta-sentiment": "cardiffnlp/twitter-xlm-roberta-base-sentiment"
}

# -----------------------------
# 3. Fonction de test
# -----------------------------
def test_model(model_name, model_id, texts, batch_size=32):
    print(f"\n=== Test du modèle : {model_name} ({model_id}) ===")

    # Charger le pipeline HF
    nlp = pipeline("sentiment-analysis", model=model_id, tokenizer=model_id)

    results = []
    start_time = time.time()

    # Prédictions batchées
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        preds = nlp(batch)
        results.extend(preds)

    elapsed = time.time() - start_time
    speed = len(texts) / elapsed

    print(f"Temps total : {elapsed:.2f} sec")
    print(f"Vitesse : {speed:.2f} tweets/sec")

    return results, speed

# -----------------------------
# 4. Lancer les tests
# -----------------------------
all_results = {}

for model_name, model_id in models.items():
    preds, speed = test_model(model_name, model_id, tweets)
    # Sauvegarder les résultats
    df_out = pd.DataFrame({
        "tweet": tweets,
        "prediction": [p["label"] for p in preds],
        "score": [p["score"] for p in preds]
    })
    out_file = f"predictions_{model_name}.csv"
    df_out.to_csv(out_file, index=False, encoding="utf-8")
    print(f"Résultats sauvegardés dans {out_file}")

    all_results[model_name] = {"speed": speed, "rows": len(df_out)}

# -----------------------------
# 5. Résumé des vitesses
# -----------------------------
print("\nRésumé des performances :")
for m, stats in all_results.items():
    print(f"{m}: {stats['rows']} tweets traités, vitesse = {stats['speed']:.2f} tweets/sec")
