import control
import matplotlib.pyplot as plt

R1 = 22_000 # ohms
R2 = 1000 # ohms
C1 = 10e-6 # farads

system_elliot = control.tf([R2*C1, 1], [R2 * C1, 1 + R1])
system_charlie = control.tf([R1 + R2, 1 / C1], [R2, 1 / C1])

plt.clf()
system_elliot.bode_plot()
plt.title("elliot's system for circuit 1")
plt.savefig("elliot_1.png")

plt.clf()
system_charlie.bode_plot()
plt.title("charlie's system for circuit 1")
plt.savefig("charlie_1.png")