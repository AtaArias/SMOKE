import matplotlib.pyplot as plt
import numpy as np

# Enable LaTeX rendering with siunitx
plt.rcParams.update({
    "text.usetex": True,
    "text.latex.preamble": r"\usepackage{siunitx}" + "\n" + r"\usepackage[T1]{fontenc}",
    "font.family": "serif",
    "font.serif":["Computer Modern"]
})
espesor = np.array([
    15.8, 24, 55.3, 158
]) #nm

campos = np.array([
    0.003554336523998637,
    0.0038977443213988796,
    0.0044846759042631665,
    0.02588142657301067
])

error_campos = np.array([
    9.969860586666022e-05,
    7.907009019012686e-05,
    0.0003938963663879719,
    9.969860586666022e-05
])

plt.grid(True, linestyle='--', alpha=0.8)
plt.errorbar(espesor, campos / 2, error_campos / 2, marker = 'o')
plt.tick_params(axis="both", direction = "in")
plt.xticks(fontsize = 13)
plt.yticks(fontsize = 13)
plt.xlabel('Espesor $[\\si{nm}]$', fontsize = 15)
plt.ylabel('B $[\\si{T}]$', fontsize = 15)
plt.xlim(-5, 161)
plt.ylim(-0.001, 0.0141)
plt.tight_layout()
plt.savefig('campo_coercitivo_vs_espesor.png')
plt.show()