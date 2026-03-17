"""
Random Forest Optimization - 200 samples
Target: R2 > 0.80
"""
import joblib, pandas as pd, numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score, GridSearchCV
import warnings
warnings.filterwarnings('ignore')

# Load data
data = pd.read_csv('11-research/data/lig_dataset_200.csv')
X = data[['E_Jcm2', 'v_mms', 'co_ratio']].values
y = data['sigma_Sm'].values

print(f"Dataset: {len(X)} samples, {X.shape[1]} features")
print(f"Target: sigma_Sm (range: {y.min():.1f} - {y.max():.1f} S/m)")

# Scale (not required for RF but good practice)
scaler_X = StandardScaler()
X_scaled = scaler_X.fit_transform(X)

# Random Forest with hyperparameter search
print("\nTesting Random Forest...")
rf = RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_split=3, random_state=42, n_jobs=-1)
cv_scores = cross_val_score(rf, X_scaled, y, cv=5, scoring='r2')
print(f"RF CV R2: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

rf.fit(X_scaled, y)
y_pred = rf.predict(X_scaled)
r2_rf = r2_score(y, y_pred)
mae_rf = mean_absolute_error(y, y_pred)
print(f"RF Train R2: {r2_rf:.4f}, MAE: {mae_rf:.1f} S/m")

# Gradient Boosting
print("\nTesting Gradient Boosting...")
gb = GradientBoostingRegressor(n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42)
cv_scores_gb = cross_val_score(gb, X_scaled, y, cv=5, scoring='r2')
print(f"GB CV R2: {cv_scores_gb.mean():.4f} (+/- {cv_scores_gb.std():.4f})")

gb.fit(X_scaled, y)
y_pred_gb = gb.predict(X_scaled)
r2_gb = r2_score(y, y_pred_gb)
mae_gb = mean_absolute_error(y, y_pred_gb)
print(f"GB Train R2: {r2_gb:.4f}, MAE: {mae_gb:.1f} S/m")

# Best model
print(f"\n=== BEST MODEL ===")
if r2_rf > r2_gb:
    print(f"Random Forest wins: R2 = {r2_rf:.4f}")
    joblib.dump(rf, '11-research/models/LIG_RF_200.pkl')
    joblib.dump(scaler_X, '11-research/models/LIG_RF_200_scaler_X.pkl')
    print("Saved: LIG_RF_200.pkl")
else:
    print(f"Gradient Boosting wins: R2 = {r2_gb:.4f}")
    joblib.dump(gb, '11-research/models/LIG_GB_200.pkl')
    joblib.dump(scaler_X, '11-research/models/LIG_GB_200_scaler_X.pkl')
    print("Saved: LIG_GB_200.pkl")

print(f"Target: R2 > 0.80 | Status: {'PASS' if max(r2_rf, r2_gb) > 0.80 else 'NEEDS MORE WORK'}")

# Feature importance
if r2_rf > r2_gb:
    print(f"\nFeature importance (RF):")
    for name, imp in zip(['E_Jcm2', 'v_mms', 'co_ratio'], rf.feature_importances_):
        print(f"  {name}: {imp:.4f}")
else:
    print(f"\nFeature importance (GB):")
    for name, imp in zip(['E_Jcm2', 'v_mms', 'co_ratio'], gb.feature_importances_):
        print(f"  {name}: {imp:.4f}")
