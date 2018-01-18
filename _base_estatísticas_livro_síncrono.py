#!/usr/bin/env python3
"""
Cálculo de estatísticas de livros solicitados disponíveis no
Project Gutenbert.
"""

import pathlib
import re
import sys
import time

from bs4 import BeautifulSoup
import requests
import yarl


_PROJECT_GUTENBERG_SOFT_LIMIT = 100

# CAMINHO_ARGUMENTO é o caminho absoluto do primeiro parâmetro de
# sys.argv
CAMINHO_ARGUMENTO = pathlib.Path(sys.argv[0]).resolve()

# DIRETÓRIO_RAIZ é o diretório raiz onde iremos armazenar
# os arquivos obtidos do Project Gutenberg.
DIRETÓRIO_RAIZ = pathlib.Path([CAMINHO_ARGUMENTO
                               if CAMINHO_ARGUMENTO.is_dir()
                               else CAMINHO_ARGUMENTO.parent][0],
                              'arquivos_project_gutenberg')

# NOME_AUTOR_ÍNDICE é uma expressão regular (regex) ingênua para
# obter dados de linhas do tipo:
# 'Nome do Livro, by Nome do Autor                                 42'
# como ('Nome do Livro', 'Nome do Autor', '42')
# Observação: essa regex é ingênua pois existem livros com nome de
#             mais de uma linha; sem autor; múltiplos autores
#             (geralmente não cabe na mesma linha nesse caso); etc.
NOME_AUTOR_ÍNDICE = re.compile(r'^(\S+.*?),\s+by\s+(\S.*?)\s+([0-9]+)\s*$')


# VAZIO, START_OF, PRODUCED_BY, END_OF e END_OF_NORMAL são regex para
# processamento de corte do arquivo obtido do Project Gutenberg para
# obter o conteúdo de fato dos livros.
VAZIO = re.compile(r'^\s*$')
START_OF = re.compile(r'^\s*{0}\s+START\s+OF'.format(re.escape('***')))
PRODUCED_BY = re.compile(r'^\s*Produced\s+by\s+')
END_OF = re.compile(r'^\s*{0}\s+END\s+OF'.format(re.escape('***')))
END_OF_NORMAL = re.compile(r'^\s*End\s+of')

# CARACTERE_VISÍVEL e VISÍVEL_CONTÍGUO são regex para estatísticas
# de linha de texto.
CARACTERE_VISÍVEL = re.compile(r'\S')
VISÍVEL_CONTÍGUO = re.compile(r'\S+')


def extrai_nome_autor_índice(linha):
    """Extrai nome do livro, autor do livro e índice do
       Project Gutenberg, quando possível.

    Args:
        linha: str a ser analisada.

    Returns:
        Entrega None caso não case a expressão regular
        NOME_AUTOR_ÍNDICE ou a tupla contendo os valores capturados da
        regex.
    """
    nome_autor_índice = re.findall(NOME_AUTOR_ÍNDICE, linha)

    # Caso em que a regex não casou.
    if not nome_autor_índice:
        return None

    return nome_autor_índice[0]


def coleta(autores=frozenset({'Machado de Assis'}), saída=sys.stderr):
    """Efetua a coleta dos textos dos livros de um autor disponíveis no
       Project Gutenberg: caso estejam armazenados localmente, fará
       a leitura dos arquivo; caso contrário, coletará do próprio
       Project Gutenberg.

    Args:
        autores: iterável que possua o nome dos autores a serem
                 buscados.
        saída: instância com métodos write e flush para exibição do
               andamento do método.

    Returns:
        Instância de dict cujas chaves são tuplas (nome do livro,
        nome do autor) de livros solicitados disponíveis no
        Project Gutenberg e cujos respectivos valores são str da
        versão txt dos livros.
    """

    # Variável que irá armazenar o resultado final.
    textos_livros = {}

    # Filtra os autores e verifica se existe ao menos um.
    autores_set = frozenset(autores)
    if not autores_set:
        saída.write("ERRO: nenhum autor encontrado. Abortando...\n")
        saída.flush()
        return textos_livros

    saída.write('Coletando os arquivos.\n')
    saída.flush()

    # Para o caso geral, se efetuarmos a coleta de muitos livros
    # (mais de 100 por dia), devemos respeitar os Termos de Uso do
    # Project Gutenberg:
    # http://www.gutenberg.org/wiki/Gutenberg:Terms_of_Use

    # Lista de mirrors:
    # http://www.gutenberg.org/MIRRORS.ALL

    # Lista de todos os livros:
    URL_ÍNDICE = yarl.URL('http://www.gutenberg.org/dirs/GUTINDEX.ALL')
    nome_arquivo_índice = URL_ÍNDICE.path.split('/')[-1]

    # Obtém as linhas do arquivo de índices.
    texto_índice = ''
    caminho_arquivo_índice = pathlib.Path(DIRETÓRIO_RAIZ,
                                          nome_arquivo_índice)
    if caminho_arquivo_índice.is_file():
        # Abre arquivo prévio e lê seu conteúdo.
        with caminho_arquivo_índice.open('rt',
                                         encoding='utf-8') as arquivo_índice:
            texto_índice = arquivo_índice.read()
        saída.write(f"Lido conteúdo de '{nome_arquivo_índice}' a partir de "
                    f"'{caminho_arquivo_índice}'.\n")
        saída.flush()
    else:
        # Obtém o arquivo de índices de Project Gutenberg.
        with requests.get(str(URL_ÍNDICE)) as resposta:
            # Status 200 é OK
            # https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
            assert resposta.status_code == 200
            texto_índice = resposta.text
        saída.write(f"Obtido conteúdo de '{URL_ÍNDICE}'.\n")
        saída.flush()
        # Armazena o arquivo de índices de Project Gutenberg.
        with caminho_arquivo_índice.open('wt',
                                         encoding='utf-8') as arquivo_índice:
            arquivo_índice.write(texto_índice)
        saída.write(f"Armazenado o conteúdo de '{URL_ÍNDICE}' em "
                    f"'{caminho_arquivo_índice}'.\n")
        saída.flush()

    # Divide o conteúdo em linhas.
    linhas_índice = texto_índice.split('\n')

    # Instancia um list para armazenar o resultado de cada linha.
    resultado_linhas = []

    # Obtém as tuplas de nome, autor, índice.
    saída.write(f"Processando as linhas de '{caminho_arquivo_índice}'.\n")
    saída.flush()
    for linha in linhas_índice:
        resultado = extrai_nome_autor_índice(linha)
        if not resultado:
            continue
        resultado_linhas.append(resultado)
    saída.write(f"Processadas as linhas de '{caminho_arquivo_índice}'.\n")
    saída.flush()

    # Filtra as tuplas de acordo com o autor estando em autores_set.
    tuplas_livros_autor = (
        [tupla
         for tupla in resultado_linhas
         if tupla and tupla[1] in autores_set])

    # Lista os livros obtidos por autor solicitado.
    autores_livros = {autor: set()
                      for autor in autores_set}

    for tupla in tuplas_livros_autor:
        # Observação: _ é uma convenção para atribuição de
        #             valores que não serão utilizados.
        nome_livro, nome_autor, _ = tupla
        autores_livros[nome_autor].add(nome_livro)

    for nome_autor in sorted(autores_livros):
        zero = not autores_livros[nome_autor]
        plural = len(autores_livros[nome_autor]) > 1
        if zero:
            saída.write(f"Não foi encontrado livro de "
                        f"{nome_autor}.\n")
        elif plural:
            saída.write(f"Foram encontrados "
                        f"{len(autores_livros[nome_autor])} livros de "
                        f"{nome_autor}: "
                        f"{', '.join(sorted(autores_livros[nome_autor]))}.\n")
        else:
            saída.write(f"Foi encontrado um livro de {nome_autor}: "
                        f"{', '.join(sorted(autores_livros[nome_autor]))}.\n")
        saída.flush()

    # Para este exemplo, iremos usar o sítio principal para coletar
    # a versão txt dos livros, com a URL base do Project Gutenberg.
    URL_BASE_LIVRO = "http://www.gutenberg.org/ebooks/{id}"

    # Sobre uso de robôs:
    # http://www.gutenberg.org/wiki/Gutenberg:Information_About_Robot_Access_to_our_Pages
    # Algumas regras sobre a coleta automatizada:
    # - Esperar 2 segundos entre as coletas;
    # - Usar mirrors para coletar os livros
    #   (deveríamos utilizar neste exemplo).

    # Em condições normais fora do escopo do Project Gutenberg,
    # poderíamos deixar todo o processo a seguir de maneira concorrente.
    # No pior caso, temos que obter os livros do Project Gutenberg e
    # os seus Termos de Uso pedem para esperarmos um intervalo de
    # 2 segundos entre os downloads. Considerando isso, iremos iterar
    # as tuplas de maneira sequencial.

    if len(tuplas_livros_autor) > _PROJECT_GUTENBERG_SOFT_LIMIT:
        saída.write(f"\n\nOBSERVAÇÃO: foram encontradas mais de "
                    f"{_PROJECT_GUTENBERG_SOFT_LIMIT} ocorrências de livros. "
                    f"Seu acesso ao conteúdo pode ser restringido pelo "
                    f"Project Gutenberg!\n\n")
        saída.flush()

    for tupla in tuplas_livros_autor:
        nome_livro, nome_autor, índice = tupla

        nome_arquivo_livro = f"{índice}.txt"
        texto_livro = ''
        caminho_arquivo_livro = pathlib.Path(DIRETÓRIO_RAIZ,
                                             nome_arquivo_livro)

        if caminho_arquivo_livro.is_file():
            # Abre arquivo prévio e lê seu conteúdo.
            with caminho_arquivo_livro.open('rt',
                                            encoding='utf-8') as arquivo_livro:
                texto_livro = arquivo_livro.read()
            saída.write(f"Lido conteúdo de '{nome_livro}' a partir de "
                        f"'{caminho_arquivo_livro}'.\n")
            saída.flush()
        else:
            # Obtém o arquivo contendo as versões do livro solicitado.
            url_versões = yarl.URL(URL_BASE_LIVRO.format(id=índice))
            with requests.get(str(url_versões)) as resposta:
                # Status 200 é OK
                # https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
                assert resposta.status_code == 200
                texto_versões = resposta.text
                saída.write(f"Obtido conteúdo de '{url_versões}'.\n")
                saída.flush()

            # Analisa o HTML para extrair a URL da versão txt.
            url_texto_sem_scheme = ''
            soup = BeautifulSoup(texto_versões, 'html.parser')
            for a_href in soup.find_all('a', href=True):
                if ('.txt' in a_href.attrs['href'] and
                        '-readme' not in a_href.attrs['href']):
                    url_texto_sem_scheme = a_href.attrs['href']
                    saída.write(f"Encontrado path da URL da versão "
                                f"txt de '{nome_livro}'.\n")
                    saída.flush()
                    break

            # Caso não encontre uma url válida, continua para
            # o próximo livro.
            if not url_texto_sem_scheme:
                saída.write(f"Não encontrado nenhum path para URL de "
                            f"versão txt de '{nome_livro}'.\n")
                saída.flush()
                continue

            # Obtém o arquivo contendo a versão txt do livro solicitado.
            url_texto = yarl.URL(f"{url_versões.scheme}:"
                                 f"{url_texto_sem_scheme}")
            with requests.get(str(url_texto)) as resposta:
                # Status 200 é OK
                # https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
                assert resposta.status_code == 200
                texto_livro = resposta.text
                saída.write(f"Obtido conteúdo de '{url_texto}'.\n")
                saída.flush()

            # Armazena o arquivo contendo a versão txt do livro solicitado.
            with caminho_arquivo_livro.open('wt',
                                            encoding='utf-8') as arquivo_livro:
                arquivo_livro.write(texto_livro)
                saída.write(f"Armazenado o conteúdo de '{url_texto}' em "
                            f"'{caminho_arquivo_livro}'.\n")
                saída.flush()

            # Respeitando a regra de coleta automatizada,
            # esperaremos 2 segundos
            saída.write(f"Esperando 2 segundos após o download de "
                        f"'{url_texto}'.\n")
            saída.flush()
            time.sleep(2.)
            saída.write(f"Esperados 2 segundos após o download de "
                        f"'{url_texto}'.\n")
            saída.flush()

        # Armazena num dict usando o nome do livro como chave e
        # o texto como valor.
        textos_livros[(nome_livro, nome_autor)] = texto_livro

    saída.write('Terminada a coleta dos arquivos.\n\n')
    saída.flush()
    return textos_livros


def processa_livro(tupla_livro, texto_bruto, saída):
    """Efetua o processamento do texto de um livro solicitado
       disponível no Project Gutenberg: extrai o texto entre
       o cabeçalho e o rodapé inserido pelo Project Gutenberg.

    Args:
        tupla_livro: tupla (nome do livro, nome do autor).
        texto_bruto: str da versão txt do livro.
        saída: instância com métodos write e flush para exibição do
               andamento do método.

    Returns:
        Entrega a list contendo todas as linhas a serem analisadas do
        livro.
    """
    nome_livro, nome_autor = tupla_livro
    saída.write(f"Processando o corte do conteúdo bruto de "
                f"'{nome_livro}' de '{nome_autor}'.\n")
    saída.flush()

    # Note que essa função foi preparada com base na versão txt dos
    # livros de Machado de Assis. Existem livros mais antigos que não
    # possuem um formato específico, como alguns livros de
    # William Shakespeare. Considere isso caso queira utilizar
    # seriamente essa função.

    # O conteúdo da versão txt dos livros do Project Gutenberg
    # possui um formato específico: está entre
    # *** START OF
    # e
    # *** END OF

    # No entanto, após
    # *** START OF
    # , ainda existem informações sobre a produção da versão do
    # livro, o que está fora do escopo da análise desse exemplo.
    # Também é possível que existam outros comentários antes do
    # título do livro.

    # Como o corte possui regras de linhas sequenciais, aparentemente
    # não há vantagem em fazer o processamento concorrentemente entre
    # as linhas.

    # Divide o texto bruto do Project Gutenberg por linhas.
    linhas = texto_bruto.split('\n')
    range_linhas = range(len(linhas))

    # Busca a primeira linha que começa com
    # *** START OF
    índice_start_of = None
    for índice in range_linhas:
        if re.findall(START_OF, linhas[índice]):
            índice_start_of = índice
            break

    # Se não foi encontrado nenhum casamento, não é
    # um formato esperado.
    if not índice_start_of:
        return list()

    # Busca a primeira linha que começa com
    # Produced by
    # após a linha que começa com
    # *** START OF
    índice_produced_by = None
    for índice in range_linhas[índice_start_of+1:]:
        if re.findall(PRODUCED_BY, linhas[índice]):
            índice_produced_by = índice
            break

    # Se não foi encontrado nenhum casamento, não é
    # um formato esperado.
    if not índice_produced_by:
        return list()

    # Busca a primeira linha com todos os caracteres de letras em
    # maiúsculo após a linha que começa com
    # Produced by
    índice_primeiro_upper = None
    for índice in range_linhas[índice_produced_by+1:]:
        if linhas[índice].isupper():
            índice_primeiro_upper = índice
            break

    # Se não foi encontrado nenhum casamento, não é
    # um formato esperado.
    if not índice_primeiro_upper:
        return list()

    # Busca a última linha que começa com
    # *** END OF
    # Note que a sequência é feita da último linha para a primeira.
    índice_end_of = None
    for índice in range_linhas[::-1]:
        if re.findall(END_OF, linhas[índice]):
            índice_end_of = índice
            break

    # Busca a última linha que começa com
    # End of
    # antes da linha que começa com
    # *** END OF
    índice_end_of_normal = None
    for índice in range_linhas[índice_end_of-1::-1]:
        if re.findall(END_OF_NORMAL, linhas[índice]):
            índice_end_of_normal = índice
            break

    # Busca a última linha com caracteres visíveis antes da linha que
    # começa com
    # End of
    índice_último_visível = None
    for índice in range_linhas[índice_end_of_normal-1::-1]:
        if not re.findall(VAZIO, linhas[índice]):
            índice_último_visível = índice
            break

    saída.write(f"Processado o corte do conteúdo bruto de "
                f"'{nome_livro}' de '{nome_autor}'.\n")
    saída.flush()

    # Uma vez determinada a primeira linha do título e a última linha
    # com caracteres visíveis, devolve um list contendo todas as linhas
    # nesse intervalo, inclusive as duas.
    return (
        linhas[índice_primeiro_upper:índice_último_visível+1])


def analisa_linha_livro(linha):
    """Extrai dados de uma linha a ser analisada de um livro.

    Args:
        linha: str a ser analisada.

    Returns:
        Entrega um dict cujas chaves são estatísticas calculadas na linha.
    """

    # Variável que irá armazenar o resultado final.
    estatísticas_linha = {}

    # Caso não possua linha a ser analisada,
    # devolve sem informações úteis.
    if not isinstance(linha, str):
        return estatísticas_linha

    # Verifica se a linha é composta somente de caracteres invisíveis.
    vazio = bool(re.findall(VAZIO, linha))
    estatísticas_linha[VAZIO] = vazio

    if vazio:
        estatísticas_linha['linha_visível'] = 0
        estatísticas_linha[CARACTERE_VISÍVEL] = 0
        estatísticas_linha[VISÍVEL_CONTÍGUO] = 0
        estatísticas_linha['caracteres visíveis'] = {}
        estatísticas_linha['visíveis contíguos'] = {}
        estatísticas_linha['caracteres visíveis insensíveis'] = {}
        estatísticas_linha['visíveis contíguos insensíveis'] = {}
    else:
        # Encontra caracteres visíveis e sequências contíguas de
        # caracteres visíveis.
        caracteres_visíveis = re.findall(CARACTERE_VISÍVEL, linha)
        visíveis_contíguos = re.findall(VISÍVEL_CONTÍGUO, linha)

        # Gera conjuntos para facilitar o histograma.
        caracteres_visíveis_set = frozenset(caracteres_visíveis)
        visíveis_contíguos_set = frozenset(visíveis_contíguos)

        # Considera a versão minúscula como versão insensível ao caso.
        caracteres_visíveis_insensíveis = [cv_.lower()
                                           for cv_ in caracteres_visíveis]
        visíveis_contíguos_insensíveis = [vc_.lower()
                                          for vc_ in visíveis_contíguos]

        # Gera conjuntos para facilitar o histograma.
        caracteres_visíveis_insensíveis_set = (
            frozenset(caracteres_visíveis_insensíveis))
        visíveis_contíguos_insensíveis_set = (
            frozenset(visíveis_contíguos_insensíveis))

        # Utiliza o método count de lista para gerar os histogramas.
        caracteres_visíveis_dict = {cv_: caracteres_visíveis.count(cv_)
                                    for cv_ in caracteres_visíveis_set}
        visíveis_contíguos_dict = {vc_: visíveis_contíguos.count(vc_)
                                   for vc_ in visíveis_contíguos_set}
        caracteres_visíveis_insensíveis_dict = {
            cvi: caracteres_visíveis_insensíveis.count(cvi)
            for cvi in caracteres_visíveis_insensíveis_set}
        visíveis_contíguos_insensíveis_dict = {
            vci: visíveis_contíguos_insensíveis.count(vci)
            for vci in visíveis_contíguos_insensíveis_set}

        # Atribui os valores obtidos.
        estatísticas_linha['linha_visível'] = 1
        estatísticas_linha[CARACTERE_VISÍVEL] = len(caracteres_visíveis)
        estatísticas_linha[VISÍVEL_CONTÍGUO] = len(visíveis_contíguos)
        estatísticas_linha['caracteres visíveis'] = (
            caracteres_visíveis_dict)
        estatísticas_linha['visíveis contíguos'] = (
            visíveis_contíguos_dict)
        estatísticas_linha['caracteres visíveis insensíveis'] = (
            caracteres_visíveis_insensíveis_dict)
        estatísticas_linha['visíveis contíguos insensíveis'] = (
            visíveis_contíguos_insensíveis_dict)

    return estatísticas_linha


def analisa_livro(tupla_livro, linhas_a_analisar, saída):
    """Efetua a análise dos texto de um livro de Machado de Assis
       disponível no Project Gutenberg: efetua uma análise
       estatística arbitrária para fins de exemplo no texto de
       cada livro.

    Args:
        tupla_livro: tupla (nome do livro, nome do autor).
        linhas_a_analisar: list das linhas a serem analisadas de
                           cada livro.
        saída: instância com métodos write e flush para exibição do
               andamento do método.

    Returns:
        Entrega o dict contendo todas as estatísticas analisadas do
        livro.
    """

    # Variável que irá armazenar o resultado final.
    estatísticas = {}

    nome_livro, nome_autor = tupla_livro

    # Caso não possua linhas a serem analisadas,
    # devolve sem informações úteis.
    if not linhas_a_analisar:
        saída.write(f"Nenhuma linha a analisar de '{nome_livro}' de "
                    f"'{nome_autor}'.\n")
        saída.flush()
        return estatísticas

    # Instancia um list para armazenar o resultado de cada linha.
    resultado_linhas = []

    saída.write(f"Analisando as linhas de '{nome_livro}' de "
                f"'{nome_autor}'.\n")
    saída.flush()

    # Obtém as estatísticas de cada linha.
    for linha in linhas_a_analisar:
        resultado = analisa_linha_livro(linha)
        if not resultado:
            continue
        resultado_linhas.append(resultado)

    saída.write(f"Analisadas as linhas de '{nome_livro}' de "
                f"'{nome_autor}'.\n")
    saída.flush()

    # Filtra os resultados válidos.
    estatísticas_a_considerar = [resultado
                                 for resultado in resultado_linhas
                                 if resultado]

    # Inicializa as entradas a serem utilizadas.
    estatísticas[VAZIO] = 0
    estatísticas['linha_visível'] = 0
    estatísticas[CARACTERE_VISÍVEL] = 0
    estatísticas[VISÍVEL_CONTÍGUO] = 0
    estatísticas['caracteres visíveis'] = {}
    estatísticas['visíveis contíguos'] = {}
    estatísticas['caracteres visíveis insensíveis'] = {}
    estatísticas['visíveis contíguos insensíveis'] = {}

    # Atualiza os valores de acordo com os resultados encontrados.
    for resultado_linha in estatísticas_a_considerar:
        for chave_int in (VAZIO, 'linha_visível', CARACTERE_VISÍVEL,
                          VISÍVEL_CONTÍGUO):
            estatísticas[chave_int] += resultado_linha[chave_int]
        for chave_dict in ('caracteres visíveis', 'visíveis contíguos',
                           'caracteres visíveis insensíveis',
                           'visíveis contíguos insensíveis'):
            for chave_chave in resultado_linha[chave_dict]:
                estatísticas[chave_dict].setdefault(chave_chave, 0)
                estatísticas[chave_dict][chave_chave] += (
                    resultado_linha[chave_dict][chave_chave])

    # Altera as chaves para facilitar o entendimento.
    for tupla in ((VAZIO, 'linhas somente caracteres invisíveis'),
                  ('linha_visível', 'linhas caracteres visíveis'),
                  (CARACTERE_VISÍVEL, 'quantidade caracteres visíveis'),
                  (VISÍVEL_CONTÍGUO,
                   'sequências visíveis contíguas')):
        chave_anterior, chave_nova = tupla
        estatísticas[chave_nova] = estatísticas[chave_anterior]
        del estatísticas[chave_anterior]

    # Uma vez calculadas as estatísticas do texto, devolve um dict
    # contendo todos os dados levantados.
    return estatísticas


def exibe_livro(tupla_livro, estatísticas, saída):
    """Exibe os principais valores de estatísticas obtidas para
       o livro.

    Args:
        tupla_livro: tupla (nome do livro, nome do autor).
        estatísticas: dict contendo as estatísticas obtidas do livro.
        saída: instância com métodos write e flush para exibição do
               andamento do método.
    """

    # Caso não existam estatísticas a serem processadas,
    # devolve a função.
    if not estatísticas:
        return

    nome_livro, nome_autor = tupla_livro

    linhas_invisíveis = estatísticas['linhas somente caracteres invisíveis']
    linhas_visíveis = estatísticas['linhas caracteres visíveis']
    total_linhas = linhas_invisíveis + linhas_visíveis

    quantidade_caractere_mais_utilizado = 0
    caracteres_mais_utilizados = set()
    for cv_ in estatísticas['caracteres visíveis']:
        if (estatísticas['caracteres visíveis'][cv_]
                > quantidade_caractere_mais_utilizado):
            quantidade_caractere_mais_utilizado = (
                estatísticas['caracteres visíveis'][cv_])
            caracteres_mais_utilizados = set({cv_})
        elif (estatísticas['caracteres visíveis'][cv_]
              == quantidade_caractere_mais_utilizado):
            caracteres_mais_utilizados.add(cv_)

    quantidade_caractere_insensível_mais_utilizado = 0
    caracteres_insensíveis_mais_utilizados = set()
    for cvi in estatísticas['caracteres visíveis insensíveis']:
        if (estatísticas['caracteres visíveis insensíveis'][cvi]
                > quantidade_caractere_insensível_mais_utilizado):
            quantidade_caractere_insensível_mais_utilizado = (
                estatísticas['caracteres visíveis insensíveis'][cvi])
            caracteres_insensíveis_mais_utilizados = set({cvi})
        elif (estatísticas['caracteres visíveis insensíveis'][cvi]
              == quantidade_caractere_insensível_mais_utilizado):
            caracteres_insensíveis_mais_utilizados.add(cvi)

    saída.write(f"[ Estatísticas de '{nome_livro}' de '{nome_autor}' ]\n")
    saída.write('\n')
    saída.write(f"    Número de linhas sem nenhum caractere visível: "
                f"{linhas_invisíveis}\n")
    saída.write(f"    Número de linhas com caractere visível: "
                f"{linhas_visíveis}\n")
    saída.write(f"    Total de linhas: {total_linhas}\n")
    saída.write('\n')
    saída.write(f"    Número de caracteres visíveis: "
                f"{estatísticas['quantidade caracteres visíveis']}\n")
    saída.write(f"    Número de sequências contíguas de caracteres "
                f"visíveis: "
                f"{estatísticas['sequências visíveis contíguas']}\n")
    saída.write('\n')

    vezes = quantidade_caractere_mais_utilizado > 1
    mais_utilizados_ordenados = (
        ', '.join("'{0}'".format(cmu)
                  for cmu in sorted(caracteres_mais_utilizados)))
    if len(caracteres_mais_utilizados) > 1:
        saída.write(f"    Caracteres sensíveis a maiúsculas e minúsculas "
                    f"mais utilizados: "
                    f"{mais_utilizados_ordenados} "
                    f"({quantidade_caractere_mais_utilizado} vez"
                    f"{'es' if vezes else ''}"
                    f" cada).\n")
    else:
        saída.write(f"    Caracter sensível a maiúsculas e minúsculas "
                    f"mais utilizado: "
                    f"{mais_utilizados_ordenados} "
                    f"({quantidade_caractere_mais_utilizado} vez"
                    f"{'es' if vezes else ''}"
                    f").\n")

    vezes_insensível = quantidade_caractere_insensível_mais_utilizado > 1
    insensíveis_mais_utilizados_ordenados = (
        ', '.join("'{0}'".format(cimu)
                  for cimu in sorted(caracteres_insensíveis_mais_utilizados)))
    if len(caracteres_insensíveis_mais_utilizados) > 1:
        saída.write(f"    Caracteres insensíveis a maiúsculas e minúsculas "
                    f"mais utilizados: "
                    f"{insensíveis_mais_utilizados_ordenados} "
                    f"({quantidade_caractere_insensível_mais_utilizado} vez"
                    f"{'es' if vezes_insensível else ''}"
                    f" cada).\n")
    else:
        saída.write(f"    Caracter insensível a maiúsculas e minúsculas "
                    f"mais utilizado: "
                    f"{insensíveis_mais_utilizados_ordenados} "
                    f"({quantidade_caractere_insensível_mais_utilizado} vez"
                    f"{'es' if vezes_insensível else ''}"
                    f").\n")
    saída.write('\n')

    quantidade_sequência_mais_utilizada = 0
    sequências_mais_utilizadas = set()
    comprimento_maior_sequência = 0
    maiores_sequências = set()
    for vc_ in estatísticas['visíveis contíguos']:
        if len(vc_) > comprimento_maior_sequência:
            comprimento_maior_sequência = len(vc_)
            maiores_sequências = set({vc_})
        elif len(vc_) == comprimento_maior_sequência:
            maiores_sequências.add(vc_)

        if (estatísticas['visíveis contíguos'][vc_]
                > quantidade_sequência_mais_utilizada):
            quantidade_sequência_mais_utilizada = (
                estatísticas['visíveis contíguos'][vc_])
            sequências_mais_utilizadas = set({vc_})
        elif (estatísticas['visíveis contíguos'][vc_]
              == quantidade_sequência_mais_utilizada):
            sequências_mais_utilizadas.add(vc_)

    quantidade_sequência_insensível_mais_utilizada = 0
    sequências_insensíveis_mais_utilizadas = set()
    comprimento_maior_sequência_insensível = 0
    maiores_sequências_insensíveis = set()
    for vci in estatísticas['visíveis contíguos insensíveis']:
        if len(vci) > comprimento_maior_sequência_insensível:
            comprimento_maior_sequência_insensível = len(vci)
            maiores_sequências_insensíveis = set({vci})
        elif len(vci) == comprimento_maior_sequência_insensível:
            maiores_sequências_insensíveis.add(vci)

        if (estatísticas['visíveis contíguos insensíveis'][vci]
                > quantidade_sequência_insensível_mais_utilizada):
            quantidade_sequência_insensível_mais_utilizada = (
                estatísticas['visíveis contíguos insensíveis'][vci])
            sequências_insensíveis_mais_utilizadas = set({vci})
        elif (estatísticas['visíveis contíguos insensíveis'][vci]
              == quantidade_sequência_insensível_mais_utilizada):
            sequências_insensíveis_mais_utilizadas.add(vci)

    vezes = quantidade_sequência_mais_utilizada > 1
    mais_utilizadas_ordenadas = (
        ', '.join("'{0}'".format(smu)
                  for smu in sorted(sequências_mais_utilizadas)))
    if len(sequências_mais_utilizadas) > 1:
        saída.write(f"    Sequências sensíveis a maiúsculas e minúsculas "
                    f"mais utilizadas: "
                    f"{mais_utilizadas_ordenadas} "
                    f"({quantidade_sequência_mais_utilizada} vez"
                    f"{'es' if vezes else ''}"
                    f" cada).\n")
    else:
        saída.write(f"    Sequência sensível a maiúsculas e minúsculas "
                    f"mais utilizada: "
                    f"{mais_utilizadas_ordenadas} "
                    f"({quantidade_sequência_mais_utilizada} vez"
                    f"{'es' if vezes else ''}"
                    f").\n")

    vezes_insensível = quantidade_sequência_insensível_mais_utilizada > 1
    insensíveis_mais_utilizadas_ordenadas = (
        ', '.join("'{0}'".format(simu)
                  for simu in sorted(sequências_insensíveis_mais_utilizadas)))
    if len(sequências_insensíveis_mais_utilizadas) > 1:
        saída.write(f"    Sequências insensíveis a maiúsculas e minúsculas "
                    f"mais utilizados: "
                    f"{insensíveis_mais_utilizadas_ordenadas} "
                    f"({quantidade_sequência_insensível_mais_utilizada} vez"
                    f"{'es' if vezes_insensível else ''}"
                    f" cada).\n")
    else:
        saída.write(f"    Sequência insensível a maiúsculas e minúsculas "
                    f"mais utilizada: "
                    f"{insensíveis_mais_utilizadas_ordenadas} "
                    f"({quantidade_sequência_insensível_mais_utilizada} vez"
                    f"{'es' if vezes_insensível else ''}"
                    f").\n")
    saída.write('\n')

    plural = len(maiores_sequências) > 1
    maiores_ordenadas = (
        ', '.join("'{0}'".format(ms_)
                  for ms_ in sorted(maiores_sequências)))
    if plural:
        saída.write(f"    Maiores sequências sensíveis a maiúsculas "
                    f"e minúsculas: {maiores_ordenadas} "
                    f"({comprimento_maior_sequência} caracteres).\n")
    else:
        saída.write(f"    Maior sequência sensível a maiúsculas "
                    f"e minúsculas: {maiores_ordenadas} "
                    f"({comprimento_maior_sequência} caracteres).\n")

    plural_insensível = len(maiores_sequências_insensíveis) > 1
    maiores_insensíveis_ordenadas = (
        ', '.join("'{0}'".format(msi)
                  for msi in sorted(maiores_sequências_insensíveis)))
    if plural_insensível:
        saída.write(f"    Maiores sequências insensíveis a maiúsculas "
                    f"e minúsculas {maiores_insensíveis_ordenadas} "
                    f"({comprimento_maior_sequência_insensível} "
                    f"caracteres).\n")
    else:
        saída.write(f"    Maior sequência insensível a maiúsculas "
                    f"e minúsculas {maiores_insensíveis_ordenadas} "
                    f"({comprimento_maior_sequência_insensível} "
                    f"caracteres).\n")
    saída.write('\n')

    saída.write('\n')
    saída.flush()


def exibe(estatísticas_por_livro, saída=sys.stdout):
    """Exibe os principais valores de estatísticas obtidas de
       cada livro.

    Args:
        estatísticas_por_livro: dict cujas chaves são tuplas
                                (nome do livro, nome do autor) e
                                cujos respectivos valores são dict
                                contendo as estatísticas obtidas de
                                cada livro.
        saída: instância com métodos write e flush para exibição do
               andamento do método.
    """

    # Caso não existam estatísticas a serem processadas,
    # devolve a função.
    if not estatísticas_por_livro:
        return

    # Distribui os livros pelos autores.
    autores_livros = {}
    for tupla_livro in estatísticas_por_livro:
        nome_livro, nome_autor = tupla_livro
        entrada_autor = autores_livros.setdefault(nome_autor, set())
        entrada_autor.add(nome_livro)

    # Exibe as estatísticas de livro ordenado primeiramente por autor
    # seguido de nome de livro.
    for nome_autor in sorted(autores_livros):
        for nome_livro in sorted(autores_livros[nome_autor]):
            tupla_livro = (nome_livro, nome_autor)
            exibe_livro(tupla_livro,
                        estatísticas_por_livro[tupla_livro],
                        saída)
