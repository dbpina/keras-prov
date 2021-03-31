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
docker pull lilianekunstmann/kerasprov
```

This image can be executed and accessed interactively through the following commands:

```
docker run --name <nome_container> -i kerasprov
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

To add new parameters to be captured and store, the user have to import the necessary packeges of dfa-lib-python and specify the new transformation. For example, if one wants to capture data related to a dense block (growth rate and number of layers in the dense block), the specification have to be added before the model.fit command and would be like:

```
from dfa_lib_python.dataflow import Dataflow
from dfa_lib_python.transformation import Transformation
from dfa_lib_python.attribute import Attribute
from dfa_lib_python.attribute_type import AttributeType
from dfa_lib_python.set import Set
from dfa_lib_python.set_type import SetType
from dfa_lib_python.task import Task
from dfa_lib_python.dataset import DataSet
from dfa_lib_python.element import Element

df = model.get_dataflow()

tf_denseb = Transformation("DenseBlock")
tf_denseb_input = Set("iDenseBlock", SetType.INPUT, 
    [Attribute("growth_rate", AttributeType.NUMERIC), 
    Attribute("layers_db", AttributeType.NUMERIC)])
tf_denseb_output = Set("oDenseBlock", SetType.OUTPUT, 
    [Attribute("output", AttributeType.TEXT)])
tf_denseb.set_sets([tf_denseb_input, tf_denseb_output])
df.add_transformation(tf_denseb) 
```

The second step is the moment when the user must instrument the code to capture the parameter value. For example:

```
t_denseb = Task(identifier=4, dataflow_tag, "DenseBlock")
##Data manipulation, example:
growth_rate = 1
layers_db = 33
t_denseb_input = DataSet("iExtrairNumeros", [Element([growth_rate, layers_db])])
t_denseb.add_dataset(t_denseb_input)
t_denseb.begin()
##Data manipulation, example:
t_denseb_output= DataSet("oExtrairNumeros", [Element([output])])
t_denseb.add_dataset(t_denseb_output)
t_denseb.end()
```


Both steps, specification of the transformation and the activity definition, follow the definitions of [dfa-lib-python](http://monografias.poli.ufrj.br/monografias/monopoli10026387.pdf) for DfAnalyzer.
