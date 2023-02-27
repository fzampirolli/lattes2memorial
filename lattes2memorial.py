
import sys
import os
if len(sys.argv) == 2 and sys.argv[1] == 'instala':
    os.system("python -m pip install -r requirements.txt")
    print('\nlattes2memorial: bibliotecas necessárias instaladas.\n')
    exit(0)

from lattesClass import *

if len(sys.argv) == 2 and len(sys.argv[1]) == len('4127260763254001'):
    IDs = [sys.argv[1]]
else:
    IDs = []  # pega os zips com prefixo "CV_"
    for f in os.listdir('./'):
        if '.zip' == f[-4:]:
            IDs.append(f[3:-4])


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
    print(lattes.jsonConfigura["NOME-COMPLETO"])

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
