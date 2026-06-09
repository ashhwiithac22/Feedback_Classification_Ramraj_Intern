import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('routed_feedback.csv')

# Merge rare classes (less than 3 samples)
dept_counts = df['Department'].value_counts()
rare_classes = dept_counts[dept_counts < 3].index.tolist()
if rare_classes:
    df['Department'] = df['Department'].apply(lambda x: 'Other' if x in rare_classes else x)

# Prepare data
X = df['Feedback'].values
y = df['Department'].values

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

# TF-IDF Vectorization
tfidf = TfidfVectorizer(max_features=300, ngram_range=(1, 2), stop_words='english', min_df=2)
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

# Logistic Regression
lr = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
lr.fit(X_train_tfidf, y_train)
lr_pred = lr.predict(X_test_tfidf)

# Naive Bayes
nb = MultinomialNB()
nb.fit(X_train_tfidf, y_train)
nb_pred = nb.predict(X_test_tfidf)

# Print results
print("="*50)
print("RAMRAJ COTTON - ML MODEL ACCURACY")
print("="*50)
print(f"\nTotal samples: {len(df)}")
print(f"Total departments: {len(np.unique(y))}")
print(f"\n📊 Logistic Regression Accuracy: {accuracy_score(y_test, lr_pred)*100:.2f}%")
print(f"📊 Naive Bayes Accuracy: {accuracy_score(y_test, nb_pred)*100:.2f}%")
print("\n" + "="*50)