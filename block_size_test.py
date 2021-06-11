from pathlib import Path
import subprocess
import csv

def fio(dir: Path, bs: int, iodepth: int = 32, direct: bool = True, runtime: int = 15) -> float:
    cmd = f"fio --rw=read --size=4g --time_based --directory={str(dir)} --name=test --bs={bs} --numjobs=1 --runtime={runtime} --ramp_time=2 --iodepth={iodepth} --direct={int(direct)} --ioengine=aiolib"
    proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    bw = proc.stdout.splitlines()[-1].decode("utf8").strip().split(" ")[1]
    assert bw.startswith("bw=")
    spd, units = bw[3:-5], bw[-5]
    if units not in ('K', 'M'):
        spd = bw[3:-3]
        units = ''
    return float(spd) * {'K': 1024, 'M': 1024*1024, '': 1}[units]

def measure(dir: Path):
    fio(dir, 1*1024*1024, direct=False) # this creates the test data and it does not take ages
    print(dir)
    with open(f"data-{dir.name}.csv", 'w') as f:
        fieldnames = ['bs', 'bw']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(1, 23*5):
            print(i, 23*5)
            exponent = i / 5
            bs = int(2**exponent)
            writer.writerow({"bs": bs, "bw": fio(dir, bs, direct=True)})


#measure(Path("/mnt/cifs"))
#measure(Path("/mnt/sshfs"))
measure(Path("/mnt/biggadisk/vasek"))