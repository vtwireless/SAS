import numpy as np
from matplotlib import pyplot as plt


class Rayleigh:
    c = 3 * np.power(10, 8)

    def __init__(self, multipaths, speed, center_frequency, samples, sampling_period):
        self.multipaths = multipaths
        self.samples = int(samples)
        self.sampling_time = sampling_period

        self.doppler_shift = (speed * center_frequency)/self.c

        low, high = 0, 2 * np.pi

        self.alpha = low + high * np.random.sample(self.multipaths)
        self.beta = low + high * np.random.sample(self.multipaths)
        self.theta = low + high * np.random.sample(self.multipaths)

        self.h, self.h_mag_db = [], []

        self.generate_model()

    def generate_model(self):
        print("Generating Rayleigh Model")
        m = np.arange(1, self.multipaths + 1, 1)
        scalar_coefficient = 1 / np.square(self.multipaths)
        phase_constant = 2 * np.pi * self.doppler_shift * self.sampling_time

        for sample_index in range(1, self.samples + 1):
            inner_coefficients = np.cos(
                (1 / (4 * self.multipaths)) * ((
                     ((2 * m) - 1) * np.pi
                ) + self.theta)
            )

            real_phase = np.cos((phase_constant * sample_index * inner_coefficients) + self.alpha)
            imag_phase = np.sin((phase_constant * sample_index * inner_coefficients) + self.beta)
            real, imag = scalar_coefficient * np.sum(real_phase), scalar_coefficient * np.sum(imag_phase)

            self.h.append(real + (1j * imag))
            h_magnitude = np.sqrt(np.square(real) + np.square(imag))
            self.h_mag_db.append(10 * np.log10(h_magnitude))

    def generate_plot(self):
        print("Plotting Rayleigh Model Results")
        time = np.arange(
            0 + self.sampling_time, (self.samples * self.sampling_time) + self.sampling_time, self.sampling_time
        )
        maxT = np.max(time)
        log_time = [np.log10(ts / maxT) for ts in time]
        sorted_h = np.sort(self.h_mag_db)

        plt.plot(sorted_h, log_time)
        plt.title('Amplitude Response of a Rayleigh Channel')
        plt.xlabel('time(s)')
        plt.ylabel('Magnitude |h(t)|')
        plt.grid()
        plt.show()


class Rician:
    r = np.linspace(0, 6, 6000)  # theoretical envelope PDF x axes
    theta = np.linspace(-np.pi, np.pi, 6000)  # theoretical phase PDF x axes

    def __init__(self, K, r_hat_2, phi, samples, sampling_time):
        # user input checks and assigns value
        self.K = self.input_Check(K, "K", 0, 50)
        self.r_hat_2 = self.input_Check(r_hat_2, "\hat{r}^2", 0.5, 2.5)
        self.phi = self.input_Check(phi, "\phi", -np.pi, np.pi)
        self.numSamples = int(samples)
        self.sampling_time = sampling_time

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
        print("Generating Rayleigh Model")
        # complex_Multipath_Fading generates the complex fading random variables

        p, q = self.calculate_Means()
        sigma = self.scattered_Component()
        real, imag = self.generate_Gaussians(p, sigma),  self.generate_Gaussians(q, sigma)

        return real, imag

    def generate_plot(self):
        print("Plotting Rayleigh Model Results")
        h_mag_db = [
            10 * np.log10(np.sqrt(np.square(self.real[index]) + np.square(self.imag[index])))
            for index in range(len(self.real))
        ]
        time = np.arange(
            0 + self.sampling_time, (self.numSamples * self.sampling_time) + self.sampling_time, self.sampling_time
        )
        maxT = np.max(time)
        log_time = [np.log10(ts / maxT) for ts in time]
        sorted_h = np.sort(h_mag_db)

        plt.plot(sorted_h, log_time)
        plt.title(f'Amplitude Response of a Rician Channel for K = {self.K}')
        plt.xlabel('Magnitude |h(t)|')
        plt.ylabel('time')
        plt.grid()
        plt.show()


if __name__ == '__main__':
    samples, sampling_period = 10e5, 10e-2

    # Rayleigh Fading
    multipaths, speed, center_frequency = 15, 30, 12e9
    rayleigh = Rayleigh(multipaths, speed, center_frequency, samples, sampling_period)

    K, hr, phi = 2, 1, 1
    rician = Rician(K, hr, phi, samples, sampling_period)

    rician.generate_plot()
    rayleigh.generate_plot()
