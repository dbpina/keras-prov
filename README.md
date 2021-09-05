# Keras-Prov

## Overview

Keras-Prov is a provenance service designed for supporting online hyperparameter analysis in Deep Neural Networks (DNNs). Keras-Prov integrates traditional retrospective provenance data (r-prov) with typical DNN software data, e.g. hyperparameters, DNN architecture attributes, etc. using W3C PROV. This solution provides an API that allows for users to develop their DNN-based workflows using Keras while being able to analyze online captured provenance data.

Keras-Prov is developed on top of [DfAnalyzer](https://gitlab.com/ssvitor/dataflow_analyzer) provenance services and with modifications on the Keras source code. It uses the columnar DBMS MonetDB to support online provenance data analysis and to generate W3C PROV compliant documents.

## Software requirements

The following softwares have to be configured/installed for running a DNN training that collects provenance with Keras-Prov.

* [Java](https://java.com/pt-BR/)
* [MonetDB](http://www.monetdb.org/Documentation/UserGuide/Tutorial)
* [PyMonetDB](https://pymonetdb.readthedocs.io/en/latest/index.html)
* [DfAnalyzer](https://github.com/dbpina/keras-prov/tree/main/DfAnalyzer)
* [dfa-lib-python](https://github.com/dbpina/keras-prov/tree/main/dfa-lib-python/) 
* [TensorFlow v2.2.0](https://www.tensorflow.org/)

## Installation

<!---### RESTful services -->


###  Python library: dfa-lib-python

The DfAnalyzer library for the programming language Python can be built with the following command lines:

```

cd dfa-lib-python
python setup.py install

```
###  DNN library with provenance capture: Keras-Prov

The Keras-Prov library can be built with the following command lines:

```

cd keras
python setup.py install

```

## RESTful services initialization

Keras-Prov depends on the initialization of DfAnalyzer and the DBMS MonetDB.

Instructions for this step can also be found at [GitLab](https://gitlab.com/ssvitor/dataflow_analyzer). The project DfAnalyzer at DfAnalyzer contains web applications and RESTful services provided by the tool. 

The following components are present in this project: Dataflow Viewer (DfViewer), Query Interface (QI), and Query Dashboard (QP). We provide a compressed file of our MonetDB database (to DfAnalyzer) for a local execution of the project DfAnalyzer. Therefore, users only need to run the script start-dfanalyzer.sh at the path DfAnalyzer. We assume the execution of these steps with a Unix-based operating system, as follows:

```

cd DfAnalyzer
./start-dfanalyzer.sh

```


## How to run DNN applications

The user needs only to set which hyperparameters to capture, and no additional instrumentation is required. After setting True to the hyperparameters of interest, the user adds a call to the method *provenance*. The provenance method is used by Keras-Prov to capture provenance data with the hyperparameters of interest. This method receives a tag to identify the workflow and associate to the provenance data, e.g. hyperparameters. This method captures provenance data as the Keras workflow executes and sends them to the provenance database managed by MonetDB. As the data reaches the database, it can be analyzed through the Dataflow Viewer (DfViewer), Query Interface (QI), and Query Dashboard (QP). In case there is an adaptation of the hyperparameters during training (e.g., an update of the learning rate), that is, the use of methods such as LearningRateScheduler offered by Keras, the hyperparameter’s values are updated and the adaptation is registered. The data received by the provenance method are defined by the user in the source code of the DNN application, as follows:

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

The path `Example` shows how to use Keras-Prov. To run it, the user just needs to run the python command, as follows: 

```
python alexnet.py
```

To add new parameters (not present in the “hyps” list )to be captured and stored, the user needs to import the packages of dfa-lib-python and specify the new transformation. For example, if they want to capture data related to the DNN architecture like a dense block (growth rate and number of layers in the dense block), the specification has to be added before the model.fit command on user's training code and should be like:

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
docker pull lilianekunstmann/keras-prov
```

This image can be executed and accessed interactively through the following commands:

```
docker run --network host --name <nome_container> -i lilianekunstmann/keras-prov
docker exec -it <nome_container> bash
```

## Presentation Video

To watch the video, please, click [here](https://www.youtube.com/watch?v=QOZY2CQfXJ8).

## Publications

* [Pina, D. B., Neves, L., Paes, A., de Oliveira, D., & Mattoso, M. (2019, November). Análise de hiperparâmetros em aplicações de aprendizado profundo por meio de dados de proveniência. In Anais do XXXIV Simpósio Brasileiro de Banco de Dados (pp. 223-228). SBC.](https://sol.sbc.org.br/index.php/sbbd/article/view/8827)

* [Pina, D., Kunstmann, L., de Oliveira, D., Valduriez, P., & Mattoso, M. (2020, September). Uma abordagem para coleta e análise de dados de configurações em redes neurais profundas. In 35ª Simpósio Brasileiro de Banco de Dados (SBBD) (pp. 1-6).](https://hal-lirmm.ccsd.cnrs.fr/lirmm-02969506/)

* [Pina, D., Kunstmann, L., de Oliveira, D., Valduriez, P., & Mattoso, M. (2020). Provenance Supporting Hyperparameter Analysis in Deep Neural Networks. In Provenance and Annotation of Data and Processes (pp. 20-38). Springer, Cham.](https://link.springer.com/chapter/10.1007/978-3-030-80960-7_2)
