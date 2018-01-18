#!/usr/bin/env python3
"""
Cálculo de estatísticas de livros de um autor disponíveis no
Project Gutenbert. O processo desse módulo agrupa os processos por
livro.
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
Project Gutenbert. O processo desse módulo agrupa os processos por
livro.
""".replace('\n', ' ').replace('  ', ' '))


def processa_e_analisa_por_livro(tupla_livro, texto_bruto, saída):
    """Efetua o processamento e a análise do textos de um livro
       solicitado disponível no Project Gutenberg: extrai o texto
       entre o cabeçalho e o rodapé inserido pelo Project Gutenberg
       no livro e efetua uma análise estatística arbitrária para
       fins de exemplo no texto de cada livro.

    Args:
        tupla_livro: tupla (nome do livro, nome do autor).
        texto_bruto: str da versão txt do livro.
        saída: instância com métodos write e flush para exibição do
               andamento do método.

    Returns:
        Entrega o dict contendo todas as estatísticas analisadas do
        livro.
    """

    # Variável que irá armazenar o resultado intermediário.
    resultado_análise = {}

    linhas_a_analisar = processa_livro(tupla_livro,
                                       texto_bruto,
                                       saída)

    if not linhas_a_analisar:
        return resultado_análise

    return analisa_livro(tupla_livro,
                         linhas_a_analisar,
                         saída)


def processa_e_analisa(textos_livros, saída=sys.stderr):
    """Efetua o processamento e a análise dos textos dos livros
       solicitados disponíveis no Project Gutenberg: extrai o texto
       entre o cabeçalho e o rodapé inserido pelo Project Gutenberg em
       cada livro e efetua uma análise estatística arbitrária para
       fins de exemplo no texto de cada livro.

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
        nome do autor) e cujos respectivos valores são list das linhas
        a serem analisadas de cada livro.
    """

    # Variável que irá armazenar o resultado intermediário.
    resultados_texto = {}

    # Obtém as estatísticas do livro processado.
    for tupla_livro in textos_livros:
        resultado = processa_e_analisa_por_livro(tupla_livro,
                                                 textos_livros[tupla_livro],
                                                 saída)
        if resultado:
            resultados_texto[tupla_livro] = resultado

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

    estatísticas_por_livro = processa_e_analisa(textos_livros)

    exibe(estatísticas_por_livro)


if __name__ == "__main__":
    main(sys.argv)
