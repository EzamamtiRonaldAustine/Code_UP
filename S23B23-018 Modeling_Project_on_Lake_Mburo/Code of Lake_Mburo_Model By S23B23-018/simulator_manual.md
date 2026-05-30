# Lake Mburo Trace-Driven Simulator Manual

This simulation models the Entry Gate queueing process of the Lake Mburo National Park during a high-congestion period (Poisson arrivals, multiple service models) over 10,000 entities.

## Scope and Assumptions
- The system is modeled as a single-server FIFO queue.
- Arrivals are Poisson (implemented through exponential inter-arrival traces).
- Each scenario processes exactly 10,000 vehicles.
- Service times follow one of four models: deterministic, exponential, hyper-exponential, or positively correlated exponential.
- Initial state is an idle server with an empty queue at simulation time 0.

## 1. Prerequisites and Compilation
The simulation is executed in a C environment and follows a modular architecture adhering to strict software construction guidelines (encapsulation with opaque pointers, single responsibility).
To compile on a standard terminal with GCC, run the provided build script from the project root:
```bash
./build.bat
```
This will place the executables in the `bin/` directory.

If you don't have the build script, you can compile manually:
```bash
gcc -Iinclude src/trace_generator.c src/sim_config.c src/rvg.c -o bin/trace_generator.exe
gcc -Iinclude src/main.c src/simulator.c src/event_queue.c src/trace_io.c src/statistics.c src/sim_config.c -o bin/mburo_sim.exe
```

## 2. Running the Simulation
Execute the compiled binary from the root directory to process the 16 automated scenarios:
```bash
.\bin\mburo_sim.exe
```

## 3. Configuration 
All parameters and constants (such as total cars `10000`, means, and lambdas) are decoupled from the code logic and can be modified in the `sim_config.h` header file. Avoid "Magic Numbers" by editing everything centrally in that file.

## 4. Key Output Explanations
The simulator tracks waiting delays using Welford's Algorithm and outputs the **Mean Delay** and **Standard Deviation** for each combination.
* You will observe that as $\lambda$ (Arrival Rate) approaches `0.65` (very close to our Service Rate capacity of $1/1.5 = 0.66$), the congestion exponentially spikes.
* **Deterministic Service** produces the lowest delays because predictability eliminates variance-driven traffic jams.
* At high load (for example at $\lambda=0.65$ in the current results), delay growth is substantial across all stochastic models, with the exponential service model producing the largest mean delay in this run.

## 5. Test Environment 
The testing of this simulator was conducted locally on this development environment. It passed compilation using GCC via `build.bat`, and the simulation executable completed all 16 scenarios successfully.

## 6. Known Limitations
- This model represents one booth only; it does not simulate all parallel entry booths.
- Warm-up analysis and confidence intervals are not currently included.
- The correlated service model uses a simple lag-1 dependency mechanism and is intended for comparative sensitivity analysis, not field calibration.
