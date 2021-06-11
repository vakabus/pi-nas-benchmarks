import seaborn as sns
import pandas as pd
from dateutil import parser
import matplotlib.pyplot as plt
from pathlib import Path
import glob

Path("results").mkdir(exist_ok=True)


colors = (".r", ".g", ".b", ".y")

for i, filename in enumerate(sorted(glob.iglob("data/02-bs-hdd-*.csv"))):
    df = pd.read_csv(filename, sep = ',')
    print(filename)
    print(df)

    plt.plot(df['bs'], df['bw'], colors[i], label=filename)

# these lines add the annotations for the plot. 
plt.legend(loc="lower right")
plt.xscale("log", base=2)
plt.yscale("log", base=10)
plt.ylabel("bytes/s")
plt.xlabel("blocksize")
plt.grid(color='lightgray', linestyle='--', linewidth=0.5)

plt.savefig('results/02-bs.png', dpi=300)

plt.clf()


for i, filename in enumerate(sorted(glob.iglob("data/02-bs-hdd-*.csv"))):
    df = pd.read_csv(filename, sep = ',')
    print(filename)
    print(df)

    plt.plot(df['bs'], df['bw'] / df['bs'], colors[i], label=filename)

# these lines add the annotations for the plot. 
plt.legend(loc="lower right")
plt.xscale("log", base=2)
plt.yscale("log", base=10)
plt.ylabel("throughput / blocksize")
plt.xlabel("blocksize")
plt.grid(color='lightgray', linestyle='--', linewidth=0.5)

plt.savefig('results/02-bs-syscalls.png', dpi=300)


plt.clf()


df = pd.read_csv("data/03-bs-hdd-local.csv", sep = ',')
print(filename)
print(df)

plt.plot(df['bs'], df['bw'], colors[i], label="data/03-bs-hdd-local.csv")

# these lines add the annotations for the plot. 
plt.legend(loc="lower right")
plt.xscale("log", base=2)
plt.yscale("log", base=10)
plt.ylabel("bytes/s")
plt.xlabel("blocksize")
plt.grid(color='lightgray', linestyle='--', linewidth=0.5)

plt.savefig('results/03-bs-local.png', dpi=300)


plt.clf()


df = pd.read_csv("data/04-bs-hdd-local-large.csv", sep = ',')
print(filename)
print(df)

plt.plot(df['bs'], df['bw'], colors[i], label="data/04-bs-hdd-local-large.csv")

# these lines add the annotations for the plot. 
plt.legend(loc="lower right")
plt.xscale("log", base=2)
plt.yscale("log", base=10)
plt.ylabel("bytes/s")
plt.xlabel("blocksize")
plt.grid(color='lightgray', linestyle='--', linewidth=0.5)

plt.savefig('results/04-bs-local-large.png', dpi=300)