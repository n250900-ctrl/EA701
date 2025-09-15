# micropython_benchmark.py

import time
import os
import gc

def run_micropython_benchmarks():
    """
    Executa os benchmarks para RAM e Flash (Sistema de Arquivos) em MicroPython.
    """
    print("=" * 40)
    print("Iniciando Benchmarks em MicroPython")
    print("=" * 40)

    # --- Teste 1: RAM write (MicroPython) ---
    print("\n--- Teste: RAM write (10 KB, 3 rodadas) ---")
    
    RAM_SIZE = 10 * 1024
    NUM_RUNS_RAM = 3
    ram_times = []
    
    buf = bytearray(RAM_SIZE)
    gc.collect()

    for i in range(NUM_RUNS_RAM):
        t0 = time.ticks_us()
        for j in range(RAM_SIZE):
            buf[j] = j & 0xFF
        t1 = time.ticks_us()
        dt_ms = time.ticks_diff(t1, t0) / 1000
        ram_times.append(dt_ms)
        
    avg_ram = sum(ram_times) / len(ram_times)
    print(f"Tempos (ms): {ram_times}")
    print(f"Média (ms): {avg_ram:.3f}")

    # --- Teste 2: Flash FS write (MicroPython) ---
    print("\n--- Teste: Flash FS write (32 KB, 5 rodadas) ---")

    FS_SIZE = 32 * 1024
    NUM_RUNS_FS = 5
    FILENAME = "fs_benchmark.bin"
    fs_times = []

    payload = bytearray(FS_SIZE)
    gc.collect()

    for i in range(NUM_RUNS_FS):
        try:
            os.remove(FILENAME)
        except OSError:
            pass

        t0 = time.ticks_us()
        with open(FILENAME, "wb") as f:
            f.write(payload)
            f.flush()
        t1 = time.ticks_us()
        dt_ms = time.ticks_diff(t1, t0) / 1000
        fs_times.append(dt_ms)
    
    try:
        os.remove(FILENAME)
    except OSError:
        pass

    avg_fs = sum(fs_times) / len(fs_times)
    print(f"Tempos (ms): {fs_times}")
    print(f"Média (ms): {avg_fs:.3f}")

    print("\n" + "=" * 40)
    print("Benchmarks em MicroPython concluídos.")
    print("=" * 40)

# Para executar, importe este arquivo no REPL.
# Ex: import micropython_benchmark
#     micropython_benchmark.run_micropython_benchmarks()
run_micropython_benchmarks()
