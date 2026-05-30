@echo off
echo Building Lake Mburo Trace-Driven Simulator...

REM Build the trace generator
gcc -Iinclude src/trace_generator.c src/sim_config.c src/rvg.c -o bin/trace_generator.exe
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to compile trace_generator!
    exit /b %ERRORLEVEL%
)
echo [SUCCESS] trace_generator.exe compiled successfully in bin/

REM Build the main simulation engine
gcc -Iinclude src/main.c src/simulator.c src/event_queue.c src/trace_io.c src/statistics.c src/sim_config.c -o bin/mburo_sim.exe
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to compile mburo_sim!
    exit /b %ERRORLEVEL%
)
echo [SUCCESS] mburo_sim.exe compiled successfully in bin/

echo All builds complete!
echo To run the trace generator: .\bin\trace_generator.exe
echo To run the simulation:      .\bin\mburo_sim.exe
