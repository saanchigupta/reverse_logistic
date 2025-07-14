import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Step 1: Read data
df = pd.read_csv("gdataset_100.csv")  # Ensure the file exists in your working directory

# Step 2: Encode categorical variable
le = LabelEncoder()
df['condition_encoded'] = le.fit_transform(df['condition'])

# Step 3: Define features and target
X = df[['condition_encoded', 'days_used']]
y = df['score']

# Step 4: Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Step 5: Initialize and train model with tuned parameters
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    min_samples_split=5,
    random_state=42
)
model.fit(X_train, y_train)

# Step 6: Cross-validation (5-fold)
cv_scores = cross_val_score(model, X_train, y_train, scoring='neg_mean_squared_error', cv=5)
cv_rmse = np.mean(np.sqrt(-cv_scores))
print(f"Average Cross-Validation RMSE: {cv_rmse:.2f}")

# Step 7: Evaluate on test set
y_pred = model.predict(X_test)
print("R² Score on Test Set:", r2_score(y_test, y_pred))
print("Mean Squared Error on Test Set:", mean_squared_error(y_test, y_pred))

# Step 8: Predict new input
new_condition = "Good"
new_days_used = 80
new_condition_encoded = le.transform([new_condition])[0]
new_input = pd.DataFrame([[new_condition_encoded, new_days_used]], columns=X.columns)
predicted_score = model.predict(new_input)[0]
print(f"Predicted score for condition = '{new_condition}', days_used = {new_days_used}: {round(predicted_score, 2)}")

# Step 9: Hyperparameter tuning (optional)
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10]
}
grid_search = GridSearchCV(
    estimator=RandomForestRegressor(random_state=42),
    param_grid=param_grid,
    cv=5,
    scoring='neg_mean_squared_error',
    n_jobs=-1
)
grid_search.fit(X_train, y_train)
print("Best parameters from grid search:", grid_search.best_params_)

# Step 10: Evaluate best model from grid search
best_model = grid_search.best_estimator_
y_pred_best = best_model.predict(X_test)
print("R² Score on Test Set with Best Model:", r2_score(y_test, y_pred_best))
print("Mean Squared Error on Test Set with Best Model:", mean_squared_error(y_test, y_pred_best))

# Step 11: Save the model and label encoder
joblib.dump(best_model, 'random_forest_model.pkl')
joblib.dump(le, 'label_encoder.pkl')

# Step 12: Predict using saved model
loaded_model = joblib.load('random_forest_model.pkl')
loaded_le = joblib.load('label_encoder.pkl')
encoded = loaded_le.transform([new_condition])[0]
new_input = pd.DataFrame([[encoded, new_days_used]], columns=["condition_encoded", "days_used"])
predicted = loaded_model.predict(new_input)[0]
print(f"Predicted score using saved model: {round(predicted, 2)}")

# Step 13: Save processed dataset
df.to_csv("processed_dataset.csv", index=False)
print("✅ Model training complete. Artifacts saved.")
