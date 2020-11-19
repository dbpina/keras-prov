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
import pymonetdb

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
		    Attribute("TIMESTAMP", AttributeType.TEXT),
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

	def create_training_transformation(self, hyps, adaptation, transformations, hyperparameters):
		self.transformations_total = 0
		self.transformations_task = {}
		new_atts = []
		for i, j in hyperparameters.items():
			new_atts.append(Attribute(i, AttributeType[j]))

		# if (bool(transformations)):
		# 	for dt_tag, dt_atts in transformations.items():
		# 		i_atts = []
		# 		o_atts = []
		# 		t = Transformation(dt_tag)

		# 		for set_type, atts in dt_atts.items():
		# 		    for key in atts:
		# 		        if (set_type == "input"):
		# 		        	i_atts.append(Attribute(key.upper(), AttributeType[atts[key].upper()]))				        
		# 		        elif (set_type == "output"):
		# 		        	o_atts.append(Attribute(key.upper(), AttributeType[atts[key].upper()]))

		# 		tf_input = Set("i" + dt_tag, SetType.INPUT, i_atts)
		# 		tf_output = Set("o" + dt_tag, SetType.OUTPUT, o_atts)
		# 		t.set_sets([tf_input, tf_output])
		# 		self.transformations_total += 1
		# 		self.transformations_task[dt_tag] = self.transformations_total
		# 		self.df.add_transformation(t)


		tf1 = Transformation("TrainingModel")	
		tf1_layers_input = Set("iLayers", SetType.INPUT, 
		    [Attribute("TIMESTAMP", AttributeType.TEXT),
		    Attribute("NAME", AttributeType.TEXT),
		    Attribute("ATTRIBUTE_TYPE", AttributeType.TEXT),
		    Attribute("VALUE", AttributeType.TEXT)])
		# tf1_input = Set("iTrainingModel", SetType.INPUT, 
		#      [Attribute("OPTIMIZER_NAME", AttributeType.TEXT), 
		#     Attribute("LEARNING_RATE", AttributeType.NUMERIC),
		#     Attribute("DECAY", AttributeType.NUMERIC),
		#     Attribute("MOMENTUM", AttributeType.NUMERIC)] + atts)
		tf1_output = Set("oTrainingModel", SetType.OUTPUT, 
		    [Attribute("TIMESTAMP", AttributeType.TEXT), 
		    Attribute("ELAPSED_TIME", AttributeType.TEXT),
		    Attribute("LOSS", AttributeType.NUMERIC),
		    Attribute("ACCURACY", AttributeType.NUMERIC),
		    Attribute("VAL_LOSS", AttributeType.NUMERIC),
		    Attribute("VAL_ACCURACY", AttributeType.NUMERIC),    
		    Attribute("EPOCH", AttributeType.NUMERIC)])

		self.transformations_total += 1
		self.transformations_task["TrainingModel"] = self.transformations_total

		atts_hyps = []
		atts_hyps.append(Attribute("TIMESTAMP", AttributeType.TEXT))
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

		#self.df.save()

		return self.transformations_task

	def create_layer_transformation(self):
		tf3 = Transformation("Layers")
		tf3_input = Set("iLayers", SetType.INPUT, 
		    [Attribute("TIMESTAMP", AttributeType.TEXT),
		    Attribute("NAME", AttributeType.TEXT),
		    Attribute("ATTRIBUTE_TYPE", AttributeType.TEXT),
		    Attribute("VALUE", AttributeType.TEXT)])
		tf3.set_sets([tf3_input])
		self.df.add_transformation(tf3)

	def add_hyperparameter(self, hyperparameters):
		print("not first run -- adding hyp")
		# set up a connection. arguments below are the defaults
		connection = pymonetdb.connect(username="monetdb", password="monetdb", hostname="localhost", database="dataflow_analyzer")
		# create a cursor
		cursor = connection.cursor()		

		for i, j in hyperparameters.items():
			print (i + " " + j)
			# atts.append(Attribute(i, AttributeType[j]))
			query_check_table = "select * from sys.columns where name='" + i.lower() + "' and table_id=(select id from sys.tables where name='ds_itrainingmodel');"
			exists = cursor.execute(query_check_table)
			if (exists == 0):			
				query_alter_table = "ALTER TABLE ds_itrainingmodel ADD " + i + " " + j + "; COMMIT;"
				rows = cursor.execute(query_alter_table)

		cursor.execute("CREATE VIEW itrainingmodel AS SELECT * FROM ds_itrainingmodel; COMMIT;")

		connection.close()

	def add_hyperparameter_from_list(self, hyps):
		# set up a connection. arguments below are the defaults
		connection = pymonetdb.connect(username="monetdb", password="monetdb", hostname="localhost", database="dataflow_analyzer")
		# create a cursor
		cursor = connection.cursor()		

		for i in hyps:
			query_check_table = "select * from sys.columns where name='" + i.lower() + "' and table_id=(select id from sys.tables where name='ds_itrainingmodel');"
			exists = cursor.execute(query_check_table)
			if (exists == 0):
				query_alter_table = "ALTER TABLE ds_itrainingmodel ADD " + i + " " + hyperparameters_types[i] + "; COMMIT;"
				rows = cursor.execute(query_alter_table)
				cursor.execute("INSERT INTO attribute (ds_id, extractor_id, name, type) VALUES (10, null, '" + i.lower() + "', '" + hyperparameters_types[i] + "'); COMMIT;")

		cursor.execute("CREATE VIEW itrainingmodel AS SELECT * FROM ds_itrainingmodel; COMMIT;")

		connection.close()

	def get_task_id(self, dataflow_tag):
		# set up a connection. arguments below are the defaults
		connection = pymonetdb.connect(username="monetdb", password="monetdb", hostname="localhost", database="dataflow_analyzer")
		# create a cursor
		cursor = connection.cursor()		
		get_tasks = "select tag, identifier from task, data_transformation where task.dt_id = data_transformation.id;"
		cursor.execute(get_tasks)
		rows = cursor.fetchall()

		for i, j in rows:
			self.transformations_task[i] = j

		connection.close()

	def get_columns_names(self, dataflow_tag):
		# set up a connection. arguments below are the defaults
		connection = pymonetdb.connect(username="monetdb", password="monetdb", hostname="localhost", database="dataflow_analyzer")
		# create a cursor
		cursor = connection.cursor()		
		get_columns = "select name from sys.columns where table_id=(select id from sys.tables where name='ds_itrainingmodel') and name <> 'id' and name <> 'trainingmodel_task_id';"
		cursor.execute(get_columns)
		columns = cursor.fetchall()
		
		for i in columns:
			self.columns.append(i[0]) 
		
		connection.close()


		# out = Set("oTrainingModel", SetType.OUTPUT, 
		#     [Attribute("TIMESTAMP", AttributeType.TEXT), 
		#     Attribute("ELAPSED_TIME", AttributeType.TEXT),
		#     Attribute("LOSS", AttributeType.NUMERIC),
		#     Attribute("ACCURACY", AttributeType.NUMERIC),
		#     Attribute("VAL_LOSS", AttributeType.NUMERIC),
		#     Attribute("VAL_ACCURACY", AttributeType.NUMERIC),    
		#     Attribute("EPOCH", AttributeType.NUMERIC)])

		# t1.set_sets([inp])
		# self.df.add_transformation(t1)	
		# self.df.save()

	def get_first_run(self, dataflow_tag):
		# set up a connection. arguments below are the defaults
		connection = pymonetdb.connect(username="monetdb", password="monetdb", hostname="localhost", database="dataflow_analyzer")
		# create a cursor
		cursor = connection.cursor()		
		query = "SELECT * FROM dataflow WHERE tag = %(tag)s"
		rows = cursor.execute(query, {'tag': dataflow_tag})
		if (rows>=1):
			return False
		elif (rows==0):
			return True

	def drop_view(self, dataflow_tag):
		# set up a connection. arguments below are the defaults
		connection = pymonetdb.connect(username="monetdb", password="monetdb", hostname="localhost", database="dataflow_analyzer")
		# create a cursor
		cursor = connection.cursor()		
		query = "DROP VIEW IF EXISTS itrainingmodel; COMMIT;"
		rows = cursor.execute(query)
		connection.close()


	def save(self, dataflow_tag):
		self.df.save()

	def get_dataflow(self):
		return self.df

	def set_dataflow(self, dataflow_tag):
		self.df = Dataflow(dataflow_tag)