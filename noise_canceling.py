from scipy.io import wavfile
import sounddevice as sound
import numpy as np
import matplotlib.pyplot as plt
import control
import control.matlab as matlab
from pyplotter_nice import make_graph_fancy

rate, signal = wavfile.read("noise.wav")
rate_music, music = wavfile.read("pirates.wav")
clip_duration = 30.0
time = np.linspace(0, clip_duration, len(signal))

R1 = 22_000 # ohms
R2 = 1_000 # ohms
# R4 = 50_000_000
R2C1 = R2 * 10e-6

R6 = 10_000
R8 = 10_000
R7 = 500_000

z = 1 + R1 / R2
a1 = 1/R2C1
V = -(R6)/R7

def process_signal(R4):
    R4C = R4 * 2e-9
    a2 = 1/R4C
    
    numerator = V * np.array([-1, a2])
    denomenator = V * np.array([1, a2])

    combined_transfer_function = control.tf(numerator, denomenator)

    signal_filtered, _, _ = matlab.lsim(combined_transfer_function, U=signal, T=time, X0=0.0)
    output_signal = signal + signal_filtered
    output_signal_plus_music = output_signal + R6 / R7 * music

    normalized_output = output_signal_plus_music
    max_value = np.max(np.abs(normalized_output))
    if max_value > 0:
        # Multiply by 0.95 to leave a small safety margin (headroom)
        normalized_output = (normalized_output / max_value) * 0.95

    return signal_filtered, output_signal, music * R6 / R7, output_signal_plus_music, normalized_output



def setup_signal_plot(signal, label=""):
    time_min = 5.0
    time_max = 5.01

    plt.cla()
    plt.xlim(time_min, time_max)
    plt.plot(time, signal, label=label)
    plt.xlabel("Time (s)")
    plt.ylabel("Audio signal")


def generate_results(R6, folder):
    make_graph_fancy()
    filtered, noiseless, music_in, music_out, music_out_normalized = process_signal(R6)

    setup_signal_plot(signal)
    # plt.title("Noise sampled from environment")
    plt.savefig(folder + "/(1) result_unfiltered.png")

    setup_signal_plot(filtered)
    # plt.title("Result of noise ran through transfer function")
    plt.savefig(folder + "/(2) result_filtered.png")

    setup_signal_plot(signal + filtered)
    # plt.title("Sampled noise combined with filtered noise")
    plt.ylim(-8000, 8000)
    plt.savefig(folder + "/(3) result_combined.png")

    setup_signal_plot(music)
    # plt.title("Sample 30 second music file")
    plt.savefig(folder + "/(4) music.png")

    setup_signal_plot(music * R6 / R7, label="Filtered music file")
    plt.plot(time, music_out, label="Unfiltered music file")
    # plt.title("Music + filtered noise signal")
    plt.legend()
    plt.savefig(folder + "/(5) result_final.png")
    # plt.legend()

    wavfile.write(f"{folder}/output.wav", rate, np.int16(music_out_normalized * 32767))

generate_results(R6=500_000, folder="results_500k")
generate_results(R6=5_000_000, folder="results_5M")
generate_results(R6=50_000_000, folder="results_50M")