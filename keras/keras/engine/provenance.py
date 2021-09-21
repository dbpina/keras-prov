from dfa_lib_python.dataflow import Dataflow
from dfa_lib_python.transformation import Transformation
from dfa_lib_python.attribute import Attribute
from dfa_lib_python.attribute_type import AttributeType
from dfa_lib_python.set import Set
from dfa_lib_python.set_type import SetType
from dfa_lib_python.task import Task
from dfa_lib_python.dataset import DataSet
from dfa_lib_python.element import Element
from dfa_lib_python.task_status import TaskStatus

from enum import Enum

hyperparameters_types = {"OPTIMIZER_NAME": "TEXT",
"LEARNING_RATE": "NUMERIC",
"DECAY": "NUMERIC",
"MOMENTUM": "NUMERIC",
"NUM_EPOCHS": "NUMERIC",
"BATCH_SIZE": "NUMERIC",
"NUM_LAYERS": "NUMERIC"}

# create and deal with transformations (e.g: if it is a re-run of the dataflow, 
# it should not run prospective provenance)

# check if adaptation is used in the user's application, if it is, this script should 
# create/use a tranformation for it
class Provenance():

	def __init__(self, dataflow_tag):
		self.dataflow_tag = dataflow_tag
		self.df = Dataflow(self.dataflow_tag)
		self.transformations_task = {}
		self.columns = []

	def create_adaptation_transformation(self):
		tf2 = Transformation("Adaptation")
		# tf2_input = Set("iAdaptation", SetType.INPUT, 
		#     [Attribute("EPOCHS_DROP", AttributeType.NUMERIC), 
		#     Attribute("DROP_N", AttributeType.NUMERIC),
		#     Attribute("INITIAL_LRATE", AttributeType.NUMERIC)])
		tf2_output = Set("oAdaptation", SetType.OUTPUT, 
		    [Attribute("NEW_LRATE", AttributeType.NUMERIC),
		    Attribute("ATIMESTAMP", AttributeType.TEXT),
		    Attribute("EPOCH_ID", AttributeType.NUMERIC),
		    Attribute("ADAPTATION_ID", AttributeType.NUMERIC)])
		self.tf1_output.set_type(SetType.INPUT)
		self.tf1_output.dependency=self.tf1._tag
		tf2.set_sets([self.tf1_output, tf2_output])
		self.df.add_transformation(tf2)  

		self.transformations_total += 1
		self.transformations_task["Adaptation"] = self.transformations_total

	# check if the user is using hyperparameters not supported, if they are, this script
	# should calls DfAnalyzer to alter table or alter table itself

	def create_training_transformation(self, hyps, adaptation, transformations, hyperparameters, metrics):
		self.transformations_total = 0
		self.transformations_task = {}

		new_atts = []
		for i, j in hyperparameters.items():
			new_atts.append(Attribute(i, AttributeType[j]))

		tf1 = Transformation("TrainingModel")	
		tf1_layers_input = Set("iLayers", SetType.INPUT, 
		    [Attribute("ILTIMESTAMP", AttributeType.TEXT),
		    Attribute("NAME", AttributeType.TEXT),
		    Attribute("ATTRIBUTE_TYPE", AttributeType.TEXT),
		    Attribute("VALUE", AttributeType.TEXT)])
		# tf1_input = Set("iTrainingModel", SetType.INPUT, 
		#      [Attribute("OPTIMIZER_NAME", AttributeType.TEXT), 
		#     Attribute("LEARNING_RATE", AttributeType.NUMERIC),
		#     Attribute("DECAY", AttributeType.NUMERIC),
		#     Attribute("MOMENTUM", AttributeType.NUMERIC)] + atts)
		# tf1_output = Set("oTrainingModel", SetType.OUTPUT, 
		#     [Attribute("OTIMESTAMP", AttributeType.TEXT), 
		#     Attribute("ELAPSED_TIME", AttributeType.TEXT),
		#     Attribute("LOSS", AttributeType.NUMERIC),
		#     Attribute("ACCURACY", AttributeType.NUMERIC),
		#     Attribute("PRECISION", AttributeType.NUMERIC),
		#     Attribute("RECALL", AttributeType.NUMERIC),
		#     Attribute("VAL_LOSS", AttributeType.NUMERIC),
		#     Attribute("VAL_ACCURACY", AttributeType.NUMERIC),  
		# 	  Attribute("VAL_PRECISION", AttributeType.NUMERIC),
		#     Attribute("VAL_RECALL", AttributeType.NUMERIC),		      
		#     Attribute("EPOCH", AttributeType.NUMERIC)])

		self.transformations_total += 1
		self.transformations_task["TrainingModel"] = self.transformations_total

		train_metrics = list(metrics)
		train_metrics += ['val_' + n for n in metrics]
		m_metrics = []
		m_metrics.append(Attribute("OTRAIN_TIMESTAMP", AttributeType.TEXT))
		m_metrics.append(Attribute("ELAPSED_TIME", AttributeType.TEXT))
		m_metrics.append(Attribute("EPOCH_ID", AttributeType.NUMERIC))
		for n in train_metrics:
			m_metrics.append(Attribute(n, AttributeType.NUMERIC))

		tf1_output = Set("oTrainingModel", SetType.OUTPUT, m_metrics)

		atts_hyps = []
		atts_hyps.append(Attribute("ITRAIN_TIMESTAMP", AttributeType.TEXT))
		for i in hyps:
			hyp_type = hyperparameters_types[i]
			atts_hyps.append(Attribute(i, AttributeType[hyp_type]))

		if(bool(atts_hyps) and bool(new_atts)):
			tf1_input = Set("iTrainingModel", SetType.INPUT, atts_hyps + new_atts)	
			self.tf1_input = tf1_input
			tf1.set_sets([tf1_layers_input, tf1_input, tf1_output])
		elif(bool(atts_hyps) and not(bool(new_atts))):
			tf1_input = Set("iTrainingModel", SetType.INPUT, atts_hyps)	
			self.tf1_input = tf1_input
			tf1.set_sets([tf1_layers_input, tf1_input, tf1_output])			
		elif(not(bool(atts_hyps)) and bool(new_atts)):
			tf1_input = Set("iTrainingModel", SetType.INPUT, new_atts)	
			self.tf1_input = tf1_input
			tf1.set_sets([tf1_layers_input, tf1_input, tf1_output])
		else:
			tf1.set_sets([tf1_layers_input, tf1_output])


		self.df.add_transformation(tf1)		

		self.tf1 = tf1
		self.tf1_output = tf1_output	

		# self.create_layer_transformation()

		if adaptation is True:
			self.create_adaptation_transformation()

		tf3 = Transformation("TestingModel")
		te_metrics = []
		te_metrics.append(Attribute("OTEST_TIMESTAMP", AttributeType.TEXT))
		for n in metrics:
			te_metrics.append(Attribute(n, AttributeType.NUMERIC))
		
		tf3_output = Set("oTestingModel", SetType.OUTPUT, te_metrics)			
		tf1_output.set_type(SetType.INPUT)
		tf1_output.dependency=tf1._tag
		tf3.set_sets([tf1_output, tf3_output])
		self.df.add_transformation(tf3) 			

		#self.df.save()

		return self.transformations_task

	def create_layer_transformation(self):
		tf3 = Transformation("Layers")
		tf3_input = Set("iLayers", SetType.INPUT, 
		    [Attribute("ILTIMESTAMP", AttributeType.TEXT),
		    Attribute("NAME", AttributeType.TEXT),
		    Attribute("ATTRIBUTE_TYPE", AttributeType.TEXT),
		    Attribute("VALUE", AttributeType.TEXT)])
		tf3.set_sets([tf3_input])
		self.df.add_transformation(tf3)

	def save(self, dataflow_tag):
		self.df.save()

	def get_dataflow(self):
		return self.df

	def set_dataflow(self, dataflow_tag):
		self.df = Dataflow(dataflow_tag)
