# keras-prov
Keras-Prov foi desenvolvido com base na [DfAnalyzer](https://gitlab.com/ssvitor/dataflow_analyzer) e com a adaptação do [Keras](https://github.com/keras-team/keras).

Para utilizar a KerasProv são requeridas as seguintes aplicações:

* [Java](https://java.com/pt-BR/)
* [MonetDB](http://www.monetdb.org/Documentation/UserGuide/Tutorial)
* [PyMonetDB](https://pymonetdb.readthedocs.io/en/latest/index.html)
* [DfAnalyzer](https://bitbucket.org/dbpina/keras-prov-schemas/src/master/dbpina-keras-prov/DfAnalyzer/)
* [dfa-lib-python](https://bitbucket.org/dbpina/keras-prov-schemas/src/master/dbpina-keras-prov/dfa-lib-python/) 

### Instalação da KerasProv

Após baixar o repositório, realize os seguintes comandos:


```

cd dfa-lib-python
python setup.py install

cd keras
python setup.py install

```

A utilização efetiva da KerasProv depende da inicialização da DfAnalyzer e do Banco de dados utilizado. Para isto execute os seguintes comandos:


```

cd DfAnalyzer
./restore-database.sh

java -Xss2000m -Xms2000m -Xmx4000m -jar target/DfAnalyzer-1.0.jar

```

Ou executar:


```

cd DfAnalyzer
./start-dfanalyzer.sh

```

No script da rede neural, especificada com o Keras, o usuário deve acrescentar o seguinte código:

```
hyps = {"OPTIMIZER_NAME": True,
"LEARNING_RATE": True,
"DECAY": False,
"MOMENTUM": False,
"NUM_EPOCHS": True,
"BATCH_SIZE": False,
"NUM_LAYERS": True}

model.provenance(dataflow_tag="keras-alexnet-df",
                 adaptation=True,
                 hyps = hyps)
```

O método provenance deve ser utilizado para capturar dados de proveniência. Esse método recebe uma tag para identificação do fluxo de dados (dataflow_tag), se existe adaptação dos hiperparâmetros durante otreinamento (atualização da taxa de aprendizado, por exemplo). Essa versão suporta apenas a utilização do método LearningRateScheduler oferecido pelo Keras, e a lista de hiperparâmetros que se deseja capturar (em que deve marcar True ou False para aqueles hiperparâmetros que deseja capturar).

