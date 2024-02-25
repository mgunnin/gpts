import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Load and preprocess the dataset
lol_data = pd.read_csv('./knowledge/lol_match_details_2023.csv')
label_encoder = LabelEncoder()
teamname_encoded = label_encoder.fit_transform(lol_data['teamname'])
reduced_features = ['kills', 'deaths', 'assists', 'teamkills', 'teamdeaths', 'firstblood', 'dragons', 'opp_dragons']
reduced_features_combined = lol_data[reduced_features].fillna(0)
reduced_features_combined['teamname_encoded'] = teamname_encoded

# Feature Scaling
scaler = StandardScaler()
features_scaled = scaler.fit_transform(reduced_features_combined)

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(features_scaled, lol_data['result'], test_size=0.2, random_state=42)

# Model Training
model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=10)
model.fit(X_train, y_train)

# Model Prediction and Evaluation
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
precision = precision_score(y_test, predictions)
recall = recall_score(y_test, predictions)
f1 = f1_score(y_test, predictions)
conf_matrix = confusion_matrix(y_test, predictions)

# Output the evaluation metrics
accuracy, precision, recall, f1, conf_matrix

# Cross-Validation
cv_scores = cross_val_score(model, features_scaled, lol_data['result'], cv=5, scoring='accuracy')
cv_mean = cv_scores.mean()
cv_std = cv_scores.std()

# Feature Importance Analysis
feature_importances = model.feature_importances_
feature_names = reduced_features_combined.columns

importances_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': feature_importances
}).sort_values(by='Importance', ascending=False)

# Plotting feature importances
plt.figure(figsize=(12, 8))
plt.barh(importances_df['Feature'], importances_df['Importance'])
plt.xlabel('Importance')
plt.ylabel('Feature')
plt.title('Feature Importances in the Predictive Model')
plt.gca().invert_yaxis()
plt.show()

# Output cross-validation results
cv_mean, cv_std, cv_scores
