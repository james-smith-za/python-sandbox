import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sp
from multiprocessing import Pool
import time

def accumulate_1_ms(x):
    # Let's create a nice analogue-looking signal for ourselves.
    # We'll do this by sampling 100 times higher than what we're going for in a ROACH,
    # i.e. 80 GHz
    nyquist = 8e9
    duration = 1e-3
    filter = sp.firwin(numtaps=301, cutoff=[50e6,350e6], pass_zero=False, nyq=nyquist)

    original_signal = np.random.normal(size=int(duration * nyquist))
    # print original_signal.size
    filtered_signal = sp.lfilter(filter, 1, original_signal)
    # print filtered_signal.size
    cont_time = np.arange(len(filtered_signal)) / nyquist

    # fig = plt.figure(figsize=(15,5))
    # ax = fig.add_subplot(111)
    # ax.set_title("Example of a random, band-limited voltage signal")
    # ax.set_xlabel("Time [us]")
    # ax.set_ylabel("Voltage [V]")
    # ax.set_xlim(4,4.5)
    # ax.plot(cont_time * 1e6, filtered_signal)
    # plt.show()

    sampling_freq = 800e6
    sampling_period_samples = int(nyquist / sampling_freq)
    sampling_period_seconds = 1 / sampling_freq
    # print sampling_period_samples

    sampled_signal = filtered_signal[::sampling_period_samples]
    # print sampled_signal.size
    sampled_time = cont_time[::sampling_period_samples]
    digitiser_bits = 4
    voltage_range = 1
    resolution = float(2 * voltage_range) / (2 ** digitiser_bits)
    digitiser_bins = np.linspace(-voltage_range, voltage_range, 2 ** digitiser_bits)
    digitised_signal = np.digitize(sampled_signal, digitiser_bins)
    digitised_signal = np.array([digitiser_bins[i - 1] + resolution / 2 for i in digitised_signal])

    # fig = plt.figure(figsize=(15,5))
    # ax = fig.add_subplot(111)
    # ax.set_title("Sampling the signal")
    # ax.set_xlabel("Time [us]")
    # ax.set_ylabel("Voltage [V]")
    # # ax.set_xlim(4,4.2)
    # ax.plot(cont_time * 1e6, filtered_signal)
    # ax.plot(sampled_time * 1e6, digitised_signal, 'o')
    # plt.show()

    spectrum_size = 1024
    n_points = spectrum_size * 2
    initial_offset = 1000  # Just so that we don't take the first (possibly not yet steady state) frame
    max_integration_period_frames = digitised_signal.size / n_points
    max_integration_period_seconds = max_integration_period_frames * (sampling_period_seconds * n_points)
    # print max_integration_period_frames, max_integration_period_seconds * 1e3

    hamming_window = sp.get_window("hamming", n_points)
    windowed_signal = sampled_signal[initial_offset:initial_offset + n_points] * hamming_window
    signal_spectrum = np.fft.fft(windowed_signal, n_points)
    frequency = np.fft.fftfreq(n_points, 1.0 / sampling_freq)

    # fig = plt.figure(figsize=(15,10))
    # ax = fig.add_subplot(111)
    # ax.set_title("Signal spectrum")
    # ax.set_xlabel("Frequency [MHz]")
    # ax.set_ylabel("Amplitude [V]")
    # ax.plot(frequency[:spectrum_size]/1e6, np.abs(signal_spectrum[:spectrum_size]))
    # ax.set_xlim(0,200)
    # plt.show()

    accumulated_spectrum = np.zeros(n_points, dtype=np.complex128)

    for i in range(max_integration_period_frames):
        windowed_signal = sampled_signal[i * n_points:(i + 1) * n_points] * hamming_window
        signal_spectrum = np.fft.fft(windowed_signal, n_points)
        accumulated_spectrum += signal_spectrum

    accumulated_spectrum /= max_integration_period_frames
    print "Integrated %d milliseconds" % x
    return accumulated_spectrum


def main():
    num_of_milliseconds_to_integrate = 1000

    # w, h = sp.freqz(filter)
    # fig = plt.figure(figsize=(14,7))
    # ax1 = fig.add_subplot(111)
    # ax1.set_title("Digital filter frequency response")
    # ax1.set_xlabel("Frequency [rad/sample]")
    # ax1.set_ylabel("Amplitude [dB]")
    # ax1.plot(w, 20*np.log10(np.abs(h)))
    # plt.show()

    # accumulated_spectrum = np.zeros(n_points, dtype=np.complex128)

    pool = Pool(processes=4)


    start_time = time.time()
    results = pool.map(accumulate_1_ms, range(4))
    results = np.array(results)

    accumulated_spectrum = np.average(results, axis=0)
    end_time = time.time()

    # print accumulated_spectrum.shape
    # print end_time - start_time

    # fig = plt.figure(figsize=(15,10))
    # ax = fig.add_subplot(111)
    # ax.set_title("Averaged signal spectrum")
    # ax.set_xlabel("Frequency [MHz]")
    # ax.set_ylabel("Amplitude [V]")
    # ax.plot(frequency[:spectrum_size]/1e6, np.abs(accumulated_spectrum[:spectrum_size]))
    # #ax.set_xlim(0,200)
    # plt.show()


if __name__ == "__main__":
    main()