from scipy.io import wavfile
import sounddevice as sound
import numpy as np
import matplotlib.pyplot as plt
import control
import control.matlab as matlab

rate, signal = wavfile.read("noise.wav")
rate_music, music = wavfile.read("pirates.wav")
clip_duration = 30.0
time = np.linspace(0, clip_duration, len(signal))

R1 = 22_000 # ohms
R2 = 1_000 # ohms
R2C1 = R2 * 10e-6
R4C = 999_000 * 2e-9

R6 = 10_000
R8 = 10_000
# R12 = 100
R7 = 500_000

z = 1 + R1 / R2
g1 = 1/R2C1
g2 = 1/R4C
V = 1#-(R6)/R7

# numerator = V * np.array([-z, g2*z - g1, g1*g2])
# denomenator = V * np.array([1, g1 + g2, g1 * g2])
numerator = V * np.array([-1, g2])
denomenator = V * np.array([1, g2])

combined_transfer_function = control.tf(numerator, denomenator)

signal_filtered, _, _ = matlab.lsim(combined_transfer_function, U=signal, T=time, X0=0.0)
output_signal = signal
normalized_output = output_signal
max_value = np.max(np.abs(normalized_output))
if max_value > 0:
    # Multiply by 0.95 to leave a small safety margin (headroom)
    normalized_output = (normalized_output / max_value) * 0.95


plt.plot(time, signal, label="Unfiltered")
plt.plot(time, signal_filtered + signal, label="Filtered")
plt.legend()
plt.savefig("result.png")
sound.play(output_signal)
wavfile.write("output.wav", rate, np.int16(normalized_output * 32767))
