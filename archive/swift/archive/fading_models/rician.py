import time
from scipy.stats import gaussian_kde as kdf
from scipy import special as sp
import numpy as np
import matplotlib.pyplot as plt


# np.random.seed(2025)


class Rice:
    r = np.linspace(0, 6, 6000)  # theoretical envelope PDF x axes
    theta = np.linspace(-np.pi, np.pi, 6000)  # theoretical phase PDF x axes

    def __init__(self, K, r_hat_2, phi, samples):

        # user input checks and assigns value
        self.K = self.input_Check(K, "K", 0, 50)
        self.r_hat_2 = self.input_Check(r_hat_2, "\hat{r}^2", 0.5, 2.5)
        self.phi = self.input_Check(phi, "\phi", -np.pi, np.pi)
        self.numSamples = samples

        # simulating and their densities
        self.real, self.imag = self.complex_Multipath_Fading()

    def input_Check(self, data, inputName, lower, upper):
        # input_Check checks the user inputs

        # has a value been entered
        if data == "":
            raise ValueError(" ".join((inputName, "must have a numeric value")))

        # incase of an non-numeric input
        try:
            data = float(data)
        except:
            raise ValueError(" ".join((inputName, "must have a numeric value")))

        # data must be within the range
        if data < lower or data > upper:
            raise ValueError(" ".join((inputName, f"must be in the range [{lower:.2f}, {upper:.2f}]")))

        return data

    def calculate_Means(self):
        # calculate_means calculates the means of the complex Gaussians representing the
        # in-phase and quadrature components

        p = np.sqrt(self.K * self.r_hat_2 / (1 + self.K)) * np.cos(self.phi)
        q = np.sqrt(self.K * self.r_hat_2 / (1 + self.K)) * np.sin(self.phi)

        return p, q

    def scattered_Component(self):
        # scattered_Component calculates the power of the scattered signal component

        sigma = np.sqrt(self.r_hat_2 / (2 * (1 + self.K)))

        return sigma

    def generate_Gaussians(self, mean, sigma):
        # generate_Gaussians generates the Gaussian random variables

        gaussians = np.random.normal(mean, sigma, self.numSamples)

        return gaussians

    def complex_Multipath_Fading(self):
        # complex_Multipath_Fading generates the complex fading random variables

        p, q = self.calculate_Means()
        sigma = self.scattered_Component()
        real, imag = self.generate_Gaussians(p, sigma),  self.generate_Gaussians(q, sigma)

        return real, imag


if __name__ == '__main__':
    samples = 100000
    Ts = 0.001

    K, hr, phi = 2, 1, 1
    s = Rice(K, hr, phi, samples)
    real, imag = s.real, s.imag

    h = [real[i] + 1j * imag[i] for i in range(len(real))]
    h_mag = [np.sqrt(np.square(real[i]) + np.square(imag[i])) for i in range(len(real))]
    h_mag_db = [10 * np.log10(item) for item in h_mag]
    phase = list(np.angle(h))
    time = np.arange(0 + Ts, (samples * Ts) + Ts, Ts)

    # fig, (plot1, plot2) = plt.subplots(2)
    # # fig.suptitle('Amplitude and Phase Response of the Flat Fading Channel')
    #
    # plot1.plot(time, h_mag_db)
    # plot1.set_title(f'Amplitude Response of a Rician Channel [K = {K}]')
    # plot1.set(xlabel='time(s)', ylabel='Magnitude |h(t)|')
    # plot1.grid()
    #
    # plot2.plot(time, phase)
    # plot2.set_title(f'Phase Response of a Rician Channel [K = {K}]')
    # plot2.set(xlabel='time(s)', ylabel='Phase angle (h(t))')
    # plot2.grid()
    #
    # step = 5 * 10 * Ts
    # start, stop = 0, (samples * Ts) + step
    # x_ticks = list(np.arange(start, stop, step))
    # plot1.set_xticks(x_ticks)
    # plot2.set_xticks(x_ticks)
    # plot1.tick_params(axis='both', which='both', labelsize=5)
    # plot2.tick_params(axis='both', which='both', labelsize=5)
    # fig.tight_layout()
    # fig.savefig('rician.png', bbox_inches='tight', dpi=1200)

    normalized_time = [ts / np.max(time) for ts in time]
    log_time = [np.log10(ts) for ts in normalized_time]
    sorted_h = np.sort(h_mag_db)
    plt.plot(sorted_h, log_time)
    # plt.set_title('Amplitude Response of a Rayleigh Channel')
    # plt.set(xlabel='time(s)', ylabel='Magnitude |h(t)|')
    plt.grid()
    plt.show()


