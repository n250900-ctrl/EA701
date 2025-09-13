import time
import machine



from ssd1306 import SSD1306_I2C


# ======================================================================
# --- CONFIGURAÇÃO DO EXPERIMENTO ---
# ======================================================================
# Pinos
PINO_SAIDA_PWM = 0
PINO_ENTRADA_ADC = 28
PINO_SDA = 2
PINO_SCL = 3
I2C_BUS = 1


# --- Documentação e Parâmetros do Filtro ---
# Frequência do PWM: Escolhemos uma frequência alta, muito maior que a de corte (fc),
# para minimizar o ripple na saída do filtro.
# fc ≈ 1 / (2 * pi * 10kΩ * 100nF) ≈ 159 Hz
PWM_FREQ = 20000  # 20 kHz (Documente este valor!)


# Constante de tempo do filtro (Tau = R * C)
R_FILTRO = 10000  # 10 kOhms
C_FILTRO = 100e-9 # 100 nF (0.0000001 F)
CONSTANTE_DE_TEMPO_MS = (R_FILTRO * C_FILTRO) * 1000 # Tau em milissegundos
# Tempo de espera para o filtro estabilizar (5 * Tau)
DELAY_ESTABILIZACAO_MS = int(CONSTANTE_DE_TEMPO_MS * 5)


# Parâmetros da Medição
AMOSTRAS_PARA_MEDIA = 100 # Número de leituras do ADC para tirar a média


# ======================================================================


# --- INICIALIZAÇÃO ---
i2c = machine.I2C(I2C_BUS, sda=machine.Pin(PINO_SDA), scl=machine.Pin(PINO_SCL), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)
adc_medida = machine.ADC(machine.Pin(PINO_ENTRADA_ADC))
pwm_out = machine.PWM(machine.Pin(PINO_SAIDA_PWM))
pwm_out.freq(PWM_FREQ)


print("--- Iniciando Caracterizacao do Filtro RC ---")
print(f"Frequencia PWM: {PWM_FREQ/1000} kHz")
print(f"Delay de estabilizacao: {DELAY_ESTABILIZACAO_MS} ms")
print("\nCopie a tabela abaixo para a sua planilha:")
# Cabeçalho da tabela para a planilha
print("Duty_Cycle(%);Tensao_Esperada(V);Tensao_Medida(V)")


# --- LOOP PRINCIPAL DO EXPERIMENTO ---
for duty_percent in range(0, 101, 10):
   
    # 1. ATUALIZA O PWM E O DISPLAY
    oled.fill(0)
    oled.text("Analisando...", 0, 0)
    oled.text(f"Duty: {duty_percent} %", 0, 20)
    oled.show()
   
    duty_u16 = int((duty_percent / 100) * 65535)
    pwm_out.duty_u16(duty_u16)
   
    # 2. AGUARDA A ESTABILIZAÇÃO DO FILTRO RC
    time.sleep_ms(DELAY_ESTABILIZACAO_MS)
   
    # 3. FAZ MÚLTIPLAS LEITURAS E CALCULA A MÉDIA
    leituras = []
    for _ in range(AMOSTRAS_PARA_MEDIA):
        leituras.append(adc_medida.read_u16())
        time.sleep_us(100) # Pequena pausa entre leituras
       
    media_16bit = sum(leituras) / len(leituras)
    valor_medido_12bit = int(media_16bit) >> 4
   
    # 4. CALCULA AS TENSÕES
    tensao_esperada = (duty_percent / 100.0) * 3.3
    tensao_medida = (valor_medido_12bit / 4095.0) * 3.3
   
    # 5. ATUALIZA O DISPLAY COM O RESULTADO FINAL
    oled.text("Resultado:", 0, 35)
    oled.text(f"Med: {tensao_medida:.3f} V", 0, 50)
    oled.show()
   
    # 6. IMPRIME OS DADOS PARA A PLANILHA
    # Usamos ponto como separador decimal e ponto e vírgula como separador de coluna
    print(f"{duty_percent};{tensao_esperada:.4f};{tensao_medida:.4f}")
   
    # Pausa para o usuário poder ver o resultado no OLED antes do próximo passo
    time.sleep_ms(2000)


# Final do experimento
oled.fill(0)
oled.text("Experimento", 0, 20)
oled.text("Finalizado!", 0, 30)
oled.show()
print("\n--- Fim do experimento ---")
