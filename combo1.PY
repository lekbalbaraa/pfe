import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE

# 1. Load and prepare the data
df = pd.read_csv('iot23_combined.csv')  # Replace with your file
label_col = 'label'

# Optional: filter very rare classes
df = df[df[label_col].map(df[label_col].value_counts()) > 1]

# 2. Split features and labels
X = df.drop(label_col, axis=1)
y = df[label_col]

# 3. Encode the labels
le_full = LabelEncoder()
y_encoded = le_full.fit_transform(y)
df['encoded_label'] = y_encoded

# 4. Binary labels for stage 1: 0 = Benign, 1 = Attack
df['binary_label'] = df[label_col].apply(lambda x: 0 if 'Benign' in x else 1)

# Features for both stages
X = df.drop([label_col, 'encoded_label', 'binary_label'], axis=1)
y_binary = df['binary_label']
y_multiclass = df['encoded_label']

# 5. Split train/test
X_train_bin, X_test_bin, y_train_bin, y_test_bin, y_train_multi, y_test_multi = train_test_split(
    X, y_binary, y_multiclass, test_size=0.2, stratify=y_binary, random_state=42
)

# 6. Apply SMOTE to balance the binary data
smote = SMOTE(random_state=42)
X_train_bin_bal, y_train_bin_bal = smote.fit_resample(X_train_bin, y_train_bin)

# 7. Stage 1: Train Random Forest to detect attack
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train_bin_bal, y_train_bin_bal)

# 8. Stage 1: Predict on test data
y_pred_bin = rf.predict(X_test_bin)
print("=== Stage 1: Binary Classification ===")
print(classification_report(y_test_bin, y_pred_bin, target_names=["Benign", "Attack"]))

# 9. Stage 2: Filter only the samples predicted as Attack
attack_indices = np.where(y_pred_bin == 1)[0]
X_test_attack = X_test_bin.iloc[attack_indices]
y_test_attack_types = y_test_multi.iloc[attack_indices]

# Train on attacks only from the original training set
X_train_multi = X_train_bin[y_train_bin == 1]
y_train_multi = y_train_multi[y_train_bin == 1]

# Optional: SMOTE on multiclass too
X_train_multi_bal, y_train_multi_bal = SMOTE(random_state=42).fit_resample(X_train_multi, y_train_multi)

# 10. Stage 2: Train XGBoost for attack type classification
xgb = XGBClassifier(
    objective='multi:softmax',
    num_class=len(np.unique(y_multiclass)),
    use_label_encoder=False,
    eval_metric='mlogloss',
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6,
    random_state=42
)
xgb.fit(X_train_multi_bal, y_train_multi_bal)

# 11. Predict on filtered test set
y_pred_attack_types = xgb.predict(X_test_attack)

# 12. Final report on attack type classification
print("=== Stage 2: Attack Type Classification ===")
print(classification_report(y_test_attack_types, y_pred_attack_types, target_names=le_full.classes_))
