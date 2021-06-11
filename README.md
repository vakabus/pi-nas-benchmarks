---
geometry: margin=1in
author: Vašek Šraier
title: Pi NAS remote file system throughput
---

# The premise

For a long time, I've been using an old Thinkpad T420 as my home server, however it kept annoying me with its humming fan. Couple months ago I changed to a Raspberry Pi 4B with external boot SSD and a massive heatsink. The Pi is powerfull enough to fulfill pretty much all my needs and it's completely silent. The only thing I hear now is the occasional sound of disk head movement.

However, not everything is as I would like it. The biggest pain point at the moment is limited throughput when accessing files over the network. It's not unusual to see transfer speeds around 20MB/s and I would expect at least four times that much. The T420 was effortlessly able to saturate 1Gbps Ethernet using SSHFS. The Pi can't do that and I don't know why. So let's find out!

# Eliminating variables

## Thermals stress test

It's widely known that the RPi version 4 generates lot of heat. I've installed a massive heatsink covering the whole board and I am convinced that the CPU won't thermal throttle.

To test this hypothesis I want to stress the system and check, that it's not throttling. I've found [this helpful script](https://gist.github.com/geerlingguy/91d4736afe9321cbfc1062165188dda4) written by [Jeff Geerling](https://www.jeffgeerling.com/), which uses `stress-ng` to stress the CPU, while simultaneously logging temperatures.

![Temperature and CPU frequency in time](results/01-throttling.png)

The stress test took 30 minutes and the temperature did not plateau. I am not sure at what temperature would the CPU start to throttle, but I guess it's north of 70°C. In 30 minutes at full gigabit speed, we could transfer roughly 200GB of raw data. That's much more than the usual data size I care about. So let's say, the CPU never throttles and ignore CPU temperatures from now on. They are not the problem. I just need to make sure that the benchmarks are shorter than 30 minutes.

## Raw network speed

Another problem might be in between the Pi and the client, my laptop. I tried launching `netcat` and monitoring the speed with `nload` (in both cases on my laptop, not on the Pi). I used these commands:

```
netcat $ip 8888 < /dev/zero
ncat -l 8888 > /dev/null
```

When the Pi was the sender, I observed 700Mbps traffic. In the other direction, my laptop was able to send 900Mbps to the Pi. With two parallel connection, the did not observe any change. I tested the same with `iperf3` and the results matched. For some reason, the Pi is slow in one direction. That's unexpected...

To find out why, I looked at the CPU load. Nothing, the Pi's CPU was pretty much idling. I tried unplugging the network cables from a 5-port gigabit switch that's in between my laptop and the Pi. And I saw a change! The speed raised to 940Mbps and it slowly decreased until it reached 700Mbps again. Weird. At least it confirms that the Pi is capable of full gigabit. After some more playing with hardware I found the problem. My laptop was the slow one, not the Pi. It was connected to the network using a Thunderbolt 3 dock and that was causing the slowdown. Connected directly, data flowed in both directions perfectly with a speed of 940Mbps.

Ok, we now know that the Pi is capable of saturating a gigabit network connection with dummy data and that there is roughly a 30% loss in performance due to my Thunderbolt dock.

## Disk performance

The Pi is connected to two disks over a single USB3 connection. One is an SSD with the system partition, second is the 4TB data HDD. In this test, I would like to check that the disks have enough througput to saturate the gigabit line. For that test, I've decided to use the [Flexible I/O Tester](https://github.com/axboe/fio), `fio` for short. `fio` is a really powerfull testing tool and I don't really know it that well, but pretty basic usage should suffice for this rough test. I've manually played with the parameters to get the most bandwidth with direct I/O. I ended up with these test:

```
# sequential write test reporting 115MiB/s (120MB/s)
> fio --rw=write --size=4g --time_based --directory=test --name=test --bs=64k \
  --numjobs=1 --runtime=30 --ramp_time=5 --iodepth=128 --direct=1 \
  --ioengine=aiolib

# sequential read test reporting 83.6MiB/s (87.7MB/s)
> fio --rw=read --size=4g --time_based --directory=test --name=test --bs=64k \
  --numjobs=4 --runtime=30 --ramp_time=5 --iodepth=32 --direct=1 \
  --ioengine=aiolib
```

The sequential read test is however quite unstable. The speed jumps from 45MiB/s to 96MiB/s and the aggregate result can be anywhere in between. From what I understand, this behavior can be caused by different speeds on different parts of the disk platter. The outer rim of the platter has the same density as the data in the inner rim. Therefore, the read/write head moves faster over the data in the outer rim.

## Conclusion

The bottlenecks we have found so far are the following:

* The network can not go faster than 940Mbps (117.5MiB/s)
* Maximum expected disk read speed is roughly 85MiB/s
* Maximum expected disk write speed is roughly 115MiB/s

The disk is not able to saturate gigabit Ethernet at all times. However, the performance is pretty close.

# Benchmarking remote file accesses

## How

For the actual test, I will mount the same directory in the remote filesystem using different technologies, measure it's performance using the `fio` testing tool and compare it to the same test running locally. Before every command, I will clean the OS caches using `echo 3 > /proc/sys/vm/drop_caches`.

This is the read test command:

```
fio --rw=read --size=4g --time_based --directory=test --name=test --bs=64k \
  --numjobs=1 --runtime=30 --ramp_time=5 --iodepth=32 --direct=1 \
  --ioengine=aiolib
```

And this is the write test command:

```
fio --rw=write --size=4g --time_based --directory=test --name=test --bs=64k \
  --numjobs=4 --runtime=30 --ramp_time=5 --iodepth=32 --direct=1 \
  --ioengine=aiolib
```

The connection will be made over the gigabit ethernet cable without the TB3 dock in between, so that we are not limited to 700Mbps but have the full potential of 1Gbps. The Pi is therefore directly connected to the same switch as the laptop.

## Results

| access method | read bw   | write bw  |
|---------------|-----------|-----------|
| local         | 85.6MiB/s | 102MiB/s  |
| gvfs-smb      | 13.9MiB/s | err: `Operation not supported`|
| sshfs         | 56.3MiB/s | 56.3MiB/s |
| cifs          | 90.2MiB/s | 94.2MiB/s |

Note: GVFS write test didn't fail due to the mount being read-only. It's definitely read-write. Probably `fio` is using some features that the FUSE driver does not support.

## Conclusion

The results are speaking for themselves. There are several takeaways:

* The performance problem were not a direct consequence of switching to a different server hardware, but rather the result of reinstalling the OS and properly configuring autodiscovery so that GVFS works.
* SSHFS is significantly slower than CIFS. Previously on the T420, I was using SSHFS and I was able to achieve similar speeds as we see now with CIFS. The current hypothesis being that SSHFS is CPU-bound.

So, in order to make the Pi NAS faster, I should fix my laptop's software. The Pi itself is fine... :)


# One additional experiment with block size

When playing with `fio`, I had to choose several parameters describing access patterns. One of them was block size - a rather innocent looking option with a huge impact. I tried to find an "optimum" manually and then used it everywhere. However, the optimum might be diffent for local and remote accesses. So let's try to measure it's impact! :)

## Methodology

I used this `fio` configuration and changed only the block size option to collect data.

```
fio --rw=read --size=4g --time_based --directory=test --name=test --bs={bs} \
  --numjobs=1 --runtime={runtime} --ramp_time=2 --iodepth=32 --direct=1 \
  --ioengine=aiolib
```

# Results

![block size impact](results/02-bs.png)

The data can be found in the `data` directory.

# Observations and hypothesis

When the block size is small, the throughput is limited by a fixed maximum number of messages passed between the disk and the testing program. This can be caused by context switch overhead, disk communication protocol limitations or something similar. The behaviour can be more clearly demonstrated using slightly modified plot with the same data.

![number of syscalls](results/02-bs-syscalls.png)

For some reason, CIFS achieves larger througput than pure local access. This can be probably attributed to the other fixed `fio` options. Accessing the disk remotely involves more caches in between the program and the disk. The access pattern can be then a bit different and lead to higher throughput. I think that we can't draw any definitive conclusions from the data we have as it won't generalise. This behavior can be observed only in systems where the disk speed is slower than the network speed and that varies a lot.

Connected to this is the interesting effect of powers of two in local accesses to the disk. I performed another experiment with more detailed steps and the effect remains. I would have expected a plot with stairs pattern or similar. However, I have no simple explanation for this behavior.

![powers of two](results/03-bs-local.png)

One more thing - the througput did not plateu. I did not expect that and so here is another plot with even larger block sizes. The plot contains multiple measurement sequences or merged together to see the context better.

![larger block sizes](results/04-bs-local-large.png)

# Conclusion

The best block size seems to be around 4MiB, 8MiB or 16MiB. However, I don't know if this generalizes and I can't assume so due to quite a few specifics in the tests.

One major takeaway for me is that streaming data from one place to another is not simple. There are lot of buffers in between and setting their size properly can have significant effect on the perfomance. In this case, block sizes of powers of two have roughly 30% larger throughput. That's definitely not insignificant.




