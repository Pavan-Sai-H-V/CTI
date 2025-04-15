import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

# Download required NLTK data
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')

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

def classify_threat(text):
    # Load model components
    vectorizer = joblib.load("vectorizer.joblib")
    classifier = joblib.load("threat_classifier.joblib")
    categories = joblib.load("categories.joblib")
    
    # Preprocess input text
    processed_text = preprocess_text(text)
    
    # Transform and predict
    X = vectorizer.transform([processed_text])
    prediction = classifier.predict(X)[0]
    probabilities = classifier.predict_proba(X)[0]
    
    # Get top 3 predictions with confidence scores
    top_n = 3
    top_indices = probabilities.argsort()[-top_n:][::-1]
    top_predictions = [(categories[i], float(probabilities[i])) for i in top_indices]
    
    return {
        "primary_prediction": prediction,
        "confidence_scores": top_predictions
    }
