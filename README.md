# **aio-exemplo**

Repositório contendo slides e códigos de exemplo relacionado a `asyncio` (Python 3.5+)


## Palestra
*Usando [asyncio](https://docs.python.org/3/library/asyncio.html) para reescrever processamento sem dependência em código concorrente*


## Evento
### [[Grupy-SP]](https://www.meetup.com/pt-BR/Grupy-SP/) [São Paulo, 18 de Janeiro de 2018](https://www.meetup.com/pt-BR/Grupy-SP/events/246561769/)


## Autor
### [Alexandre Harano](https://alexandre.harano.net.br/)&nbsp;&nbsp;&nbsp;[@GitHub](https://github.com/ayharano)&nbsp;&nbsp;&nbsp;[@Keybase](https://keybase.io/ayharano)&nbsp;&nbsp;&nbsp;[@Telegram](https://t.me/ayharano)&nbsp;&nbsp;&nbsp;[@Twitter](https://twitter.com/ayharano)


## Slides
### [![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/) &nbsp;&nbsp;&nbsp; [PDF](https://github.com/ayharano/aio-exemplo/blob/master/slides/20180118_grupy_sp_aio_exemplo.pdf) &nbsp;&nbsp;&nbsp; [@Speaker Deck](https://speakerdeck.com/ayharano/usando-asyncio-para-reescrever-processamento-sem-dependencia-em-codigo-concorrente)


## Código
### [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) &nbsp;&nbsp;&nbsp; [ayharano/aio-exemplo](https://github.com/ayharano/aio-exemplo)


## Vídeo
### [![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/) &nbsp;&nbsp;&nbsp; [YouTube](https://www.youtube.com/watch?v=LAkW7bxgHjQ)


## Modo de uso

Alguns dos módulos contidos nesse repositório usam `f-strings` ([PEP 498 — Literal String Interpolation](https://www.python.org/dev/peps/pep-0498/)), recurso disponível a partir do Python 3.6. Para a gerência de múltiplas versões do Python, incluindo a versão 3.6+, é recomendado o uso do [pyenv](https://github.com/pyenv/pyenv).

Para efetuar a configuração do ambiente:

```sh
$ git clone https://github.com/ayharano/aio-exemplo.git aio-exemplo # Clona o repositório
$ cd aio-exemplo      # Ir ao diretório para onde o git clone foi realizado
$ pip3 install pipenv # Instala pipenv a nível de usuário
$ pipenv --python 3.6 # Executa pipenv para configurar a versão do binário do python para o 3.6
$ pipenv update       # Executa pipenv para instalar as dependências e configurar o virtualenv do ambiente
```

Para usar os arquivos contidos no repositório:

```sh
$ cd aio-exemplo # Ir ao diretório para onde o git clone foi realizado
$ pipenv shell   # Utiliza o shell fornecido pelo virtualenv configurado pelo pipenv
```

Uma vez que esteja no `shell` fornecido por `pipenv`,
executar o seguinte comando para verificar o funcionamento:

```sh
(aio-exemplo-RANDOM) $ python3 nome_arquivo.py -h # Verifica o help fornecido pelo módulo nome_arquivo
```

onde `nome_arquivo.py` é um placeholder para um arquivo `*.py`
contido no repositório, com exceção de `_*.py`
(esses arquivos são utilizados como denominador comum de dois ou
mais módulos).


## Referências
- [The Python Software Foundation](https://www.python.org/psf/)&nbsp;&nbsp;&nbsp;[@GitHub](https://github.com/python)
  - [asyncio — Asynchronous I/O, event loop, coroutines and tasks](https://docs.python.org/3/library/asyncio.html)
  - [PEP 380 — Syntax for Delegating to a Subgenerator](https://www.python.org/dev/peps/pep-0380/)
  - [PEP 3156 — Asynchronous IO Support Rebooted: the "asyncio" Module](https://www.python.org/dev/peps/pep-3156/)
  - [PEP 492 — Coroutines with `async` and `await` syntax](https://www.python.org/dev/peps/pep-0492/)
  - [PEP 525 — Asynchronous Generators](https://www.python.org/dev/peps/pep-0525/)
  - [PEP 530 — Asynchronous Comprehensions](https://www.python.org/dev/peps/pep-0530/)

- [aio-libs](https://groups.google.com/forum/#!forum/aio-libs)&nbsp;&nbsp;&nbsp;[@GitHub](https://github.com/aio-libs)

- [Jake VanderPlas](http://vanderplas.com/)&nbsp;&nbsp;&nbsp;[@GitHub](https://github.com/jakevdp)
  - [Why Python is Slow: Looking Under the Hood](https://jakevdp.github.io/blog/2014/05/09/why-python-is-slow/)

- [Luciano Ramalho](https://ramalho.org/)&nbsp;&nbsp;&nbsp;[@GitHub](https://github.com/ramalho)
  - [Fluent Python](http://shop.oreilly.com/product/0636920032519.do)&nbsp;&nbsp;&nbsp;[en](https://www.amazon.com/Fluent-Python-Concise-Effective-Programming/dp/1491946008/)&nbsp;&nbsp;&nbsp;[pt](https://www.amazon.com.br/Python-Fluente-Luciano-Ramalho/dp/857522462X)

- [Brett Cannon](https://snarky.ca/)&nbsp;&nbsp;&nbsp;[@GitHub](https://github.com/brettcannon)
  - [How the heck does async/await work in Python 3.5?](https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/)

- [Łukasz Langa](http://lukasz.langa.pl/)&nbsp;&nbsp;&nbsp;[@GitHub](http://github.com/ambv)
  - [Thinking In Coroutines - PyCon 2016](https://us.pycon.org/2016/schedule/presentation/1801/)
    - [Vídeo](https://www.youtube.com/watch?v=l4Nn-y9ktd4)
    - [Slides](https://speakerdeck.com/pycon2016/lukasz-langa-thinking-in-coroutines)

- [Laura F. D.](https://veriny.tf/)&nbsp;&nbsp;&nbsp;[@GitHub](https://github.com/SunDwarf)
  - [asyncio: A dumpster fire of bad design](https://veriny.tf/asyncio-a-dumpster-fire-of-bad-design/)
