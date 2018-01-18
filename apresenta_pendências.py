#!/usr/bin/env python3
"""
Exemplo para listagem de pendências assíncronas para o usuário.
"""

import argparse
import asyncio
from concurrent.futures import ALL_COMPLETED, FIRST_COMPLETED
import sys


DESCRIÇÃO = ''.join("""\
Exemplo para listagem de pendências assíncronas para o usuário.
""".replace('\n', ' ').replace('  ', ' '))


async def fatorial(número, futuro):
    """Calcula fatorial de número e devolve através de futuro.

    Para fins de exemplo de corrotina com asyncio.Future, baseado em
    https://docs.python.org/3/library/asyncio-task.html#example-parallel-execution-of-tasks

    Args:
        número: int cujo fatorial será calculado.
        futuro: asyncio.Future para armazenar o resultado.

    Returns:
        Oficialmente, None.

        Via futuro.set_result, é entregue o valor do
        fatorial de número.
    """
    produtório = 1
    for _ in range(2, número+1):
        await asyncio.sleep(1.)
        produtório *= 1
    futuro.set_result(produtório)
    return


async def apresenta_pendências(
        rótulos, saída=sys.stderr, intervalo=.1, ciclo=5.):
    """Apresenta um '.' a cada período de intervalo passado sem
       uma tarefa concluída. A cada período de ciclo passado sem
       uma tarefa concluída, é mostrado uma lista das tarefas
       pendentes.

    Recebe um dict que mapeia as tarefas em andamento aos
    respectivos rótulos e indica por saída o andamento das tarefas,
    mostrando as pendências a cada ciclo sem tarefas completas.

    Args:
        rótulos: dict mapeando cada asyncio.Future a um rótulo da
                 tarefa em andamento.
        saída: instância com métodos write e flush para exibição do
               andamento das tarefas.
        intervalo: número em segundos para a apresentação de '.'
                   caso nenhuma tarefa foi concluída dentro do
                   intervalo.
        ciclo: número em segundos para a apresentação da lista das
               tarefas pendentes caso nenhuma tarefa foi concluída
               dentro do ciclo.
    """

    # Conjunto das tarefas iniciais.
    rotuladas = set(rótulo
                    for rótulo in rótulos
                    if issubclass(type(rótulo), asyncio.Future))

    pendentes = rotuladas

    # A cada tarefa completa, a contagem é zerada.
    # Se, após ciclo segundos, não tiver uma tarefa completa, é
    # apresentada uma lista das tarefas pendentes de acordo com
    # o rótulo de cada uma das tarefas.
    contador_intervalos = 0

    # Utilizado para esperar os potenciais sleep abandonados.
    tarefas_espera = set()

    # Executa enquanto ainda tiver alguma tarefa pendente.
    while pendentes:

        # Tarefa para a espera de intervalo segundos.
        tarefa_espera_atual = asyncio.ensure_future(asyncio.sleep(intervalo))
        pendentes.add(tarefa_espera_atual)
        tarefas_espera.add(tarefa_espera_atual)

        # Raciocínio do mecanismo:
        # ou uma tarefa que é chave de rótulos irá completar
        # ou o sleep de intervalo segundos.

        # Observação: asyncio.wait não pode receber
        # um iterável vazio.
        # Essa condição para nosso caso é evitada pela condição do
        # while, já que pendentes só é considerado True quando possui
        # pelo menos um elemento.

        prontos, ainda_pendentes = (await asyncio
                                    .wait(pendentes,
                                          return_when=FIRST_COMPLETED))

        # Trata as tarefas completadas.
        # Caso tenha uma tarefa de rótulos completada junto com
        # uma espera, não apresentar '.'.

        apresentar_ponto = False
        completadas = set()

        for pronto in prontos:

            if pronto in tarefas_espera:
                # Terminou uma tarefa de espera.

                # Se não for a tarefa de tempo atual, ignora.
                if pronto != tarefa_espera_atual:
                    continue

                # Marca como potencial apresentação de '.'.
                apresentar_ponto = True
            else:
                # Terminou uma tarefa que é chave de rótulos.
                # Indica qual tarefa completou, através de seu rótulo.
                completadas.add(rótulos[pronto])

        for completada in sorted(completadas):
            saída.write(f" {completada} completou!\n")
            saída.flush()

        if completadas:

            # Zera a contagem de intervalos.
            contador_intervalos = 0

        elif apresentar_ponto:

            # Terminou o sleep de intervalo segundos sem tarefa de
            # rótulo: apresenta visualmente essa informação
            # através da exibição do caractere '.'.
            contador_intervalos += 1
            saída.write('.')
            saída.flush()

            if contador_intervalos * intervalo >= ciclo:
                # A cada ciclo segundos sem tarefas completadas,
                # apresenta pendentes.

                rótulos_pendentes = sorted(str(rótulos[p])
                                           for p in ainda_pendentes)
                saída.write(f" [falta"
                            f"{'m' if len(ainda_pendentes) > 1 else ''} "
                            f"{', '.join(rótulos_pendentes)}]\n")
                saída.flush()

                # Zera a contagem de intervalos.
                contador_intervalos = 0

        # Atualiza o conjunto de pendentes.
        pendentes = ainda_pendentes.intersection(rotuladas)

    # Indica o término com "!".
    saída.write('!\n')
    saída.flush()

    # Espera finalizar as tarefas de espera potencialmente pendentes.
    await asyncio.wait(tarefas_espera, return_when=ALL_COMPLETED)


async def main(argv):
    """Função main para executar a exibição de tarefas pendentes.

    A execução é montada para ser similar ao exemplo encontrado em
    https://docs.python.org/3/library/asyncio-task.html#example-parallel-execution-of-tasks

    Args:
        argv: lista de argumentos a serem tratados.
    """

    parser = argparse.ArgumentParser(description=DESCRIÇÃO)
    args = parser.parse_args(argv[1:])

    # Mapeamento de rótulos com parâmetros.
    valores = {'A': 23,
               'B': 34,
               'C': 45}

    # As instâncias de asyncio.Future aqui instanciadas são para
    # armazenamento de resultado de execução não bloqueante de
    # corrotinas.
    futuros = {rótulo: asyncio.Future()
               for rótulo in valores}

    # O dict instancia uma Task como chave mapeando rótulo como valor.
    rótulos = {
        asyncio.ensure_future(fatorial(valores[rótulo], futuros[rótulo])):
        rótulo
        for rótulo in futuros}

    # Apresenta as tarefas pendentes.
    await apresenta_pendências(rótulos)

    # Processamento dos resultados poderia ser feito a partir daqui,
    # uma vez que todos os resultados já foram calculados.


if __name__ == "__main__":
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(main(sys.argv))
    LOOP.close()
