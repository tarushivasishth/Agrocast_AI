import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress INFO and WARNING logs
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

import os
print("Current Working Directory:", os.getcwd())
print("Files in models:", os.listdir("models"))

import numpy as np

# class labels
from labels import CLASS_NAMES

# loading model

model = tf.keras.models.load_model("models/resnet50_finetuned.keras")

# import sys
# print("Python Executable:", sys.executable)
# print("Python Version:", sys.version)


# predict disease
def predict(img):
    img = img.resize((224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = np.expand_dims(img_array, 0)

    predictions = model.predict(img_array)
    predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
    confidence = np.round(100 * max(predictions[0]), 2)

    return predicted_class, confidence
