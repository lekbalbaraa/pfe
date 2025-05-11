import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.feature_selection import SelectKBest, f_classif

# === 1. Load dataset ===
print("Loading dataset...")
df = pd.read_csv('iot23_combined.csv')  # Ensure correct path
label_col = 'label'

# === 2. Filter rare classes (less than 2 samples) ===
min_samples_required = 2
class_counts = df[label_col].value_counts()
valid_classes = class_counts[class_counts >= min_samples_required].index
df = df[df[label_col].isin(valid_classes)]

# === 3. Handle missing values ===
print("Handling missing values...")
imputer = SimpleImputer(strategy='median')
X = pd.DataFrame(imputer.fit_transform(df.drop(label_col, axis=1)), columns=df.drop(label_col, axis=1).columns)
y = df[label_col]

# === 4. Encode labels ===
print("Encoding labels...")
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# === 5. Feature scaling ===
print("Scaling features...")
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

# === 6. Feature selection (Select top 20 features) ===
print("Selecting best features...")
selector = SelectKBest(score_func=f_classif, k=20)
X_selected = selector.fit_transform(X_scaled, y_encoded)

# === 7. Train-test split ===
print("Splitting dataset...")
X_train, X_test, y_train, y_test = train_test_split(
    X_selected, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# === 8. Balance classes using SMOTE ===
print("Balancing classes using SMOTE...")
smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)

# === 9. Hyperparameter tuning for Random Forest ===
print("Optimizing Random Forest...")
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10]
}
grid_search = GridSearchCV(RandomForestClassifier(class_weight='balanced', random_state=42), param_grid, cv=3, verbose=2, n_jobs=-1)
grid_search.fit(X_train_bal, y_train_bal)

rf_best = grid_search.best_estimator_

# === 10. Alternative models (Boosting: XGBoost & LightGBM) ===
print("Training XGBoost...")
xgb = XGBClassifier(n_estimators=300, max_depth=8, learning_rate=0.1, use_label_encoder=False, eval_metric='logloss')
xgb.fit(X_train_bal, y_train_bal)

print("Training LightGBM...")
lgbm = LGBMClassifier(n_estimators=300, max_depth=8, learning_rate=0.1)
lgbm.fit(X_train_bal, y_train_bal)

# === 11. Predictions ===
print("Making predictions...")
models = {"RandomForest": rf_best, "XGBoost": xgb, "LightGBM": lgbm}
for name, model in models.items():
    y_pred = model.predict(X_test)
    y_test_labels = le.inverse_transform(y_test)
    y_pred_labels = le.inverse_transform(y_pred)

    print(f"\n=== Classification Report for {name} ===")
    print(classification_report(y_test_labels, y_pred_labels, target_names=le.classes_))

# === 12. Feature Importance Visualization (RandomForest) ===
print("Plotting feature importances...")
importances = rf_best.feature_importances_
feat_names = X.columns[selector.get_support()]
feat_importance_df = pd.DataFrame({'feature': feat_names, 'importance': importances})
feat_importance_df = feat_importance_df.sort_values(by='importance', ascending=False).head(20)

plt.figure(figsize=(10, 6))
sns.barplot(data=feat_importance_df, x='importance', y='feature', palette='Blues_d')
plt.title('Top 20 Feature Importances (Random Forest)')
plt.tight_layout()
plt.show()
