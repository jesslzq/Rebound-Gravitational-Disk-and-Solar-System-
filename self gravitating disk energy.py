import rebound
import numpy as np
import matplotlib.pyplot as plt
sim = rebound.Simulation()
sim.units = ('pc', 'Msun', 'Myr')
sim.start_server(port=1234)
sim.integrator     = "leapfrog"
sim.gravity        = "tree"
sim.boundary       = "open"
sim.opening_angle2 = 0.7
sim.G              = 0.0045
sim.softening      = 30
sim.dt             = 1e-2
boxsize = 80000
sim.root_size = boxsize
disc_mass = 5e10
N = 2500
star_m = 4e6
sim.add(m=star_m)
def random_powerlaw(min_val, max_val, slope):
    y = np.random.uniform(0, 1)
    p = slope + 1
    pow_min = min_val ** p
    pow_max = max_val ** p
    val = pow_min + y * (pow_max - pow_min)
    return val ** (1.0 / p)
slope = -1.7
for i in range(N):
    a   = random_powerlaw(1000, 15000, slope)
    phi = np.random.uniform(0, 2 * np.pi)
    x = a * np.cos(phi)
    y = a * np.sin(phi)
    z = a * np.random.normal(0, 0.001)
    mu   = star_m + disc_mass * (a**(slope) - (1000)**(slope)) / \
                                ((15000)**(slope) - (1000)**(slope))
    vkep = np.sqrt(sim.G * mu / a)
    vx =  vkep * np.sin(phi)
    vy = -vkep * np.cos(phi)
    vz =  0.0
    sim.add(m=disc_mass/N, x=x, y=y, z=z, vx=vx, vy=vy, vz=vz)
from ctypes import CFUNCTYPE, POINTER
AFF = CFUNCTYPE(None, POINTER(rebound.Simulation))
E0 = sim.energy()
times, KE_list, PE_list, E_Total,Virial,E_Diff = [], [], [], [], [],[]
def heartbeat(sim_pointer):
    sim = sim_pointer.contents
    if sim.t % (10.0 * sim.dt) < sim.dt:
        sim.move_to_com() 
        KE = 0.0
        for p in sim.particles:
            KE += 0.5 * p.m * (p.vx**2 + p.vy**2 + p.vz**2)
        E_total = sim.energy()
        PE = E_total - KE
        KKU = 2*KE+PE
        E_difference = sim.energy() - E0
        times.append(sim.t)
        KE_list.append(KE)
        PE_list.append(PE)
        E_Total.append(E_total)
        E_Diff.append(E_difference)
        Virial.append(KKU)
        print(f"t={sim.t:.3f}, N={sim.N}, KE={KE:.4e}, PE={PE:.4e}, E={E_total:.4e}")
_hb_ref = AFF(heartbeat)
sim._heartbeat = _hb_ref
tmax = 20.0   
sim.integrate(tmax)
