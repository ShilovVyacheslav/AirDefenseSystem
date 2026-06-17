<div style="text-align: center;">
  <pre style="color: #cc0000; display: inline-block; text-align: left;">
 █████╗    ██████╗    ███████╗
██╔══██╗   ██╔══██╗   ██╔════╝
███████║   ██║  ██║   ███████╗
██╔══██║   ██║  ██║   ╚════██║
██║  ██║██╗██████╔╝██╗███████║██╗
╚═╝  ╚═╝╚═╝╚═════╝ ╚═╝╚══════╝╚═╝
  </pre>

# AIR DEFENSE SYSTEM

**Optimal-pursuit interception simulator for unmanned aerial vehicles**

![Python](https://img.shields.io/badge/python-3.11+-blue?style=flat-square&logo=python&logoColor=white)
![Numba](https://img.shields.io/badge/JIT-Numba-orange?style=flat-square)
![Pygame](https://img.shields.io/badge/render-pygame-green?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-red?style=flat-square)

*Real-time simulation of guaranteed-capture pursuit strategies, built on*
*closed-form analytical models of optimal interception under uncertainty.*

</div>

---

## ▏OVERVIEW

**A.D.S.** simulates how a swarm of interceptors hunts down a swarm of evading drones
when the targets' parameters are only partially known. Each interceptor must
**guarantee** capture despite uncertainty about a target's speed, heading, or
starting position — and the system assigns interceptors to targets so that the
**slowest interception in the whole operation is as fast as possible** (bottleneck 
assignment problem).

---

## ▏INTERCEPTION MODELS

Three strategies, each defeating a different class of uncertainty.

<table>
<tr>
<td width="33%" valign="top">

### ◢ SPIRAL
**Unknown heading**

Speed known to a finite set, direction unknown. The interceptor runs a straight
leg, then a **logarithmic spiral** matching the target's radial distance —
sweeping every possible heading. Capture guaranteed within one revolution.

</td>
<td width="33%" valign="top">

### ◢ CIRCULAR
**Unknown everything**

Only a *circle* of possible starts, plus finite speed and heading sets. Reduces to
a differential equation solved through **incomplete elliptic integrals of the
second kind**. The hardest case.

</td>
<td width="33%" valign="top">

### ◢ TARGETING
**Pure pursuit**

The velocity vector points permanently at a target crossing at constant altitude.
The classic pursuit curve — closed-form trajectory and time-to-capture.

</td>
</tr>
</table>

---

## ▏MULTI-TARGET ASSIGNMENT

> **n** interceptors, **n** targets. **Which hunts which?**

A.D.S. solves the **bottleneck assignment problem** — minimize the maximum
interception time across all pairs. It binary-searches a threshold, builds 
a bipartite graph of pairs reachable within the threshold, and tests for a 
**perfect matching** via **Hopcroft–Karp**.

---

## ▏WHAT MAKES IT DIFFERENT

```
  ▸ ANALYTICAL      positions from closed-form solutions, not numerical
                    integration — zero accumulating drift
  ▸ GUARANTEED      strategies are provably complete: every admissible
                    target is caught, not merely chased
  ▸ OPTIMAL         true minimax bottleneck assignment, not greedy heuristics
  ▸ FAST            elliptic-integral hot path JIT-compiled with Numba,
                    backed by a precomputed lookup table
  ▸ LAYERED         pursuit math isolated from rendering and I/O across
                    compute / domain / ui / loaders
```

---

## ▏INSTALL

> **Requires Python 3.11+**

1.  **Clone the repository**
    ```bash
    git clone https://github.com/ShilovVyacheslav/AirDefenseSystem.git
    cd AirDefenseSystem
    ```
    
2.  **Create and activate virtual environment**

    **Windows:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
    **Linux / macOS:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ``` 
    
3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ``` 
    
4.  **Install the package**
    ```bash
    pip install -e .
    ``` 
    
5.  **Run the simulation**
    ```bash
    ads --help
    ``` 

---

## ▏DEPLOY

```bash
ads                                          # single spiral pursuit
ads -m multiple_circular -r -c 50            # 50-on-50 elliptic scan + matrix
ads -m multiple_spiral -r -c 100 --no-preview # 100-craft swarm, skip intro
ads -s scenarios/demo.yaml                   # hand-authored scenario
ads -m multiple_targeting -r -c 30 --respawn # endless waves
ads --scenario-info                          # scenario format reference
```

<details>
<summary><b>All flags</b></summary>

<br>

| Flag | Description |
|------|-------------|
| `-m, --mode MODE` | `single`/`multiple` × `spiral`/`circular`/`targeting` |
| `-r, --random` | Procedural random world |
| `-c, --count N` | Entity count for `multiple` modes |
| `-s, --scenario PATH` | Load world from a `.yaml`/`.json` file |
| `--respawn` | Auto-respawn a wave after every wipe |
| `--no-matrix` | Disable the pursuit-matrix overlay |
| `--no-preview` | Skip the boot sequence |
| `--scenario-info` | Print scenario format reference and exit |
| `-h, --help` | Usage and exit |

**World source is exclusive** — `--scenario` *or* `--random` *or* neither (loads
the mode default). `--mode` / `--count` / `--random` cannot combine with
`--scenario`: the file owns the mode and count.

</details>

<details>
<summary><b>In-sim controls</b></summary>

<br>

| Input | Action |
|-------|--------|
| `1`–`6` | Switch interception mode |
| `M` | Toggle pursuit-matrix overlay |
| `Arrows` | Scroll the matrix |
| `RMB` drag · `Scroll` · `Space` | Pan · Zoom · Recenter |

</details>

<details>
<summary><b>Scenario file format</b></summary>

<br>

YAML or JSON. Fields accept human names or the mathematical symbols from the
derivations (`speed`/`V_P`, `center`/`C_0`, `radius`/`D_0`, `angles`/`A_E`).
Inputs are validated for type, positivity, and speed feasibility before launch.

```yaml
mode: spiral
predators:
  - id: P1
    pos: [13.56, 18.91]
    speed: 18.34
evaders:
  - id: E1
    pos: [15.81, 4.84]
    speeds: [1.68, 2.91, 3.34]
```

</details>

---

## ▏ARCHITECTURE

```
src/
  cli.py          ▏ command-line interface, argument validation
  compute/        ▏ pursuit mathematics
    interception/ ▏   spiral · circular · targeting solvers
    ellipe/       ▏   elliptic-integral LUT + numba kernels
  domain/         ▏ entities · motion · assignment · setups
  loaders/        ▏ scenario parsing + schema validation
  ui/             ▏ tactical HUD · grid · overlays · boot
  core/           ▏ simulation loop · camera · input · render
  config/         ▏ settings · theme · fonts
scenarios/        ▏ default + example worlds
```

---

## ▏FOUNDATION

Implements the models from the undergraduate thesis *"On methods of optimal
pursuit of unmanned aerial vehicles"* (Applied Mathematics & Computer Science),
which derives the analytical trajectories, interception times, and the bottleneck
assignment algorithm. This project makes that mathematics interactive.
