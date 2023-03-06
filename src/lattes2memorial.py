
'''
=====================================================================
Copyright (C) 2023 Francisco de Assis Zampirolli
from Federal University of ABC. All rights reserved.

lattes2memorial is free: you can redistribute it and/or modify
it under the terms of the GNU General Public License
(gnu.org/licenses/gpl.txt) as published by the Free Software
Foundation, either version 3 of the License, or (at your option)
any later version.

lattes2memorial is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
=====================================================================
'''

import sys
import os
if len(sys.argv) == 2 and sys.argv[1] == 'instala':
    os.system("python -m pip install -r requirements.txt")
    print('\nlattes2memorial: bibliotecas necessárias instaladas.\n')
    exit(0)

if not os.path.exists('texLattes'):
    os.makedirs('texLattes')

from lattesClass import *

if len(sys.argv) == 2 and len(sys.argv[1]) == len('4127260763254001'):
    IDs = [sys.argv[1]]
else:
    IDs = []  # pega os zips com prefixo "CV_"
    for f in os.listdir('./'):
        if '.zip' == f[-4:]:
            IDs.append(f[3:-4])


################################################################
#  IMPLEMENTAÇÃO RECURSIVA - GENÉRICO!!! - EM CONSTRUÇAO
'''
recursoes = 0


def dist_raiz(no):
    if isinstance(no, dict):
        return 1 + (max(map(dist_raiz, no.values())) if no else 0)
    return 0


def dist_folha(nodo):
    def folha_aux(valor):
        if isinstance(valor, list):
            return max(dist_folha(v) for v in valor)
        else:
            return dist_folha(valor)

    if isinstance(nodo, dict):
        return 1 + max(folha_aux(v) for v in nodo.values())
    else:
        return 0


def formataSaida(v):
    ano = 0
    s = '\n\n\\item '
    if isinstance(v, dict):
        for k1, v1 in v.items():
            if isinstance(v1, str) and len(v1):
                s += v1 + '. '
                if '@ANO' in k1:
                    ano = int(v1)
    return [ano, s]


def pegaFilhos(d):
    global recursoes
    recursoes += 1
    ss0 = '\\begin{enumerate}'
    ssLista = []
    file = '_Geral_'
    if isinstance(d, list):
        for f in d:
            pegaFilhos(f)
    elif isinstance(d, dict):
        for k, v in d.items():
            if dist_folha(v):
                print()
                print(dist_folha(v), k)
                file = '_Geral_'+k
                s = formataSaida(v)
                if len(s[1]) > 12:
                    ssLista.append(s)
                pegaFilhos(v)

    if isinstance(ssLista, list) and len(ssLista) and len(ssLista[0][1]) > 12:
        print(file)
        print(ssLista)
        vSort = sorted(ssLista, key=lambda x: (-x[0], x[1]))
        ss0 += ''.join([v[1] for v in vSort])
        ss0 += '\n\n\\end{enumerate}\n'
        with open('./texLattes/'+file+'.tex', 'w') as f:
            f.writelines(ss0)
        f.close()
'''
#  IMPLEMENTAÇÃO RECURSIVA - GENÉRICO!!!
################################################################


def geraLattes2Memorial(id):
    file = id+'.tex'
    if len(sys.argv) == 2:  # and lattes.lerConfigJson(id+'config.json'):
        if sys.argv[1] == 'limpa':
            lattes.limpaDadosGerados(id)
            return 1

    lattes.criaConfiguraJson(id)
    print(lattes.jsonConfigura["NUMERO-IDENTIFICADOR"])

    lattes.qualisRevistaPDF2CSV()
    # print(lattes.getQualisRevista('ACM Transactions on Information Systems'))

    lattes.qualisEventoPDF2CSV()
    # print(lattes.getQualisEvento('Workshop de Visão Computacional'))

    ################################################################
    # começa a popular um json com informações do xml
    # Meu Lattes

    lattes.lattesXML2Json()
    lattes.verificaID()

    lattes.lattes2bib()  # converte xml para bib

    lattes.pegaDadosGerais(id)
    print("lattes2memorial:", lattes.jsonConfigura["NOME-COMPLETO"], "\n")

    lattes.atualizaDadosExtras()

    text = open("./extras/latexInicio.tex", "r", encoding='UTF-8').read()

    text += '''
    \include{capitulos/01introducao}
    \include{capitulos/02ensino}
    \include{capitulos/03pesquisa}
    \include{capitulos/04extensao}
    \include{capitulos/05admin}
    \include{capitulos/06conclusao}
    '''
    d = lattes.jsonLattes["CURRICULO-VITAE"]

    # pegaFilhos(d) # RECURSIVO
    # print(recursoes)

    # Bancas
    for tipo in ["Doutorado", "Mestrado", "Qualificacao", "Especializacao", "Graduacao"]:
        lattes.pegaDadosBancas(tipo)
    # return ''

    # Orientações
    for tipo in lattes.natureza:
        lattes.pegaDadosOrientacoes(tipo)

    # Orientações em andamanto
    for tipo in lattes.naturezaAndamento:
        lattes.pegaDadosOrientacoesAndamanto(tipo)

    #  Apresentações de Trabalhos
    lattes.pegaApresentacoes()

    #  Participações em eventos
    for tipo in ['Participante', 'Ouvinte']:
        lattes.pegaEventos(tipo)

    # Publicações em periódicos e eventos (completo)
    for tipo in ['ARTIGO', 'TRABALHO']:
        lattes.pegaDadosArtigos(tipo, "COMPLETO")

    # Publicações em eventos (resumo)
    lattes.pegaDadosArtigos("TRABALHO", "RESUMO")

    # Livros e Capítulos Publicados
    for tipo in ["LIVROS", "CAPITULOS"]:
        lattes.pegaPublicacoes(tipo)

    # Produções técnicas
    for tipo in ['SOFTWARE']:
        lattes.pegaProducoesTecnicas(tipo)

    # Bancas
    for tipo in ["Doutorado", "Mestrado", "Qualificacao", "Especializacao", "Graduacao"]:
        lattes.pegaDadosBancas(tipo)

    # Prêmios
    lattes.pegaPremios()

    tex_fim = open("./extras/latexFim.tex", "r", encoding='UTF-8').read()
    text += tex_fim.replace('__bib__', lattes.NUMERO_IDENTIFICADOR)

    # save question in question.tex
    with open(file, 'w') as writefile:
        writefile.write(text.encode().decode())

    if len(sys.argv) == 2:
        if sys.argv[1] != 'tex':
            lattes.rodaLatex(file)
    else:
        lattes.rodaLatex(file)


for id in IDs:
    geraLattes2Memorial(id)
