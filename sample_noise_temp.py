import imageio
import numpy as np
from matplotlib import pyplot as plt

image = imageio.imread('./pnoise/pnoise.png')

image = plt.imshow(image)
print(np.shape(image))
plt.show()
