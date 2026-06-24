import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

df = pd.read_csv(
    "new_data_test.csv",
    sep="\t"
)

df = df[["reviewContent", "flagged"]]

df.dropna(inplace=True)

X = df["reviewContent"]
y = df["flagged"]

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=10000,
    ngram_range=(1, 2)
)

X_vec = vectorizer.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_vec,
    y,
    test_size=0.2,
    random_state=42
)

model = LogisticRegression(
    max_iter=1000
)

model.fit(X_train, y_train)

pred = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    pred
)

print(
    "Accuracy:",
    round(accuracy * 100, 2),
    "%"
)

pickle.dump(
    model,
    open("model.pkl", "wb")
)

pickle.dump(
    vectorizer,
    open("vectorizer.pkl", "wb")
)

print("Model Saved Successfully")