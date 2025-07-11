import os
import sys
from dataclasses import dataclass

from catboost import CatBoostRegressor
from sklearn.ensemble import (
    AdaBoostRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from src.exception import CustomException
from src.logger import logging
from src.utlis import save_object, evaluate_models

@dataclass
class ModelTrainerConfig:
    trained_model_file_path: str = os.path.join('artifacts', 'model.pkl')

# ✅ Unindented class definition
class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()

    def initiate_model_trainer(self, train_array, test_array, preprocessor_path):
        try:
            logging.info("Splitting training and testing input data")
            x_train, y_train, x_test, y_test = (
                train_array[:, :-1],
                train_array[:, -1],
                test_array[:, :-1],
                test_array[:, -1]
            )

            models = {
                "Random Forest": RandomForestRegressor(),
                "Decision Tree": DecisionTreeRegressor(),
                "Gradient Boosting": GradientBoostingRegressor(),
                "Linear Regression": LinearRegression(),
                "KNeighbors Regressor": KNeighborsRegressor(),
                "XGBClassifier": XGBRegressor(),
                "CatBoosting Classifier": CatBoostRegressor(verbose=False),
                "AdaBoost Regressor": AdaBoostRegressor()
            }
            params = {
                "Decision Tree":{
                    'criterion': ['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                    #'splitter': ['best', 'random'], 
                },
                "Random Forest": {
                    'n_estimators': [8, 16, 32, 64, 128,256],
                    #'max_features': ['auto', 'sqrt', 'log2'],
                    #'criterion': ['squared_error', 'absolute_error', 'poisson']
                },
                "Gradient Boosting": {
                    #'loss': ['squared_error', 'absolute_error', 'huber', 'quantile'],
                    'learning_rate': [.1,.01,.05,.001],
                    'subsample': [0.6,0.7,.75,.8,0.85,0.9],
                    'n_estimators': [8, 16, 32, 64, 128,256],
                    #'max_depth': [3, 5, 7]
                },
                "Linear Regression": {},
                "XGBRegressor":{
                    'learning_rate': [.1,.01,.05,.001],
                    'n_estimators': [8, 16, 32, 64, 128,256],
                },
                "CatBoosting Regressor": {
                    'learning_rate': [0.01,0.05,0.1],
                    'iterations': [30,5,100],
                    'depth': [6,8,10]
                },
                "AdaBoost Regressor": {
                    'learning_rate': [.1,.01,.05,.001],
                    'n_estimators': [8, 16, 32, 64,128,256]
                }
            }
            
            

            # ⛔ Also check if you have defined `params`
            # Otherwise remove param=params if not needed
            model_report: dict = evaluate_models(
                X_train=x_train, y_train=y_train,
                X_test=x_test, y_test=y_test,
                models=models, param=params
                # , param=params  ⛔ remove or fix this line
            )

            best_model_score = max(sorted(model_report.values()))
            best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]
            best_model = models[best_model_name]

            if best_model_score < 0.6:
                raise CustomException("No best model found with sufficient accuracy")

            logging.info(f"Best model found: {best_model_name} with score: {best_model_score}")

            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )

            predicted = best_model.predict(x_test)
            r2_square = r2_score(y_test, predicted)
            return r2_square

        except Exception as e:
            raise CustomException(e, sys)
