"""
GP Model Optimization - 200 samples
Target: R² > 0.80
"""
import joblib, pandas as pd, numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C, Matern, WhiteKernel
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

# Load data
data = pd.read_csv('11-research/data/lig_dataset_200.csv')
X = data[['E_Jcm2', 'v_mms', 'co_ratio']].values
y = data['sigma_Sm'].values

print(f"Dataset: {len(X)} samples, {X.shape[1]} features")
print(f"Target: sigma_Sm (range: {y.min():.1f} - {y.max():.1f} S/m)")

# Scale
scaler_X = StandardScaler()
scaler_y = StandardScaler()
X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()

# Kernel optimization
kernels = [
    C(1.0) * RBF(length_scale=1.0),
    C(1.0) * Matern(length_scale=1.0, nu=2.5),
    C(1.0) * RBF(length_scale=1.0) + WhiteKernel(noise_level=0.1),
    C(1.0) * Matern(length_scale=1.0, nu=1.5) + WhiteKernel(noise_level=0.1),
]

best_r2 = -np.inf
best_kernel = None
best_model = None

print("\nTesting kernels...")
for i, kernel in enumerate(kernels):
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, random_state=42)
    cv_scores = cross_val_score(gp, X_scaled, y_scaled, cv=5, scoring='r2')
    mean_r2 = cv_scores.mean()
    print(f"  Kernel {i +1}: CV R2 = {mean_r2:.4f} (+/- {cv_scores.std():.4f})")
    if mean_r2 > best_r2:
        best_r2 = mean_r2
        best_kernel = kernel
        best_model = gp

print(f"\nBest kernel: CV R2 = {best_r2:.4f}")

# Train final model
print("\nTraining final model...")
gp_final = GaussianProcessRegressor(kernel=best_kernel, n_restarts_optimizer=20, random_state=42)
gp_final.fit(X_scaled, y_scaled)

# Evaluate
y_pred_scaled = gp_final.predict(X_scaled)
y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()

r2 = r2_score(y, y_pred)
mae = mean_absolute_error(y, y_pred)
rmse = np.sqrt(np.mean((y - y_pred)**2))
nrmse = rmse / (y.max() - y.min()) * 100

print(f"\n=== FINAL RESULTS ===")
print(f"R2 = {r2:.4f}")
print(f"MAE = {mae:.2f} S/m")
print(f"RMSE = {rmse:.2f} S/m")
print(f"NRMSE = {nrmse:.1f}%")
print(f"Target: R2 > 0.80 | Status: {'PASS' if r2 > 0.80 else 'NEEDS WORK'}")

# Save
joblib.dump(gp_final, '11-research/models/LIG_GP_optimized_200.pkl')
joblib.dump(scaler_X, '11-research/models/LIG_GP_optimized_200_scaler_X.pkl')
joblib.dump(scaler_y, '11-research/models/LIG_GP_optimized_200_scaler_y.pkl')
print("\nModels saved to 11-research/models/")

# Feature importance (via length scales)
if hasattr(gp_final.kernel_, 'k1'):
    print(f"\nKernel: {gp_final.kernel_}")
else:
    print(f"\nKernel: {gp_final.kernel_}")
    if hasattr(gp_final.kernel_, 'length_scale'):
        print(f"Length scales: {gp_final.kernel_.length_scale}")
