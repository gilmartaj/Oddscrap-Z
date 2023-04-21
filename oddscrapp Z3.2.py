#!/usr/bin/env python

# coding: utf-8

from datetime import date, timedelta
from getopt import getopt
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from sys import argv
from time import sleep, time
import pandas as pd

def apagar_linhas(numero_linhas):
    print(f"{esc}[{numero_linhas}A\r{esc}[0J", end="")
    
def segundos_para_tempo_formatado(segundos):
    horas = segundos // 3600;
    segundos = segundos - horas * 3600
    minutos = segundos // 60
    segundos = segundos - minutos * 60
    return "{:0>2}h {:0>2}m {:0>2}s".format(horas, minutos, segundos)

print("Inicializando...")
tempo_inicio = time()
optlist, args = getopt(argv[1:], 'd:n:xot:h:')

dias = 1
nome_inicial_arquivo = "jogos"
extensao = ".xls"
gerar_arquivo_ordenado = False
tempo_parada = 0
horario_inicial = None

for opcao, valor in optlist:
    try:
        if opcao == "-d":
            dias = int(valor)
        if opcao == "-n":
            nome_inicial_arquivo = valor
        if opcao == "-x":
            extensao += "x"
        if opcao == "-o":
            gerar_arquivo_ordenado = True
        if opcao == "-t":
            tempo_parada = float(valor)
        if opcao == "-h":
            horario_inicial = int(valor)
    except:
        if opcao == "-d":
            print("Erro: -d precisa ser um inteiro entre -7 e 7")                 

data = date.today() + timedelta(days = dias)
nome_arquivo = f"{nome_inicial_arquivo}_{data.year:04d}_{data.month:02d}_{data.day:02d}"

esc = "\x1b"
linhas_apagar = 1

options = Options()
options.headless = True
driver = webdriver.Firefox(executable_path='./geckodriver', options = options)

driver.implicitly_wait(10)

apagar_linhas(1)
print("Inicializando... Ok")
print("Carregando a página...")
driver.get("https://www.flashscore.com.br")
apagar_linhas(1)
print("Carregando a página... Ok")

print("Ajustando a data...")
for i in range(0, abs(dias)):
    if dias > 0:
        #driver.find_element_by_class_name("calendar__direction--tomorrow").click()
        driver.execute_script("arguments[0].click();", driver.find_element_by_class_name("calendar__navigation--tomorrow"))
    else:
        driver.find_element_by_class_name("calendar__navigation--yesterday").click()
apagar_linhas(1)
print("Ajustando a data... Ok")

print("Carregando aba de odds...")
#driver.find_elements_by_class_name("tabs__tab")[2].click()
driver.execute_script("arguments[0].click();", driver.find_elements_by_class_name("filters__tab")[2])
apagar_linhas(1)
sleep(10)
print("Carregando aba de odds... Ok")

print("Verificando a página...")
camp = driver.find_elements_by_css_selector(".event__expanderBlock")
camp_len = len(camp)
apagar_linhas(1)
print("Verificando a página... Ok")

print("Preparando a página...")

for i, e in enumerate(camp):
    if e.get_property("title") == "Exibir todos os jogos desta competição!":
        driver.execute_script("arguments[0].click();", e)
        apagar_linhas(1)
        print("Preparando a página... %.2f%%" % (i*100 / camp_len))
apagar_linhas(1)
print("Preparando a página... Ok\n")

elements = driver.find_elements_by_class_name("event__match")
janela_principal = driver.window_handles[0]
jogos = []
h1 = []
h2 = []
dif = []
dif3 = []
odd1 = []
odd2 = []
odd3 = []
camps = []
horarios = []
result = []

print("Número de jogos: ", len(elements), "\n")

elements_len = len(elements)

for i, e in enumerate(elements):
    print("Jogo %d / %d (%.2f%%)" % (i+1, elements_len, i*100 / elements_len))

    if horario_inicial != None:
        horario_jogo = 0;
        horario_jogo = e.find_element_by_css_selector(".event__time,.event__stage").text.strip()
        if len(horario_jogo) != 5 or int(horario_jogo[0:2]) < horario_inicial:
            print("Jogo fora do escopo de horário definido.\n")
            continue

    o1 = e.find_element_by_class_name("event__odd--odd1").text
    o2 = e.find_element_by_class_name("event__odd--odd2").text      
    o3 = e.find_element_by_class_name("event__odd--odd3").text

    driver.execute_script("arguments[0].click();", e)

    #obtain browser tab window
    nova_aba = driver.window_handles[-1]
    #switch to tab browser
    driver.switch_to.window(nova_aba)
    
    h2h_aba = None
    try:
        h2h_aba = driver.find_element_by_link_text('H2H')
    except:
        pass
    #h = driver.find_elements_by_class_name('tabs__tab')[2]
        
    if h2h_aba:
        odd1.append(float(o1) if len(o1) > 1 else o1)
        odd2.append(float(o2) if len(o2) > 1 else o2)
        odd3.append(float(o3) if len(o3) > 1 else o3)
        h2h_aba.click()
        camp = driver.find_element_by_class_name("tournamentHeader__country").text
        clubes = driver.find_elements_by_css_selector("a.participant__participantName")
        mandante = clubes[0].text
        visitante = clubes[1].text
        hora = driver.find_element_by_class_name("duelParticipant__startTime").text[-5:]
        placar = driver.find_element_by_class_name("detailScore__wrapper").text.replace("\n", "")
        print(camp)
        print("Mandante: " + mandante)
        print("Visitante: " + visitante)
        print("Hora:" + hora)
        jogos.append(mandante + " X " + visitante)
        camps.append(camp)
        horarios.append(hora)
        result.append(placar)

        resultados = driver.find_elements_by_class_name("h2h__icon")
        if len(resultados) >= 10:
            m = resultados[0:5]
            v= resultados[5:10]
            pm = 0
            pv = 0
            hm = ""
            hh1 = ""
            hh2 = ""

            for r in m[0:3]:
                print(r.text, end = " ")
                hh1 += r.text + " "
                if r.text == "E":
                    pm += 1
                elif r.text == "V":
                    pm += 3
            pm3 = pm     
            for r in m[3:]:
                print(r.text, end = " ")
                hh1 += r.text + " "
                if r.text == "E":
                    pm += 1
                elif r.text == "V":
                    pm += 3
            print("")
            for r in v[0:3]:
                print(r.text, end = " ")
                hh2 += r.text + " "
                if r.text == "E":
                    pv += 1
                elif r.text == "V":
                    pv += 3
            pv3 = pv
            for r in v[3:]:
                print(r.text, end = " ")
                hh2 += r.text + " "
                if r.text == "E":
                    pv += 1
                elif r.text == "V":
                    pv += 3
            print("")

            print(pm, " - ", pv, " -> ", pm - pv)
            h1.append(hh1)
            h2.append(hh2)
            dif.append(pm - pv)
            dif3.append(pm3 - pv3)
            print(f"[{placar}]")
            print(o1, "  ", o2, "  ", o3)
        else:
            print("Jogos insuficientes.")
            h1.append("-")
            h2.append("-")
            dif.append(0)
            dif3.append(0)
        print("")
        
    #close browser tab window
    driver.close()
    #switch to parent window
    driver.switch_to.window(janela_principal)
    
    #sleep(tempo_parada)
    
driver.close()

print("Gerando planilha(s)...")
    
dataframe = pd.DataFrame({"Horários": horarios, "Jogo": jogos, "H2H(1)": h1, "H2H(2)": h2, "Diferença": dif, "Dif(3)": dif3, "Placar": result, "1": odd1, "X": odd2, "2": odd3, "Campeonato": camps})
if gerar_arquivo_ordenado:
    dataframe.to_excel(nome_arquivo + "_ordenado" + extensao, index=False)
"""
dataframe["Aux1"] = dataframe["Diferença"]
dataframe["Aux2"] = dataframe["Dif(3)"]

dataframe["Aux1"] = dataframe["Aux1"].abs()
dataframe["Aux2"] = dataframe["Aux2"].abs()

dataframe = dataframe.sort_values(["Aux1", "Aux2"], ascending=[False, False])
    
dataframe = dataframe.drop(['Aux1', 'Aux2'], axis=1)
"""    
dataframe = dataframe.reindex(dataframe[["Diferença", "Dif(3)"]].abs().sort_values(["Diferença", "Dif(3)"], ascending = [False, False]).index)
#.sort_values(by=["Diferença", "Dif(3)"], key=lambda d: d.map({"Diferença": abs(d[0]), "Dif(3)": abs(d[1])}))
#display(dataframe)
dataframe.to_excel(nome_arquivo + extensao, index=False)

apagar_linhas(1)
print("Gerando planilha(s)... Ok")

tempo_execucao = segundos_para_tempo_formatado(int(time() - tempo_inicio))
print(f"\nPrograma executado em {tempo_execucao}.")