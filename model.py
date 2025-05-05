import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Load the CSV
file_path = r'C:\Users\lekba\Desktop\pfe\cic_ids_2018.csv'
data = pd.read_csv(file_path)

# Step 2: Display columns
print("Columns in the dataset:", data.columns)

# Step 3: Drop rows with missing values
data = data.dropna()

# Step 4: Encode target label
label_col = 'Label' if 'Label' in data.columns else 'type'
label_encoder = LabelEncoder()
data[label_col] = label_encoder.fit_transform(data[label_col])

# Step 5: Separate features and labels
X = data.drop(columns=[label_col])
y = data[label_col]

# Optional: Drop non-numeric features (e.g., Flow ID, Timestamp)
X = X.select_dtypes(include=['number'])

# Step 6: Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Step 7: Train/Test Split (80/20)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Step 8: Train XGBoost
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
model.fit(X_train, y_train)

# Step 9: Evaluate
y_pred = model.predict(X_test)
print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# Step 10: Plot feature importance
xgb.plot_importance(model, max_num_features=10)
plt.tight_layout()
plt.show()
