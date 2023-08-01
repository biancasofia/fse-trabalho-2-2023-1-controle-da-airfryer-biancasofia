
import datetime

def seta_lcd_manual(self):
        self.lcd.clear()
        if self.esquentando.is_set():
            self.lcd.text(f'TI:{round(self.tempe_interna_air, 2)} TR:{round(self.tempe_referencia_air, 2)}', 1)
            self.lcd.text(f'pre aquecendo...', 2)
        elif self.resfriando.is_set():
            self.lcd.text(f'TI:{round(self.tempe_interna_air, 2)} TR:{round(self.tempe_referencia_air, 2)}', 1)
            self.lcd.text(f'resfriando...', 2)
        else:
            self.lcd.text(f'TI:{round(self.tempe_interna_air, 2)} TR:{round(self.tempe_referencia_air, 2)}', 1)
            self.lcd.text(f'Tempo: {str(datetime.timedelta(seconds=self.temp_segundos))}', 2)
            
def seta_lcd_automatico(self):
    self.lcd.clear()
    if self.sorteou_alimento.is_set():
        self.lcd.text(f'Comida:{self.alimento} ',1)
        self.lcd.text(f'Temp:{round(self.tempe_interna_air, 2)} Tempo:{round(self.tempe_referencia_air, 2)}',2)
        self.sorteou_alimento.clear()
    elif self.esquentando.is_set():
        self.lcd.text(f'TI:{round(self.tempe_interna_air, 2)} TR:{round(self.tempe_referencia_air, 2)}', 1)
        self.lcd.text(f'pre aquecendo...', 2)
    elif self.resfriando.is_set():
        self.lcd.text(f'TI:{round(self.tempe_interna_air, 2)} TR:{round(self.tempe_referencia_air, 2)}', 1)
        self.lcd.text(f'resfriando...', 2)
    else:
        self.lcd.text(f':{round(self.tempe_interna_air, 2)} TR:{round(self.tempe_referencia_air, 2)}', 1)
        self.lcd.text(f'Tempo: {str(datetime.timedelta(seconds=self.temp_segundos))}', 2)