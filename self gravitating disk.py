import rebound
import numpy as np
sim = rebound.Simulation()
sim.units=('pc','Msun','Myr')
sim.start_server(port=1234)
sim.integrator     = "leapfrog"
sim.gravity        = "tree"
sim.boundary       = "open"
sim.opening_angle2 = 0.7      # Accuracy of tree code gravity estimate
sim.G              = 0.0045      # Gravitational constant
sim.softening      = 200      # Gravitational softening
sim.dt             = 1e-2     # timestep 
boxsize = 80000     #
sim.root_size = boxsize
#Mass
disc_mass = 5e10       #in solar mass   
N = 2500             # Number of particles
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
# Adding particles
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
from ctypes import CFUNCTYPE, POINTER, c_void_p
AFF = CFUNCTYPE(None, POINTER(rebound.Simulation))
def heartbeat(sim_pointer):
    sim = sim_pointer.contents
    if sim.t % (10.0 * sim.dt) < sim.dt:
        sim.move_to_com()
        print(f"t={sim.t:.3f}, N={sim.N}, dt={sim.dt:.4f}")

        for i in range(3):  # first n particles
            p = sim.particles[i]
            print(f"  particle {i}: x={p.x:.4f}, y={p.y:.4f}, z={p.z:.4f}")

_hb_ref = AFF(heartbeat)   
sim._heartbeat = _hb_ref
# Integrate
sim.integrate(np.inf)
