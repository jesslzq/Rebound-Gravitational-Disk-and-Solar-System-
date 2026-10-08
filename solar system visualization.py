import rebound
import numpy as np
import os
import time
from ctypes import CFUNCTYPE, POINTER
AFF = CFUNCTYPE(None, POINTER(rebound.Simulation))



sim = rebound.Simulation()
sim.start_server(port=1235)

sim.dt = (0.2/365.25) * np.pi * 2.0      
tmax   = 20 * np.pi * 2.0       
output_interval = 10 * np.pi * 2.0

sim.integrator = "whfast"
sim.integrator.safe_mode = 0
sim.integrator.corrector = 11
sim.exact_finish_time = 1

body_names = ["Sun", "Mercury", "Venus", "399", "499",
              "599", "699", "799", "899"]

for body in body_names:
    sim.add(body)

sim.move_to_com()
E0 = sim.energy()

if os.path.exists("energy.txt"):
    os.remove("energy.txt")

def heartbeat(sim_pointer):
    sim = sim_pointer.contents
    time.sleep(0.01)
    if sim.t % output_interval < sim.dt:
        sim.synchronize()
        e = sim.energy()
        with open("energy.txt", "ab") as f:
            f.write(f"{sim.t:e} {abs((e - E0)/E0):e}\n".encode())
        print(f"t={sim.t:.2f} / {tmax:.2f}")

_hb_ref = AFF(heartbeat)     
sim._heartbeat = _hb_ref     

sim.integrate(tmax)

