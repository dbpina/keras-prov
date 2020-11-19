import requests
import os
from .ProvenanceObject import ProvenanceObject
from .transformation import Transformation

dfa_url = os.environ.get('DFA_URL', "http://localhost:22000/")


class Dataflow(ProvenanceObject):
    """
    This class defines a dataflow.
    
    Attributes:
        - tag (str): Dataflow tag.
        - transformations (list, optional): Dataflow transformations.
    """
    def __init__(self, tag, transformations=[]):
        ProvenanceObject.__init__(self, tag)
        self.transformations = transformations

    @property
    def transformations(self):
        """Get or set the dataflow transformations."""
        return self._transformations

    @transformations.setter
    def transformations(self, transformations):
        assert isinstance(transformations, list), \
            "The Transformations must be in a list."
        result = []
        for transformation in transformations:
            assert isinstance(transformation, Transformation), \
                "The Transformation must be valid."
            result.append(transformation.get_specification())
        self._transformations = result

    def add_transformation(self, transformation):
        """ Add a transformation to the dataflow.

        Args:
            transformation (:obj:`Transformation`): A dataflow transformation.
        """
        assert isinstance(transformation, Transformation), \
            "The parameter must must be a transformation."
        self._transformations.append(transformation.get_specification())

    def save(self):
        """ Send a post request to the Dataflow Analyzer API to store
            the dataflow.
        """
        url = dfa_url + '/pde/dataflow/json'
        r = requests.post(url, json=self.get_specification())      
        print(r.status_code)
