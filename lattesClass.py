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


class lattes(object):

    #### INICIALIZATION ####
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
    renomeia["Dissertação de mestrado"] = "Dissertação de mestrado"
    renomeia["ORIENTACAO-DE-OUTRA-NATUREZA"] = "Orientação de outra natureza"
    renomeia["ORIENTADOR_PRINCIPAL"] = "Orientador principal"

    natureza = ["Doutorado", "Mestrado",
                "ORIENTACAO-DE-OUTRA-NATUREZA",
                "INICIACAO_CIENTIFICA",
                "TRABALHO_DE_CONCLUSAO_DE_CURSO_GRADUACAO",
                "MONOGRAFIA_DE_CONCLUSAO_DE_CURSO_APERFEICOAMENTO_E_ESPECIALIZACAO",
                "ORIENTACAO-DE-OUTRA-NATUREZA"]

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
                return '\cite{'+k+'}'
        return ''

    def lattes2bib():
        # crédito: https://arademaker.github.io/blog/2012/02/15/lattes-to-bibtex.html
        # lattes.lerConfigJson()
        id = lattes.jsonConfigura["NUMERO-IDENTIFICADOR"]
        os.system("git clone git@github.com:arademaker/SLattes.git")
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
        if not os.path.exists(id+lattes.arquivoConfiguraJson):
            print(f"\nERRO: {id}{lattes.arquivoConfiguraJson} não existe!\n")
            exit(0)
        f = open(lattes.arquivoConfiguraJson)
        lattes.jsonConfigura = json.load(f)
        return 1

    def rodaLatex(file='lattesMemorial.tex'):
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
            print("rm "+id+"*")
            os.system("rm "+id+"*")
        os.system("rm texLattes/*")
        os.system("rm figs/qualis*")
        os.system("rm figs/orient*")
        os.system("rm figs/evento*")
        os.system("rm figs/aprese*")
        os.system("rm data/novoQualis2017-2020.csv")
        os.system("rm extras/dados.tex")
        os.system("rm **/*.aux")
        os.system("rm **/*.fdb_latexmk")
        os.system("rm **/*.fls")
        os.system("rm **/*.log")
        os.system("rm -rf SLattes")
        os.system("rm mods-3-4*")
        print('\nlattes2memorial: Arquivos temporários removidos.\n')

    def saveJsonConfig(id):
        json_formatted_str = json.dumps(lattes.jsonConfigura, indent=2)
        with open(id+lattes.arquivoConfiguraJson, "w") as outfile:
            outfile.write(json_formatted_str)
        outfile.close()

    def criaConfiguraJson(id):
        import zipfile

        print('CV_'+id+'.zip')
        if os.path.exists('CV_'+id+'.zip'):
            with zipfile.ZipFile('CV_'+id+'.zip', "r") as zip_ref:
                zip_ref.extractall("./")
        else:
            print('ERRO: não existe zip do seu lattes, com nome:',
                  'CV_'+id+'.zip')
            exit(0)

        lattes.NUMERO_IDENTIFICADOR = id
        if not os.path.exists(id+lattes.arquivoConfiguraJson):
            lattes.jsonConfigura = dict()
            lattes.jsonConfigura["NUMERO-IDENTIFICADOR"] = id
            lattes.saveJsonConfig(id)

        f = open(id+lattes.arquivoConfiguraJson)
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

        lattes.jsonConfigura["QUALIS-REVISTA-URL"] = 'https://www.ufrgs.br/ppggeo/ppggeo/wp-content/uploads/2019/12/QUALIS-NOVO-1.pdf'
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
            periodo = ' ('+periodo[-13:-4]+')'
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

        lattes.jsonConfigura["QUALIS-EVENTO-URL"] = 'https://www.gov.br/capes/pt-br/centrais-de-conteudo/documentos/avaliacao/09012022_RELATORIOQUALISEVENTOS20172020COMPUTACAO.PDF'
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
            periodo = ' ('+periodo[-13:-4]+')'
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
        with open(f0[:-4]+".json", "w") as outfile:
            outfile.write(json_formatted_str)
        outfile.close()

    def verificaID():
        if lattes.jsonLattes['CURRICULO-VITAE']["@NUMERO-IDENTIFICADOR"] != lattes.jsonConfigura["NUMERO-IDENTIFICADOR"]:
            print(
                f"ERRO: ID de {lattes.arquivoConfiguraJson} é diferente do xml")
            exit(0)

    def pegaDadosGerais(id):
        if not os.path.exists(lattes.arquivoConfiguraJson):
            print(f"ERRO: {id}{lattes.arquivoConfiguraJson} não existe!")
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
        lattes.jsonConfigura["NOME-INSTITUICAO-EMPRESA"] = d0["ENDERECO"]["ENDERECO-PROFISSIONAL"]["@NOME-INSTITUICAO-EMPRESA"]
        lattes.jsonConfigura["CIDADE"] = d0["ENDERECO"]["ENDERECO-PROFISSIONAL"]["@CIDADE"]
        lattes.jsonConfigura["E-MAIL"] = d0["ENDERECO"]["ENDERECO-PROFISSIONAL"]["@E-MAIL"]
        s = lattes.jsonLattes['CURRICULO-VITAE']["@DATA-ATUALIZACAO"]
        lattes.jsonConfigura["DATA-ATUALIZACAO"] = s[:2]+'/'+s[2:4]+'/'+s[4:]

        if not "ATUACOES-PROFISSIONAIS" in lattes.jsonLattes['CURRICULO-VITAE']['DADOS-GERAIS'].keys():
            print("Sem Atuações Profissionais")
            return 1

        lattes.saveJsonConfig(lattes.NUMERO_IDENTIFICADOR)

        # "@NOME-ORGAO": "Centro de Matem\u00e1tica, Computa\u00e7\u00e3o e Cogni\u00e7\u00e3o",
        # "@CODIGO-UNIDADE": "",
        # "@NOME-UNIDADE": "",
        # "@LOGRADOURO-COMPLEMENTO": "Rua Santa Ad\u00e9lia, 166",
        # "@PAIS": "Brasil",
        # "@UF": "SP",
        # "@CEP": "09210170",
        # "@CIDADE": "Santo Andr\u00e9",
        # "@BAIRRO": "Bangu",
        # "@DDD": "11",
        # "@TELEFONE": "44371600",
        # "@RAMAL": "",
        # "@FAX": "",
        # "@CAIXA-POSTAL": "",
        # "@E-MAIL": "fzampirolli@ufabc.edu.br",

        # atuacoes = []
        # for p in lattes.jsonLattes['CURRICULO-VITAE']['DADOS-GERAIS']['ATUACOES-PROFISSIONAIS']['ATUACAO-PROFISSIONAL']:
        #     atuacoes.append(p['@NOME-INSTITUICAO'])
        # # print(atuacoes) # verificar manualmente qual é o índice da atuação prof. atual
        # atuacaoIndice = 7  # UFABC
        # lattes.jsonConfigura['ATUACAO-PROFISSIONAL'] = atuacoes[atuacaoIndice]
        # lattes.jsonConfigura['ANO-INICIO'] = lattes.jsonLattes['CURRICULO-VITAE']['DADOS-GERAIS'][
        #     'ATUACOES-PROFISSIONAIS']['ATUACAO-PROFISSIONAL'][atuacaoIndice]['VINCULOS']['@ANO-INICIO']

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
        with open(file[:-5]+'.tex', 'w') as fd:
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
            ss0 = '\\begin{enumerate}'
            d = lattes.jsonLattes["CURRICULO-VITAE"]["OUTRA-PRODUCAO"]
            vo = orientacoes[tipo]
            ssLista = []
            if not d:
                return ''
            for k, v in d.items():
                if k == "ORIENTACOES-CONCLUIDAS":
                    for k0, v0 in d[k].items():
                        if k0 == vo[0]:
                            for i in d[k][k0]:
                                if tipo in lattes.natureza[:2] or (tipo2 and tipo2 == i[vo[1]]["@NATUREZA"]):
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

            ts = ''
            if tipo2:
                ts += lattes.renomeia[tipo2]

            v0 = sorted([v[0] for v in vSort], reverse=True)
            if len(v0) > 2:  # desenha gráficos

                s = '''
A Figura \\ref{figs:orientacoes__tipo____tipo2__} mostra o número de orientações por ano de __tipo3__, 
considerando a data de início.
\\begin{figure}[h]
\centering
\includegraphics[width=0.8\\textwidth]{figs/orientacoes__tipo____tipo2__.png}
\caption{Orientações por Ano (__tipo3__)}
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

                plt.figure(figsize=[8, 5])
                fig, ax = plt.subplots()
                ax.tick_params(axis='x', labelrotation=90)
                if tipo2:
                    ax.set_title(
                        'Orientações por Ano (' + ts + ')')
                else:
                    ax.set_title('Orientações por Ano (' + tipo + ')')
                ax.set_ylabel("Quantidade")
                # ax.set_xlabel('Qualis')
                ax.set_ylim([0, int(1+1.1*max(frequencia))])

                pps = ax.bar(x, frequencia, label='population')

                plt.savefig('figs/orientacoes'+tipo + ts[:4]+'.png')
                plt.close()

            with open('./texLattes/Orientacoes'+tipo+ts[:4]+'.tex', 'w') as f:
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

        ss0 = '\\begin{enumerate}'
        d = lattes.jsonLattes["CURRICULO-VITAE"]["DADOS-COMPLEMENTARES"]
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

        with open('./texLattes/OrientacoesAndamento'+tipo+'.tex', 'w') as f:
            f.writelines(ss0)
        f.close()

    def pegaDadosArtigos(tipo='TRABALHO', tamanho="COMPLETO"):

        def ordenaArtigosAno(D, reverse=True):
            valores = [(p['DADOS-BASICOS-DO-'+tipo]['@ANO-DO-'+tipo], p)
                       for a, b in D.items() for p in b]
            return [t[1] for t in sorted(valores, key=lambda x: x[0], reverse=True)]

        if tipo == 'TRABALHO':
            if not lattes.jsonLattes['CURRICULO-VITAE']['PRODUCAO-BIBLIOGRAFICA']:
                return ''
            if not "TRABALHOS-EM-EVENTOS" in lattes.jsonLattes['CURRICULO-VITAE']['PRODUCAO-BIBLIOGRAFICA'].keys():
                print("Sem trabalhos em eventos")
                return 1
            D = lattes.jsonLattes['CURRICULO-VITAE']['PRODUCAO-BIBLIOGRAFICA']['TRABALHOS-EM-EVENTOS']
        else:
            if not lattes.jsonLattes['CURRICULO-VITAE']['PRODUCAO-BIBLIOGRAFICA']:
                return ''
            if not "ARTIGOS-PUBLICADOS" in lattes.jsonLattes['CURRICULO-VITAE']['PRODUCAO-BIBLIOGRAFICA'].keys():
                print("Sem artigos em revistas")
                return 1
            D = lattes.jsonLattes['CURRICULO-VITAE']['PRODUCAO-BIBLIOGRAFICA']['ARTIGOS-PUBLICADOS']

        D_order = ordenaArtigosAno(D)

        qualisAno = dict()
        ss0 = '\\begin{enumerate}'
        for p in D_order:
            if p['DADOS-BASICOS-DO-'+tipo]["@NATUREZA"] == tamanho:

                ss0 += '\n\n\\item '
                if p['DADOS-BASICOS-DO-'+tipo]['@DOI']:
                    s = p['DADOS-BASICOS-DO-'+tipo]['@DOI']
                    ss0 += '\\href{https://doi.org/' + s + \
                        '}{{\\color{white}\\hl{\\textbf{doi$>$}}}} '
                elif p['DADOS-BASICOS-DO-'+tipo]['@HOME-PAGE-DO-TRABALHO']:
                    ss0 += '\\href{' + p['DADOS-BASICOS-DO-'+tipo]['@HOME-PAGE-DO-TRABALHO'][1:-1] + \
                        '}{{\\color{yellow}\\hl{\\textbf{url$>$}}}} '
                ano = ''
                try:
                    ss0 += p['AUTORES']['@NOME-PARA-CITACAO'].upper()+"; "
                except:
                    pass
                for d in p['AUTORES']:
                    if isinstance(d, dict):
                        ss0 += d['@NOME-PARA-CITACAO'].upper()+"; "
                ss0 = ss0[: -2]+'. '

                for c, d in p['DADOS-BASICOS-DO-'+tipo].items():
                    if d and c[1:] == 'TITULO-DO-'+tipo:
                        ss0 += d + '. '
                        cite = lattes.pegaIDbib(d)
                    if d and c[1:] == 'ANO-DO-'+tipo:
                        ano = d

                for c, d in p['DETALHAMENTO-DO-'+tipo].items():
                    if d and c[1:] == 'TITULO-DO-PERIODICO-OU-REVISTA' or c[1:] == "NOME-DO-EVENTO":
                        ss0 += d.upper()
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

        ss0 += '\n\n\\end{enumerate}\n'

        ss0 = ss0.replace('&#8208;', '-').replace('&', '\&')

        try:
            qualisAno['C'] = qualisAno.pop('C,')  # rename
        except:
            pass

        if tamanho == "COMPLETO":

            # desenha figuras

            plt.figure(figsize=[8, 5])
            x = list(sorted(qualisAno.keys()))

            frequencia = [len(qualisAno[q]) for q in x]

            width = 0.35  # the width of the bars

            fig, ax = plt.subplots()
            ax.set_title('Artigos por Qualis em ' + lattes.renomeia[tipo])
            ax.set_ylabel("Quantidade")
            # ax.set_xlabel('Qualis')
            ax.set_ylim([0, int(1+1.1*max(frequencia))])

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

            plt.savefig('figs/qualis'+lattes.renomeia[tipo]+'.png')
            plt.close()

            s = '''
A Figura \\ref{figs:qualis__tipo__} mostra o número de artigos por Qualis em __tipo__.
\\begin{figure}[h]
\centering
\includegraphics[width=0.8\\textwidth]{figs/qualis__tipo__.png}
\caption{Artigos por Qualis em __tipo__}
\label{figs:qualis__tipo__}
\end{figure}
    '''
            ss0 += s.replace('__tipo__', lattes.renomeia[tipo])

        # Artigos com Qualis por ano
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
        plt.figure(figsize=[20, 10])
        # x = anos  # np.arange(len(anos))  # the label locations
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots()

        tamanhoStr = ''
        if tamanho == 'RESUMO':
            tamanhoStr += ' (Resumo)'

        ax.set_title('Artigos por Ano em ' +
                     lattes.renomeia[tipo] + tamanhoStr)
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
                        s += str(v.count(q))+q+'+'
                    else:
                        s += q+'+'
            tmax = max(tmax, len(s))
            vet.append(s[:-1])

        ax.set_ylim([0, 2*tmax + int(max(qualisAno3.values()))])

        c = 0
        for p in pps:
            height = p.get_height()
            ax.annotate('{}'.format(vet[c]),
                        xy=(p.get_x() + p.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points", rotation=90,
                        ha='center', va='bottom')
            c += 1

        plt.savefig('figs/qualis'+lattes.renomeia[tipo]+tamanho+'Ano.png')
        plt.close()

        s = '''
A Figura \\ref{figs:qualis__tipo____tipo2__Ano} mostra o número de artigos __tipo3__ 
com Qualis, se existirem por ano em __tipo__.
Considerar no eixo vertical o somatório de artigos, sendo A1=10, A2=9, $\cdots$, C=2, SQ=1.
Onde SQ é Sem Qualis e nesta figura tem peso de apenas uma unidade na vertical.
\\begin{figure}[h]
\centering
\includegraphics[width=0.8\\textwidth]{figs/qualis__tipo____tipo2__Ano.png}
\caption{Artigos por Ano em __tipo__ __tipo3__}
\label{figs:qualis__tipo____tipo2__Ano}
\end{figure}
'''
        ss0 += s.replace('__tipo__',
                         lattes.renomeia[tipo]).replace('__tipo2__', tamanho).replace('__tipo3__', tamanhoStr)

        with open('./texLattes/'+lattes.renomeia[tipo]+tamanho+'.tex', 'w') as f:
            f.writelines(ss0)
        f.close()

    def pegaEventos(tipo):
        ss0 = '\\begin{enumerate}'
        ssLista = []
        for tipoEvento in lattes.eventos:
            evento = ["PARTICIPACAO-EM-"+tipoEvento,
                      "DADOS-BASICOS-DA-PARTICIPACAO-EM-"+tipoEvento,
                      "DETALHAMENTO-DA-PARTICIPACAO-EM-"+tipoEvento,
                      "PARTICIPANTE-DE-EVENTOS-CONGRESSOS"+tipoEvento]
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
                                    ss += v1[evento[1]]["@NATUREZA"].lower() + \
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
        if len(v0) > 2:  # desenha gráficos

            s = '''
A Figura \\ref{figs:eventos__tipo__} mostra o número de eventos como __tipo__ por ano.
\\begin{figure}[h]
\centering
\includegraphics[width=0.8\\textwidth]{figs/eventos__tipo__.png}
\caption{Eventos por Ano (__tipo__)}
\label{figs:eventos__tipo__}
\end{figure}
'''
            ss0 += s.replace('__tipo__', tipo)

            eventosAno = {i: v0.count(i) for i in set(v0)}
            x = sorted(list(eventosAno.keys()), reverse=True)
            frequencia = [eventosAno[i] for i in x]
            x = [str(i) for i in x]

            plt.figure(figsize=[8, 5])
            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelrotation=90)
            ax.set_title('Eventos por Ano (' + tipo + ')')
            ax.set_ylabel("Quantidade")
            # ax.set_xlabel('Qualis')
            ax.set_ylim([0, int(1+1.1*max(frequencia))])

            pps = ax.bar(x, frequencia, label='population')

            plt.savefig('figs/eventos'+tipo + '.png')
            plt.close()

        with open('./texLattes/Eventos'+tipo+'.tex', 'w') as f:
            f.writelines(ss0)
        f.close()

    def pegaApresentacoes():
        ss0 = '\\begin{enumerate}'
        ssLista = []

        evento = ["APRESENTACAO-DE-TRABALHO",
                  "DADOS-BASICOS-DA-APRESENTACAO-DE-TRABALHO",
                  "DETALHAMENTO-DA-APRESENTACAO-DE-TRABALHO"]
        d = lattes.jsonLattes["CURRICULO-VITAE"]["PRODUCAO-TECNICA"]
        if not d:
            return ''
        for k, v in d.items():
            if k == "DEMAIS-TIPOS-DE-PRODUCAO-TECNICA":
                for k0, v0 in d[k].items():
                    if k0 == evento[0] and isinstance(v0, list):
                        for v1 in v0:
                            # print()
                            # print(k0)
                            # print(v1)

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
                            ss += v1[evento[1]]["@NATUREZA"].lower() + \
                                '). '
                            ss += lattes.pegaIDbib(titulo)
                            ssLista.append([int(ano), ss])

        vSort = sorted(ssLista, key=lambda x: (-x[0], x[1]))
        ss0 += ''.join([v[1] for v in vSort])
        ss0 += '\n\n\\end{enumerate}\n'

        v0 = sorted([v[0] for v in vSort], reverse=True)
        if len(v0) > 2:  # desenha gráficos

            s = '''
A Figura \\ref{figs:apresentacoes} mostra o número de apresentações por ano.
\\begin{figure}[h]
\centering
\includegraphics[width=0.8\\textwidth]{figs/apresentacoes.png}
\caption{Apresentações por Ano}
\label{figs:apresentacoes}
\end{figure}
'''
            ss0 += s  # .replace('__tipo__', tipo)

            apresentacoesAno = {i: v0.count(i) for i in set(v0)}
            x = sorted(list(apresentacoesAno.keys()), reverse=True)
            frequencia = [apresentacoesAno[i] for i in x]
            x = [str(i) for i in x]

            plt.figure(figsize=[8, 5])
            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelrotation=90)
            ax.set_title('Apresentações por Ano')
            ax.set_ylabel("Quantidade")
            # ax.set_xlabel('Qualis')
            ax.set_ylim([0, int(1+1.1*max(frequencia))])

            pps = ax.bar(x, frequencia, label='population')

            plt.savefig('figs/apresentacoes.png')
            plt.close()

        with open('./texLattes/Apresentacoes.tex', 'w') as f:
            f.writelines(ss0)
        f.close()
