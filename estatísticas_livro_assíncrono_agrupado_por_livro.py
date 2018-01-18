#!/usr/bin/env python3
"""
Cálculo de estatísticas de livros de um autor disponíveis no
Project Gutenbert. O processo desse módulo agrupa os processos por
livro.
"""

import argparse
import asyncio
import sys

from _base_estatísticas_livro_assíncrono import (
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


async def processa_e_analisa_por_livro(
        tupla_livro, texto_bruto, saída, futuro):
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
        futuro: instância de asyncio.Future a armazenar o resultado.

    Returns:
        Oficialmente, None.

        Via futuro.set_result, é entregue o dict contendo todas
        as estatísticas analisadas do livro.
    """

    # Instancia um asyncio.Future para o processamento do livro.
    futuro_processa_livro = asyncio.Future()

    # Obtém o livro processado.
    await asyncio.wait(
        [asyncio.ensure_future(
            processa_livro(tupla_livro, texto_bruto,
                           saída, futuro_processa_livro))])

    linhas_a_analisar = futuro_processa_livro.result()

    # Obtém as estatísticas do livro processado.
    await asyncio.wait(
        [asyncio.ensure_future(
            analisa_livro(tupla_livro,
                          linhas_a_analisar,
                          saída, futuro))])


async def processa_e_analisa(textos_livros, saída=sys.stderr):
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

    # Instancia um asyncio.Future para cada livro.
    futuros_texto = {tupla_livro: asyncio.Future()
                     for tupla_livro in textos_livros}

    # Obtém as estatísticas do livro processado.
    await asyncio.wait(
        [asyncio.ensure_future(
            processa_e_analisa_por_livro(tupla_livro,
                                         textos_livros[tupla_livro],
                                         saída,
                                         futuros_texto[tupla_livro]))
         for tupla_livro in futuros_texto])

    # Uma vez analisadas as linhas do texto do livro, devolve um dict
    # cujas chaves são tuplas (nome do livro, nome do autor) e cujos
    # respectivos valores são dict contendo as estatísticas obtidas
    # por cada livro.
    estatísticas_por_livro = {tupla_livro: resultado
                              for tupla_livro in futuros_texto
                              for resultado in
                              (futuros_texto[tupla_livro].result(), )
                              if resultado}

    return estatísticas_por_livro


async def main(argv):
    """Função main para coletar, processar, analisar e exibir
       as informações relacionadas aos livros de um autor
       disponíveis no Project Gutenberg de maneira assíncrona.

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
        textos_livros = await coleta(autores)
    else:
        textos_livros = await coleta()

    estatísticas_por_livro = await processa_e_analisa(textos_livros)

    await exibe(estatísticas_por_livro)


if __name__ == "__main__":
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(main(sys.argv))
    LOOP.close()
