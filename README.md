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

