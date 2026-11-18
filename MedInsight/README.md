Project Overview

The purpose of this project is to develop a machine learning system that can classify medical conditions based on patient drug reviews. The system focuses on three conditions:

Depression
High Blood Pressure
Type 2 Diabetes

The model analyses patient review text together with numerical information such as ratings and usefulness scores to identify patterns related to each condition. Using these patterns, the system predicts the most likely medical condition from a given review.

The main business objective of the project is to improve the use of patient experience data in healthcare and pharmaceutical environments. Instead of manually analysing large amounts of unstructured reviews, the system automatically extracts useful information from patient feedback. This helps healthcare professionals and researchers understand drug effectiveness, identify common side effects, and recommend suitable treatments based on patient experiences.

The system is deployed through an interactive web dashboard that allows users to make predictions in real time.

Dataset

The dataset used in this project was obtained from the UCI Machine Learning Repository (Drug Review Dataset from Drugs.com). The dataset contains the following features:

Feature	Description
drugName	Name of the reviewed drug
condition	Medical condition treated by the drug
review	Patient review text
rating	Patient rating score from 1 to 10
date	Date the review was submitted
usefulCount	Number of users who found the review helpful

Only records related to the three selected conditions were used in the project. After data cleaning, the dataset contained 18,628 records distributed as follows:

Depression — 12,162 reviews
Type 2 Diabetes — 3,362 reviews
High Blood Pressure — 3,104 reviews
Machine Learning Pipeline

The project follows a complete machine learning pipeline from data preparation to deployment.

Stage 1 — Data Cleaning (src/data_cleaning.py)

The raw training and testing datasets were loaded, combined, and filtered to include only the three selected medical conditions. Missing values in important columns such as review and condition were removed. Numerical missing values were replaced using column averages.

Outliers in the usefulCount feature were identified using the Interquartile Range (IQR) method and limited to reduce their effect on model performance. The cleaned dataset was then saved as cleaned_data.csv.

Stage 2 — Feature Extraction and Preprocessing (src/features.py)

The review text was preprocessed using standard Natural Language Processing (NLP) techniques, including:

Converting text to lowercase
Removing punctuation and special characters
Removing stop words
Stemming and lemmatisation

After preprocessing, the text was converted into numerical form using TF-IDF (Term Frequency–Inverse Document Frequency). A maximum vocabulary size of 5,000 features was used together with bigrams to capture important word combinations.

The numerical features rating and usefulCount were normalised using Min-Max scaling and combined with the TF-IDF features to create the final dataset used for training.

Stage 3 — Model Selection (src/model.py)

Three machine learning algorithms were evaluated:

Naïve Bayes
Decision Tree
Logistic Regression

The models were compared using accuracy, precision, recall, and F1-score.

Logistic Regression was selected as the final model because it achieved the best overall performance. It also handled high-dimensional TF-IDF data effectively and provided better interpretability, which is important in healthcare-related applications.

Stage 4 — Model Training (src/model.py)

The dataset was divided into:

80% training data
20% testing data

Stratified sampling was used to maintain balanced class distributions.

The Logistic Regression model was trained using class_weight='balanced' to reduce the impact of class imbalance between Depression and the smaller classes. During training, the model learned patterns that distinguish the three medical conditions.

Stage 5 — Model Tuning (src/tuning.py)

Hyperparameter tuning was performed using Grid Search Cross-Validation. Different values of the regularisation parameter C and the maximum iteration count were tested.

The best parameter combination was selected based on the highest F1-score. This process improved the model’s ability to generalise and reduced overfitting.

Stage 6 — Prediction Dashboard (Home.py, pages/Predict.py, pages/Analytics.py)

An interactive dashboard was developed using Streamlit.

The dashboard allows users to:

Enter drug review text
Receive a predicted medical condition
View prediction probabilities for all conditions
Get drug recommendations based on historical ratings

All prediction activities are stored in a SQLite database (prediction_logs.db) for future analysis and auditing.

Project Structure
groupassignment/
│
├── Home.py
├── cleaned_data.csv
├── final_model.pkl
├── tfidf_vectorizer.pkl
├── requirements.txt
├── README.md
│
├── pages/
│   ├── Predict.py
│   ├── Analytics.py
│   └── Login.py
│
├── src/
│   ├── data_cleaning.py
│   ├── features.py
│   ├── model.py
│   ├── tuning.py
│   ├── model_training.py
│   ├── utils.py
│   ├── auth_db.py
│   ├── logs_db.py
│   └── styles.py
│
├── data/
│   ├── drugsComTrain_raw.csv
│   ├── drugsComTest_raw.csv
│   └── prediction_logs.db
│
├── notebooks/
│   └── eda.ipynb
│
├── backups/
│   ├── best_model_*.pkl
│   ├── final_model_*.pkl
│   └── tfidf_vectorizer_*.pkl
│
└── assets/
    └── logo.jpeg
Installation and Setup
Prerequisites
Python 3.8 or higher
pip package manager
Setup Instructions
1. Clone or download the project repository
git clone <repository-url>
cd groupassignment
2. Install required packages
pip install -r requirements.txt
3. Place the dataset files inside the data/ folder
drugsComTrain_raw.csv
drugsComTest_raw.csv
4. Run data cleaning
python src/data_cleaning.py
5. Extract features
python src/features.py
6. Train and evaluate models
python src/model.py
7. Run hyperparameter tuning
python src/tuning.py
8. Start the dashboard
streamlit run Home.py
Dependencies
Package	Purpose
pandas	Data analysis and manipulation
numpy	Numerical operations
scikit-learn	Machine learning and TF-IDF processing
matplotlib	Data visualisation
seaborn	Statistical visualisation
streamlit	Web dashboard development

Install all dependencies using:

pip install -r requirements.txt
Model Performance

The final Logistic Regression model was tested using the 20% test dataset. The following evaluation metrics were used:

Accuracy — Measures overall prediction correctness
Precision — Measures the accuracy of positive predictions
Recall — Measures how many actual positives were correctly identified
F1-Score — Balances precision and recall

The model achieved strong performance across all three conditions. The highest accuracy was achieved for Depression because it had the largest number of training samples. More detailed evaluation results and confusion matrices are available in the Analytics dashboard.

Key Design Decisions
Why Logistic Regression?

Logistic Regression performed better than Naïve Bayes and Decision Trees during model evaluation. It handled TF-IDF text features effectively, produced stable results, and provided interpretable predictions.

Naïve Bayes was fast but limited by its assumption that features are independent. Decision Trees showed signs of overfitting when working with high-dimensional text data.

Why TF-IDF Instead of Bag of Words?

TF-IDF reduces the importance of common words that appear in all reviews and increases the importance of condition-specific words. This improves the model’s ability to distinguish between different medical conditions.

Why Retrain the Model at Startup?

The model and vectoriser are retrained at application startup to avoid compatibility issues between different versions of scikit-learn. This prevents errors such as NotFittedError and AttributeError during deployment.
