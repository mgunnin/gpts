import asyncio
from typing import Dict, List

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from database.database import get_db


class MachineLearningModels:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)

    async def fetch_training_data(self) -> List[Dict]:
        """
        Fetches training data from the database.
        This function assumes that the MatchData table contains columns for match outcomes and features used for training.
        """
        async with get_db() as session:
            async with session.begin():
                result = await session.execute(
                    """
                    SELECT win, feature1, feature2, feature3
                    FROM match_data
                    """
                )
                return result.fetchall()

    def prepare_data(self, data: List[Dict]) -> (np.ndarray, np.ndarray):
        """
        Prepares the data for training the model.
        """
        X = np.array([[d["feature1"], d["feature2"], d["feature3"]] for d in data])
        y = np.array([d["win"] for d in data])
        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train_model(self, X_train: np.ndarray, y_train: np.ndarray):
        """
        Trains the machine learning model.
        """
        self.model.fit(X_train, y_train)

    def evaluate_model(self, X_test: np.ndarray, y_test: np.ndarray) -> float:
        """
        Evaluates the model's performance.
        """
        predictions = self.model.predict(X_test)
        return accuracy_score(y_test, predictions)

    async def run(self):
        """
        Main function to run the machine learning pipeline.
        """
        data = await self.fetch_training_data()
        X_train, X_test, y_train, y_test = self.prepare_data(data)
        self.train_model(X_train, y_train)
        accuracy = self.evaluate_model(X_test, y_test)
        print(f"Model Accuracy: {accuracy}")


# Example usage
if __name__ == "__main__":
    ml_models = MachineLearningModels()
    asyncio.run(ml_models.run())
