"""
Ensemble Model: GP + ElasticNet
Test if ensemble improves prediction
"""
import joblib, pandas as pd, numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import ElasticNet
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

# Load data
data = pd.read_csv('11-research/data/lig_dataset_200.csv')

# Features for each model
features_3 = ['E_Jcm2', 'v_mms', 'co_ratio']
features_6 = ['E_Jcm2', 'v_mms', 'co_ratio', 'ssa_m2g', 'id_ig', 'P_W']
target = 'sigma_Sm'

X_3 = data[features_3].values
X_6 = data[features_6].values
y = data[target].values

print(f"Dataset: {len(X_6)} samples")
print(f"Features (3): {features_3}")
print(f"Features (6): {features_6}")

# Scale
scaler_3 = StandardScaler()
scaler_6 = StandardScaler()
X_3_scaled = scaler_3.fit_transform(X_3)
X_6_scaled = scaler_6.fit_transform(X_6)

# Load existing models or train new ones
print("\n=== TRAINING BASE MODELS ===")

# GP model (3 features)
print("Training GP (3 features)...")
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, ConstantKernel as C, WhiteKernel

kernel = C(1.0) * Matern(length_scale=1.0, nu=1.5) + WhiteKernel(noise_level=0.1)
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, random_state=42)
gp.fit(X_3_scaled, y)
y_pred_gp = gp.predict(X_3_scaled)
r2_gp = r2_score(y, y_pred_gp)
print(f"  GP R2: {r2_gp:.4f}")

# ElasticNet model (6 features)
print("Training ElasticNet (6 features)...")
en = ElasticNet(alpha=0.1, l1_ratio=0.5, max_iter=10000)
en.fit(X_6_scaled, y)
y_pred_en = en.predict(X_6_scaled)
r2_en = r2_score(y, y_pred_en)
print(f"  ElasticNet R2: {r2_en:.4f}")

# Ensemble: weighted average
print("\n=== TESTING ENSEMBLE WEIGHTS ===")

best_r2 = 0
best_weight = 0

for gp_weight in np.arange(0.0, 1.05, 0.05):
    en_weight = 1.0 - gp_weight

    # For ensemble, we need predictions from both models
    # GP uses 3 features, EN uses 6 features - need to align
    # Simple approach: use GP weight for GP prediction, EN weight for EN prediction
    y_pred_ensemble = gp_weight * y_pred_gp + en_weight * y_pred_en

    r2_ens = r2_score(y, y_pred_ensemble)
    if r2_ens > best_r2:
        best_r2 = r2_ens
        best_weight = gp_weight
    print(f"  GP:{gp_weight:.2f} + EN:{en_weight:.2f} -> R2 = {r2_ens:.4f}")

print(f"\n=== BEST ENSEMBLE ===")
print(f"GP weight: {best_weight:.2f}")
print(f"EN weight: {1 -best_weight:.2f}")
print(f"Ensemble R2: {best_r2:.4f}")

# Compare
print(f"\n=== COMPARISON ===")
print(f"GP alone:        R2 = {r2_gp:.4f}")
print(f"ElasticNet alone: R2 = {r2_en:.4f}")
print(f"Ensemble:        R2 = {best_r2:.4f}")
print(f"Improvement:     +{best_r2 - max(r2_gp, r2_en):.4f}")

# Save best ensemble
if best_r2 > max(r2_gp, r2_en):
    ensemble_config = {
        'gp_weight': best_weight,
        'gp_model': gp,
        'en_model': en,
        'scaler_3': scaler_3,
        'scaler_6': scaler_6,
        'features_3': features_3,
        'features_6': features_6
    }
    joblib.dump(ensemble_config, '11-research/models/LIG_ensemble_GP_EN.pkl')
    print(f"\nSaved: LIG_ensemble_GP_EN.pkl")
else:
    print(f"\nEnsemble did not improve. Keeping ElasticNet.")
