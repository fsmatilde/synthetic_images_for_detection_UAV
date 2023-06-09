import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# Open and read log file
with open("loss_log.txt") as f:
    lines = f.readlines()

# Extract loss values
losses_list = ['KLD', 'GAN', 'GAN_Feat', 'VGG', 'D_Fake', 'D_real']
iterations = []
x_structure = 2
y_structure = 3
figure, axis = plt.subplots(x_structure, y_structure)
for i, loss in enumerate(losses_list, start=1):
    yy = []
    for line in lines:
        if "KLD:" in line:
            yy.append(float(line.split(loss + ": ")[1].split(" ")[0]))
            iterations.append(int(line.split("iters: ")[1].split(",")[0]))

    # Define x and y
    yy = savgol_filter(yy, window_length=200, polyorder=2)
    xx = len(yy)

    # Plot loss values in y axis and iteration number in x axis
    plt.subplot(x_structure, y_structure, i)
    plt.title(loss)
    plt.plot(range(len(yy)), yy)
    plt.xlabel("Total iterations")
    plt.ylabel(loss)

plt.show()