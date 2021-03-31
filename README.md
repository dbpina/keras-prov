# keras-prov
Keras-Prov was developed based on [DfAnalyzer](https://gitlab.com/ssvitor/dataflow_analyzer) and with adaptation on [Keras](https://github.com/keras-team/keras) source code.

The following softwares have to be configured / installed for running this application.

* [Java](https://java.com/pt-BR/)
* [MonetDB](http://www.monetdb.org/Documentation/UserGuide/Tutorial)
* [PyMonetDB](https://pymonetdb.readthedocs.io/en/latest/index.html)
* [DfAnalyzer](https://github.com/dbpina/keras-prov/tree/main/DfAnalyzer)
* [dfa-lib-python](https://github.com/dbpina/keras-prov/tree/main/dfa-lib-python/) 

### Keras-Prov installation

Download (or clone) this repository, and run:


```

cd dfa-lib-python
python setup.py install

cd ..

cd keras
python setup.py install

```

The use of KerasProv depends on the initialization of DfAnalyzer and the database used. To do this, run the following commands:


```

cd DfAnalyzer
./restore-database.sh

java -jar target/DfAnalyzer-1.0.jar

```

Or run:


```

cd DfAnalyzer
./start-dfanalyzer.sh

```

Important: In the neural network script, specified with Keras, the user must add the following code:

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

The method provenance is used to define the dataflow (prospective provenance) and to capture provenance data. This method receives a tag to identify the dataflow, if there is an adaptation of the hyperparameters during training (e.g., an update of the learning rate), that is, the use of methods such as LearningRateScheduler offered by Keras, and the list of hyperparameters to be captured. 

### Note

Instead of importing tensorflow.keras module, one should import the keras from the source code. Example:

```
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.layers import BatchNormalization
```

should be replaced with:


```
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.layers import BatchNormalization
```

## Docker
We provide an image of the environment. The Dockerfile present in the folder creates the image of a container with the data from this repository. 

```
docker push lilianekunstmann/tensorflow_i
```

This image can be executed and accessed interactively through the following commands:

```
docker run --name <nome_container> -i tensorflow_i
docker exec -it <nome_container> bash
```
## MonetDB

To install MonetDB follow the tutorial at: https://www.monetdb.org/Documentation/Tutorial

To run and query the dump (which is available in the directory "sql" in the directory "Example"), run the following commands: 

```
monetdb create dataflow_analyzer
monetdb release dataflow_analyzer
mclient –u monetdb –lsql –database=dataflow_analyzer dump.sql

```

The database schema is also available and can be accessed in the directory "sql" in the directory "Example".

## Example

In the directory Example, the user may find a usage example of KerasProv. To run it, just run the following command:

```
python alexnet.py
```
