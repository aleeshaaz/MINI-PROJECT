# train_urgency_model.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# Step 1: Load dataset
df = pd.read_csv("urgency_dataset.csv")
df.dropna(inplace=True)

# Step 2: Combine text features
df["text"] = df["ItemName"] + " " + df["Description"] + " " + df["Category"]

# Step 3: Split data
X_train, X_test, y_train, y_test = train_test_split(df["text"], df["Urgency"], test_size=0.2, random_state=42)

# Step 4: Vectorize text
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Step 5: Train model
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# Step 6: Evaluate
pred = model.predict(X_test_vec)
print("Accuracy:", accuracy_score(y_test, pred))

# Step 7: Save model and vectorizer
joblib.dump(model, "urgency_model.pkl")
joblib.dump(vectorizer, "urgency_vectorizer.pkl")
print("✅ Model and vectorizer saved successfully!")
