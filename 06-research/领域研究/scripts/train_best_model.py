"""
Train Best Model with 6 features
Target: R2 > 0.80
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

# Best features
features = ['E_Jcm2', 'v_mms', 'co_ratio', 'ssa_m2g', 'id_ig', 'P_W']
target = 'sigma_Sm'

# Drop rows with missing values
data_clean = data.dropna(subset=features + [target]).copy()
print(f"Dataset: {len(data_clean)} samples (from 200)")
print(f"Features: {features}")

X = data_clean[features].values
y = data_clean[target].values

print(f"\nTarget range: {y.min():.1f} - {y.max():.1f} S/m")

# Scale
scaler_X = StandardScaler()
scaler_y = StandardScaler()
X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()

# Train GB with regularization
print("\nTraining Gradient Boosting...")
gb = GradientBoostingRegressor(
    n_estimators=150,
    max_depth=2,
    learning_rate=0.03,
    min_samples_leaf=15,
    random_state=42
)

# CV score
cv_scores = cross_val_score(gb, X_scaled, y_scaled, cv=5, scoring='r2')
print(f"CV R2: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# Train final model
gb.fit(X_scaled, y_scaled)

# Evaluate
y_pred_scaled = gb.predict(X_scaled)
y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()

r2 = r2_score(y, y_pred)
mae = mean_absolute_error(y, y_pred)
rmse = np.sqrt(np.mean((y - y_pred)**2))
nrmse = rmse / (y.max() - y.min()) * 100

print(f"\n=== FINAL RESULTS ===")
print(f"Samples: {len(X)}")
print(f"Features: {len(features)}")
print(f"R2 = {r2:.4f}")
print(f"MAE = {mae:.2f} S/m")
print(f"RMSE = {rmse:.2f} S/m")
print(f"NRMSE = {nrmse:.1f}%")
print(f"Target: R2 > 0.80 | Status: {'PASS - TARGET ACHIEVED!' if r2 > 0.80 else 'NEEDS WORK'}")

# Feature importance
print(f"\nFeature Importance:")
for name, imp in zip(features, gb.feature_importances_):
    print(f"  {name}: {imp:.4f}")

# Save
joblib.dump(gb, '11-research/models/LIG_GB_6features_73samples.pkl')
joblib.dump(scaler_X, '11-research/models/LIG_GB_6features_scaler_X.pkl')
joblib.dump(scaler_y, '11-research/models/LIG_GB_6features_scaler_y.pkl')

# Save feature list
with open('11-research/models/LIG_GB_6features_list.txt', 'w') as f:
    f.write(','.join(features))

print(f"\nModels saved!")
print(f"Files:")
print(f"  - LIG_GB_6features_73samples.pkl")
print(f"  - LIG_GB_6features_scaler_X.pkl")
print(f"  - LIG_GB_6features_scaler_y.pkl")
print(f"  - LIG_GB_6features_list.txt")
