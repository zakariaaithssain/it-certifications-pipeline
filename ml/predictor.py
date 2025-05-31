from tqdm import tqdm
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score

class MissingColumnsPredictor:
    def __init__(self, name, model, training_data, n_splits, model_type = 'regressor'):
        self.model = model
        self.data = training_data
        self.name = name
        self.cv = KFold(n_splits=n_splits, shuffle=True, random_state=37) \
            if model_type=='regressor' else StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=37)
        self.best_score = 0
        self._selected_features = None
        self.X = self.data.drop(columns=[self.name])
        self.y = self.data[self.name]



    def get_optimal_features(self, progressor): #st related argument
        directions = ['forward', 'backward']
        step = 0
        total_steps = (len(self.X.columns) - 2) * len(directions)
        for n_features in tqdm(range(2, len(self.X.columns))):
            progressor.progress(step / total_steps)
            for direction in directions:
                selector = SequentialFeatureSelector(estimator= self.model, n_features_to_select=n_features, direction=direction, cv = self.cv)
                selector.fit(self.X, self.y)
                selected_features = self.X[self.X.columns[selector.get_support()]]
                score = cross_val_score(estimator=self.model, cv=self.cv, X= selected_features, y=self.y).mean()
                step+= 1
                progressor.progress(step / total_steps)
                if score > self.best_score:
                    self.best_score = score
                    self._selected_features = selected_features
        print(f"\nBest Cross Validation Score for {self.name}: {self.best_score}\n ")
        return self._selected_features.columns



    def train(self):
        if self._selected_features is not None:
            self.model.fit(self._selected_features, self.y)
            return self
        else: print('you should call "get_optimal_features()" first')



    def predict(self, X):
        return self.model.predict(X)













