from utils.create_fake_log import create_fake_log
from pm4py.objects.log.importer.xes import importer as xes_importer
from directly_follows_graph import DFG, DFGNode, DFGEdge
from networkx import Graph

from bpmn_python.bpmn_diagram_rep import BpmnDiagramGraph
from bpmn_python.bpmn_diagram_layouter import generate_layout
from bpmn_python.bpmn_diagram_visualizer import bpmn_diagram_to_png, visualize_diagram

from bpmn_diagram import BPMNDiagram

artificial_log = create_fake_log(with_loops=False)


if __name__ == "__main__":
    # log = xes_importer.apply('../data/logs/Sepsis_Cases.xes')
    # dfg2 = DFG(log, concurrency_threshold=0.5, filtering_percentile_threshold=0.3)
    # print(DFGEdge(DFGNode("Leucocytes"), DFGNode("CRP")) in dfg.concurrency_relations)

    dfg2 = DFG(artificial_log, concurrency_threshold=0.4, filtering_percentile_threshold=0.1, artificial_log=True)
    # dfg2.show_dfg(filename="graph.png")
    diagram = BPMNDiagram(dfg2, dfg2.concurrency_relations, artificial=False)
    # diagram.generate_simple_joins()
    diagram.export_as_png('diagram')
    diagram.export_as_xml('.', 'diagram.xml')
    diagram.visualize()















