# -*- coding: utf-8 -*-

import time
import os
import gc

# --- Configurações do Teste ---
FILENAME = "data.bin"
# Altere o tamanho aqui (em KB). Teste com 8, 32, 64, etc.
FILE_SIZE_KB = 32
NUM_RUNS = 5  # Número de rodadas para calcular a média

# Converte KB para bytes
FILE_SIZE_BYTES = FILE_SIZE_KB * 1024

# --- Início do Benchmark ---

print("=" * 40)
print("Iniciando Benchmark de Escrita em Flash")
print(f"Arquivo: '{FILENAME}', Tamanho: {FILE_SIZE_KB} KB, Rodadas: {NUM_RUNS}")
print("=" * 40)

# 1. Gera o bloco de dados (payload) uma única vez
# Fazemos isso fora do loop para não medir o tempo de criação dos dados.
print(f"Gerando payload de {FILE_SIZE_KB} KB na RAM...")
payload = bytearray(FILE_SIZE_BYTES)
# Opcional: preenche com dados para garantir que não seja otimizado
for i in range(FILE_SIZE_BYTES):
    payload[i] = i & 0xFF

# Limpa a memória antes de começar para um resultado mais consistente
gc.collect() 
time.sleep_ms(100)

# --- Teste 1: Escrevendo um arquivo NOVO a cada vez ---
print("\n--- Teste 1: Criando o arquivo a cada escrita ---")
print("Mede o tempo de alocação de blocos + escrita.")

times_create = []
for i in range(NUM_RUNS):
    # Garante que o arquivo seja apagado antes de cada medição
    try:
        os.remove(FILENAME)
    except OSError:
        pass  # Ignora erro se o arquivo não existir na primeira rodada

    # Mede o tempo de open -> write -> flush -> close
    t0 = time.ticks_us()
    with open(FILENAME, "wb") as f:
        f.write(payload)
        f.flush()
        # O 'close' é chamado automaticamente ao sair do bloco 'with'
    t1 = time.ticks_us()
    
    # Calcula e armazena o tempo em milissegundos
    dt_ms = time.ticks_diff(t1, t0) / 1000
    times_create.append(dt_ms)
    print(f"  Rodada {i+1}: {dt_ms:.3f} ms")

# Calcula e exibe a média do Teste 1
avg_create = sum(times_create) / len(times_create)
print(f"-> Média (Criar): {avg_create:.3f} ms")


# --- Teste 2: SOBRESCREVENDO um arquivo existente ---
print("\n--- Teste 2: Sobrescrevendo o arquivo existente ---")
print("Mede o tempo de reescrita em blocos já alocados.")

# O arquivo já existe da última rodada do Teste 1
times_overwrite = []
for i in range(NUM_RUNS):
    # Mede o tempo de open -> write -> flush -> close
    t0 = time.ticks_us()
    with open(FILENAME, "wb") as f: # O modo "wb" já sobrescreve o arquivo
        f.write(payload)
        f.flush()
    t1 = time.ticks_us()
    
    # Calcula e armazena o tempo em milissegundos
    dt_ms = time.ticks_diff(t1, t0) / 1000
    times_overwrite.append(dt_ms)
    print(f"  Rodada {i+1}: {dt_ms:.3f} ms")

# Calcula e exibe a média do Teste 2
avg_overwrite = sum(times_overwrite) / len(times_overwrite)
print(f"-> Média (Sobrescrever): {avg_overwrite:.3f} ms")


# --- Limpeza Final ---
try:
    os.remove(FILENAME)
except OSError:
    pass
print("\nBenchmark concluído.")
print("=" * 40)
