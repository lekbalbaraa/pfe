import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
from sklearn.impute import SimpleImputer
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# === 1. Load and clean data ===
print("Loading data...")
df = pd.read_csv('iot23_combined.csv')  # Replace with actual dataset path
label_col = 'label'

# Drop rows with missing labels and rare classes
print("Cleaning data...")
df = df.dropna(subset=[label_col])
df = df[df[label_col].map(df[label_col].value_counts()) > 1]

# === 2. Encode labels ===
print("Encoding labels...")
le_full = LabelEncoder()
df['encoded_label'] = le_full.fit_transform(df[label_col])
df['binary_label'] = df[label_col].apply(lambda x: 0 if 'Benign' in x else 1)

# === 3. Feature preparation ===
print("Preparing features...")
X = df.drop(columns=[label_col, 'encoded_label', 'binary_label'])
y_binary = df['binary_label']
y_multiclass = df['encoded_label']

# Impute missing values
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)

# === 4. Train-test split ===
print("Splitting data...")
X_train, X_test, y_train_binary, y_test_binary, y_train_multi, y_test_multi = train_test_split(
    X_imputed, y_binary, y_multiclass, test_size=0.2, stratify=y_binary, random_state=42
)

# === 5. Stage 1: Binary classification (Benign vs Attack) ===
print("Binary classification stage...")
smote = SMOTE(random_state=42)
X_train_bin_bal, y_train_bin_bal = smote.fit_resample(X_train, y_train_binary)

rf_binary = RandomForestClassifier(n_estimators=100, random_state=42)
rf_binary.fit(X_train_bin_bal, y_train_bin_bal)

y_pred_binary = rf_binary.predict(X_test)
print("\n=== Stage 1: Binary Classification ===")
print(classification_report(y_test_binary, y_pred_binary, target_names=["Benign", "Attack"]))

# Confusion matrix for Stage 1
cm_binary = confusion_matrix(y_test_binary, y_pred_binary)
disp_binary = ConfusionMatrixDisplay(confusion_matrix=cm_binary, display_labels=["Benign", "Attack"])
disp_binary.plot(cmap='Blues')
plt.title("Confusion Matrix - Stage 1 (Binary)")
plt.show()

# === 6. Stage 2: Multiclass attack classification ===

# Filter predicted attacks
print("Filtering predicted attacks...")
attack_indices = np.where(y_pred_binary == 1)[0]
X_test_attack = X_test[attack_indices]

# **Retrieve correct attack labels as text strings (fix)**
y_test_attack_labels = df.loc[y_test_binary.index, label_col].iloc[attack_indices]

# Extract training data for actual attacks only
print("Extracting training data for attacks...")
X_train_attacks = X_train[y_train_binary == 1]

# **Retrieve attack labels as text before encoding (fix)**
y_train_attacks_labels = df.loc[y_train_binary.index, label_col][y_train_binary == 1]

# === Debugging: Check Unique Labels in Training Data ===
print("\nDEBUG: Unique attack labels in training dataset:", y_train_attacks_labels.unique())

# Encode attack labels
print("Encoding attack labels...")
le_multi = LabelEncoder()
le_multi.fit(df[df['binary_label'] == 1][label_col])  # Ensure all attack labels are used

# === Debugging: Check LabelEncoder learned labels ===
print("\nDEBUG: Labels seen by LabelEncoder:", le_multi.classes_)

# === Debugging: Compare Dataset Labels vs LabelEncoder ===
missing_labels = set(y_train_attacks_labels) - set(le_multi.classes_)
print("\nDEBUG: Labels missing from LabelEncoder:", missing_labels)

# **Filter out labels not seen during encoding (fix)**
if missing_labels:
    y_train_attacks_labels = y_train_attacks_labels[y_train_attacks_labels.isin(le_multi.classes_)]

# Transform attack labels (now correctly using text labels)
print("Transforming attack labels...")
y_train_attacks_encoded = le_multi.transform(y_train_attacks_labels)
y_test_attack_encoded = le_multi.transform(y_test_attack_labels)

# Balance attack training data with SMOTE
print("Applying SMOTE on attack classes...")
X_train_multi_bal, y_train_multi_bal = SMOTE(random_state=42).fit_resample(
    X_train_attacks, y_train_attacks_encoded
)

# Train Random Forest for multiclass classification
print("Training multiclass model...")
rf_multi = RandomForestClassifier(n_estimators=100, random_state=42)
rf_multi.fit(X_train_multi_bal, y_train_multi_bal)

# Predict attack types
y_pred_attack_types = rf_multi.predict(X_test_attack)

print("\n=== Stage 2: Attack Type Classification (Random Forest) ===")
print(classification_report(y_test_attack_encoded, y_pred_attack_types, target_names=le_multi.classes_))
