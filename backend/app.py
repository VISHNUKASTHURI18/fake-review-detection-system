from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import sqlite3
import numpy as np

app = Flask(__name__)
CORS(app)

conn = sqlite3.connect("reviews.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    text TEXT,
    prediction INTEGER,
    confidence REAL
)
""")

conn.commit()

model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

def get_explanation(text):

    reasons = []

    suspicious_words = [
        "best",
        "must buy",
        "amazing",
        "excellent",
        "perfect",
        "highly recommended",
        "buy now"
    ]

    found_words = []

    text_lower = text.lower()

    for word in suspicious_words:
        if word in text_lower:
            found_words.append(word)

    if found_words:
        reasons.append("Contains promotional language")

    if "!!!" in text:
        reasons.append("Excessive punctuation detected")

    if len(text.split()) < 4:
        reasons.append("Very short review")

    if not reasons:
        reasons.append("Balanced review with no suspicious patterns")

    return reasons, found_words


def calculate_trust_score():

    cursor.execute("SELECT prediction FROM reviews")

    rows = cursor.fetchall()

    total = len(rows)

    if total == 0:
        return 100

    fake_count = len(
        [r for r in rows if r[0] == 0]
    )

    return round(
        100 - ((fake_count / total) * 100),
        2
    )


@app.route("/register", methods=["POST"])
def register():

    data = request.json

    try:

        cursor.execute(
            "INSERT INTO users(email,password) VALUES(?,?)",
            (
                data["email"],
                data["password"]
            )
        )

        conn.commit()

        return {
            "msg": "Registered Successfully"
        }

    except:

        return {
            "msg": "User already exists"
        }


@app.route("/login", methods=["POST"])
def login():

    data = request.json

    cursor.execute(
        """
        SELECT * FROM users
        WHERE email=? AND password=?
        """,
        (
            data["email"],
            data["password"]
        )
    )

    user = cursor.fetchone()

    return {
        "msg": "success" if user else "fail"
    }


@app.route("/predict", methods=["POST"])
def predict():

    data = request.json

    text = data["text"]
    email = data["email"]

    vec = vectorizer.transform([text])

    prediction = int(
        model.predict(vec)[0]
    )

    text_lower = text.lower()

    fake_keywords = [
        "must buy",
        "highly recommended",
        "buy now",
        "best product",
        "perfect product",
        "amazing product",
        "excellent product",
        "best ever"
    ]

    score = 0

    for word in fake_keywords:
        if word in text_lower:
            score += 1

    if "!!!" in text:
        score += 1

    if len(text.split()) < 4:
        score += 1

    if score >= 2:
        prediction = 0

    probabilities = model.predict_proba(vec)[0]

    confidence = float(
        np.max(probabilities)
    )

    explanation, suspicious_words = get_explanation(text)

    cursor.execute(
        """
        INSERT INTO reviews
        (email,text,prediction,confidence)
        VALUES(?,?,?,?)
        """,
        (
            email,
            text,
            prediction,
            round(confidence * 100, 2)
        )
    )

    conn.commit()

    trust_score = calculate_trust_score()

    return jsonify({

        "prediction":
        "Genuine Review"
        if prediction == 1
        else "Fake Review",

        "confidence":
        round(confidence * 100, 2),

        "explanation":
        explanation,

        "suspicious_words":
        suspicious_words,

        "trust_score":
        trust_score
    })


@app.route("/history/<email>")
def history(email):

    cursor.execute(
        """
        SELECT text,prediction,confidence
        FROM reviews
        WHERE email=?
        """,
        (email,)
    )

    rows = cursor.fetchall()

    data = []

    for row in rows:

        data.append({

            "text": row[0],

            "prediction": row[1],

            "confidence": row[2]
        })

    return jsonify(data)


@app.route("/analytics")
def analytics():

    cursor.execute(
        "SELECT prediction FROM reviews"
    )

    rows = cursor.fetchall()

    total = len(rows)

    fake_count = len(
        [r for r in rows if r[0] == 0]
    )

    real_count = total - fake_count

    trust_score = calculate_trust_score()

    return jsonify({

        "total_reviews": total,

        "fake_reviews": fake_count,

        "real_reviews": real_count,

        "trust_score": trust_score
    })


@app.route("/chat", methods=["POST"])
def chat():

    msg = request.json["message"].lower()

    if "fake" in msg:

        reply = (
            "Paste a review and I will analyze it."
        )

    elif "why" in msg:

        reply = (
            "Fake reviews often contain promotional language and excessive punctuation."
        )

    elif "trust score" in msg:

        reply = (
            "Trust score is calculated using all analyzed reviews."
        )

    else:

        reply = (
            "I help detect fake reviews and explain results."
        )

    return {
        "reply": reply
    }


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000,
        debug=True
    )