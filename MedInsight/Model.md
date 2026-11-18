Overview of the Machine Learning Pipeline
Raw CSV Data
     │
     ▼
Stage 1: Data Cleaning          src/data_cleaning.py
     │
     ▼
Stage 2: Feature Extraction     src/features.py
     │
     ▼
Stage 3: Model Comparison       src/model.py
     │
     ▼
Stage 4: Hyperparameter Tuning  src/tuning.py
     │
     ▼
Final Model: final_model.pkl
(Logistic Regression Model)
Stage 1 — Data Cleaning (src/data_cleaning.py)
1.1 Loading and Merging the Dataset

The original dataset was provided in two separate CSV files for training and testing. Both files were loaded and merged into a single dataset so that all available records could be used during training.

import pandas as pd
import numpy as np
import re

train = pd.read_csv("data/drugsComTrain_raw.csv")
test = pd.read_csv("data/drugsComTest_raw.csv")

df = pd.concat([train, test], ignore_index=True)

df = df[['drugName', 'condition', 'review',
         'rating', 'date', 'usefulCount']]
Reason for This Step

Combining the datasets increases the amount of training data available for the model. This is especially important for the minority classes, which contain fewer reviews than the Depression class.

1.2 Handling Missing Values

Records with missing values in important columns were removed.

df = df.dropna(subset=['condition', 'review', 'rating'])
Reason for This Step
Records without a condition label cannot be used for supervised learning.
Records without review text provide no textual information for classification.
Missing values in these columns cannot be meaningfully estimated.
1.3 Standardising Condition Labels

Some records used different labels for the same condition. These labels were standardised to ensure consistency.

df['condition'] = df['condition'].replace({
    'Diabetes, Type 2': 'Type 2 Diabetes'
})
Reason for This Step

Without standardisation, the model would treat the same condition as different categories, reducing training quality and prediction accuracy.

1.4 Filtering Target Conditions

The dataset originally contained reviews for many medical conditions. Only the three target conditions were retained.

conditions = [
    'Depression',
    'High Blood Pressure',
    'Type 2 Diabetes'
]

df = df[df['condition'].isin(conditions)]
1.5 Removing Outliers
Rating Validation

Only ratings between 1 and 10 were kept.

df = df[(df['rating'] >= 1) & (df['rating'] <= 10)]
UsefulCount Outliers

Reviews with extremely large usefulness counts were removed.

df = df[df['usefulCount'] < 1000]
Reason for This Step

The usefulCount feature contained several extremely high values that could distort feature scaling and influence the model unfairly. Removing these outliers improved data consistency.

1.6 Text Cleaning

The review text was cleaned and normalised before feature extraction.

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

df['review'] = df['review'].apply(clean_text)
Text Cleaning Operations
Convert text to lowercase
Remove punctuation and special characters
Remove extra spaces
Reason for This Step

Text cleaning improves consistency and reduces noise in the dataset. It ensures that words such as “Good” and “good” are treated as the same token during feature extraction.

1.7 Removing Duplicate Records

Duplicate rows were removed before saving the cleaned dataset.

df = df.drop_duplicates()

df.to_csv("cleaned_data.csv", index=False)
Final Dataset Size
Condition	Number of Reviews
Depression	12,162
Type 2 Diabetes	3,362
High Blood Pressure	3,104

Total Records: 18,628

Stage 2 — Feature Extraction (src/features.py)
2.1 TF-IDF Vectorisation

The cleaned review text was transformed into numerical form using TF-IDF vectorisation.

from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words='english',
    ngram_range=(1, 2),
    sublinear_tf=True
)

X_text = vectorizer.fit_transform(df['review'])
TF-IDF Parameter Explanation
Parameter	Value	Purpose
max_features	5000	Limits vocabulary size to the most informative terms
stop_words	english	Removes common English words
ngram_range	(1,2)	Includes single words and two-word phrases
sublinear_tf	True	Reduces the influence of highly repeated words
2.2 Numerical Feature Scaling

The numerical features were normalised using Min-Max Scaling.

from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import hstack, csr_matrix

scaler = MinMaxScaler()

numerical_scaled = scaler.fit_transform(
    df[['rating', 'usefulCount']].fillna(0).values
)

X_numerical = csr_matrix(numerical_scaled)

X_combined = hstack([X_text, X_numerical])

y = df['condition']
Reason for This Step

Feature scaling ensures that large numerical values do not dominate smaller features during training.

2.3 Splitting Training and Testing Data

The dataset was divided into training and testing sets.

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X_combined,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
Dataset Split
Dataset	Records
Training Set	14,902
Testing Set	3,726
Reason for Using Stratification

Stratified sampling preserves the class distribution in both datasets, ensuring reliable evaluation results.

Stage 3 — Model Comparison (src/model.py)

Three machine learning models were evaluated using the same feature set.

from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

# Naïve Bayes
nb = MultinomialNB(alpha=1.0)
nb.fit(X_train, y_train)

# Logistic Regression
lr = LogisticRegression(
    max_iter=300,
    class_weight='balanced',
    C=1.0,
    random_state=42
)
lr.fit(X_train, y_train)

# Linear SVC
svc = LinearSVC(
    max_iter=1000,
    class_weight='balanced',
    C=1.0,
    random_state=42
)
svc.fit(X_train, y_train)
Model Comparison Results
Model	Evaluation
Naïve Bayes	Fast but less accurate on minority classes
Linear SVC	Strong performance but no probability output
Logistic Regression	Best balance of accuracy and interpretability
Selected Model — Logistic Regression

Logistic Regression was selected because:

It performed best overall on TF-IDF features
It provides probability predictions
It is easier to interpret in healthcare applications
It handles high-dimensional sparse data effectively

The parameter class_weight='balanced' was used to reduce the effect of class imbalance.

Stage 4 — Hyperparameter Tuning (src/tuning.py)
4.1 Baseline Model Evaluation

A baseline Logistic Regression model was first evaluated.

baseline = LogisticRegression(
    max_iter=300,
    class_weight='balanced',
    random_state=42
)

baseline.fit(X_train, y_train)

baseline_acc = accuracy_score(
    y_test,
    baseline.predict(X_test)
)
4.2 Grid Search Cross-Validation

Grid Search was used to test multiple parameter combinations.

from sklearn.model_selection import GridSearchCV

param_grid = {
    'C': [0.01, 0.1, 1.0, 5.0, 10.0],
    'solver': ['lbfgs', 'saga'],
    'max_iter': [300, 500]
}

grid_search = GridSearchCV(
    LogisticRegression(
        class_weight='balanced',
        random_state=42
    ),
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train, y_train)
Hyperparameter Explanation
Parameter	Purpose
C	Controls regularisation strength
solver	Determines the optimisation algorithm
max_iter	Maximum training iterations
4.3 Final Model Evaluation

The best model from Grid Search was evaluated using classification metrics.

tuned_model = grid_search.best_estimator_

tuned_preds = tuned_model.predict(X_test)

print(classification_report(y_test, tuned_preds))

Cross-validation was also performed to confirm model stability.

from sklearn.model_selection import cross_val_score

cv_scores = cross_val_score(
    tuned_model,
    X_train,
    y_train,
    cv=5,
    scoring='accuracy'
)
4.4 Saving the Final Model

The final trained model and TF-IDF vectoriser were saved using Pickle.

import pickle

with open("final_model.pkl", "wb") as f:
    pickle.dump(tuned_model, f)
with open("tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

These files are later loaded by the Streamlit dashboard during prediction.

Final Model Summary
Property	Value
Algorithm	Logistic Regression
Feature Representation	TF-IDF + Numerical Features
Vocabulary Size	5,000 Terms
Total Features	5,002
Train-Test Split	80/20
Split Method	Stratified Sampling
Hyperparameter Tuning	GridSearchCV
Output	Predicted Condition + Probabilities
Reproducing the Model

To reproduce the model from the beginning, run the following commands in order:

python src/data_cleaning.py
python src/features.py
python src/model.py
python src/tuning.py

The final trained model is saved as:

final_model.pkl
tfidf_vectorizer.pkl