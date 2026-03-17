"""
GP Model with Log Transform - 200 samples
Target: R2 > 0.80
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

# Log transform target
y_log = np.log1p(y)  # log(1 + y) to handle 0
print(f"Log target: range {y_log.min():.2f} - {y_log.max():.2f}")

# Scale
scaler_X = StandardScaler()
scaler_y = StandardScaler()
X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y_log.reshape(-1, 1)).flatten()

# Kernel
kernel = C(1.0) * Matern(length_scale=1.0, nu=1.5) + WhiteKernel(noise_level=0.1)

print("\nTraining GP with log-transformed target...")
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=20, random_state=42)
gp.fit(X_scaled, y_scaled)

# CV score
cv_scores = cross_val_score(gp, X_scaled, y_scaled, cv=5, scoring='r2')
print(f"CV R2: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

# Evaluate on training
y_pred_scaled = gp.predict(X_scaled)
y_pred_log = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
y_pred = np.expm1(y_pred_log)  # Inverse log transform

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
joblib.dump(gp, '11-research/models/LIG_GP_log_200.pkl')
joblib.dump(scaler_X, '11-research/models/LIG_GP_log_200_scaler_X.pkl')
joblib.dump(scaler_y, '11-research/models/LIG_GP_log_200_scaler_y.pkl')
print("\nModels saved!")
