import os
import matplotlib.pyplot as plt
import re
import numpy as np
text = """size: 64, time: 8 adj
size: 128, time: 7 adj
size: 256, time: 7 adj
size: 512, time: 7 adj
size: 1024, time: 8 adj
size: 2048, time: 9 adj
size: 4096, time: 29 adj
size: 8192, time: 40 adj
size: 16384, time: 46 adj
size: 32768, time: 49 adj
size: 65536, time: 50 adj
size: 131072, time: 51 adj
size: 262144, time: 51 adj
size: 524288, time: 52 adj
size: 1048576, time: 52 adj
size: 2097152, time: 52 adj
size: 4194304, time: 52 adj"""

xs = []
ys = []
for line in text.split("\n"):
    _, x, _, y, *_ = line.split()
    x = int(x[:-1])
    y = int(y)
    xs.append(x)
    ys.append(y)

fig = plt.figure(figsize=(8,4))
plt.plot(range(len(xs)), ys)
plt.title("physical memory random access latency")
ax = plt.gca()
ax.set_xticks(range(len(xs)))
ax.set_xticklabels(xs)
plt.xticks(rotation=45)
ax.set_ylabel("cycles")
ax.set_xlabel("64bit words")
fig.tight_layout()
plt.savefig(f"p_ram_random.png")
plt.show()