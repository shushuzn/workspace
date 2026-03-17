"""
Compare models: Strong Regularization vs Linear
Find best balance between train and CV performance
"""
import joblib, pandas as pd, numpy as np
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

# Load data
data = pd.read_csv('11-research/data/lig_dataset_200.csv')
features = ['E_Jcm2', 'v_mms', 'co_ratio', 'ssa_m2g', 'id_ig', 'P_W']
target = 'sigma_Sm'

X = data[features].values
y = data[target].values

print(f"Dataset: {len(X)} samples, {len(features)} features")

# Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("\n=== TESTING MODELS ===\n")

results = []

# 1. GB with very strong regularization
print("1. GB (very strong reg)...")
gb_strong = GradientBoostingRegressor(n_estimators=50, max_depth=1, learning_rate=0.01, min_samples_leaf=30, random_state=42)
cv_gb = cross_val_score(gb_strong, X_scaled, y, cv=5, scoring='r2').mean()
gb_strong.fit(X_scaled, y)
r2_gb = r2_score(y, gb_strong.predict(X_scaled))
print(f"   Train R2: {r2_gb:.4f}, CV R2: {cv_gb:.4f}")
results.append(('GB_Strong', r2_gb, cv_gb, gb_strong))

# 2. Ridge Regression
print("2. Ridge Regression...")
for alpha in [0.1, 1.0, 10.0, 100.0]:
    ridge = Ridge(alpha=alpha)
    cv_ridge = cross_val_score(ridge, X_scaled, y, cv=5, scoring='r2').mean()
    ridge.fit(X_scaled, y)
    r2_ridge = r2_score(y, ridge.predict(X_scaled))
    print(f"   Ridge (alpha={alpha}): Train R2: {r2_ridge:.4f}, CV R2: {cv_ridge:.4f}")
    results.append((f'Ridge_{alpha}', r2_ridge, cv_ridge, ridge))

# 3. ElasticNet
print("3. ElasticNet...")
for alpha in [0.1, 1.0]:
    en = ElasticNet(alpha=alpha, l1_ratio=0.5, max_iter=10000)
    cv_en = cross_val_score(en, X_scaled, y, cv=5, scoring='r2').mean()
    en.fit(X_scaled, y)
    r2_en = r2_score(y, en.predict(X_scaled))
    print(f"   ElasticNet (alpha={alpha}): Train R2: {r2_en:.4f}, CV R2: {cv_en:.4f}")
    results.append((f'ElasticNet_{alpha}', r2_en, cv_en, en))

# Find best by CV
print("\n=== BEST BY CV R2 ===")
results.sort(key=lambda x: x[2], reverse=True)
best = results[0]
print(f"Model: {best[0]}")
print(f"Train R2: {best[1]:.4f}")
print(f"CV R2: {best[2]:.4f}")

# Save best model
joblib.dump(best[3], f'11-research/models/LIG_{best[0]}_200.pkl')
joblib.dump(scaler, '11-research/models/LIG_best_scaler_X.pkl')
with open('11-research/models/LIG_best_features.txt', 'w') as f:
    f.write(','.join(features))
print(f"\nSaved: LIG_{best[0]}_200.pkl")

# Feature importance (if GB or linear)
if hasattr(best[3], 'feature_importances_') or hasattr(best[3], 'coef_'):
    print(f"\nFeature Importance:")
    if hasattr(best[3], 'feature_importances_'):
        imps = best[3].feature_importances_
    else:
        imps = np.abs(best[3].coef_)
    for name, imp in zip(features, imps):
        print(f"  {name}: {imp:.4f}")
