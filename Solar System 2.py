import rebound
import numpy as np
import os
import time
from ctypes import CFUNCTYPE, POINTER

AFF = CFUNCTYPE(None, POINTER(rebound.Simulation))

sim = rebound.Simulation()
#sim.start_server(port=1235)

sim.dt = (0.2/365.25) * np.pi * 2.0
tmax   = 20 * np.pi * 2.0
output_interval = 10 * np.pi * 2.0
position_output_interval = sim.dt

sim.integrator = "whfast"
sim.integrator.safe_mode = 0
sim.integrator.corrector = 11
sim.exact_finish_time = 1

body_names = ["Sun","Mercury","Venus","399","499","599","699","799","899","999",
              "301",              # Moon
              "401", "402",       # 
              "501","502","503","504","505","506","514","515","516",   # Jupiter
              "601","602","603","604","605","606","607","608","609","610","611","612","615","616","617", # Saturn's moons
              "701","702","703","704","705",  # Uranus
              "801","803","804","805","806","807","808",  # Neptune
              
              ]

for body in body_names:
    sim.add(body)

sim.move_to_com()
e_init = sim.energy()

for fname in ["energy.txt", "positions.csv"]:
    if os.path.exists(fname):
        os.remove(fname)

with open("positions.csv", "w") as f:
    header = "t," + ",".join(f"{name}_x,{name}_y,{name}_z" for name in body_names)
    f.write(header + "\n")

next_pos_log = 0.0

def heartbeat(sim_pointer):
    global next_pos_log
    sim = sim_pointer.contents
    #time.sleep(0.01)

    if sim.t >= next_pos_log:
        sim.synchronize()
        row = [f"{sim.t:.6f}"]
        for p in sim.particles:
            row.extend([f"{p.x:.8f}", f"{p.y:.8f}", f"{p.z:.8f}"])
        with open("positions.csv", "a") as f:
            f.write(",".join(row) + "\n")
        print(f"t={sim.t:.4f}/{tmax:.2f}")
        next_pos_log += position_output_interval

    if sim.t % output_interval < sim.dt:
        sim.synchronize
        e = sim.energy()
        with open("energy.txt", "ab") as f:
            f.write(f"{sim.t:e} {abs((e - e_init)/e_init):e}\n".encode())

_hb_ref = AFF(heartbeat)
sim._heartbeat = _hb_ref

sim.integrate(tmax)

with open("positions.csv", "a") as f:
    f.write("# Done\n")
