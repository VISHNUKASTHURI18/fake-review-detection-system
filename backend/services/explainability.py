def get_suspicious_words(review):
    suspicious = [
        "best",
        "must buy",
        "amazing",
        "highly recommended",
        "perfect",
        "excellent"
    ]

    found = []

    review_lower = review.lower()

    for word in suspicious:
        if word in review_lower:
            found.append(word)

    return found