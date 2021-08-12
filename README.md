# Keras-Prov

## Overview

Keras-Prov is a provenance service management approach designed for supporting hyperparameter analysis in Deep Neural Networks (DNNs). Keras-Prov integrates traditional retrospective provenance data (r-prov) with domain-specific DL data. This solution provides an API that allows for users to develop their ML-based workflows using Keras while being able to share and analyze captured provenance data using W3C PROV. 

Keras-Prov was developed based on [DfAnalyzer](https://gitlab.com/ssvitor/dataflow_analyzer) and with modifications on [Keras](https://github.com/keras-team/keras) source code.

## Software requirements

The following softwares have to be configured/installed for running a DNN training that collects provenance with Keras-Prov.

* [Java](https://java.com/pt-BR/)
* [MonetDB](http://www.monetdb.org/Documentation/UserGuide/Tutorial)
* [PyMonetDB](https://pymonetdb.readthedocs.io/en/latest/index.html)
* [DfAnalyzer](https://github.com/dbpina/keras-prov/tree/main/DfAnalyzer)
* [dfa-lib-python](https://github.com/dbpina/keras-prov/tree/main/dfa-lib-python/) 

## Installation

### MonetDB

To install MonetDB follow the tutorial at: https://www.monetdb.org/Documentation/Tutorial

To run and query the dump (which is available in the directory "sql" in the directory "Example"), run the following commands: 

```
monetdb create dataflow_analyzer
monetdb release dataflow_analyzer
mclient –u monetdb –lsql –database=dataflow_analyzer dump.sql

```

The database schema is also available and can be accessed in the directory "sql" in the directory "Example".


<!---### RESTful services -->


###  Python library: dfa-lib-python

Download (or clone) this repository, and run:


```

cd dfa-lib-python
python setup.py install

cd ..

cd keras
python setup.py install

```

## RESTful services initialization

Keras-Prov depends on the initialization of DfAnalyzer and the SGBD MonetDB. 

Instructions for this step can also be found at GITLAB. The project DfAnalyzer at `DfAnalyzer` contains all web applications and RESTful services provided by the tool. Therefore, the following components are present in this project: Dataflow Viewer (DfViewer), Query Interface (QI), and Query Dashboard (QP). We provide a compressed file of our MonetDB database (to DfAnalyzer) for a local execution of the project DfAnalyzer. Therefore, users only need to run the script start-dfanalyzer.sh at the path DfAnalyzer. We assume the execution of these steps in an Unix-based operating system, as follows:

```

cd DfAnalyzer
./start-dfanalyzer.sh

```


## How to run DNN applications

Keras-Prov contains a method *provenance* to capture provenance data. This method receives a tag to identify the experiment, if there is an adaptation of the hyperparameters during training (e.g., an update of the learning rate), that is, the use of methods such as LearningRateScheduler offered by Keras, and the list of hyperparameters to be captured. The user needs only to set which hyperparameters to capture, and no additional instrumentation is required. After setting True to the hyperparameters of interest, the user adds a call to the method provenance. The data received by the provenance method are defined by the user in the source code of the DNN application, as follows:

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

## Example

At the path `Example`, the user can find a usage example of Keras-Prov. To run it, the user just needs to run the python command as it is normally done, as follows:

```
python alexnet.py
```

To add new parameters to be captured and stored, the user need to import the necessary packages of dfa-lib-python and specify the new transformation. For example, if they want to capture data related to a dense block (growth rate and number of layers in the dense block), the specification have to be added before the *model.fit* command and should be like:

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

## Note

Instead of importing *tensorflow.keras* module, one should import *keras*. For instance:

```
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.layers import BatchNormalization
```

should be replaced by:


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

## Presentation Video

To watch the video, please, click [here](https://www.youtube.com/watch?v=QOZY2CQfXJ8).

## Publications

* [Pina, D. B., Neves, L., Paes, A., de Oliveira, D., & Mattoso, M. (2019, November). Análise de hiperparâmetros em aplicações de aprendizado profundo por meio de dados de proveniência. In Anais do XXXIV Simpósio Brasileiro de Banco de Dados (pp. 223-228). SBC.](https://sol.sbc.org.br/index.php/sbbd/article/view/8827)

* [Pina, D., Kunstmann, L., de Oliveira, D., Valduriez, P., & Mattoso, M. (2020, September). Uma abordagem para coleta e análise de dados de configurações em redes neurais profundas. In 35ª Simpósio Brasileiro de Banco de Dados (SBBD) (pp. 1-6).](https://hal-lirmm.ccsd.cnrs.fr/lirmm-02969506/)

* [Pina, D., Kunstmann, L., de Oliveira, D., Valduriez, P., & Mattoso, M. (2020). Provenance Supporting Hyperparameter Analysis in Deep Neural Networks. In Provenance and Annotation of Data and Processes (pp. 20-38). Springer, Cham.](https://link.springer.com/chapter/10.1007/978-3-030-80960-7_2)
