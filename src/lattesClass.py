'''
=====================================================================
Copyright (C) 2023d Francisco de Assis Zampirolli
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


import fileinput
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import operator
import ast
import os
import subprocess
import xmltodict
import json
import pandas as pd
from PyPDF2 import PdfReader
from datetime import datetime


class lattes(object):
    #### INICIALIZATION ####
    desenhaGraficos = 4  # desenha se #itens > 4
    figsize = [8, 5]
    figsizeBig = [20, 20]
    dfRevistasUpper = None
    dfEventosUpper = None
    jsonConfigura = None
    jsonLattes = None
    jsonLattesBib = None
    jsonBibId = None
    NUMERO_IDENTIFICADOR = ''
    arquivoConfiguraJson = 'config.json'
    renomeia = dict({'ARTIGO': 'Revistas', 'TRABALHO': 'Eventos'})
    renomeia["INICIACAO_CIENTIFICA"] = "Iniciação Científica"
    renomeia["TRABALHO_DE_CONCLUSAO_DE_CURSO_GRADUACAO"] = 'Trabalho de Conclusão de Curso'
    renomeia["MONOGRAFIA_DE_CONCLUSAO_DE_CURSO_APERFEICOAMENTO_E_ESPECIALIZACAO"] = 'Aperfeiçoamento/Especialização'
    renomeia["Doutorado"] = "Doutorado"
    renomeia["Mestrado"] = "Mestrado"
    renomeia["LIVROS"] = "Livros"
    renomeia["CAPITULOS"] = "Capítulos"
    renomeia["SOFTWARE"] = "Software"
    renomeia["Dissertação de mestrado"] = "Dissertação de mestrado"
    renomeia["ORIENTACAO-DE-OUTRA-NATUREZA"] = "Orientação de outra natureza"
    renomeia["ORIENTADOR_PRINCIPAL"] = "Orientador principal"
    renomeia["Trabalho de conclusão de curso de graduação"] = "Trabalho de conclusão de curso de graduação"
    renomeia["Tese de doutorado"] = "Tese de doutorado"
    renomeia["SEQUENCIA-PRODUCAO"] = "Sequência de produção"
    renomeia["DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO"] = "Detalhamento de orientações concluídas para doutorado"
    renomeia["CO_ORIENTADOR"] = "Co-orientador"
    renomeia["PROJETO-DE-PESQUISA"] = "Projeto de Pesquisa"

    natureza = ["Doutorado", "Mestrado",
                "ORIENTACAO-DE-OUTRA-NATUREZA",
                "INICIACAO_CIENTIFICA",
                "TRABALHO_DE_CONCLUSAO_DE_CURSO_GRADUACAO",
                "MONOGRAFIA_DE_CONCLUSAO_DE_CURSO_APERFEICOAMENTO_E_ESPECIALIZACAO",
                "ORIENTACAO-DE-OUTRA-NATUREZA",
                "DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO"]

    naturezaAndamento = ["Doutorado", "Mestrado",
                         "Graduacao"]
    # "ORIENTACAO-DE-OUTRA-NATUREZA"] # atualizar
    # "INICIACAO_CIENTIFICA",  # atualizar
    # "MONOGRAFIA_DE_CONCLUSAO_DE_CURSO_APERFEICOAMENTO_E_ESPECIALIZACAO",  # atualizar
    eventos = ["CONGRESSO", "SEMINARIO", "SIMPOSIO", "OFICINA", "ENCONTRO"]

    def __init__(self):
        pass

    def pegaIDbib(title):
        title = title.replace('\n', '').replace(' ', '')
        for k, v in lattes.jsonBibId.items():
            if v == title:
                return '\cite{' + k + '}. '
        return ''

    def lattes2bib():
        # crédito: https://arademaker.github.io/blog/2012/02/15/lattes-to-bibtex.html
        # lattes.lerConfigJson()
        id = lattes.jsonConfigura["NUMERO-IDENTIFICADOR"]
        # os.system("git clone git@github.com:arademaker/SLattes.git")
        os.system(f"xsltproc ./SLattes/lattes2mods.xsl {id}.xml > {id}.mods")
        # para validar xml >> mods
        # os.system("wget https://www.loc.gov/standards/mods/v3/mods-3-4.xsd")
        # os.system(f"xmllint --schema mods-3-4.xsd {id}.mods")
        # exit(0)
        ####
        os.system(f"xml2bib -b -w {id}.mods > {id}_.bib")
        os.system(f'bibtool -f "%4d(year):%n(author)" -s {id}_.bib > {id}.bib')
        # os.system(f"rm {id}_.bib")
        print(f'\nlattes2memorial: {id}.bib criado.\n')

        import bibtexparser
        from pylatexenc.latex2text import LatexNodes2Text

        if lattes.jsonLattesBib == None:
            with open(f"{lattes.NUMERO_IDENTIFICADOR}.bib") as file:
                bib_database = bibtexparser.load(file)

        lattes.jsonBibId = dict()
        for v in bib_database.entries:
            t = LatexNodes2Text().latex_to_text(v['title']).replace('@', '')
            t = t.replace('\n', '').replace(' ', '')
            lattes.jsonBibId[v["ID"]] = t

    def lerConfigJson(id):
        if not os.path.exists(id + lattes.arquivoConfiguraJson):
            print(f"\nERRO: {id}{lattes.arquivoConfiguraJson} não existe!\n")
            exit(0)
        f = open(lattes.arquivoConfiguraJson)
        lattes.jsonConfigura = json.load(f)
        return 1

    def rodaLatex(file):
        def _rodaLatex(file):
            cmd = ['pdflatex', '-interaction', 'nonstopmode', file]
            proc = subprocess.Popen(cmd)
            proc.communicate()

        _rodaLatex(file)

        cmd = ['bibtex', file[:-4]]
        proc = subprocess.Popen(cmd)
        proc.communicate()

        _rodaLatex(file)
        _rodaLatex(file)

    def limpaDadosGerados(id):
        if id:
            print("rm " + id + "*")
            os.system("rm " + id + "*")
        os.system("rm texLattes/*")
        os.system("rm figs/Qualis*")
        os.system("rm figs/Orient*")
        os.system("rm figs/Evento*")
        os.system("rm figs/Aprese*")
        os.system("rm figs/Grafo*")
        os.system("rm figs/Producoes*")
        os.system("rm figs/Publicacoes*")
        os.system("rm figs/Bancas*")
        os.system("rm figs/Premios*")
        os.system("rm data/novoQualis2017-2020.csv")
        os.system("rm extras/dados.tex")
        os.system("rm **/*.aux")
        os.system("rm **/*.fdb_latexmk")
        os.system("rm **/*.fls")
        os.system("rm **/*.log")
        # os.system("rm -rf SLattes")
        os.system("rm mods-3-4*")
        print('\nlattes2memorial: Arquivos temporários removidos.\n')

    def saveJsonConfig(id):
        json_formatted_str = json.dumps(lattes.jsonConfigura, indent=2)
        with open(id + lattes.arquivoConfiguraJson, "w") as outfile:
            outfile.write(json_formatted_str)
        outfile.close()

    def criaConfiguraJson(id):
        import zipfile

        print('CV_' + id + '.zip')
        if os.path.exists('CV_' + id + '.zip'):
            with zipfile.ZipFile('CV_' + id + '.zip', "r") as zip_ref:
                zip_ref.extractall("./")
        else:
            print('ERRO: não existe zip do seu lattes, com nome:',
                  'CV_' + id + '.zip')
            exit(0)

        lattes.NUMERO_IDENTIFICADOR = id
        if not os.path.exists(id + lattes.arquivoConfiguraJson):
            lattes.jsonConfigura = dict()
            lattes.jsonConfigura["NUMERO-IDENTIFICADOR"] = id
            lattes.saveJsonConfig(id)

        f = open(id + lattes.arquivoConfiguraJson)
        lattes.jsonConfigura = json.load(f)

        return lattes.jsonConfigura

    def qualisRevistaPDF2CSV(url=''):
        '''
        dfRevistas = qualisRevistaPDF2CSV()

        Converte arquivo.PDF e retorna planilha pandas
        Ler pdf de url, salva na pasta data,
        Converte para csv não formatado data/arquivo-Linha.csv,
        formata para data/arquivo.csv,
        '''
        if lattes.jsonConfigura == None:
            print("ERRO: confing não existe")
            exit(1)

        if "QUALIS-REVISTA-CSV" in lattes.jsonConfigura.keys():
            print(
                f'lattes2memorial: {lattes.jsonConfigura["QUALIS-REVISTA-CSV"]} não atualizado. Removê-lo para cc.')

        lattes.jsonConfigura[
            "QUALIS-REVISTA-URL"] = 'https://www.ufrgs.br/ppggeo/ppggeo/wp-content/uploads/2019/12/QUALIS-NOVO-1.pdf'
        lattes.jsonConfigura["QUALIS-REVISTA-LINHA"] = './data/novoQualis2017-2020-Linha.csv'
        lattes.jsonConfigura["QUALIS-REVISTA-CSV"] = './data/novoQualis2017-2020.csv'

        ''' >>> desatualizado!!!
        # url = 'https://www.ufrgs.br/ppggeo/ppggeo/wp-content/uploads/2019/12/QUALIS-NOVO-1.pdf'
        os.system('wget ' + url)
        os.system('mv QUALIS-NOVO-1.pdf ./data/')

        reader = PdfReader('./data/QUALIS-NOVO-1.pdf')

        text = ''
        for p in range(1, len(reader.pages)+1):
            # text += "\n\n============" + str(p) + "\n"
            page = reader.pages[p]
            text += page.extract_text()
        # <<< desatualizado!!!'''

        # converte linha não formatada para csv
        with open(lattes.jsonConfigura["QUALIS-REVISTA-LINHA"], 'r') as fd:
            texto = fd.read()
        novoQualis = []
        for l in texto.split('\n'):
            v = [s for s in l.split('\t') if s]
            if len(v) == 3:
                novoQualis.append(v)
            elif len(v) == 2:
                v0 = [v[0], v[1][:-3], v[1][-2:]]
                novoQualis.append(v0)
            else:
                print(v)

        file = lattes.jsonConfigura["QUALIS-REVISTA-CSV"]
        np.savetxt(file, novoQualis, delimiter=";", fmt='% s')

        dfRevistas = pd.read_csv(file, sep=";")
        lattes.dfRevistasUpper = dfRevistas
        # tudo maiúsculo
        lattes.dfRevistasUpper['Titulo'] = dfRevistas['Titulo'].str.upper()
        lattes.saveJsonConfig(lattes.NUMERO_IDENTIFICADOR)

    def getQualisRevista(s):
        try:
            periodo = lattes.jsonConfigura["QUALIS-REVISTA-CSV"]
            periodo = ' (' + periodo[-13:-4] + ')'
            ss = lattes.dfRevistasUpper.loc[lattes.dfRevistasUpper['Titulo'] == s.upper(
            )]
            ss = ss.values[0][2] + ', ISSN ' + ss.values[0][0] + periodo
        except:
            ss = 'SQ'
        return ss

    def qualisEventoPDF2CSV(url=''):
        '''
        dfEventos = qualisEventoPDF2CSV()

        Converte arquivo.PDF e retorna planilha pandas
        Ler pdf de url, salva na pasta data,
        Converte e formata para data/arquivo.csv,
        '''
        if lattes.jsonConfigura == None:
            print("ERRO: confing não existe")

        lattes.jsonConfigura[
            "QUALIS-EVENTO-URL"] = 'https://www.gov.br/capes/pt-br/centrais-de-conteudo/documentos/avaliacao/09012022_RELATORIOQUALISEVENTOS20172020COMPUTACAO.PDF'
        file = "./data/sucupiraEventos2017-2020.csv"
        lattes.jsonConfigura["QUALIS-EVENTO-CSV"] = file
        lattes.saveJsonConfig(lattes.NUMERO_IDENTIFICADOR)

        # pdf to cvs automático está desatualizado

        #########################################
        dfEventos = pd.read_csv(file, sep=";")
        lattes.dfEventosUpper = dfEventos
        # tudo maiúsculo
        lattes.dfEventosUpper['Nome do evento'] = dfEventos['Nome do evento'].str.upper(
        )

    def getQualisEvento(s):
        try:
            periodo = lattes.jsonConfigura["QUALIS-EVENTO-CSV"]
            periodo = ' (' + periodo[-13:-4] + ')'
            ss = lattes.dfEventosUpper.loc[lattes.dfEventosUpper['Nome do evento'] == s.upper(
            )]
            ss = ss.values[0][2] + ', Sigla ' + \
                ss.values[0][0] + periodo
        except:
            ss = 'SQ'
        return ss

    def lattesXML2Json():
        f0 = lattes.NUMERO_IDENTIFICADOR + '.xml'

        with open(f0, 'rb') as fd:
            f = fd.read()
            doc = xmltodict.parse(f, process_namespaces=True)

        doc1 = json.dumps(doc)
        lattes.jsonLattes = json.loads(doc1)

        json_formatted_str = json.dumps(lattes.jsonLattes, indent=2)
        with open(f0[:-4] + ".json", "w") as outfile:
            outfile.write(json_formatted_str)
        outfile.close()

    def verificaID():
        if lattes.jsonLattes['CURRICULO-VITAE']["@NUMERO-IDENTIFICADOR"] != lattes.jsonConfigura[
                "NUMERO-IDENTIFICADOR"]:
            print(
                f"ERRO: ID de {lattes.arquivoConfiguraJson} é diferente do xml")
            exit(0)

    def pegaDadosGerais(id):
        # if not os.path.exists(lattes.arquivoConfiguraJson):
        #    print(f"ERRO: {id}{lattes.arquivoConfiguraJson} não existe!")
        d0 = lattes.jsonLattes['CURRICULO-VITAE']['DADOS-GERAIS']

        if not "RESUMO-CV" in d0.keys():
            print("Sem Resumo")
            resumo = 'SEM RESUMO'
        else:
            resumo = d0['RESUMO-CV']['@TEXTO-RESUMO-CV-RH']

        with open('./texLattes/Resumo.tex', 'w') as f:
            f.writelines(resumo)
        f.close()
        lattes.jsonConfigura['TEXTO-RESUMO-CV-RH'] = resumo

        lattes.jsonConfigura['NOME-COMPLETO'] = d0['@NOME-COMPLETO']
        lattes.jsonConfigura["NOME-ORGAO"] = d0["ENDERECO"]["ENDERECO-PROFISSIONAL"]["@NOME-ORGAO"]
        lattes.jsonConfigura["NOME-INSTITUICAO-EMPRESA"] = d0["ENDERECO"]["ENDERECO-PROFISSIONAL"][
            "@NOME-INSTITUICAO-EMPRESA"]
        lattes.jsonConfigura["CIDADE"] = d0["ENDERECO"]["ENDERECO-PROFISSIONAL"]["@CIDADE"]
        lattes.jsonConfigura["E-MAIL"] = d0["ENDERECO"]["ENDERECO-PROFISSIONAL"]["@E-MAIL"]
        s = lattes.jsonLattes['CURRICULO-VITAE']["@DATA-ATUALIZACAO"]
        lattes.jsonConfigura["DATA-ATUALIZACAO"] = s[:2] + \
            '/' + s[2:4] + '/' + s[4:]

        if not "ATUACOES-PROFISSIONAIS" in lattes.jsonLattes['CURRICULO-VITAE']['DADOS-GERAIS'].keys():
            print("Sem Atuações Profissionais")
            return 1

        lattes.saveJsonConfig(lattes.NUMERO_IDENTIFICADOR)

    def atualizaDadosExtras():
        file = './extras/dados_.tex'
        if not os.path.exists(file):
            print(f"ERRO: {file} não existe!")

        with open(file, 'r') as fd:
            text = fd.read()
            text = text.replace('__NOME-COMPLETO__',
                                lattes.jsonConfigura['NOME-COMPLETO'])
            text = text.replace(
                '__NOME-ORGAO__', lattes.jsonConfigura['NOME-ORGAO'])
            text = text.replace('__NOME-INSTITUICAO-EMPRESA__',
                                lattes.jsonConfigura['NOME-INSTITUICAO-EMPRESA'])
            text = text.replace(
                '__CIDADE__', lattes.jsonConfigura['CIDADE'])
            text = text.replace('__DATA-ATUALIZACAO__',
                                lattes.jsonConfigura['DATA-ATUALIZACAO'])
        fd.close()
        with open(file[:-5] + '.tex', 'w') as fd:
            fd.writelines(text)
        fd.close()

    def pegaDadosOrientacoes(tipo):
        orientacoes = dict()
        orientacoes["Doutorado"] = ["ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO",
                                    "DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO",
                                    "DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-DOUTORADO"]
        orientacoes["Mestrado"] = ["ORIENTACOES-CONCLUIDAS-PARA-MESTRADO",
                                   "DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO",
                                   "DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO"]
        orientacoes["Outras"] = ["OUTRAS-ORIENTACOES-CONCLUIDAS",
                                 "DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS",
                                 "DETALHAMENTO-DE-OUTRAS-ORIENTACOES-CONCLUIDAS"]

        def geraTex(tipo, tipo2):
            d = lattes.jsonLattes["CURRICULO-VITAE"]["OUTRA-PRODUCAO"]
            vo = orientacoes[tipo]

            ts = lattes.renomeia[tipo2] if tipo2 else ''

            if not d:
                with open('./texLattes/Orientacoes' + tipo + ts[:4] + '.tex', 'w') as f:
                    f.writelines('')
                f.close()
                return ''
            ssLista = []
            ss0 = '\\begin{enumerate}'
            for k, v in d.items():
                if k == "ORIENTACOES-CONCLUIDAS":
                    for k0, v0 in d[k].items():
                        if k0 == vo[0]:
                            for i in d[k][k0]:
                                if tipo in lattes.natureza[:2] or (tipo2 and tipo2 == i[vo[1]]["@NATUREZA"]):
                                    if isinstance(i, str) or vo[2] not in i.keys():
                                        continue
                                    ss = '\n\n\\item '
                                    ss += i[vo[2]]["@NOME-DO-ORIENTADO"] + '. '
                                    ss += i[vo[1]]["@TITULO"] + '. '
                                    ano = i[vo[1]]["@ANO"]
                                    ss += ano + '. '
                                    ss += lattes.renomeia[i[vo[1]]
                                                          ["@NATUREZA"]] + ' ('
                                    ss += i[vo[2]]["@NOME-DO-CURSO"] + ') - '
                                    ss += i[vo[2]
                                            ]["@NOME-DA-INSTITUICAO"] + '. '
                                    if i[vo[2]]["@NOME-DA-AGENCIA"]:
                                        ss += i[vo[2]
                                                ]["@NOME-DA-AGENCIA"] + '. '
                                    if tipo in ['Mestrado', 'Doutorado']:
                                        ss += lattes.renomeia[i[vo[2]]
                                                              ["@TIPO-DE-ORIENTACAO"]] + '. '
                                    ssLista.append([int(ano), ss])

            vSort = sorted(ssLista, key=lambda x: (-x[0], x[1]))
            ss0 += ''.join([v[1] for v in vSort])
            ss0 += '\n\n\\end{enumerate}\n'

            v0 = sorted([v[0] for v in vSort], reverse=True)
            if len(v0) > lattes.desenhaGraficos:  # desenha gráficos

                s = '''
A Figura \\ref{figs:orientacoes__tipo____tipo2__} mostra, considerando a data de início, o número de orientações por ano de __tipo3__.
\\begin{figure}[!h]
\centering
\includegraphics[width=0.8\\textwidth]{figs/Orientacoes__tipo____tipo2__.png}
\caption{Orientações por ano (__tipo3__)}
\label{figs:orientacoes__tipo____tipo2__}
\end{figure}
    '''
                if ts:
                    ss0 += s.replace('__tipo__', tipo).replace('__tipo2__',
                                                               ts[:4]).replace('__tipo3__', ts)
                else:
                    ss0 += s.replace('__tipo__', tipo).replace('__tipo2__',
                                                               ts[:4]).replace('__tipo3__', tipo)

                orientacoesAno = {i: v0.count(i) for i in set(v0)}
                x = sorted(list(orientacoesAno.keys()), reverse=True)
                frequencia = [orientacoesAno[i] for i in x]
                x = [str(i) for i in x]

                plt.figure(figsize=lattes.figsize)
                fig, ax = plt.subplots()
                ax.tick_params(axis='x', labelrotation=90)
                # if tipo2:
                #     ax.set_title(
                #         'Orientações por ano (' + ts + ')')
                # else:
                #     ax.set_title('Orientações por ano (' + tipo + ')')
                ax.set_ylabel("Quantidade")
                # ax.set_xlabel('Qualis')
                ax.set_ylim([0, int(1 + 1.1 * max(frequencia))])

                pps = ax.bar(x, frequencia, label='population')

                plt.savefig('figs/Orientacoes' + tipo + ts[:4] + '.png')
                plt.close()

            # ss0 = ss0.replace('Aperfeiçoamento/Especialização',
            #                  'Aperfeiçoamento / Especialização')
            if len(ss0) < 100:
                ss0 = 'sem dados'
            with open('./texLattes/Orientacoes' + tipo + ts[:4] + '.tex', 'w') as f:
                f.writelines(ss0)
            f.close()

        if tipo in ["Mestrado", "Doutorado"]:
            geraTex(tipo, '')
        else:
            geraTex("Outras", tipo)

    def pegaDadosOrientacoesAndamanto(tipo):
        orientacoes = dict()
        orientacoes["Doutorado"] = ["ORIENTACAO-EM-ANDAMENTO-DE-DOUTORADO",
                                    "DADOS-BASICOS-DA-ORIENTACAO-EM-ANDAMENTO-DE-DOUTORADO",
                                    "DETALHAMENTO-DA-ORIENTACAO-EM-ANDAMENTO-DE-DOUTORADO"]
        orientacoes["Mestrado"] = ["ORIENTACAO-EM-ANDAMENTO-DE-MESTRADO",
                                   "DADOS-BASICOS-DA-ORIENTACAO-EM-ANDAMENTO-DE-MESTRADO",
                                   "DETALHAMENTO-DA-ORIENTACAO-EM-ANDAMENTO-DE-MESTRADO"]
        orientacoes["Graduacao"] = ["ORIENTACAO-EM-ANDAMENTO-DE-GRADUACAO",
                                    "DADOS-BASICOS-DA-ORIENTACAO-EM-ANDAMENTO-DE-GRADUACAO",
                                    "DETALHAMENTO-DA-ORIENTACAO-EM-ANDAMENTO-DE-GRADUACAO"]

        d = lattes.jsonLattes["CURRICULO-VITAE"]["DADOS-COMPLEMENTARES"]

        if not d:
            with open('./texLattes/OrientacoesAndamento' + tipo + '.tex', 'w') as f:
                f.writelines('')
            f.close()
            return ''

        ss0 = '\\begin{enumerate}'
        vo = orientacoes[tipo]
        ssLista = []
        for k, v in d.items():
            if k == "ORIENTACOES-EM-ANDAMENTO":
                for k0, v0 in d[k].items():
                    if k0 == vo[0]:
                        if isinstance(v0, list):
                            for v1 in v0:
                                if tipo in lattes.naturezaAndamento:

                                    ss = '\n\n\\item '
                                    ss += v1[vo[2]
                                             ]["@NOME-DO-ORIENTANDO"] + '. '
                                    ss += v1[vo[1]
                                             ]["@TITULO-DO-TRABALHO"] + '. '
                                    ano = v1[vo[1]]["@ANO"]
                                    ss += ano + '. '
                                    ss += lattes.renomeia[v1[vo[1]]
                                                          ["@NATUREZA"]] + ' ('
                                    ss += v1[vo[2]]["@NOME-CURSO"] + ') - '
                                    ss += v1[vo[2]]["@NOME-INSTITUICAO"] + '. '
                                    if v1[vo[2]]["@NOME-DA-AGENCIA"]:
                                        ss += v1[vo[2]
                                                 ]["@NOME-DA-AGENCIA"] + '. '
                                    if tipo in ['Mestrado', 'Doutorado']:
                                        ss += lattes.renomeia[v1[vo[2]]
                                                              ["@TIPO-DE-ORIENTACAO"]] + '. '
                                    ssLista.append([int(ano), ss])
                        elif tipo in lattes.naturezaAndamento:
                            ss = '\n\n\\item '
                            ss += v0[vo[2]
                                     ]["@NOME-DO-ORIENTANDO"] + '. '
                            ss += v0[vo[1]
                                     ]["@TITULO-DO-TRABALHO"] + '. '
                            ano = v0[vo[1]]["@ANO"]
                            ss += ano + '. '
                            ss += v0[vo[1]]["@NATUREZA"] + ' ('
                            ss += v0[vo[2]]["@NOME-CURSO"] + ') - '
                            ss += v0[vo[2]]["@NOME-INSTITUICAO"] + '. '
                            if v0[vo[2]]["@NOME-DA-AGENCIA"]:
                                ss += v0[vo[2]
                                         ]["@NOME-DA-AGENCIA"] + '. '
                            if tipo in ['Mestrado', 'Doutorado']:
                                ss += lattes.renomeia[v0[vo[2]]
                                                      ["@TIPO-DE-ORIENTACAO"]] + '. '
                            ssLista.append([int(ano), ss])

        vSort = sorted(ssLista, key=lambda x: (-x[0], x[1]))
        ss0 += ''.join([v[1] for v in vSort])
        ss0 += '\n\n\\end{enumerate}\n'

        if len(ss0) < 100:
            ss0 = 'sem orientações e andamento - ' + tipo
        with open('./texLattes/OrientacoesAndamento' + tipo + '.tex', 'w') as f:
            f.writelines(ss0)
        f.close()

    def pegaDadosArtigos(tipo='TRABALHO', tamanho="COMPLETO"):

        def ordenaArtigosAno(D, reverse=True):
            valores = [(p['DADOS-BASICOS-DO-' + tipo]['@ANO-DO-' + tipo], p)
                       for a, b in D.items() for p in b]
            return [t[1] for t in sorted(valores, key=lambda x: x[0], reverse=True)]

        # with open('./texLattes/' + lattes.renomeia[tipo] + tamanho.upper() + '.tex', 'w') as f:
        #     f.writelines('')
        # f.close()
        with open('./texLattes/' + lattes.renomeia[tipo] + tamanho + '.tex', 'w') as f:
            f.writelines('vazio')
        f.close()

        if tipo == 'TRABALHO':
            if not lattes.jsonLattes['CURRICULO-VITAE']['PRODUCAO-BIBLIOGRAFICA']:
                return ''
            if not "TRABALHOS-EM-EVENTOS" in lattes.jsonLattes['CURRICULO-VITAE']['PRODUCAO-BIBLIOGRAFICA'].keys():
                print("Sem trabalhos em eventos")
                return ''
            D = lattes.jsonLattes['CURRICULO-VITAE']['PRODUCAO-BIBLIOGRAFICA']['TRABALHOS-EM-EVENTOS']
        else:
            if not lattes.jsonLattes['CURRICULO-VITAE']['PRODUCAO-BIBLIOGRAFICA']:
                return ''
            if not "ARTIGOS-PUBLICADOS" in lattes.jsonLattes['CURRICULO-VITAE']['PRODUCAO-BIBLIOGRAFICA'].keys():
                print("Sem artigos em revistas")
                return ''
            D = lattes.jsonLattes['CURRICULO-VITAE']['PRODUCAO-BIBLIOGRAFICA']['ARTIGOS-PUBLICADOS']

        D_order = ordenaArtigosAno(D)

        autoresTodos = []

        qualisAno = dict()
        ss0 = '\\begin{enumerate}'
        for p in D_order:
            autores = []
            if p['DADOS-BASICOS-DO-' + tipo]["@NATUREZA"] == tamanho:

                ss0 += '\n\n\\item '
                if p['DADOS-BASICOS-DO-' + tipo]['@DOI']:
                    s = p['DADOS-BASICOS-DO-' + tipo]['@DOI']
                    ss0 += '\\href{https://doi.org/' + s + \
                           '}{{\\color{white}\\hl{\\textbf{doi$>$}}}} '
                elif p['DADOS-BASICOS-DO-' + tipo]['@HOME-PAGE-DO-TRABALHO']:
                    ss0 += '\\href{' + p['DADOS-BASICOS-DO-' + tipo]['@HOME-PAGE-DO-TRABALHO'][1:-1] + \
                           '}{{\\color{yellow}\\hl{\\textbf{url$>$}}}} '
                ano = ''

                if isinstance(p['AUTORES'], list):
                    for a in p['AUTORES']:
                        if a['@NOME-PARA-CITACAO']:
                            a0 = a['@NOME-PARA-CITACAO'].upper()
                            # ss0 += a0 + "; "
                            autores.append(a0)
                elif p['AUTORES']['@NOME-PARA-CITACAO']:
                    a0 = p['AUTORES']['@NOME-PARA-CITACAO'].upper()
                    # ss0 += a0 + "; "
                    autores.append(a0)

                # ss0 = ss0[: -2] + '. '

                for c, d in p['DADOS-BASICOS-DO-' + tipo].items():
                    if d and c[1:] == 'TITULO-DO-' + tipo:
                        ss0 += d + '. '
                        cite = lattes.pegaIDbib(d)
                    if d and c[1:] == 'ANO-DO-' + tipo:
                        ano = d

                for c, d in p['DETALHAMENTO-DO-' + tipo].items():
                    if d and c[1:] == 'TITULO-DO-PERIODICO-OU-REVISTA' or c[1:] == "NOME-DO-EVENTO":
                        ss0 += '\\textit{' + d + '}'  # .upper()
                        ss0 += '. ' + ano + '. ' + cite
                        if tipo == 'TRABALHO':
                            qualis = lattes.getQualisEvento(d)
                        else:
                            qualis = lattes.getQualisRevista(d)
                        if qualis != 'SQ':
                            ss0 += '\\\\ {\\color{gray}' + qualis + '}'

                if qualis[:2] in qualisAno.keys():
                    qualisAno[qualis[:2]].append(ano)
                else:
                    qualisAno[qualis[:2]] = [ano]

            if autores:
                autoresTodos.append(autores)

        ss0 += '\n\n\\end{enumerate}\n'

        ss0 = ss0.replace('&#8208;', '-').replace('&', '\&').replace('`', "'")

        try:
            qualisAno['C'] = qualisAno.pop('C,')  # rename
        except:
            pass

        if tamanho == "COMPLETO" and len(qualisAno):

            # DESENHA FIGURA ARTIGOS POR QUALIS

            plt.figure(figsize=lattes.figsize)
            x = list(sorted(qualisAno.keys()))

            frequencia = [len(qualisAno[q]) for q in x]

            width = 0.35  # the width of the bars

            fig, ax = plt.subplots()
            #ax.set_title('Artigos por Qualis em ' + lattes.renomeia[tipo])
            ax.set_ylabel("Quantidade")
            # ax.set_xlabel('Qualis')
            ax.set_ylim([0, int(1 + 1.1 * max(frequencia))])

            pps = ax.bar(x, frequencia, label='population')

            vet = ['+'.join(v) for v in qualisAno.values()]
            c = 0
            for p in pps:
                height = p.get_height()
                ax.annotate('{}'.format(height),
                            xy=(p.get_x() + p.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')
                c += 1

            plt.savefig(
                'figs/Qualis' + lattes.renomeia[tipo] + '.png')
            plt.close()

            s = '''
A Figura \\ref{figs:qualis__tipo__} mostra o número de artigos por Qualis em __tipo__.
\\begin{figure}[!h]
\centering
\includegraphics[width=0.8\\textwidth]{figs/Qualis__tipo__.png}
\caption{Artigos por Qualis em __tipo__}
\label{figs:qualis__tipo__}
\end{figure}'''
            ss0 += s.replace('__tipo__', lattes.renomeia[tipo])

        # DESENHA FIGURA QUALIS por ano
        if len(qualisAno):

            qualisAno2 = dict()
            for k, q in qualisAno.items():
                for a in q:
                    if a in qualisAno2.keys():
                        qualisAno2[a].append(k)
                    else:
                        qualisAno2[a] = [k]

            listaQualis = ['A1', 'A2', 'A3', 'A4',
                           'B1', 'B2', 'B3', 'B4', 'C', 'SQ']
            qualisAno3 = dict()
            for k, q in qualisAno.items():
                for a in q:
                    if a in qualisAno3.keys():
                        qualisAno3[a] += len(listaQualis) - \
                            listaQualis.index(k)
                    else:
                        qualisAno3[a] = len(listaQualis) - listaQualis.index(k)
            myKeys = [int(i) for i in qualisAno3.keys()]
            myKeys.sort(reverse=True)
            qualisAno3 = {str(i): qualisAno3[str(i)] for i in myKeys}
            qualisAno2 = {str(i): qualisAno2[str(i)] for i in myKeys}
            anos = list(qualisAno3.keys())

            plt.figure(figsize=lattes.figsize)
            # x = anos  # np.arange(len(anos))  # the label locations

            fig, ax = plt.subplots()

            tamanhoStr = ''
            if tamanho == 'RESUMO':
                tamanhoStr += ' (Resumo)'

            #ax.set_title('Artigos por ano em ' +
            #             lattes.renomeia[tipo] + tamanhoStr)
            ax.set_ylabel("Soma (A1=10, ..., C=2, SQ=1) ")
            # ax.set_xlabel('Anos')

            ax.tick_params(axis='x', labelrotation=90)

            pps = ax.bar(anos,
                         qualisAno3.values(), label='population')

            vet = []
            tmax = 0
            for v in qualisAno2.values():
                s = ''
                for q in listaQualis:
                    if q in v:
                        if v.count(q) > 1:
                            s += str(v.count(q)) + q + '+'
                        else:
                            s += q + '+'
                tmax = max(tmax, len(s))
                vet.append(s[:-1])

            ax.set_ylim([0, 2 * tmax + int(max(qualisAno3.values()))])

            c = 0
            for p in pps:
                height = p.get_height()
                ax.annotate('{}'.format(vet[c]),
                            xy=(p.get_x() + p.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points", rotation=90,
                            ha='center', va='bottom')
                c += 1

            plt.savefig('figs/Qualis' +
                        lattes.renomeia[tipo] + tamanho + 'Ano.png')
            plt.close()

            s = '''
A Figura \\ref{figs:qualis__tipo____tipo2__Ano} mostra o número de artigos __tipo3__
com Qualis, se existirem por ano em __tipo__.
Considerar no eixo vertical o somatório de artigos, sendo A1=10, A2=9, $\cdots$, C=2, SQ=1.
Onde SQ é Sem Qualis e nesta figura tem peso de apenas uma unidade na vertical.
\\begin{figure}[!h]
\centering
\includegraphics[width=0.8\\textwidth]{figs/Qualis__tipo____tipo2__Ano.png}
\caption{Artigos por ano em __tipo__ __tipo3__}
\label{figs:qualis__tipo____tipo2__Ano}
\end{figure}  '''
            ss0 += s.replace('__tipo__',
                             lattes.renomeia[tipo]).replace('__tipo2__', tamanho).replace('__tipo3__', tamanhoStr)

        if len(autoresTodos):

            # DESENHA FIGURA RELAÇÕES DE AUTORES
            import itertools
            import networkx as nx

            dic = {}
            for p in autoresTodos:
                aa = []
                for a in p:
                    s = a.split(',')[0].lower()
                    aa.append(s)
                for r in list(itertools.combinations(aa, 2)):
                    if r[0] in dic.keys():
                        dic[r[0]].append(r[1])
                    else:
                        dic[r[0]] = [r[1]]
                    if r[1] in dic.keys():
                        dic[r[1]].append(r[0])
                    else:
                        dic[r[1]] = [r[0]]
            plt.figure(figsize=lattes.figsize)
            # print(dic)
            G_authors = nx.Graph(dic)
            # nx.draw(g, with_labels=True, node_size=600, node_color="skyblue", node_shape="s", alpha=0.8, linewidths=40,  font_weight='bold')

            # inicio

            import networkx.algorithms.community as nxcom
            # from matplotlib import pyplot as plt

            plt.rcParams.update(plt.rcParamsDefault)
            plt.rcParams.update({'figure.figsize': (list(lattes.figsize))})
            # get reproducible results
            import random
            from numpy import random as nprand
            random.seed(137)
            nprand.seed(137)
            communities = sorted(nxcom.greedy_modularity_communities(
                G_authors), key=len, reverse=True)
            print(
                f"O agrupamento de autores em {len(communities)} comunidades em {lattes.renomeia[tipo]} ({tamanho}).")

            def set_node_community(G, communities):
                '''Add community to node attributes'''
                for c, v_c in enumerate(communities):
                    for v in v_c:
                        # Add 1 to save 0 for external edges
                        G.nodes[v]['community'] = c + 1

            def set_edge_community(G):
                '''Find internal edges and add their community to their attributes'''
                for v, w, in G.edges:
                    if G.nodes[v]['community'] == G.nodes[w]['community']:
                        # Internal edge, mark with community
                        G.edges[v, w]['community'] = G.nodes[v]['community']
                    else:
                        # External edge, mark as 0
                        G.edges[v, w]['community'] = 0

            def get_color(i, r_off=1, g_off=1, b_off=1):
                '''Assign a color to a vertex.'''
                r0, g0, b0 = 0, 0, 0
                n = 16
                low, high = 0.1, 0.9
                span = high - low
                r = low + span * (((i + r_off) * 3) % n) / (n - 1)
                g = low + span * (((i + g_off) * 5) % n) / (n - 1)
                b = low + span * (((i + b_off) * 7) % n) / (n - 1)
                return (r, g, b)

                # Set node and edge communities

            set_node_community(G_authors, communities)
            set_edge_community(G_authors)
            node_color = [get_color(G_authors.nodes[v]['community'])
                          for v in G_authors.nodes]
            # Set community color for edges between members of the same community (internal) and intra-community edges (external)
            external = [
                (v, w) for v, w in G_authors.edges if G_authors.edges[v, w]['community'] == 0]
            internal = [
                (v, w) for v, w in G_authors.edges if G_authors.edges[v, w]['community'] > 0]
            internal_color = ['black' for e in internal]

            karate_pos = nx.spring_layout(G_authors)
            li = [int(e * 0.6) for e in lattes.figsizeBig]
            li2 = [int(e * 1.3) for e in lattes.figsizeBig]
            plt.figure(figsize=li)
            plt.rcParams.update({'figure.figsize': li2})
            # Draw external edges
            nx.draw_networkx(
                G_authors,
                pos=karate_pos,
                node_size=0,
                edgelist=external,
                edge_color="silver")
            # Draw nodes and internal edges
            nx.draw_networkx(
                G_authors, node_size=600, alpha=0.5, linewidths=30,
                pos=karate_pos,
                node_color=node_color,
                edgelist=internal,
                edge_color=internal_color)

            # fim

            from pyvis.network import Network
            net = Network()
            net.from_nx(G_authors)
            net.save_graph(
                'figs/Grafo' + lattes.renomeia[tipo] + tamanho + 'Ano.html')

            plt.savefig(
                'figs/Grafo' + lattes.renomeia[tipo] + tamanho + 'Ano.png')
            plt.close('all')
            plt.rcdefaults()

            s = '''
A Figura \\ref{figs:grafo__tipo____tipo2__Ano} mostra os relacionamentos
de autores dos artigos em __tipo____tipo3__.
Ver também \href{http://mctest.ufabc.edu.br:8000/lattes2memorial/src/figs/Grafo__tipo____tipo2__Ano.html}
{grafo com movimento} para uma melhor visualização.
\
Os relacionamentos dos autores na Figura 
\\ref{figs:grafo__tipo____tipo2__Ano} foram gerados utilizando a biblioteca 
\href{https://networkx.org/documentation/stable/reference/algorithms/community.html}
{\\texttt{networkx.algorithms.community}}. A URL para o grafo dos relacionamentos dos 
autores, agora com movimentos, foi gerada utilizando a biblioteca 
\href{https://pyvis.readthedocs.io/en/latest/tutorial.html}{\\texttt{pyvis.network}}.
\\begin{figure}[!h]
\centering
\includegraphics[width=1.0\\textwidth]{figs/Grafo__tipo____tipo2__Ano.png}\\vspace{-1cm}
\caption{Relacionamentos de autores dos artigos em __tipo__ __tipo3__ - ver
\href{http://mctest.ufabc.edu.br:8000/lattes2memorial/src/figs/Grafo__tipo____tipo2__Ano.html}{grafo com movimento}}
\label{figs:grafo__tipo____tipo2__Ano}
\end{figure} '''
            ss0 += s.replace('__tipo__',
                             lattes.renomeia[tipo]).replace('__tipo2__', tamanho).replace('__tipo3__', tamanhoStr)

        if len(ss0) < 100:
            ss0 = 'sem dados'

        with open('./texLattes/' + lattes.renomeia[tipo] + tamanho + '.tex', 'w') as f:
            f.writelines(ss0)
        f.close()

    def pegaEventos(tipo):
        ss0 = '\\begin{enumerate}'
        ssLista = []
        for tipoEvento in lattes.eventos:
            evento = ["PARTICIPACAO-EM-" + tipoEvento,
                      "DADOS-BASICOS-DA-PARTICIPACAO-EM-" + tipoEvento,
                      "DETALHAMENTO-DA-PARTICIPACAO-EM-" + tipoEvento,
                      "PARTICIPANTE-DE-EVENTOS-CONGRESSOS" + tipoEvento]
            d = lattes.jsonLattes["CURRICULO-VITAE"]["DADOS-COMPLEMENTARES"]
            for k, v in d.items():
                if k == "PARTICIPACAO-EM-EVENTOS-CONGRESSOS":
                    for k0, v0 in d[k].items():
                        if k0 == evento[0] and isinstance(v0, list):
                            for v1 in v0:
                                # print()
                                # print(k0)
                                # print(v1)

                                forma = v1[evento[1]]['@FORMA-PARTICIPACAO']
                                if forma == tipo:

                                    ss = '\n\n\\item '
                                    titulo = v1[evento[1]]["@TITULO"]
                                    if titulo:
                                        ss += titulo + '. '
                                    ss += v1[evento[2]
                                             ]["@NOME-DO-EVENTO"].replace('&', '\&') + '. '
                                    ano = v1[evento[1]]["@ANO"]
                                    t = v1[evento[2]]["@CIDADE-DO-EVENTO"]
                                    if t:
                                        ss += t + '. '
                                    ss += ano + ' ('
                                    ss += v1[evento[1]]["@NATUREZA"].lower().replace('simposio', 'simpósio').replace('seminario', 'seminário') + \
                                        '). '
                                    t = v1[evento[1]]['@TIPO-PARTICIPACAO']
                                    if t:
                                        ss += t + '. '
                                    ss += lattes.pegaIDbib(titulo)
                                    ssLista.append([int(ano), ss])

        vSort = sorted(ssLista, key=lambda x: (-x[0], x[1]))
        ss0 += ''.join([v[1] for v in vSort])
        ss0 += '\n\n\\end{enumerate}\n'

        v0 = sorted([v[0] for v in vSort], reverse=True)
        if len(v0) > lattes.desenhaGraficos:  # desenha gráficos

            s = '''
A Figura \\ref{figs:eventos__tipo__} mostra o número de eventos como __tipo__ por ano.
\\begin{figure}[!h]
\centering
\includegraphics[width=0.8\\textwidth]{figs/Eventos__tipo__.png}
\caption{Eventos por ano (__tipo__)}
\label{figs:eventos__tipo__}
\end{figure}
'''
            ss0 += s.replace('__tipo__', tipo)

            eventosAno = {i: v0.count(i) for i in set(v0)}
            x = sorted(list(eventosAno.keys()), reverse=True)
            frequencia = [eventosAno[i] for i in x]
            x = [str(i) for i in x]

            plt.figure(figsize=lattes.figsize)
            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelrotation=90)
            #ax.set_title('Eventos por ano (' + tipo + ')')
            ax.set_ylabel("Quantidade")
            # ax.set_xlabel('Qualis')
            ax.set_ylim([0, int(1 + 1.1 * max(frequencia))])

            pps = ax.bar(x, frequencia, label='population')

            plt.savefig('figs/Eventos' + tipo + '.png')
            plt.close()

        if len(ss0) < 100:
            ss0 = 'sem dados'

        with open('./texLattes/Eventos' + tipo + '.tex', 'w') as f:
            f.writelines(ss0)
        f.close()

    def pegaApresentacoes():
        evento = ["APRESENTACAO-DE-TRABALHO",
                  "DADOS-BASICOS-DA-APRESENTACAO-DE-TRABALHO",
                  "DETALHAMENTO-DA-APRESENTACAO-DE-TRABALHO"]
        d = lattes.jsonLattes["CURRICULO-VITAE"]["PRODUCAO-TECNICA"]

        if not d:
            with open('./texLattes/Apresentacoes.tex', 'w') as f:
                f.writelines('')
            f.close()
            return ''
        ssLista = []
        ss0 = '\\begin{enumerate}'
        for k, v in d.items():
            if k == "DEMAIS-TIPOS-DE-PRODUCAO-TECNICA":
                for k0, v0 in d[k].items():
                    if k0 == evento[0] and isinstance(v0, list):
                        for v1 in v0:
                            ss = '\n\n\\item '
                            titulo = v1[evento[1]]["@TITULO"]
                            if titulo:
                                ss += titulo + '. '
                            ss += v1[evento[2]
                                     ]["@NOME-DO-EVENTO"].replace('&', '\&') + '. '
                            ano = v1[evento[1]]["@ANO"]
                            t = v1[evento[2]]["@CIDADE-DA-APRESENTACAO"]
                            if t:
                                ss += t + '. '
                            ss += ano + ' ('
                            ss += v1[evento[1]]["@NATUREZA"].lower().replace('simposio', 'simpósio').replace('seminario', 'seminário') + \
                                '). '
                            ss += lattes.pegaIDbib(titulo)
                            ssLista.append([int(ano), ss])

        vSort = sorted(ssLista, key=lambda x: (-x[0], x[1]))
        ss0 += ''.join([v[1] for v in vSort])
        ss0 += '\n\n\\end{enumerate}\n'

        v0 = sorted([v[0] for v in vSort], reverse=True)
        if len(v0) > lattes.desenhaGraficos:  # desenha gráficos

            s = '''
A Figura \\ref{figs:apresentacoes} mostra o número de apresentações por ano.
\\begin{figure}[!h]
\centering
\includegraphics[width=0.8\\textwidth]{figs/Apresentacoes.png}
\caption{Apresentações por ano}
\label{figs:apresentacoes}
\end{figure}
'''
            ss0 += s  # .replace('__tipo__', tipo)

            apresentacoesAno = {i: v0.count(i) for i in set(v0)}
            x = sorted(list(apresentacoesAno.keys()), reverse=True)
            frequencia = [apresentacoesAno[i] for i in x]
            x = [str(i) for i in x]

            plt.figure(figsize=lattes.figsize)
            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelrotation=90)
            #ax.set_title('Apresentações por ano')
            ax.set_ylabel("Quantidade")
            # ax.set_xlabel('Qualis')
            ax.set_ylim([0, int(1 + 1.1 * max(frequencia))])

            pps = ax.bar(x, frequencia, label='population')

            plt.savefig('figs/Apresentacoes.png')
            plt.close()

        with open('./texLattes/Apresentacoes.tex', 'w') as f:
            f.writelines(ss0)
        f.close()

    def pegaPublicacoes(tipo):
        if tipo == 'LIVROS':
            publicacoes = [tipo+"-PUBLICADO-OU-ORGANIZADO",
                           "DADOS-BASICOS-DO-"+tipo[:-1],
                           "DETALHAMENTO-DO-" + tipo[:-1]]
        else:
            publicacoes = [tipo+"-PUBLICADO",
                           "DADOS-BASICOS-DO-"+tipo[:-1],
                           "DETALHAMENTO-DO-" + tipo[:-1]]
        dicPub = {}
        dicPub['LIVROS'] = "LIVROS-PUBLICADOS-OU-ORGANIZADOS"
        dicPub['CAPITULOS'] = "CAPITULOS-DE-LIVROS-PUBLICADOS"

        d = lattes.jsonLattes["CURRICULO-VITAE"]["PRODUCAO-BIBLIOGRAFICA"]

        if not d:
            with open('./texLattes/Publicacoes'+tipo+'.tex', 'w') as f:
                f.writelines('sem dados em publicacoes:' + tipo)
            f.close()
            return ''
        ssLista = []
        ss0 = '\\begin{enumerate}'
        for k, v in d.items():
            if k == "LIVROS-E-CAPITULOS":
                for k0, v0 in d[k].items():
                    if k0 == dicPub[tipo] and isinstance(v0, dict):
                        for k1, v1 in v0.items():
                            if isinstance(v1, list):
                                for v2 in v1:
                                    ss = '\n\n\\item '
                                    if tipo == 'LIVROS':
                                        titulo = v2[publicacoes[1]
                                                    ]["@TITULO-DO-LIVRO"]
                                    else:
                                        titulo = v2[publicacoes[1]
                                                    ]["@TITULO-DO-CAPITULO-DO-LIVRO"]
                                    if titulo:
                                        ss += titulo + '. '

                                    ano = v2[publicacoes[1]]["@ANO"]

                                    ss += ano + '. '
                                    ss += lattes.pegaIDbib(titulo)
                                    ssLista.append([int(ano), ss])

        vSort = sorted(ssLista, key=lambda x: (-x[0], x[1]))
        ss0 += ''.join([v[1] for v in vSort])
        ss0 += '\n\n\\end{enumerate}\n'

        v0 = sorted([v[0] for v in vSort], reverse=True)
        if len(v0) > lattes.desenhaGraficos:  # desenha gráficos

            s = '''
A Figura \\ref{figs:publicacoes__tipo__} mostra as publicações (__tipo1__) por ano.
\\begin{figure}[!h]
\centering
\includegraphics[width=0.8\\textwidth]{figs/Publicacoes__tipo__.png}
\caption{Publicações (__tipo1__)}
\label{figs:publicacoes__tipo__}
\end{figure}
'''
            ss0 += s.replace('__tipo__', tipo
                             ).replace('__tipo1__', lattes.renomeia[tipo])

            apresentacoesAno = {i: v0.count(i) for i in set(v0)}
            x = sorted(list(apresentacoesAno.keys()), reverse=True)
            frequencia = [apresentacoesAno[i] for i in x]
            x = [str(i) for i in x]

            plt.figure(figsize=lattes.figsize)
            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelrotation=90)
            #ax.set_title(f'Publicações ({lattes.renomeia[tipo]})')
            ax.set_ylabel("Quantidade")
            # ax.set_xlabel('Qualis')
            ax.set_ylim([0, int(1 + 1.1 * max(frequencia))])

            pps = ax.bar(x, frequencia, label='population')

            plt.savefig('figs/Publicacoes'+tipo+'.png')
            plt.close()

        if len(ss0) < 100:
            with open('./texLattes/Publicacoes'+tipo+'.tex', 'w') as f:
                f.writelines('sem dados em publicacoes:' + tipo)
            f.close()
            return ''
        else:
            with open('./texLattes/Publicacoes'+tipo+'.tex', 'w') as f:
                f.writelines(ss0)
            f.close()

    def pegaProducoesTecnicas(tipo):

        # "PRODUCAO-TECNICA": {
        #     "SOFTWARE": [
        #       {
        #         "@SEQUENCIA-PRODUCAO": "15",
        #       "DADOS-BASICOS-DO-SOFTWARE":
        # DETALHAMENTO-DO-SOFTWARE

        if tipo == 'SOFTWARE':
            producoes = [tipo+"-PUBLICADO-OU-ORGANIZADO",
                         "DADOS-BASICOS-DO-"+tipo,
                         "DETALHAMENTO-DO-" + tipo,
                         "AUTORES"]

        dicPub = {}
        dicPub['SOFTWARE'] = "SOFTWARE"
        dicPub['TRABALHO-TECNICO'] = "TRABALHO-TECNICO"
        dicPub['DEMAIS-TIPOS-DE-PRODUCAO-TECNICA'] = "DEMAIS-TIPOS-DE-PRODUCAO-TECNICA"

        d = lattes.jsonLattes["CURRICULO-VITAE"]["PRODUCAO-TECNICA"]

        if not d:
            with open('./texLattes/ProducoesTecnicas'+tipo+'.tex', 'w') as f:
                f.writelines('sem dados em ProducoesTecnicas:' + tipo)
            f.close()
            return ''
        ssLista = []
        ss0 = '\\begin{enumerate}'
        for k, v in d.items():
            # print(k)
            if k == dicPub[tipo] and isinstance(v, list):
                for v2 in d[k]:
                    if "REGISTRO-OU-PATENTE" in v2[producoes[2]].keys():
                        ss = '\n\n\\item '
                        if tipo == 'SOFTWARE':
                            titulo = v2[producoes[1]
                                        ]["@TITULO-DO-SOFTWARE"]

                        if titulo:
                            ss += titulo + '. '

                        registro = v2[producoes[2]
                                      ]["REGISTRO-OU-PATENTE"]["@CODIGO-DO-REGISTRO-OU-PATENTE"]
                        if registro:
                            ss += "Registro: " + registro + '. '

                        instituicao = v2[producoes[2]
                                         ]["REGISTRO-OU-PATENTE"]["@INSTITUICAO-DEPOSITO-REGISTRO"]
                        if instituicao:
                            ss += instituicao + '. '

                        ano = v2[producoes[1]]["@ANO"]

                        ss += ano + '. '
                        ss += lattes.pegaIDbib(titulo)

                        autores = []

                        if isinstance(v2, list):
                            for a in v2[producoes[3]]:
                                if a['@NOME-PARA-CITACAO']:
                                    a0 = a['@NOME-PARA-CITACAO'].upper()
                                    ss += a0 + "; "
                                    autores.append(a0)
                        elif 'AUTORES' in v2.keys() and v2['AUTORES']:
                            for a in v2['AUTORES']:
                                if isinstance(a, dict):
                                    a0 = a['@NOME-PARA-CITACAO'].upper() # <<< ERRO
                                    ss += a0 + "; "
                                    autores.append(a0)
                                else:
                                    autores.append('ERRO 1255 !!!; ')

                        ss = ss[:-2] + '. '
                        ssLista.append([int(ano), ss])

        vSort = sorted(ssLista, key=lambda x: (-x[0], x[1]))
        ss0 += ''.join([v[1] for v in vSort])
        ss0 += '\n\n\\end{enumerate}\n'

        v0 = sorted([v[0] for v in vSort], reverse=True)
        if len(v0) > lattes.desenhaGraficos:  # desenha gráficos

            s = '''
A Figura \\ref{figs:ProducoesTecnicas__tipo__} mostra as produções técnicas (__tipo1__) por ano.
\\begin{figure}[!h]
\centering
\includegraphics[width=0.8\\textwidth]{figs/ProducoesTecnicas__tipo__.png}
\caption{Produções Técnicas (__tipo1__)}
\label{figs:ProducoesTecnicas__tipo__}
\end{figure}
'''
            ss0 += s.replace('__tipo__', tipo
                             ).replace('__tipo1__', lattes.renomeia[tipo])

            apresentacoesAno = {i: v0.count(i) for i in set(v0)}
            x = sorted(list(apresentacoesAno.keys()), reverse=True)
            frequencia = [apresentacoesAno[i] for i in x]
            x = [str(i) for i in x]

            plt.figure(figsize=lattes.figsize)
            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelrotation=90)
            #ax.set_title(f'Produções Técnicas ({lattes.renomeia[tipo]})')
            ax.set_ylabel("Quantidade")
            # ax.set_xlabel('Qualis')
            ax.set_ylim([0, int(1 + 1.1 * max(frequencia))])

            pps = ax.bar(x, frequencia, label='population')

            plt.savefig('figs/ProducoesTecnicas'+tipo+'.png')
            plt.close()

        with open('./texLattes/ProducoesTecnicas'+tipo+'.tex', 'w') as f:
            f.writelines(ss0)
        f.close()

    def pegaPremios():
        # DADOS-GERAIS
        #   "PREMIOS-TITULOS": {
        #     "PREMIO-TITULO": [
        #       {
        #         "@NOME-DO-PREMIO-OU-TITULO": "Primeiro lugar no Concurso de Software do IME",
        #         "@NOME-DA-ENTIDADE-PROMOTORA": "USP",
        #         "@ANO-DA-PREMIACAO": "1996",

        if not "PREMIOS-TITULOS" in lattes.jsonLattes["CURRICULO-VITAE"]["DADOS-GERAIS"].keys() or not lattes.jsonLattes["CURRICULO-VITAE"]["DADOS-GERAIS"]["PREMIOS-TITULOS"]:
            with open('./texLattes/Premios.tex', 'w') as f:
                f.writelines('sem dados em Premios')
            f.close()
            return ''

        d = lattes.jsonLattes["CURRICULO-VITAE"]["DADOS-GERAIS"]["PREMIOS-TITULOS"]

        ssLista = []
        ss0 = '\\begin{enumerate}'
        for k, v in d.items():
            if isinstance(v, list):
                for v2 in v:
                    ss = '\n\n\\item '

                    titulo = v2["@NOME-DO-PREMIO-OU-TITULO"]
                    if titulo:
                        ss += titulo.replace('&quot;', '') + '. '

                    ano = v2['@ANO-DA-PREMIACAO']
                    ss += ano + '. '

                    entidade = v2['@NOME-DA-ENTIDADE-PROMOTORA']
                    ss += entidade + '. '

                    ssLista.append([int(ano), ss])

        vSort = sorted(ssLista, key=lambda x: (-x[0], x[1]))
        ss0 += ''.join([v[1] for v in vSort])
        ss0 += '\n\n\\end{enumerate}\n'

        v0 = sorted([v[0] for v in vSort], reverse=True)
        if len(v0) > lattes.desenhaGraficos:  # desenha gráficos

            s = '''
A Figura \\ref{figs:Premios} mostra o número de prêmios por ano.
\\begin{figure}[!h]
\centering
\includegraphics[width=0.8\\textwidth]{figs/Premios.png}
\caption{Prêmios por ano}
\label{figs:Premios}
\end{figure}
'''
            ss0 += s  # .replace('__tipo__', tipo).replace('__tipo1__', lattes.renomeia[tipo])

            apresentacoesAno = {i: v0.count(i) for i in set(v0)}
            x = sorted(list(apresentacoesAno.keys()), reverse=True)
            frequencia = [apresentacoesAno[i] for i in x]
            x = [str(i) for i in x]

            plt.figure(figsize=lattes.figsize)
            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelrotation=90)
            #ax.set_title(f'Prêmios por ano')
            ax.set_ylabel("Quantidade")
            # ax.set_xlabel('Qualis')
            ax.set_ylim([0, int(1 + 1.1 * max(frequencia))])

            pps = ax.bar(x, frequencia, label='population')

            plt.savefig('figs/Premios.png')
            plt.close()

        with open('./texLattes/Premios.tex', 'w') as f:
            f.writelines(ss0)
        f.close()

    def pegaDadosBancas(tipo):
        bancas = dict()
        bancas["Doutorado"] = ["PARTICIPACAO-EM-BANCA-DE-DOUTORADO",
                               "DADOS-BASICOS-DA-PARTICIPACAO-EM-BANCA-DE-DOUTORADO",
                               "DETALHAMENTO-DA-PARTICIPACAO-EM-BANCA-DE-DOUTORADO"]
        bancas["Mestrado"] = ["PARTICIPACAO-EM-BANCA-DE-MESTRADO",
                              "DADOS-BASICOS-DA-PARTICIPACAO-EM-BANCA-DE-MESTRADO",
                              "DETALHAMENTO-DA-PARTICIPACAO-EM-BANCA-DE-MESTRADO"]
        bancas["Qualificacao"] = ["PARTICIPACAO-EM-BANCA-DE-EXAME-QUALIFICACAO",
                                  "DADOS-BASICOS-DA-PARTICIPACAO-EM-BANCA-DE-EXAME-QUALIFICACAO",
                                  "DETALHAMENTO-DA-PARTICIPACAO-EM-BANCA-DE-EXAME-QUALIFICACAO"]
        bancas["Especializacao"] = ["PARTICIPACAO-EM-BANCA-DE-APERFEICOAMENTO-ESPECIALIZACAO",
                                    "DADOS-BASICOS-DA-PARTICIPACAO-EM-BANCA-DE-APERFEICOAMENTO-ESPECIALIZACAO",
                                    "DETALHAMENTO-DA-PARTICIPACAO-EM-BANCA-DE-APERFEICOAMENTO-ESPECIALIZACAO"]
        bancas["Graduacao"] = ["PARTICIPACAO-EM-BANCA-DE-GRADUACAO",
                               "DADOS-BASICOS-DA-PARTICIPACAO-EM-BANCA-DE-GRADUACAO",
                               "DETALHAMENTO-DA-PARTICIPACAO-EM-BANCA-DE-GRADUACAO"]

        d = lattes.jsonLattes["CURRICULO-VITAE"]["DADOS-COMPLEMENTARES"]

        if not d:
            with open('./texLattes/Bancas' + tipo + '.tex', 'w') as f:
                f.writelines('')
            f.close()
            return ''

        ss0 = '\\begin{enumerate}'
        vo = bancas[tipo]
        ssLista = []
        for k, v in d.items():
            if k == "PARTICIPACAO-EM-BANCA-TRABALHOS-CONCLUSAO":
                for k0, v0 in d[k].items():
                    # print(k0)
                    if k0 == vo[0]:
                        if isinstance(v0, list):
                            for v1 in v0:
                                ss = '\n\n\\item '
                                ss += v1[vo[2]
                                         ]["@NOME-DO-CANDIDATO"] + '. '
                                ss += v1[vo[1]
                                         ]["@TITULO"] + '. '
                                ano = v1[vo[1]]["@ANO"]
                                ss += ano + '. '
                                ss += v1[vo[1]]["@NATUREZA"] + ' ('
                                ss += v1[vo[2]]["@NOME-CURSO"] + ') - '
                                ss += v1[vo[2]]["@NOME-INSTITUICAO"] + '. '
                                ssLista.append([int(ano), ss])
                        else:
                            ss = '\n\n\\item '
                            ss += v0[vo[2]
                                     ]["@NOME-DO-CANDIDATO"] + '. '
                            ss += v0[vo[1]
                                     ]["@TITULO"] + '. '
                            ano = v0[vo[1]]["@ANO"]
                            ss += ano + '. '
                            ss += v0[vo[1]]["@NATUREZA"] + ' ('
                            ss += v0[vo[2]]["@NOME-CURSO"] + ') - '
                            ss += v0[vo[2]]["@NOME-INSTITUICAO"] + '. '
                            ssLista.append([int(ano), ss])

        vSort = sorted(ssLista, key=lambda x: (-x[0], x[1]))
        ss0 += ''.join([v[1] for v in vSort])
        ss0 += '\n\n\\end{enumerate}\n'

        v0 = sorted([v[0] for v in vSort], reverse=True)
        if len(v0) > lattes.desenhaGraficos:  # desenha gráficos

            s = '''
A Figura \\ref{figs:Bancas__tipo__} mostra o número participações em bancas (__tipo__) por ano.
\\begin{figure}[!h]
\centering
\includegraphics[width=0.8\\textwidth]{figs/Bancas__tipo__.png}
\caption{Bancas (__tipo__) por ano}
\label{figs:Bancas__tipo__}
\end{figure}
'''
            ss0 += s.replace('__tipo__', tipo)

            apresentacoesAno = {i: v0.count(i) for i in set(v0)}
            x = sorted(list(apresentacoesAno.keys()), reverse=True)
            frequencia = [apresentacoesAno[i] for i in x]
            x = [str(i) for i in x]

            plt.figure(figsize=lattes.figsize)
            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelrotation=90)
            #ax.set_title(f'Bancas ({tipo}) por ano')
            ax.set_ylabel("Quantidade")
            # ax.set_xlabel('Qualis')
            ax.set_ylim([0, int(1 + 1.1 * max(frequencia))])

            pps = ax.bar(x, frequencia, label='population')

            plt.savefig(f'figs/Bancas{tipo}.png')
            plt.close()

        if len(ss0) < 100:
            ss0 = 'sem bancas - ' + tipo
        with open('./texLattes/Bancas' + tipo + '.tex', 'w') as f:
            f.writelines(ss0)
        f.close()

    # --- Função Auxiliar ---
    @staticmethod
    def to_list(value):
        """Garante que o valor de entrada seja sempre uma lista."""
        if isinstance(value, list):
            return value
        # Se o valor for None (não encontrado), retorna uma lista vazia
        elif value is None:
            return []
        # Se for um único item (dicionário), coloca-o dentro de uma lista
        else:
            return [value]


    def pegaProjetosPesquisa():
        """
        Extrai, formata e salva os projetos de pesquisa do currículo Lattes,
        incluindo detalhes e destacando o coordenador do projeto.
        """
        dados_gerais = lattes.jsonLattes.get("CURRICULO-VITAE", {}).get("DADOS-GERAIS", {})
        atuacoes_profissionais = dados_gerais.get("ATUACOES-PROFISSIONAIS", {})

        nome_pesquisador = dados_gerais.get("@NOME-COMPLETO", "Pesquisador Principal")

        ssLista = []
        lista_atuacoes = lattes.to_list(atuacoes_profissionais.get("ATUACAO-PROFISSIONAL"))

        for atuacao in lista_atuacoes:
            atividades_participacao = atuacao.get("ATIVIDADES-DE-PARTICIPACAO-EM-PROJETO")
            if not atividades_participacao:
                continue

            lista_participacoes = lattes.to_list(atividades_participacao.get("PARTICIPACAO-EM-PROJETO"))

            for participacao in lista_participacoes:
                lista_projetos_pesquisa = lattes.to_list(participacao.get("PROJETO-DE-PESQUISA"))

                for projeto in lista_projetos_pesquisa:
                    nome_projeto = projeto.get("@NOME-DO-PROJETO", "Nome não informado")
                    ano_inicio = projeto.get("@ANO-INICIO", "")
                    ano_fim = projeto.get("@ANO-FIM", "")
                    natureza = projeto.get("@NATUREZA", "")
                    descricao = projeto.get("@DESCRICAO-DO-PROJETO", "")
                    eh_coordenador = projeto.get("@FLAG-RESPONSAVEL", "NAO") == "SIM"

                    situacao = ""
                    if ano_fim:
                        try:
                            if int(ano_fim) < datetime.now().year:
                                situacao = "Concluído"
                            else:
                                situacao = "Em andamento"
                        except (ValueError, TypeError):
                            situacao = "Situação indefinida"
                    elif ano_inicio:
                        situacao = "Em andamento"

                    # Extrai a equipe mantendo os dados completos de cada integrante
                    equipe_projeto = projeto.get("EQUIPE-DO-PROJETO", {})
                    lista_integrantes = lattes.to_list(equipe_projeto.get("INTEGRANTES-DO-PROJETO"))

                    financiadores_projeto = projeto.get("FINANCIADORES-DO-PROJETO", {})
                    lista_financiadores = lattes.to_list(financiadores_projeto.get("FINANCIADOR-DO-PROJETO"))
                    nomes_financiadores = [f.get("@NOME-INSTITUICAO", "") for f in lista_financiadores if f.get("@NOME-INSTITUICAO")]

                    alunos_parts = []
                    if 'ALUNOS-ENVOLVIDOS' in projeto:
                        alunos_info = projeto["ALUNOS-ENVOLVIDOS"]
                        if alunos_info.get('@NUMERO-ALUNOS-GRADUACAO', '0') != '0': alunos_parts.append(f"Graduação ({alunos_info['@NUMERO-ALUNOS-GRADUACAO']})")
                        if alunos_info.get('@NUMERO-ALUNOS-MESTRADO', '0') != '0': alunos_parts.append(f"Mestrado ({alunos_info['@NUMERO-ALUNOS-MESTRADO']})")
                        if alunos_info.get('@NUMERO-ALUNOS-DOUTORADO', '0') != '0': alunos_parts.append(f"Doutorado ({alunos_info['@NUMERO-ALUNOS-DOUTORADO']})")

                    producoes_ct = projeto.get("PRODUCOES-CT-DO-PROJETO", {})
                    num_producoes = len(lattes.to_list(producoes_ct.get("PRODUCAO-CT-DO-PROJETO")))

                    # --- Montagem da string LaTeX no novo formato ---
                    ss = f'\n\n\\item \\textbf{{{nome_projeto}}}'

                    details1 = []
                    if ano_inicio:
                        periodo_str = f"{ano_inicio} -- {ano_fim}" if ano_fim else ano_inicio
                        details1.append(f"\\textbf{{Período:}} {periodo_str}")
                    if situacao: details1.append(f"\\textbf{{Situação:}} {situacao}")
                    if natureza: details1.append(f"\\textbf{{Natureza:}} {natureza}")
                    if details1: ss += '\n\\par\n' + '. '.join(details1) + '.'

                    if descricao: ss += f'\n\\par\n\\textbf{{Descrição:}} {descricao}'

                    # --- INÍCIO DA ALTERAÇÃO ---
                    # Bloco: Integrantes com destaque para o Coordenador
                    integrantes_formatado = []

                    # 1. Adiciona o dono do currículo, verificando se ele é o coordenador
                    if eh_coordenador:
                        # Formata com negrito e adiciona o texto (Coordenador)
                        integrantes_formatado.append(f"\\textbf{{{nome_pesquisador} (Coordenador)}}")
                    else:
                        integrantes_formatado.append(nome_pesquisador)

                    # 2. Adiciona os outros membros, verificando se algum deles é o coordenador
                    for integrante in lista_integrantes:
                        nome_membro = integrante.get("@NOME-COMPLETO", "")
                        # Garante que o nome existe e não é uma duplicata do dono do currículo
                        if nome_membro and nome_membro != nome_pesquisador:
                            is_membro_coordenador = integrante.get("@FLAG-RESPONSAVEL", "NAO") == "SIM"
                            if is_membro_coordenador:
                                integrantes_formatado.append(f"\\textbf{{{nome_membro} (Coordenador)}}")
                            else:
                                integrantes_formatado.append(nome_membro)

                    if integrantes_formatado:
                        ss += f'\n\\par\n\\textbf{{Integrantes:}} {", ".join(integrantes_formatado)}.'
                    # --- FIM DA ALTERAÇÃO ---

                    if alunos_parts: ss += f'\n\\par\n\\textbf{{Alunos envolvidos:}} {", ".join(alunos_parts)}.'

                    if nomes_financiadores: ss += f'\n\\par\n\\textbf{{Financiador(es):}} {", ".join(nomes_financiadores)}.'

                    if num_producoes > 0: ss += f'\n\\par\n\\textbf{{Número de produções C, T \\& A:}} {num_producoes}.'

                    try:
                        ano_int = int(ano_inicio) if ano_inicio else 0
                    except (ValueError, TypeError):
                        ano_int = 0

                    ssLista.append([ano_int, ss])

        # --- O restante da função (geração de arquivo e gráfico) permanece o mesmo ---
        if not ssLista:
            print("Nenhum projeto de pesquisa encontrado.")
            os.makedirs('texLattes', exist_ok=True)
            with open('./texLattes/ProjetosPesquisa.tex', 'w', encoding='utf-8') as f:
                f.write('')
            return ''

        vSort = sorted(ssLista, key=lambda x: (-x[0], x[1]))
        ss0 = '\\begin{enumerate}'
        ss0 += ''.join([item[1] for item in vSort])
        ss0 += '\n\n\\end{enumerate}\n'

        anos = [item[0] for item in vSort if item[0] > 0]
        if anos and len(anos) > lattes.desenhaGraficos:
            s = '''
    A Figura \\ref{figs:ProjetosPesquisa} mostra o número de projetos de pesquisa por ano.
    \\begin{figure}[!h]
    \\centering
    \\includegraphics[width=0.8\\textwidth]{figs/ProjetosPesquisa.png}
    \\caption{Projetos de pesquisa por ano}
    \\label{figs:ProjetosPesquisa}
    \\end{figure}
    '''
            ss0 += s
            freqAno = {i: anos.count(i) for i in set(anos)}
            x = sorted(list(freqAno.keys()), reverse=True)
            frequencia = [freqAno[i] for i in x]
            x_labels = [str(i) for i in x]
            plt.figure(figsize=lattes.figsize)
            fig, ax = plt.subplots()
            ax.bar(x_labels, frequencia)
            ax.set_ylabel("Quantidade")
            ax.set_ylim([0, int(1 + 1.1 * max(frequencia))])
            ax.tick_params(axis='x', rotation=90)
            plt.tight_layout()
            os.makedirs('figs', exist_ok=True)
            plt.savefig('figs/ProjetosPesquisa.png')
            plt.close()

        if len(ss0) < 100: ss0 = 'sem projetos de pesquisa'

        os.makedirs('texLattes', exist_ok=True)
        with open('./texLattes/ProjetosPesquisa.tex', 'w', encoding='utf-8') as f:
            f.write(ss0)

        print(f"{len(ssLista)} projetos de pesquisa encontrados e arquivo 'ProjetosPesquisa.tex' gerado.")
        return ss0

'''
CURRICULO-VITAE
├── DADOS-GERAIS
│   ├── RESUMO-CV
│   ├── OUTRAS-INFORMACOES-RELEVANTES
│   ├── ENDERECO
│   │   ├── ENDERECO-PROFISSIONAL
│   │   └── ENDERECO-RESIDENCIAL
│   ├── FORMACAO-ACADEMICA-TITULACAO
│   │   ├── GRADUACAO
│   │   ├── MESTRADO
│   │   │   ├── PALAVRAS-CHAVE
│   │   │   ├── AREAS-DO-CONHECIMENTO
│   │   │   │   └── AREA-DO-CONHECIMENTO-1
│   │   │   └── SETORES-DE-ATIVIDADE
│   │   └── DOUTORADO
│   │       ├── PALAVRAS-CHAVE
│   │       ├── AREAS-DO-CONHECIMENTO
│   │       │   └── AREA-DO-CONHECIMENTO-1
│   │       └── SETORES-DE-ATIVIDADE
│   ├── ATUACOES-PROFISSIONAIS
│   │   └── ATUACAO-PROFISSIONAL
│   │       ├── VINCULOS
│   │       ├── ATIVIDADES-DE-DIRECAO-E-ADMINISTRACAO
│   │       │   └── DIRECAO-E-ADMINISTRACAO
│   │       ├── ATIVIDADES-DE-ENSINO
│   │       │   └── ENSINO
│   │       │       └── DISCIPLINA
│   │       ├── ATIVIDADES-DE-CONSELHO-COMISSAO-E-CONSULTORIA
│   │       │   └── CONSELHO-COMISSAO-E-CONSULTORIA
│   │       ├── ATIVIDADES-DE-PESQUISA-E-DESENVOLVIMENTO
│   │       │   └── PESQUISA-E-DESENVOLVIMENTO
│   │       │       └── LINHA-DE-PESQUISA
│   │       │           ├── PALAVRAS-CHAVE
│   │       │           └── AREAS-DO-CONHECIMENTO
│   │       │               └── AREA-DO-CONHECIMENTO-1
│   │       ├── ATIVIDADES-DE-EXTENSAO-UNIVERSITARIA
│   │       │   └── EXTENSAO-UNIVERSITARIA
│   │       └── ATIVIDADES-DE-PARTICIPACAO-EM-PROJETO
│   │           └── PARTICIPACAO-EM-PROJETO
│   │               └── PROJETO-DE-PESQUISA
│   │                   ├── EQUIPE-DO-PROJETO
│   │                   │   └── INTEGRANTES-DO-PROJETO
│   │                   ├── FINANCIADORES-DO-PROJETO
│   │                   │   └── FINANCIADOR-DO-PROJETO
│   │                   ├── PRODUCOES-CT-DO-PROJETO
│   │                   │   └── PRODUCAO-CT-DO-PROJETO
│   │                   └── ORIENTACOES
│   │                       └── ORIENTACAO
│   ├── AREAS-DE-ATUACAO
│   │   └── AREA-DE-ATUACAO
│   ├── IDIOMAS
│   │   └── IDIOMA
│   └── PREMIOS-TITULOS
│       └── PREMIO-TITULO
├── PRODUCAO-BIBLIOGRAFICA
│   ├── TRABALHOS-EM-EVENTOS
│   │   └── TRABALHO-EM-EVENTOS
│   │       ├── DADOS-BASICOS-DO-TRABALHO
│   │       ├── DETALHAMENTO-DO-TRABALHO
│   │       ├── AUTORES
│   │       ├── PALAVRAS-CHAVE
│   │       ├── AREAS-DO-CONHECIMENTO
│   │       │   └── AREA-DO-CONHECIMENTO-1
│   │       ├── SETORES-DE-ATIVIDADE
│   │       └── INFORMACOES-ADICIONAIS
│   ├── ARTIGOS-PUBLICADOS
│   │   └── ARTIGO-PUBLICADO
│   │       ├── DADOS-BASICOS-DO-ARTIGO
│   │       ├── DETALHAMENTO-DO-ARTIGO
│   │       ├── AUTORES
│   │       ├── PALAVRAS-CHAVE
│   │       └── AREAS-DO-CONHECIMENTO
│   │           └── AREA-DO-CONHECIMENTO-1
│   ├── LIVROS-E-CAPITULOS
│   │   ├── LIVROS-PUBLICADOS-OU-ORGANIZADOS
│   │   │   └── LIVRO-PUBLICADO-OU-ORGANIZADO
│   │   │       ├── DADOS-BASICOS-DO-LIVRO
│   │   │       ├── DETALHAMENTO-DO-LIVRO
│   │   │       ├── AUTORES
│   │   │       ├── PALAVRAS-CHAVE
│   │   │       └── AREAS-DO-CONHECIMENTO
│   │   │           └── AREA-DO-CONHECIMENTO-1
│   │   └── CAPITULOS-DE-LIVROS-PUBLICADOS
│   │       └── CAPITULO-DE-LIVRO-PUBLICADO
│   │           ├── DADOS-BASICOS-DO-CAPITULO
│   │           ├── DETALHAMENTO-DO-CAPITULO
│   │           ├── AUTORES
│   │           └── AREAS-DO-CONHECIMENTO
│   │               └── AREA-DO-CONHECIMENTO-1
│   ├── TEXTOS-EM-JORNAIS-OU-REVISTAS
│   │   └── TEXTO-EM-JORNAL-OU-REVISTA
│   │       ├── DADOS-BASICOS-DO-TEXTO
│   │       ├── DETALHAMENTO-DO-TEXTO
│   │       └── AUTORES
│   └── ARTIGOS-ACEITOS-PARA-PUBLICACAO
│       └── ARTIGO-ACEITO-PARA-PUBLICACAO
│           ├── DADOS-BASICOS-DO-ARTIGO
│           ├── DETALHAMENTO-DO-ARTIGO
│           └── AUTORES
├── PRODUCAO-TECNICA
│   ├── SOFTWARE
│   │   ├── DADOS-BASICOS-DO-SOFTWARE
│   │   ├── DETALHAMENTO-DO-SOFTWARE
│   │   │   └── REGISTRO-OU-PATENTE
│   │   ├── AUTORES
│   │   ├── PALAVRAS-CHAVE
│   │   ├── AREAS-DO-CONHECIMENTO
│   │   │   └── AREA-DO-CONHECIMENTO-1
│   │   ├── SETORES-DE-ATIVIDADE
│   │   └── INFORMACOES-ADICIONAIS
│   ├── TRABALHO-TECNICO
│   │   ├── DADOS-BASICOS-DO-TRABALHO-TECNICO
│   │   ├── DETALHAMENTO-DO-TRABALHO-TECNICO
│   │   ├── AUTORES
│   │   ├── PALAVRAS-CHAVE
│   │   ├── AREAS-DO-CONHECIMENTO
│   │   │   └── AREA-DO-CONHECIMENTO-1
│   │   ├── SETORES-DE-ATIVIDADE
│   │   └── INFORMACOES-ADICIONAIS
│   └── DEMAIS-TIPOS-DE-PRODUCAO-TECNICA
│       ├── APRESENTACAO-DE-TRABALHO
│       │   ├── DADOS-BASICOS-DA-APRESENTACAO-DE-TRABALHO
│       │   ├── DETALHAMENTO-DA-APRESENTACAO-DE-TRABALHO
│       │   ├── AUTORES
│       │   └── AREAS-DO-CONHECIMENTO
│       │       └── AREA-DO-CONHECIMENTO-1
│       └── CURSO-DE-CURTA-DURACAO-MINISTRADO
│           ├── DADOS-BASICOS-DE-CURSOS-CURTA-DURACAO-MINISTRADO
│           ├── DETALHAMENTO-DE-CURSOS-CURTA-DURACAO-MINISTRADO
│           ├── AUTORES
│           ├── PALAVRAS-CHAVE
│           ├── AREAS-DO-CONHECIMENTO
│           │   └── AREA-DO-CONHECIMENTO-1
│           └── INFORMACOES-ADICIONAIS
└── OUTRA-PRODUCAO
    ├── ORIENTACOES-CONCLUIDAS
    │   ├── ORIENTACOES-CONCLUIDAS-PARA-MESTRADO
    │   │   ├── DADOS-BASICOS-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO
    │   │   ├── DETALHAMENTO-DE-ORIENTACOES-CONCLUIDAS-PARA-MESTRADO
    │   │   ├── PALAVRAS-CHAVE
    │   │   └── AREAS-DO-CONHECIMENTO
    │   │       └── AREA-DO-CONHECIMENTO-1
    │   └── OUTRAS-ORIENTACOES-CONCLUIDAS
    │       ├── DADOS-BASICOS-DE-OUTRAS-ORIENTACOES-CONCLUIDAS
    │       ├── DETALHAMENTO-DE-OUTRAS-ORIENTACOES-CONCLUIDAS
    │       ├── PALAVRAS-CHAVE
    │       ├── AREAS-DO-CONHECIMENTO
    │       │   └── AREA-DO-CONHECIMENTO-1
    │       ├── SETORES-DE-ATIVIDADE
    │       └── INFORMACOES-ADICIONAIS
    └── DEMAIS-TRABALHOS
        ├── DADOS-BASICOS-DE-DEMAIS-TRABALHOS
        ├── DETALHAMENTO-DE-DEMAIS-TRABALHOS
        ├── AUTORES
        ├── PALAVRAS-CHAVE
        ├── AREAS-DO-CONHECIMENTO
        │   └── AREA-DO-CONHECIMENTO-1
        ├── SETORES-DE-ATIVIDADE
        └── INFORMACOES-ADICIONAIS
'''