import numpy as np

def train_model(temps_history=None):
    """
    Train an LSTM model on temperature data.
    Uses real forecast data if available, else synthetic demo data.
    Returns the trained Keras model.
    """
    try:
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense
        import tensorflow as tf
        tf.get_logger().setLevel("ERROR")  # suppress TF warnings in UI
    except ImportError:
        return None

    # Use real temperatures if provided, else demo data
    if temps_history and len(temps_history) >= 6:
        data = np.array(temps_history[:10])
    else:
        data = np.array([28.0, 29.5, 31.0, 32.5, 33.0, 34.5, 35.0, 36.0, 37.5, 38.0])

    # Create sequences: window=3, predict next
    SEQ_LEN = 3
    X, y = [], []
    for i in range(len(data) - SEQ_LEN):
        X.append(data[i:i + SEQ_LEN])
        y.append(data[i + SEQ_LEN])

    X = np.array(X).reshape(-1, SEQ_LEN, 1)
    y = np.array(y)

    model = Sequential([
        LSTM(64, activation="relu", input_shape=(SEQ_LEN, 1), return_sequences=False),
        Dense(32, activation="relu"),
        Dense(1),
    ])
    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=100, verbose=0)

    return model


def predict_next(model, recent_temps, steps=7):
    """
    Predict the next `steps` temperature values using LSTM model.
    recent_temps: list of last 3+ temperature readings.
    Returns a list of predicted float values.
    """
    if model is None:
        # Fallback: simple trend extrapolation
        if recent_temps:
            last = recent_temps[-1]
            return [last + i * 0.3 for i in range(steps)]
        return [30 + i * 0.3 for i in range(steps)]

    SEQ_LEN = 3
    # Use last 3 temps as seed
    seed = np.array(recent_temps[-SEQ_LEN:], dtype=float).reshape(1, SEQ_LEN, 1)
    preds = []

    for _ in range(steps):
        p = model.predict(seed, verbose=0)[0][0]
        preds.append(float(p))
        # Slide window forward
        seed = np.append(seed[:, 1:, :], [[[p]]], axis=1)

    return preds
