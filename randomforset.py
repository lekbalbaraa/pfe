import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load dataset
df = pd.read_csv('iot23_combined.csv')  # Make sure this path is correct

# 2. Filter out rare classes (less than 2 samples)
min_samples_required = 2
label_col = 'label'
class_counts = df[label_col].value_counts()
valid_classes = class_counts[class_counts >= min_samples_required].index
df = df[df[label_col].isin(valid_classes)]

# 3. Split features and labels
X = df.drop(label_col, axis=1)
y = df[label_col]

# 4. Encode the labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# 5. Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# 6. Train Random Forest
rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=None,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train, y_train)

# 7. Predict
y_pred = rf.predict(X_test)

# 8. Decode predictions back to labels
y_test_labels = le.inverse_transform(y_test)
y_pred_labels = le.inverse_transform(y_pred)

# 9. Classification report
report = classification_report(y_test_labels, y_pred_labels, target_names=le.classes_, output_dict=True)
report_df = pd.DataFrame(report).transpose()
print("\nClassification Report:\n")
print(report_df)

# 10. Optional: save report to CSV
# report_df.to_csv("rf_classification_report.csv", index=True)

# 11. Plot Feature Importance (top 20)
importances = rf.feature_importances_
feat_names = X.columns
feat_importance_df = pd.DataFrame({'feature': feat_names, 'importance': importances})
feat_importance_df = feat_importance_df.sort_values(by='importance', ascending=False).head(20)

plt.figure(figsize=(10, 6))
sns.barplot(data=feat_importance_df, x='importance', y='feature', palette='Blues_d')
plt.title('Top 20 Feature Importances (Random Forest)')
plt.tight_layout()
plt.show()
