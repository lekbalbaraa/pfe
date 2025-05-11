import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
from sklearn.impute import SimpleImputer

# === 1. Load and clean data ===
df = pd.read_csv('iot23_combined.csv')  # Replace with your actual file
label_col = 'label'

# Drop rows with missing labels and rare classes
df = df.dropna(subset=[label_col])
df = df[df[label_col].map(df[label_col].value_counts()) > 1]

# === 2. Encode labels ===
le_full = LabelEncoder()
df['encoded_label'] = le_full.fit_transform(df[label_col])
df['binary_label'] = df[label_col].apply(lambda x: 0 if 'Benign' in x else 1)

# === 3. Feature preparation ===
X = df.drop(columns=[label_col, 'encoded_label', 'binary_label'])
y_binary = df['binary_label']
y_multiclass = df['encoded_label']

# Impute missing values in features
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)

# === 4. Train-test split ===
X_train, X_test, y_train_binary, y_test_binary, y_train_multi, y_test_multi = train_test_split(
    X_imputed, y_binary, y_multiclass, test_size=0.2, stratify=y_binary, random_state=42
)

# === 5. Stage 1: Binary classification ===
smote = SMOTE(random_state=42)
X_train_bin_bal, y_train_bin_bal = smote.fit_resample(X_train, y_train_binary)

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train_bin_bal, y_train_bin_bal)

y_pred_binary = rf.predict(X_test)
print("=== Stage 1: Binary Classification ===")
print(classification_report(y_test_binary, y_pred_binary, target_names=["Benign", "Attack"]))

# === 6. Stage 2: Multiclass (fine-grained attack type) classification ===
# Filter predicted attacks from test set
attack_indices = np.where(y_pred_binary == 1)[0]
X_test_attack = X_test[attack_indices]
y_test_attack_labels = y_test_multi.iloc[attack_indices]

# Extract training data for attacks only
X_train_attacks = X_train[y_train_binary == 1]
y_train_attacks_labels = y_train_multi[y_train_binary == 1]

# === ✅ Fix: Encode only based on training attack labels ===
le_multi = LabelEncoder()
le_multi.fit(y_train_attacks_labels)

y_train_attacks_encoded = le_multi.transform(y_train_attacks_labels)
y_test_attack_encoded = le_multi.transform(y_test_attack_labels)

# === ✅ Filter out test samples with unseen labels ===
valid_classes = np.unique(y_train_attacks_encoded)
mask = np.isin(y_test_attack_encoded, valid_classes)
X_test_attack = X_test_attack[mask]
y_test_attack_encoded = y_test_attack_encoded[mask]

# Apply SMOTE for balanced attack types
X_train_multi_bal, y_train_multi_bal = SMOTE(random_state=42).fit_resample(
    X_train_attacks, y_train_attacks_encoded
)

# Train XGBoost for multiclass classification
xgb = XGBClassifier(
    objective='multi:softmax',
    num_class=len(valid_classes),
    use_label_encoder=False,
    eval_metric='mlogloss',
    n_estimators=100,
    learning_rate=0.1,
    max_depth=6,
    random_state=42
)
xgb.fit(X_train_multi_bal, y_train_multi_bal)

# Predict on filtered test attacks
y_pred_attack_types = xgb.predict(X_test_attack)

print("=== Stage 2: Attack Type Classification ===")
print(classification_report(y_test_attack_encoded, y_pred_attack_types, target_names=le_multi.classes_))
