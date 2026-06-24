import pickle

model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

text = "Best product ever!!! Must buy!!! Highly recommended!!!"

vec = vectorizer.transform([text])

pred = model.predict(vec)[0]
prob = model.predict_proba(vec)[0]

print("Prediction:", pred)
print("Probabilities:", prob)