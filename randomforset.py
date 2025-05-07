import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import time
from imblearn.over_sampling import SMOTE

# Load dataset
filepath = "iot23_combined.csv"
df = pd.read_csv(filepath)
del df['Unnamed: 0']

# Remove classes with fewer than 2 samples
value_counts = df['label'].value_counts()
valid_labels = value_counts[value_counts >= 2].index
df = df[df['label'].isin(valid_labels)]

# Feature selection
X = df[['duration', 'orig_bytes', 'resp_bytes', 'missed_bytes', 'orig_pkts', 'orig_ip_bytes', 
        'resp_pkts', 'resp_ip_bytes', 'proto_icmp', 'proto_tcp', 'proto_udp', 
        'conn_state_OTH', 'conn_state_REJ', 'conn_state_RSTO', 'conn_state_RSTOS0', 
        'conn_state_RSTR', 'conn_state_RSTRH', 'conn_state_S0', 'conn_state_S1', 
        'conn_state_S2', 'conn_state_S3', 'conn_state_SF', 'conn_state_SH', 'conn_state_SHR']]
Y = df['label']

# Stratified train/test split
X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=10, stratify=Y)

# Apply SMOTE to handle class imbalance
smote = SMOTE(random_state=10)
X_train_res, Y_train_res = smote.fit_resample(X_train, Y_train)

# Hyperparameter tuning with GridSearchCV
param_grid = {
    'n_estimators': [100, 150, 200],
    'max_depth': [10, 20, 30],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2],
    'class_weight': ['balanced', None]  # Trying balanced class weight
}

rf = RandomForestClassifier(random_state=10)

grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=3, verbose=2, n_jobs=-1, scoring='accuracy')
grid_search.fit(X_train_res, Y_train_res)

# Best hyperparameters
print("Best Hyperparameters:", grid_search.best_params_)

# Best Random Forest Model
best_rf = grid_search.best_estimator_

# Start timer
start = time.time()
print("Training Random Forest...\n")

# Fit the model
best_rf.fit(X_train_res, Y_train_res)

# Predict
y_pred = best_rf.predict(X_test)

# End timer
end = time.time()

# Evaluation
print("Random Forest Accuracy:", best_rf.score(X_test, Y_test))
print("\nClassification Report:")
print(classification_report(Y_test, y_pred))

print("Time cost:", round(end - start, 2), "seconds")

# Confusion Matrix
cm = confusion_matrix(Y_test, y_pred, labels=best_rf.classes_)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=best_rf.classes_)
fig, ax = plt.subplots(figsize=(12, 10))
disp.plot(ax=ax, xticks_rotation='vertical', cmap="Blues")
plt.title("Confusion Matrix")
plt.tight_layout()
plt.show()
