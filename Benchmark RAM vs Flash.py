# -*- coding: utf-8 -*-

import time
import os
import gc # Garbage Collector, útil para garantir um estado de memória limpo

# --- Funções de Benchmark ---

def benchmark_ram_write(payload_size):
    """Mede o tempo para escrever dados em um buffer na RAM."""
    
    # Prepara os dados (fora da cronometragem)
    buf = bytearray(payload_size)
    
    # Força uma coleta de lixo para um ambiente mais estável
    gc.collect()
    
    # Inicia a medição
    t0 = time.ticks_us()
    for i in range(payload_size):
        buf[i] = i & 0xFF  # Escrita byte a byte na RAM
    t1 = time.ticks_us()
    
    dt_ms = time.ticks_diff(t1, t0) / 1000
    return dt_ms

def perform_flash_write(path, payload):
    """Função auxiliar que realiza uma única operação de escrita na Flash."""
    t0 = time.ticks_us()
    with open(path, "wb") as f:
        f.write(payload)
        # Em muitos sistemas de arquivos de MCUs, o flush() e o close() (implícito no 'with')
        # são as operações que realmente "custam" tempo, pois é quando os dados
        # são enviados para o hardware da Flash.
        f.flush()
    t1 = time.ticks_us()
    return time.ticks_diff(t1, t0) / 1000

def benchmark_flash(payload_size, num_runs=5):
    """
    Mede o tempo de escrita na Flash, comparando a criação de um novo arquivo
    com a sobrescrita de um arquivo existente.
    """
    
    # Gera o bloco de dados para gravar (fora da cronometragem)
    print(f"  Gerando payload de {payload_size // 1024} KB...")
    payload = bytes([i & 0xFF for i in range(payload_size)])
    filepath = "data.bin"
    
    # Força uma coleta de lixo
    gc.collect()

    # --- Teste 1: Criando o arquivo a cada vez ---
    # Isso mede o custo de alocação de blocos + escrita.
    times_create = []
    for _ in range(num_runs):
        try:
            os.remove(filepath) # Garante que o arquivo não existe
        except OSError:
            pass # Ignora o erro se o arquivo não existir na primeira vez
        
        times_create.append(perform_flash_write(filepath, payload))
        time.sleep_ms(10) # Pequena pausa para o sistema de arquivos "respirar"

    # --- Teste 2: Sobrescrevendo o arquivo existente ---
    # O arquivo já existe da última rodada do teste anterior.
    # Mede o custo de encontrar os blocos e reescrevê-los.
    times_overwrite = []
    for _ in range(num_runs):
        times_overwrite.append(perform_flash_write(filepath, payload))
        time.sleep_ms(10)
        
    # Limpeza final
    try:
        os.remove(filepath)
    except OSError:
        pass
        
    # Calcula as médias
    avg_create = sum(times_create) / len(times_create)
    avg_overwrite = sum(times_overwrite) / len(times_overwrite)
    
    return avg_create, avg_overwrite


# --- Execução Principal do Teste ---

if __name__ == "__main__":
    # Pausa para dar tempo de conectar o terminal serial
    time.sleep(2)
    print("Iniciando Benchmark de Escrita RAM vs. Flash...")
    print("-" * 40)
    
    # "Aquecimento" do sistema de arquivos para evitar medir latências iniciais
    with open("warmup.bin", "wb") as f:
        f.write(b'\x00' * 1024)
    os.remove("warmup.bin")

    # Lista de tamanhos para testar (em bytes)
    SIZES_TO_TEST = [8 * 1024, 32 * 1024, 64 * 1024]
    
    for size in SIZES_TO_TEST:
        kb_size = size // 1024
        print(f"\nIniciando testes para {kb_size} KB:")
        
        # 1. Medir escrita em RAM
        ram_time = benchmark_ram_write(size)
        print(f"-> Escrita em RAM: {ram_time:.3f} ms")
        
        # 2. Medir escrita em Flash
        avg_create, avg_overwrite = benchmark_flash(size, num_runs=5)
        print(f"-> Escrita em Flash (Criar): {avg_create:.3f} ms (média de 5)")
        print(f"-> Escrita em Flash (Sobrescrever): {avg_overwrite:.3f} ms (média de 5)")
        print("-" * 20)

    print("\nBenchmark concluído.")
