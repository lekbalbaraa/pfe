import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
folder_paths = ['C:/Users/lekba/Desktop/pfe/archive (7)/', 
                'C:/Users/lekba/Desktop/pfe/archive (8)/', 
                'C:/Users/lekba/Desktop/pfe/archive (9)/']  # Adjust paths to your folders

# List to store dataframes from each dataset
datasets = []

# Loop through each folder and load the CSV files
for folder in folder_paths:
    for filename in os.listdir(folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder, filename)
            df = pd.read_csv(file_path)
            datasets.append(df)

# Step 2: Combine all datasets into a single DataFrame
data = pd.concat(datasets, axis=0, ignore_index=True)

# Step 3: Check for missing values
print("Missing values per column:")
print(data.isnull().sum())

# Step 4: Handle missing values
# Option 1: Drop rows with missing values
# data = data.dropna()

# Option 2: Fill missing values with the column mean (for numerical columns)
data.fillna(data.mean(), inplace=True)

# Step 5: Handle categorical variables (One-Hot Encoding)
# Assuming there are categorical columns, e.g., 'category_column'
categorical_columns = ['category_column1', 'category_column2']  # Modify with actual categorical columns

# Perform One-Hot Encoding for categorical columns
data = pd.get_dummies(data, columns=categorical_columns)

# Step 6: Scale the numerical features (Standard Scaling)
numerical_columns = ['feature1', 'feature2', 'feature3']  # Modify with your numerical columns

scaler = StandardScaler()
data[numerical_columns] = scaler.fit_transform(data[numerical_columns])

# Step 7: Handle duplicates
data = data.drop_duplicates()

# Step 8: Feature Engineering (Optional)
# Example: Creating a new feature 'new_feature' as a combination of existing features
# data['new_feature'] = data['feature1'] + data['feature2']

# Step 9: Exploratory Data Analysis (Optional)
# Correlation heatmap
import seaborn as sns
import matplotlib.pyplot as plt

sns.heatmap(data.corr(), annot=True, cmap='coolwarm')
plt.show()

# Step 10: Check the first few rows of the cleaned data
print("Cleaned Data Preview:")
print(data.head())

# Step 11: Save the cleaned data (optional)
# data.to_csv('cleaned_combined_dataset.csv', index=False)
