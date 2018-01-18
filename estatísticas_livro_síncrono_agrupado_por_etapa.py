#!/usr/bin/env python3
"""
Cálculo de estatísticas de livros de um autor disponíveis no
Project Gutenbert. O processo desse módulo agrupa os livros por
etapas do processo.
"""

import argparse
import sys

from _base_estatísticas_livro_síncrono import (
    DIRETÓRIO_RAIZ,
    coleta,
    processa_livro,
    analisa_livro,
    exibe,
)


DESCRIÇÃO = ''.join("""\
Cálculo de estatísticas de livros de um autor disponíveis no
Project Gutenbert. O processo desse módulo agrupa os livros por
etapas do processo.
""".replace('\n', ' ').replace('  ', ' '))


def processa(textos_livros, saída=sys.stderr):
    """Efetua o processamento dos textos dos livros solicitados
       disponíveis no Project Gutenberg: extrai o texto entre
       o cabeçalho e o rodapé inserido pelo Project Gutenberg em
       cada livro.

    Args:
        textos_livros: dict cujas chaves são tuplas
                       (nome do livro, nome do autor) de livros
                       solicitados disponíveis no Project Gutenberg e
                       cujos respectivos valores são str da versão
                       txt dos livros.
        saída: instância com métodos write e flush para exibição do
               andamento do método.

    Returns:
        Instância de dict cujas chaves são tuplas (nome do livro,
        nome do autor) de livros solicitados disponíveis no
        Project Gutenberg e cujos respectivos valores são list das
        linhas a serem analisadas de cada livro.
    """

    # Variável que irá armazenar o resultado intermediário.
    resultados_texto = {}

    # Obtém o processamento de todos os livros.
    plural = len(textos_livros) > 1
    saída.write(f"Processando o corte do"
                f"{f's {len(textos_livros)}' if plural else ''} "
                f"livro"
                f"{'s' if plural else ''}.\n")
    saída.flush()
    for tupla_livro in textos_livros:
        resultado = processa_livro(tupla_livro,
                                   textos_livros[tupla_livro],
                                   saída)
        if resultado:
            resultados_texto[tupla_livro] = resultado
    saída.write(f"Processado o corte do"
                f"{f's {len(textos_livros)}' if plural else ''} "
                f"livro"
                f"{'s' if plural else ''}.\n\n")
    saída.flush()

    # Uma vez determinada a primeira linha do título e a última linha
    # com caracteres visíveis, devolve um dict cuja chaves são tuplas
    # (nome do livro, nome do autor) e cujos respectivos valores são
    # list contendo todas as linhas a serem analisadas do livro.
    linhas_a_analisar_por_livro = {tupla_livro: resultado
                                   for tupla_livro in resultados_texto
                                   for resultado in
                                   (resultados_texto[tupla_livro], )
                                   if resultado}

    return linhas_a_analisar_por_livro


def analisa(linhas_a_analisar_por_livro, saída=sys.stderr):
    """Efetua a análise dos textos de livros: efetua uma análise
       estatística arbitrária para fins de exemplo no texto de
       cada livro.

    Args:
        linhas_a_analisar_por_livro: dict cujas chaves são tuplas
                                     (nome do livro, nome do autor) e
                                     cujos respectivos valores são list
                                     das linhas a serem analisadas de
                                     cada livro.
        saída: instância com métodos write e flush para exibição do
               andamento do método.

    Returns:
        Instância de dict cujas chaves são tuplas (nome do livro,
        nome do autor) e cujos respectivos valores são list das linhas
        a serem analisadas de cada livro.
    """

    # Variável que irá armazenar o resultado intermediário.
    resultados_texto = {}

    # Obtém o processamento de todos os livros.
    plural = len(linhas_a_analisar_por_livro) > 1
    saída.write(f"Analisando as linhas do"
                f"{f's {len(linhas_a_analisar_por_livro)}' if plural else ''} "
                f"livro"
                f"{'s' if plural else ''}.\n")
    saída.flush()
    for tupla_livro in linhas_a_analisar_por_livro:
        resultado = analisa_livro(tupla_livro,
                                  linhas_a_analisar_por_livro[tupla_livro],
                                  saída)
        if resultado:
            resultados_texto[tupla_livro] = resultado
    saída.write(f"Analisadas as linhas do"
                f"{f's {len(linhas_a_analisar_por_livro)}' if plural else ''} "
                f"livro"
                f"{'s' if plural else ''}.\n\n")
    saída.flush()

    # Uma vez analisadas as linhas do texto do livro, devolve um dict
    # cujas chaves são tuplas (nome do livro, nome do autor) e cujos
    # respectivos valores são dict contendo as estatísticas obtidas
    # por cada livro.
    estatísticas_por_livro = {tupla_livro: resultado
                              for tupla_livro in resultados_texto
                              for resultado in
                              (resultados_texto[tupla_livro], )
                              if resultado}

    return estatísticas_por_livro


def main(argv):
    """Função main para coletar, processar, analisar e exibir
       as informações relacionadas aos livros de um autor
       disponíveis no Project Gutenberg de maneira síncrona.

    Args:
        argv: lista de argumentos a serem tratados.
    """

    parser = argparse.ArgumentParser(description=DESCRIÇÃO)
    parser.add_argument('nome_autor', metavar='NOME_AUTOR', type=str,
                        nargs='*', help='autor cujos livros serão buscados')
    args = parser.parse_args(argv[1:])

    try:
        DIRETÓRIO_RAIZ.mkdir(mode=0o755, parents=True, exist_ok=True)
    except FileExistsError:
        sys.stderr.write(f"ERRO: '{DIRETÓRIO_RAIZ}' existe e não é "
                         f"diretório. Abortando...\n")
        return

    textos_livros = None

    # Caso autores sejam passados como argumento, serão buscados.
    # Caso contrário, será utilizado o default de coleta.
    autores = frozenset(args.nome_autor)
    if autores:
        textos_livros = coleta(autores)
    else:
        textos_livros = coleta()

    linhas_a_analisar_por_livro = processa(textos_livros)

    estatísticas_por_livro = analisa(linhas_a_analisar_por_livro)

    exibe(estatísticas_por_livro)


if __name__ == "__main__":
    main(sys.argv)
