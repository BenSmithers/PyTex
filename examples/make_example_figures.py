import numpy as np
import matplotlib.pyplot as plt 
import os

for i in range(25):
    a = np.random.rand()-0.5
    b = np.random.rand()-0.5
    c = np.random.rand()-0.5
    d = np.random.rand()-0.5

    x = np.linspace(-1,1,1000)
    y = a + b*x + c*(x**2) + c*(x**3)

    plt.plot(x,y)
    plt.xlabel("X [unitless]")
    plt.ylabel("Y [unitless]")
    plt.savefig(os.path.join(os.path.dirname(__file__),"ex_plots", "test_plot_{}.png".format(i)))
    plt.clf()