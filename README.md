# lattes2memorial
Converte zip exportado do lattes para latex

Script em construção, adaptado para o lattes do autor. Melhorias são necessárias!

# Instalar python, pip e git (se ainda não tiver instalado)

## 👇️ Debian / Ubuntu
```
sudo apt update
sudo apt install python3-venv python3-pip
python3 -m pip install --upgrade pip
sudo apt install git-all
```

## 👇️ macOS
```
brew install python
python3 -m pip install --upgrade pip
```

## 👇️ Windows
```
py -m pip install --upgrade pip
```
instalar git: https://git-scm.com/download/mac

# Instalar virtualenv (se desejar)
```
pip install virtualenv
virtualenv ../lattesEnv
source ../lattesEnv/bin/activate
```

# Download do seu Lattes (arquivo zip)
* https://lattes.cnpq.br/
* Atualizar currículo
* Exportar (final da aba vertical à esquerda)
* Escolher xml e Continuar
* Mover esse zip para a pasta lattes2memorial, criada a seguir

# Download e instalar lattes2memorial 
```
git clone git@github.com:fzampirolli/lattes2memorial.git
python lattes2memorial.py instala
python lattes2memorial.py
python lattes2memorial.py limpa #(se desejar apagar todos os arquivos criados)
```

