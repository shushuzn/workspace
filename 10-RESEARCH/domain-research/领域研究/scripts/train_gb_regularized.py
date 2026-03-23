"""
Gradient Boosting with Strong Regularization - 200 samples
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
X = data[['E_Jcm2', 'v_mms', 'co_ratio']].values
y = data['sigma_Sm'].values

print(f"Dataset: {len(X)} samples")

# Scale
scaler_X = StandardScaler()
X_scaled = scaler_X.fit_transform(X)

# Test different regularization levels
configs = [
    {'n_estimators': 50, 'max_depth': 2, 'learning_rate': 0.05, 'min_samples_leaf': 10},
    {'n_estimators': 100, 'max_depth': 3, 'learning_rate': 0.05, 'min_samples_leaf': 5},
    {'n_estimators': 100, 'max_depth': 3, 'learning_rate': 0.1, 'min_samples_leaf': 8},
    {'n_estimators': 150, 'max_depth': 2, 'learning_rate': 0.03, 'min_samples_leaf': 15},
    {'n_estimators': 200, 'max_depth': 2, 'learning_rate': 0.02, 'min_samples_leaf': 20},
]

print("\nTesting configurations...")
best_cv = -np.inf
best_config = None
best_model = None

for i, cfg in enumerate(configs):
    gb = GradientBoostingRegressor(**cfg, random_state=42)
    cv_scores = cross_val_score(gb, X_scaled, y, cv=5, scoring='r2')
    mean_cv = cv_scores.mean()
    print(f"  Config {i +1}: CV R2 = {mean_cv:.4f} (+/- {cv_scores.std():.4f})")
    if mean_cv > best_cv:
        best_cv = mean_cv
        best_config = cfg
        best_model = gb

print(f"\nBest config: CV R2 = {best_cv:.4f}")
print(f"Params: {best_config}")

# Train final model
print("\nTraining final model...")
best_model.fit(X_scaled, y)
y_pred = best_model.predict(X_scaled)

r2_train = r2_score(y, y_pred)
mae_train = mean_absolute_error(y, y_pred)
print(f"Train R2: {r2_train:.4f}, MAE: {mae_train:.1f} S/m")

# Save
joblib.dump(best_model, '11-research/models/LIG_GB_regularized_200.pkl')
joblib.dump(scaler_X, '11-research/models/LIG_GB_reg_200_scaler_X.pkl')
print("\nSaved: LIG_GB_regularized_200.pkl")

print(f"\nNote: With 200 samples and 3 features, CV R2 = {best_cv:.4f}")
print(f"May need more data or better features to reach R2 > 0.80")
