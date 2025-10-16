import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

# 1️⃣ Load your saved model and vectorizer
model = joblib.load("urgency_model.pkl")
vectorizer = joblib.load("urgency_vectorizer.pkl")

# 2️⃣ Load your dataset
data = pd.read_csv("urgency_dataset.csv")

# 3️⃣ Combine the text columns
data["text"] = data["ItemName"] + " " + data["Description"] + " " + data["Category"]

# 4️⃣ Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    data["text"], data["Urgency"], test_size=0.2, random_state=42
)

# 5️⃣ Convert the text to numerical vectors using the same vectorizer
X_test_vec = vectorizer.transform(X_test)

# 6️⃣ Predict urgency for the test data
y_pred = model.predict(X_test_vec)

# 7️⃣ Check the accuracy
print("✅ Model Accuracy:", accuracy_score(y_test, y_pred))
print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))
