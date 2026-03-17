"""
Model Visualization
Generate prediction plots and feature importance
"""
import joblib, pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Load data
data = pd.read_csv('11-research/data/lig_dataset_200.csv')
features = ['E_Jcm2', 'v_mms', 'co_ratio', 'ssa_m2g', 'id_ig', 'P_W']
target = 'sigma_Sm'

X = data[features].values
y = data[target].values

# Load ensemble model
ensemble = joblib.load('11-research/models/LIG_ensemble_GP_EN.pkl')
gp = ensemble['gp_model']
en = ensemble['en_model']
scaler_3 = ensemble['scaler_3']
scaler_6 = ensemble['scaler_6']
gp_weight = ensemble['gp_weight']

# Predict
X_3 = data[ensemble['features_3']].values
X_6 = data[ensemble['features_6']].values
X_3_scaled = scaler_3.transform(X_3)
X_6_scaled = scaler_6.transform(X_6)

y_pred_gp = gp.predict(X_3_scaled)
y_pred_en = en.predict(X_6_scaled)
y_pred = gp_weight * y_pred_gp + (1 - gp_weight) * y_pred_en

# Metrics
r2 = r2_score(y, y_pred)
mae = mean_absolute_error(y, y_pred)
rmse = np.sqrt(np.mean((y - y_pred)**2))

print(f"Ensemble R2: {r2:.4f}")
print(f"MAE: {mae:.1f} S/m")
print(f"RMSE: {rmse:.1f} S/m")

# Create plots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# 1. Prediction vs Actual
ax = axes[0, 0]
ax.scatter(y, y_pred, alpha=0.6, edgecolors='k', linewidth=0.5)
ax.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
ax.set_xlabel('Actual (S/m)', fontsize=11)
ax.set_ylabel('Predicted (S/m)', fontsize=11)
ax.set_title(f'Prediction vs Actual\nR² = {r2:.4f}, MAE = {mae:.1f} S/m', fontsize=12)
ax.set_xscale('log')
ax.set_yscale('log')
ax.grid(True, alpha=0.3)

# 2. Residuals
ax = axes[0, 1]
residuals = y - y_pred
ax.scatter(y_pred, residuals, alpha=0.6, edgecolors='k', linewidth=0.5)
ax.axhline(y=0, color='r', linestyle='--', lw=2)
ax.set_xlabel('Predicted (S/m)', fontsize=11)
ax.set_ylabel('Residuals (S/m)', fontsize=11)
ax.set_title('Residual Plot', fontsize=12)
ax.grid(True, alpha=0.3)

# 3. Feature Importance (ElasticNet coefficients)
ax = axes[1, 0]
coefs = np.abs(en.coef_)
feat_names = ensemble['features_6']
y_pos = np.arange(len(feat_names))
ax.barh(y_pos, coefs, color='steelblue')
ax.set_yticks(y_pos)
ax.set_yticklabels(feat_names)
ax.invert_yaxis()
ax.set_xlabel('Absolute Coefficient', fontsize=11)
ax.set_title('Feature Importance (ElasticNet)', fontsize=12)
ax.grid(True, alpha=0.3, axis='x')

# 4. Prediction Distribution
ax = axes[1, 1]
ax.hist(y, bins=20, alpha=0.6, label='Actual', edgecolor='k')
ax.hist(y_pred, bins=20, alpha=0.6, label='Predicted', edgecolor='k')
ax.set_xlabel('Conductivity (S/m)', fontsize=11)
ax.set_ylabel('Count', fontsize=11)
ax.set_title('Distribution Comparison', fontsize=12)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('11-research/figures/ensemble_model_performance.png', dpi=150, bbox_inches='tight')
plt.close()

print(f"\nSaved: 11-research/figures/ensemble_model_performance.png")

# Save prediction results
results = pd.DataFrame({
    'actual': y,
    'predicted': y_pred,
    'residual': residuals,
    'error_pct': np.abs(residuals / y) * 100
})
results.to_csv('11-research/data/ensemble_predictions.csv', index=False)
print(f"Saved: 11-research/data/ensemble_predictions.csv")

# Summary stats
print(f"\n=== PREDICTION ACCURACY ===")
print(f"Mean error: {np.mean(np.abs(residuals)):.1f} S/m")
print(f"Median error: {np.median(np.abs(residuals)):.1f} S/m")
print(f"Error < 10%: {(results['error_pct'] < 10).sum()} / {len(results)} ({(results['error_pct'] < 10).mean()*100:.1f}%)")
print(f"Error < 20%: {(results['error_pct'] < 20).sum()} / {len(results)} ({(results['error_pct'] < 20).mean()*100:.1f}%)")
