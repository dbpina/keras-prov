# Keras-Prov

### Overview

Keras-Prov is a provenance service management approach designed for supporting hyperparameter analysis in Deep Neural Networks (DNNs). Keras-Prov integrates traditional retrospective provenance data (r-prov) with domain-specific DL data. This solution provides an API that allows for users to develop their ML-based workflows using Keras while being able to share and analyze captured provenance data using W3C PROV. 

Keras-Prov was developed based on [DfAnalyzer](https://gitlab.com/ssvitor/dataflow_analyzer) and with modifications on [Keras](https://github.com/keras-team/keras) source code.

### Keras-Prov installation

The following softwares have to be configured/installed for running an DNN training with provenance capture.

* [Java](https://java.com/pt-BR/)
* [MonetDB](http://www.monetdb.org/Documentation/UserGuide/Tutorial)
* [PyMonetDB](https://pymonetdb.readthedocs.io/en/latest/index.html)
* [DfAnalyzer](https://github.com/dbpina/keras-prov/tree/main/DfAnalyzer)
* [dfa-lib-python](https://github.com/dbpina/keras-prov/tree/main/dfa-lib-python/) 

Download (or clone) this repository, and run:


```

cd dfa-lib-python
python setup.py install

cd ..

cd keras
python setup.py install

```

The use of Keras-Prov depends on the initialization of DfAnalyzer and the database used. To do this, run the following commands:


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

Important: In the neural network script specified with Keras, the user must add the following code:

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


## Presentation Video

To watch the video, please, click [here](https://www.youtube.com/watch?v=QOZY2CQfXJ8).

## Publications

* [MURTA, L. G. P.; BRAGANHOLO, V.; CHIRIGATI, F. S.; KOOP, D.; FREIRE, J.; noWorkflow: Capturing and Analyzing Provenance of Scripts. In: International Provenance and Annotation Workshop (IPAW), 2014, Cologne, Germany.](https://github.com/gems-uff/noworkflow/raw/master/docs/ipaw2014.pdf)

* [Pina, D. B., Neves, L., Paes, A., de Oliveira, D., & Mattoso, M. (2019, November). Análise de hiperparâmetros em aplicações de aprendizado profundo por meio de dados de proveniência. In Anais do XXXIV Simpósio Brasileiro de Banco de Dados (pp. 223-228). SBC.](https://sol.sbc.org.br/index.php/sbbd/article/view/8827)

* [Pina, D., Kunstmann, L., de Oliveira, D., Valduriez, P., & Mattoso, M. (2020, September). Uma abordagem para coleta e análise de dados de configurações em redes neurais profundas. In 35ª Simpósio Brasileiro de Banco de Dados (SBBD) (pp. 1-6).](https://hal-lirmm.ccsd.cnrs.fr/lirmm-02969506/)

* [Pina, D., Kunstmann, L., de Oliveira, D., Valduriez, P., & Mattoso, M. (2020). Provenance Supporting Hyperparameter Analysis in Deep Neural Networks. In Provenance and Annotation of Data and Processes (pp. 20-38). Springer, Cham.](https://link.springer.com/chapter/10.1007/978-3-030-80960-7_2)
