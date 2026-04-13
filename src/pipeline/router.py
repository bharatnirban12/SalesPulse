import yaml
import pickle
import numpy as np
import pandas as pd


class ModelRouter:
    def __init__(self):
        with open("src/config/config.yaml", "r") as f:
            config = yaml.safe_load(f)

        self.sparse_categories = set(config["sparse_categories"])

        # Load dense model
        with open("models/model.pkl", "rb") as f:
            self.dense_model = pickle.load(f)

        # Load sparse model
        with open("models/sparse_model.pkl", "rb") as f:
            self.sparse_model = pickle.load(f)


    def predict(self, features):

        if not isinstance(features, pd.DataFrame):
            if isinstance(features, pd.Series):
                features = features.to_frame().T
            else:
                features = pd.DataFrame([features])

        results = np.zeros(len(features))
        
        # Identify sparse vs dense rows
        sparse_mask = features['family'].isin(self.sparse_categories)
        
        # 1. DENSE MODEL PREDICTIONS
        if (~sparse_mask).any():
            dense_feats = features[~sparse_mask]
            # print(f"Routing {len(dense_feats)} rows to DENSE model")
            preds_log = self.dense_model.predict(dense_feats)
            results[~sparse_mask] = np.expm1(preds_log)

        # 2. SPARSE MODEL PREDICTIONS
        if sparse_mask.any():
            sparse_feats = features[sparse_mask]
            # print(f"Routing {len(sparse_feats)} rows to SPARSE model")
            
            clf = self.sparse_model["classifier"]
            reg = self.sparse_model["regressor"]
            
            probs = clf.predict(sparse_feats)
            
            nonzero_mask = (probs == 1)
            
            sparse_results = np.zeros(len(sparse_feats))
            
            if nonzero_mask.any():
                reg_preds_log = reg.predict(sparse_feats[nonzero_mask])
                sparse_results[nonzero_mask] = np.expm1(reg_preds_log)
            
            results[sparse_mask] = sparse_results

        if len(results) == 1:
            return float(results[0])
        return results

