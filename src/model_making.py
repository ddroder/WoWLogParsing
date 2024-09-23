import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report  # 3. Model Definition


def build_model(input_shape, num_classes):
    """
    Builds and returns a Keras model.
    """
    model = models.Sequential()
    model.add(layers.Dense(128, activation="relu", input_shape=(input_shape,)))
    model.add(layers.Dense(64, activation="relu"))
    model.add(layers.Dense(num_classes, activation="softmax"))
    return model


# 4. Training the Model
def train_model(model, X_train, y_train, X_val, y_val):
    """
    Compiles and trains the model.
    """
    model.compile(
        optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
    )

    history = model.fit(
        X_train, y_train, epochs=20, batch_size=32, validation_data=(X_val, y_val)
    )

    return history


# 5. Evaluating the Model
def evaluate_model(model, X_test, y_test, spell_encoder):
    """
    Evaluates the model on the test set and prints a classification report.
    """
    y_pred = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred, axis=1)

    print(
        classification_report(
            y_test, y_pred_classes, target_names=spell_encoder.classes_
        )
    )


# Main script execution
if __name__ == "__main__":
    # Specify the directory containing your log files
    log_directory = "/Users/ddroder/code/wow-log-ml/data"
    # log_directory = "path/to/your/log/files"

    # Load and preprocess data
    df = load_data(log_directory)
    X, y, spell_encoder = preprocess_data(df)

    # Split the dataset
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=0.15, random_state=42
    )

    # Build and train the model
    num_classes = len(spell_encoder.classes_)
    model = build_model(input_shape=X.shape[1], num_classes=num_classes)
    history = train_model(model, X_train, y_train, X_val, y_val)

    # Evaluate the model
    evaluate_model(model, X_test, y_test, spell_encoder)

    # Save the trained model
    model.save("wow_arena_coach_model.h5")
    print("Model saved as 'wow_arena_coach_model.h5'")
