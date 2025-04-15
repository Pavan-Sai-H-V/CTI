import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

# Download required NLTK data
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')

# Text preprocessing function
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Tokenize
    tokens = nltk.word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(tokens)

# Load and preprocess dataset
print("Loading dataset...")
df = pd.read_csv("threats_dataset.csv")
df['processed_description'] = df['description'].apply(preprocess_text)

X = df["processed_description"]
y = df["category"]

# Print dataset statistics
print("\nDataset Statistics:")
print(f"Total samples: {len(df)}")
print("\nSamples per category:")
print(y.value_counts())

# Split for training/testing
print("\nSplitting dataset...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Create pipeline with enhanced features
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),  # Include both single words and word pairs
        min_df=2,  # Minimum document frequency
        max_df=0.95  # Maximum document frequency
    )),
    ("clf", RandomForestClassifier(
        n_estimators=200,
        max_depth=50,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight='balanced',
        random_state=42
    ))
])

# Train model
print("\nTraining model...")
pipeline.fit(X_train, y_train)

# Evaluate
print("\nEvaluating on test set...")
y_pred = pipeline.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save model components
print("\nSaving model components...")
joblib.dump(pipeline.named_steps['clf'], "threat_classifier.joblib")
joblib.dump(pipeline.named_steps['tfidf'], "vectorizer.joblib")

# Save categories
categories = sorted(y.unique())
joblib.dump(categories, "categories.joblib")

print("\n✅ Model training complete. Components saved:")
print("- threat_classifier.joblib")
print("- vectorizer.joblib")
print("- categories.joblib")
