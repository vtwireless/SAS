import numpy as np
import matplotlib.pyplot as plt


def rayleigh_fading():
    # velocity of either TX or RX, in miles per hour
    v_mph = 60
    # convert to m/s
    v = v_mph * 0.44704

    # RF carrier frequency in Hz
    center_freq = 200e6  # 200MHz
    # max Doppler shift
    fd = v * center_freq / 3e8

    # sample rate of simulation
    Fs = 1e5

    # number of sinusoids to sum
    N = 100

    print("max Doppler shift:", fd)

    # time vector. (start, stop, step)
    t = np.arange(0, 1, 1/Fs)
    x = np.zeros(len(t))
    y = np.zeros(len(t))

    for i in range(N):
        alpha = (np.random.rand() - 0.5) * 2 * np.pi
        phi = (np.random.rand() - 0.5) * 2 * np.pi
        x = x + np.random.randn() * np.cos(2 * np.pi * fd * t * np.cos(alpha) + phi)
        y = y + np.random.randn() * np.sin(2 * np.pi * fd * t * np.cos(alpha) + phi)

    # z is the complex coefficient representing channel, you can think of this as a phase shift and magnitude scale
    # this is what you would actually use when simulating the channel
    z = (1/np.sqrt(N)) * (x + 1j * y)

    # take magnitude for the sake of plotting
    z_mag = np.abs(z)
    # convert to dB
    z_mag_dB = 10 * np.log10(z_mag)

    # Plot fading over time
    plt.plot(t, z_mag_dB)
    plt.plot([0, 1], [0, 0], ':r') # 0 dB
    plt.legend(['Rayleigh Fading', 'No Fading'])
    plt.axis([0, 1, -15, 5])
    plt.show()


if __name__ == '__main__':
    rayleigh_fading()
