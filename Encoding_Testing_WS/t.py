import os
from skopt import dump, load

for file in os.listdir("model"):
    index = file[6:file.find(".pkl")]

    loaded_res = load("model/" + str(file))

    