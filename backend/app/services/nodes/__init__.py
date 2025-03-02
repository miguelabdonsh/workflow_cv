# Importar nodos para facilitar su uso
from .base_node import BaseNode, NodeMetadata
from .workflow import WorkflowManager, WorkflowStatus, WorkflowMetadata
from .extractor_node import ExtractorNode, ExtractorInput
from .classifier_node import ClassifierNode
from .skills_evaluator_node import SkillsEvaluatorNode, SkillsEvaluatorInput

# Versión del módulo de nodos
__version__ = "0.1.0" 