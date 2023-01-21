import numpy as np
from matplotlib import pyplot as plt
import os

# if os.path.exists('rayleigh.png'):
#     os.remove('rayleigh.png')

# np.random.seed(2025)

c = 3e8
speed = 20.1168
center_freq = 12e9

M = 5  # Number of multipaths
N = np.power(10, 6)  # Number of samples
# [speed=20.1168m/s, center_freq=12e9, fd=(v*f)/c]
fd = (speed * center_freq)/c
Ts = 0.001  # period in sec

h_re, h_im, h, h_abs, h_mag_dB = [], [], [], [], []
a, b = 0, 2 * np.pi
alpha = a + b * np.random.sample(M)
beta = a + b * np.random.sample(M)
theta = a + b * np.random.sample(M)
time = np.arange(0 + Ts, (N * Ts) + Ts, Ts)

for n in range(N):
    coeff = 1 / np.sqrt(M)
    real, imag = 0.0, 0.0
    for m in range(M):
        coeff2 = ((((2 * m) - 1) * np.pi) + theta[m])/(4 * M)
        coeff3 = 2 * np.pi * fd * np.cos(coeff2) * n * Ts
        real += np.cos(coeff3 + alpha[m])
        imag += np.cos(coeff3 + beta[m])

    real *= coeff
    imag *= coeff

    h_re.append(real)
    h_im.append(imag)
    h.append(real + 1j * imag)
    h_mag = np.sqrt(np.square(real) + np.square(imag))
    h_abs.append(h_mag)
    h_mag_dB.append(10 * np.log10(h_mag))

    if (n + 1) % 1000 == 0:
        print(f'{n + 1} samples sampled')

# fig, (plot1, plot2) = plt.subplots(2)
# fig.suptitle('Amplitude and Phase Response of the Flat Fading Channel')
#
# plot1.plot(time, h_mag_dB)
# plot1.set_title('Amplitude Response of a Rayleigh Channel')
# plot1.set(xlabel='time(s)', ylabel='Magnitude |h(t)|')
# plot1.grid()
#
# plot2.plot(time, list(np.angle(h)))
# plot2.set_title('Phase Response of a Rayleigh Channel')
# plot2.set(xlabel='time(s)', ylabel='Phase angle (h(t))')
# plot2.grid()
#
# step = 5 * 10 * Ts
# start, stop = 0, (N * Ts) + step
# x_ticks = list(np.arange(start, stop, step))
# plot1.set_xticks(x_ticks)
# plot2.set_xticks(x_ticks)
# plot1.tick_params(axis='both', which='both', labelsize=5)
# plot2.tick_params(axis='both', which='both', labelsize=5)
# fig.tight_layout()
# fig.savefig('rayleigh.png', bbox_inches='tight', dpi=1200)

print("preparing")
maxT = np.max(time)
# normalized_time = [ts/np.max(time) for ts in time]
log_time = [np.log10(ts/maxT) for ts in time]
sorted_h = np.sort(h_mag_dB)
print("complete")

plt.plot(sorted_h, log_time)
# plt.set_title('Amplitude Response of a Rayleigh Channel')
# plt.set(xlabel='time(s)', ylabel='Magnitude |h(t)|')
plt.grid()
plt.show()

# -------- logarithmic time scale ---------


