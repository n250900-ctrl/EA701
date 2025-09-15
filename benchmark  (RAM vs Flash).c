#include "pico/stdlib.h"
#include "hardware/flash.h"
#include "hardware/sync.h"
#include <stdio.h>
#include <string.h>

// --- Configurações do Benchmark ---
// ATENÇÃO: Use um offset grande para não sobrescrever seu programa.
// O PICO_BOOT_STAGE2_SIZE_BYTES geralmente define o fim do código.
// Por segurança, usar 1MB de offset é uma boa prática.
#define FLASH_TARGET_OFFSET (1024 * 1024) 
#define NUM_RUNS 5 // Número de rodadas para as médias

// Tamanhos padrão da Flash do Pico (W25Q16JV)
#define SECTOR_SIZE FLASH_SECTOR_SIZE   // 4096 bytes
#define PAGE_SIZE   FLASH_PAGE_SIZE     // 256 bytes

// Buffers para os testes
static uint8_t ram_buf[10 * 1024];
static uint8_t flash_page_buf[PAGE_SIZE];
static uint8_t flash_block_buf[32 * 1024];

// Função para imprimir um array de tempos
void print_times(const char* label, int64_t times[], int n) {
    printf("%s Tempos (ms): [", label);
    double sum = 0;
    for (int i = 0; i < n; i++) {
        double ms = times[i] / 1000.0;
        printf("%.3f%s", ms, (i == n - 1) ? "" : ", ");
        sum += ms;
    }
    printf("], Média: %.3f ms\n", sum / n);
}


int main() {
    stdio_init_all();
    // Pausa longa para garantir que o terminal serial conecte
    sleep_ms(4000); 
    printf("\n--- Iniciando Benchmark de RAM e Flash (Pico SDK) ---\n");

    // Preenche os buffers de dados uma única vez
    for (int i=0; i < sizeof(flash_page_buf); i++) flash_page_buf[i] = i & 0xFF;
    for (int i=0; i < sizeof(flash_block_buf); i++) flash_block_buf[i] = i & 0xFF;

    // --- 1. Medindo escrita em RAM (C) ---
    int64_t ram_times[NUM_RUNS];
    for(int run = 0; run < NUM_RUNS; run++) {
        absolute_time_t t0 = get_absolute_time();
        for (int i = 0; i < sizeof(ram_buf); i++) ram_buf[i] = i & 0xFF;
        absolute_time_t t1 = get_absolute_time();
        ram_times[run] = absolute_time_diff_us(t0, t1);
    }
    print_times("RAM write (10 KB, C):", ram_times, 3); // Usando 3 rodadas conforme planilha


    // --- 2. Medindo Flash ERASE (1 setor) ---
    int64_t erase_times[NUM_RUNS];
    for (int run = 0; run < NUM_RUNS; run++) {
        // Usamos um offset diferente a cada rodada para não desgastar o mesmo setor
        uint32_t offset = FLASH_TARGET_OFFSET + (run * SECTOR_SIZE);
        
        absolute_time_t t0 = get_absolute_time();
        uint32_t ints = save_and_disable_interrupts();
        flash_range_erase(offset, SECTOR_SIZE);
        restore_interrupts(ints);
        absolute_time_t t1 = get_absolute_time();
        erase_times[run] = absolute_time_diff_us(t0, t1);
    }
    print_times("Flash ERASE (4 KB, C):", erase_times, 3); // Usando 3 rodadas


    // --- 3. Medindo Flash PROGRAM (1 página) ---
    int64_t page_prog_times[NUM_RUNS];
    // Primeiro, apaga a área que vamos usar
    uint32_t ints = save_and_disable_interrupts();
    flash_range_erase(FLASH_TARGET_OFFSET, SECTOR_SIZE);
    restore_interrupts(ints);
    
    for (int run = 0; run < NUM_RUNS; run++) {
        absolute_time_t t0 = get_absolute_time();
        ints = save_and_disable_interrupts();
        flash_range_program(FLASH_TARGET_OFFSET, flash_page_buf, PAGE_SIZE);
        restore_interrupts(ints);
        absolute_time_t t1 = get_absolute_time();
        page_prog_times[run] = absolute_time_diff_us(t0, t1);
    }
    print_times("Flash PROGRAM (256 B, C):", page_prog_times, 5); // Usando 5 rodadas


    // --- 4. Medindo Flash PROGRAM (bloco de 32 KB) ---
    const int TOTAL_SIZE = sizeof(flash_block_buf);
    int64_t block_prog_times[NUM_RUNS];
    
    for (int run = 0; run < NUM_RUNS; run++) {
        uint32_t offset = FLASH_TARGET_OFFSET + (run * TOTAL_SIZE);
        
        // Apaga toda a região de 32KB antes de programar
        ints = save_and_disable_interrupts();
        flash_range_erase(offset, TOTAL_SIZE);
        restore_interrupts(ints);

        absolute_time_t t0 = get_absolute_time();
        ints = save_and_disable_interrupts();
        flash_range_program(offset, flash_block_buf, TOTAL_SIZE);
        restore_interrupts(ints);
        absolute_time_t t1 = get_absolute_time();
        block_prog_times[run] = absolute_time_diff_us(t0, t1);
    }
    print_times("Flash PROGRAM (32 KB, C):", block_prog_times, 3); // Usando 3 rodadas

    printf("\n--- Benchmark Concluído ---\n");

    while (1) tight_loop_contents();
}
