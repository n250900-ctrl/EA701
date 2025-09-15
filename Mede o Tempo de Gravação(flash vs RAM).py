# -*- coding: utf-8 -*-

from machine import Pin
import time
import os

# --- Funções de Benchmark ---

def benchmark_ram_write():
    """Mede o tempo para escrever dados em um buffer na RAM."""
    N = 128  # Quantidade de bytes para o teste
    buf = bytearray(N)
    
    print(f"Iniciando teste de escrita em RAM ({N} bytes)...")
    
    t0 = time.ticks_us()
    for i in range(N):
        buf[i] = i & 0xFF  # Escreve um byte na RAM
    t1 = time.ticks_us()
    
    dt_ms = time.ticks_diff(t1, t0) / 1000
    print(f"-> Tempo de escrita em RAM: {dt_ms:.4f} ms\n")
    return dt_ms

def benchmark_flash_write():
    """Mede o tempo para escrever dados em um arquivo na Flash."""
    N = 128  # Mesma quantidade de bytes
    data_to_write = bytearray(N)
    for i in range(N):
        data_to_write[i] = i & 0xFF
        
    print(f"Iniciando teste de escrita em FLASH ({N} bytes)...")
    
    # A "escrita segura" envolve criar um arquivo temporário e renomeá-lo.
    # Vamos medir todo esse processo, que é o custo real de uma gravação segura.
    config_file = "benchmark_data.txt"
    temp_file = config_file + ".tmp"

    t0 = time.ticks_us()
    
    # 1. Abre, escreve e fecha o arquivo temporário
    with open(temp_file, "wb") as f: # "wb" para escrever em modo binário
        f.write(data_to_write)
    
    # 2. Renomeia o arquivo (operação atômica)
    os.rename(temp_file, config_file)
    
    t1 = time.ticks_us()
    
    dt_ms = time.ticks_diff(t1, t0) / 1000
    print(f"-> Tempo de escrita em FLASH: {dt_ms:.4f} ms\n")
    
    # Limpeza
    try:
        os.remove(config_file)
    except OSError:
        pass
        
    return dt_ms

# --- Execução ---
if __name__ == "__main__":
    time.sleep(2) # Pausa inicial para conectar o terminal serial

    ram_time_ms = benchmark_ram_write()
    flash_time_ms = benchmark_flash_write()
    
    if ram_time_ms > 0:
        diferenca = flash_time_ms / ram_time_ms
        print(f"Conclusão: A escrita na Flash foi ~{diferenca:.0f} vezes mais lenta que na RAM para este teste.")
    else:
        print("Conclusão: A escrita na RAM foi tão rápida que a diferença é imensa.")
