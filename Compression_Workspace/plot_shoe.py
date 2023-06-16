# TensorFlow and tf.keras
import tensorflow as tf
from pyzfp import compress, decompress

# Helper libraries
import numpy as np
import matplotlib.pyplot as plt

fashion_mnist = tf.keras.datasets.fashion_mnist
(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

data_in = train_images[90]/255.0

plt.figure()
plt.imshow(data_in)
plt.colorbar()
plt.grid(False)
plt.savefig('fig1.png',dpi=100)

tolerance = 1e-4
compressed = compress(data_in, tolerance=tolerance)
recovered = decompress(compressed, data_in.shape, data_in.dtype, tolerance=tolerance)

plt.figure()
plt.imshow(recovered)
plt.colorbar()
plt.grid(False)
plt.savefig('fig2.png',dpi=1200)


tolerance = 5
compressed = compress(data_in, tolerance=tolerance)
recovered = decompress(compressed, data_in.shape, data_in.dtype, tolerance=tolerance)

plt.figure()
plt.imshow(recovered)
plt.colorbar()
plt.grid(False)
plt.savefig('fig3.png',dpi=1200)


plt.show()
