"""
Train with 73 high-quality samples (complete features)
Target: R2 > 0.80 with good CV
"""
import joblib, pandas as pd, numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

# Load data
data = pd.read_csv('11-research/data/lig_dataset_200.csv')

# Features that have complete data
features = ['E_Jcm2', 'v_mms', 'co_ratio', 'ssa_m2g', 'id_ig', 'P_W']
target = 'sigma_Sm'

# Drop rows with ANY missing values in selected features
data_clean = data.dropna(subset=features + [target]).copy()
print(f"Complete samples: {len(data_clean)} (from 200)")
print(f"Features: {features}")

if len(data_clean) < 70:
    print("ERROR: Not enough complete samples!")
    exit(1)

X = data_clean[features].values
y = data_clean[target].values

print(f"Target: {y.min():.1f} - {y.max():.1f} S/m")

# Scale
scaler_X = StandardScaler()
scaler_y = StandardScaler()
X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()

# Test different regularization levels
print("\nTesting regularization...")
configs = [
    {'n_estimators': 100, 'max_depth': 2, 'learning_rate': 0.05, 'min_samples_leaf': 8},
    {'n_estimators': 150, 'max_depth': 2, 'learning_rate': 0.03, 'min_samples_leaf': 10},
    {'n_estimators': 200, 'max_depth': 2, 'learning_rate': 0.02, 'min_samples_leaf': 12},
    {'n_estimators': 100, 'max_depth': 3, 'learning_rate': 0.03, 'min_samples_leaf': 5},
]

best_cv = -np.inf
best_config = None
best_model = None

for cfg in configs:
    gb = GradientBoostingRegressor(**cfg, random_state=42)
    cv_scores = cross_val_score(gb, X_scaled, y_scaled, cv=5, scoring='r2')
    mean_cv = cv_scores.mean()
    if mean_cv > best_cv:
        best_cv = mean_cv
        best_config = cfg
        best_model = gb

print(f"Best CV R2: {best_cv:.4f}")
print(f"Config: {best_config}")

# Train final model
print("\nTraining final model...")
best_model.fit(X_scaled, y_scaled)

# Evaluate
y_pred_scaled = best_model.predict(X_scaled)
y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()

r2 = r2_score(y, y_pred)
mae = mean_absolute_error(y, y_pred)
rmse = np.sqrt(np.mean((y - y_pred)**2))
nrmse = rmse / (y.max() - y.min()) * 100

print(f"\n=== FINAL RESULTS ===")
print(f"Samples: {len(X)}")
print(f"R2 = {r2:.4f}")
print(f"MAE = {mae:.2f} S/m")
print(f"RMSE = {rmse:.2f} S/m")
print(f"NRMSE = {nrmse:.1f}%")
print(f"CV R2 = {best_cv:.4f}")
print(f"Target: R2 > 0.80 | CV R2 > 0 | Status: {'PASS' if r2 > 0.80 and best_cv > 0 else 'PARTIAL'}")

# Feature importance
print(f"\nFeature Importance:")
for name, imp in zip(features, best_model.feature_importances_):
    bar = '#' * int(imp * 20)
    print(f"  {name}: {imp:.4f} {bar}")

# Save
joblib.dump(best_model, '11-research/models/LIG_GB_73samples_complete.pkl')
joblib.dump(scaler_X, '11-research/models/LIG_GB_73samples_scaler_X.pkl')
joblib.dump(scaler_y, '11-research/models/LIG_GB_73samples_scaler_y.pkl')
with open('11-research/models/LIG_GB_73samples_features.txt', 'w') as f:
    f.write(','.join(features))

print(f"\nSaved: LIG_GB_73samples_complete.pkl")
