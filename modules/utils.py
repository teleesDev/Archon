def formatar_telefone(entry, event=None):
    if event and event.keysym == "BackSpace": return
    texto = entry.get()
    numeros = "".join(filter(str.isdigit, texto))[:11] 
    resultado = ""
    if len(numeros) > 0:
        if len(numeros) <= 2: resultado = f"({numeros}"
        elif len(numeros) <= 6: resultado = f"({numeros[:2]}) {numeros[2:]}"
        elif len(numeros) <= 10: resultado = f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
        else: resultado = f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    if texto != resultado:
        entry.delete(0, 'end')
        entry.insert(0, resultado)

def formatar_cpf(entry, event=None):
    if event and event.keysym == "BackSpace": return
    texto = entry.get()
    numeros = "".join(filter(str.isdigit, texto))[:11] 
    resultado = ""
    if len(numeros) > 0: resultado += numeros[:3]
    if len(numeros) > 3: resultado += "." + numeros[3:6]
    if len(numeros) > 6: resultado += "." + numeros[6:9]
    if len(numeros) > 9: resultado += "-" + numeros[9:]
    if texto != resultado:
        entry.delete(0, 'end')
        entry.insert(0, resultado)

def formatar_cnpj(entry, event=None):
    if event and event.keysym == "BackSpace": return
    texto = entry.get()
    numeros = "".join(filter(str.isdigit, texto))[:14] 
    resultado = ""
    if len(numeros) > 0: resultado += numeros[:2]
    if len(numeros) > 2: resultado += "." + numeros[2:5]
    if len(numeros) > 5: resultado += "." + numeros[5:8]
    if len(numeros) > 8: resultado += "/" + numeros[8:12]
    if len(numeros) > 12: resultado += "-" + numeros[12:]
    if texto != resultado:
        entry.delete(0, 'end')
        entry.insert(0, resultado)

def formatar_rg(entry, event=None):
    if event and event.keysym == "BackSpace": return
    texto = entry.get()
    numeros = "".join(filter(str.isdigit, texto))[:9]
    resultado = ""
    if len(numeros) > 0: resultado += numeros[:2]
    if len(numeros) > 2: resultado += "." + numeros[2:5]
    if len(numeros) > 5: resultado += "." + numeros[5:8]
    if len(numeros) > 8: resultado += "-" + numeros[8:]
    if texto != resultado:
        entry.delete(0, 'end')
        entry.insert(0, resultado)

def formatar_cnj(entry, event=None):
    if event and event.keysym == "BackSpace": return
    texto = entry.get()
    numeros = "".join(filter(str.isdigit, texto))[:20] # CNJ tem exatos 20 números
    resultado = ""
    if len(numeros) > 0: resultado += numeros[:7]
    if len(numeros) > 7: resultado += "-" + numeros[7:9]
    if len(numeros) > 9: resultado += "." + numeros[9:13]
    if len(numeros) > 13: resultado += "." + numeros[13:14]
    if len(numeros) > 14: resultado += "." + numeros[14:16]
    if len(numeros) > 16: resultado += "." + numeros[16:20]
    if texto != resultado:
        entry.delete(0, 'end')
        entry.insert(0, resultado)

def formatar_data(entry, event=None):
    if event and event.keysym == "BackSpace": return
    texto = entry.get()
    numeros = "".join(filter(str.isdigit, texto))[:8]
    
    # 🟢 BLOQUEIOS DE DATA REAL
    if len(numeros) >= 2:
        dia = int(numeros[:2])
        if dia > 31: dia = 31
        elif dia == 0 and len(numeros) >= 2: dia = 1
        numeros = f"{dia:02d}" + numeros[2:]
        
    if len(numeros) >= 4:
        mes = int(numeros[2:4])
        if mes > 12: mes = 12
        elif mes == 0 and len(numeros) >= 4: mes = 1
        # Ajuste de dias limites por mês
        dia = int(numeros[:2])
        if mes in [4, 6, 9, 11] and dia > 30: dia = 30
        elif mes == 2 and dia > 29: dia = 29
        numeros = f"{dia:02d}{mes:02d}" + numeros[4:]
        
    if len(numeros) == 8:
        ano = int(numeros[4:8])
        if ano > 2030: ano = 2030 # Limita o ano máximo
        elif ano < 2000: ano = 2000
        numeros = numeros[:4] + f"{ano:04d}"

    resultado = ""
    for i in range(len(numeros)):
        if i == 2 or i == 4: resultado += "/"
        resultado += numeros[i]
        
    if texto != resultado:
        entry.delete(0, 'end')
        entry.insert(0, resultado)