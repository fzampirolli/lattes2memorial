# lattes2memorial
Converte zip exportado do lattes para latex:
* gera tex de várias partes do lattes na pasta `texLattes`
* gera gráficos na pasta `figs`
* gera bib do lattes usando SLattes e referencia de forma automática nos tex da pasta `texLattes`

Serviço em construção, portanto melhorias são necessárias nesse processo!

Porém, podem testar localmente ou no servidor abaixo sem ter que instalar nada:
* http://mctest.ufabc.edu.br:8000/lattes2memorial/

O conteúdo deste GitHub é exatamente o que está rodando nesses servidores.

Créditos: 
* https://pt.overleaf.com/latex/templates/template-ufabc-dissertacao/zmwgdkcsrxjb (adaptado)
* https://arademaker.github.io/blog/2012/02/15/lattes-to-bibtex.html
* https://ppgcc.github.io/discentesPPGCC/pt-BR/qualis/
* `networkx.algorithms.community` para agrupamento de autores
* `pyvis.network` para grafo com movimento de agrupamento de autores

Ver um trabalho relacionado, gerando html, em https://github.com/rafatieppo/lucylattes.

# Exemplo de Memorial Gerado

Esse arquivo foi gerado automaticamente a partir deste serviço, que foi adaptado para atender aos conteúdos específicos do Lattes do autor:

[memorial-zampirolli.pdf](https://github.com/fzampirolli/lattes2memorial/blob/main/memorial-zampirolli.pdf)


# Para executar no Colab ou localmente

## Executar no Colab

Fazer download do arquivo [lattes2memorial.ipynb](https://github.com/fzampirolli/lattes2memorial/blob/main/lattes2memorial.ipynb) e abrir no Google Drive. 

Ou executar diretamente esse [link](https://drive.google.com/open?id=1qFGri7CySne3gc2l5YFfdKXQkCq3lULa&usp=drive_fs).

## Instalar python, pip, git, etc (se ainda não tiver instalado)

### 👇️ Debian / Ubuntu
```
sudo apt update
sudo apt install python3-venv python3-pip
python3 -m pip install --upgrade pip
sudo apt install git-all
sudo apt install bibtool bibutils xsltproc libxml2-utils
```

### 👇️ macOS
```
brew install python
python3 -m pip install --upgrade pip
```

### 👇️ Windows
```
py -m pip install --upgrade pip
```
instalar git: https://git-scm.com/download/mac

## 👇️ Download lattes2memorial 
```
git clone git@github.com:fzampirolli/lattes2memorial.git
```

## 👇️ Instalar virtualenv (se desejar)
```
cd lattes2memorial
pip install virtualenv
virtualenv -p python lattesEnv
source lattesEnv/bin/activate
```

# 👇️ Download do seu Lattes (arquivo "CV_*.zip")
* https://lattes.cnpq.br/
* Atualizar currículo
* Exportar (final da aba vertical à esquerda)
* Escolher XML e Continuar

# 👇️ Mover "CV_*.zip" para a pasta correta
```
mv CV_*.zip lattes2memorial/src
```

# 👇️ Instalar bibliotecas e executar na pasta src
```
python lattes2memorial.py instala
python lattes2memorial.py
python lattes2memorial.py limpa #(se desejar apagar todos os arquivos criados)
```
