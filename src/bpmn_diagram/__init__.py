from .bpmn_edge import BPMNEdge
from .bpmn_node import BPMNNode
from .diagram_crawler import DiagramCrawler, CrawlerMerger
from bpmn_python.bpmn_diagram_rep import BpmnDiagramGraph
from bpmn_python.bpmn_diagram_layouter import generate_layout
from bpmn_python.bpmn_diagram_visualizer import bpmn_diagram_to_png, visualize_diagram


class BPMNDiagram:
    def __init__(self, dfg, dfg_concurrency, artificial=False):
        self.dfg = dfg
        self.concurrency_relations = []
        self.start = None
        self.end = None
        self.tasks = []
        self.flows = []
        self.gateways = []
        self.candidate_joins = {}
        self.outgoing = {}
        self.incoming = {}
        self.bpmn_model = None
        self.and_counter = 1
        self.xor_counter = 1
        self.or_counter = 1
        self.create_from_dfg(dfg_concurrency, artificial)

    def create_from_dfg(self, concurrency, artificial):
        # Create a task for each node in diagram
        for node in self.dfg.nodes:
            if node == self.dfg.source and not artificial:
                bpmn_task = BPMNNode(task_name=node.label, is_start=True)
                self.start = bpmn_task
            elif node == self.dfg.sink and not artificial:
                bpmn_task = BPMNNode(task_name=node.label, is_end=True)
                self.end = bpmn_task
            else:
                bpmn_task = BPMNNode(task_name=node.label)
            self.tasks.append(bpmn_task)

        # Create flows from DFG Edges
        for edge in self.dfg.edges:
            flow = BPMNEdge(BPMNNode(edge.src.label), BPMNNode(edge.tgt.label))
            self.flows.append(flow)

        if artificial:
            self.start = BPMNNode(task_name='Start', is_start=True)
            self.end = BPMNNode(task_name='End', is_end=True)
            self.tasks.append(self.start)
            self.tasks.append(self.end)
            flowstart = BPMNEdge(self.start, BPMNNode('a'))
            flowend = BPMNEdge(BPMNNode('h'), self.end)
            self.flows += [flowstart, flowend]

        # Transform Concurrency relations to BPMNNode
        for pair in concurrency:
            relation = (BPMNNode(pair.src.label), BPMNNode(pair.tgt.label))
            inverse_relation = (BPMNNode(pair.tgt.label), BPMNNode(pair.src.label))
            if relation not in self.concurrency_relations and inverse_relation not in self.concurrency_relations:
                self.concurrency_relations.append(relation)
        self.generate_splits()
        self.generate_simple_joins()
        self.remove_join_splits()

    def discover_outgoing_flows(self):
        for task in self.tasks:
            self.outgoing[task] = []
            for flow in self.flows:
                if flow.src == task:
                    self.outgoing[task].append(flow)
        for gate in self.gateways:
            self.outgoing[gate] = []
            for flow in self.flows:
                if flow.src == gate:
                    self.outgoing[gate].append(flow)

    def discover_incoming_flows(self):
        for task in self.tasks:
            self.incoming[task] = []
            for flow in self.flows:
                if flow.tgt == task:
                    self.incoming[task].append(flow)
        for gate in self.gateways:
            self.incoming[gate] = []
            for flow in self.flows:
                if flow.tgt == gate:
                    self.incoming[gate].append(flow)

    def are_concurrent(self, task, other):
        pair = (task, other)
        inverse_pair = (other, task)
        return pair in self.concurrency_relations or inverse_pair in self.concurrency_relations

    def get_direct_successors(self, task):
        successors = []
        for flow in self.outgoing[task]:
            successors.append(flow.tgt)
        return successors

    def get_direct_predecessors(self, task):
        predecessors = []
        for flow in self.incoming[task]:
            predecessors.append(flow.src)
        return predecessors

    def generate_splits(self):
        self.discover_outgoing_flows()
        self.discover_incoming_flows()
        tovisit = [self.start]
        visited = []

        while len(tovisit) > 0:
            entry = tovisit.pop(0)
            visited.append(entry)

            if entry == self.end:
                continue
            if not entry.is_gateway:
                if len(self.outgoing[entry]) > 1:
                    direct_successors = self.get_direct_successors(entry)
                    for successor in direct_successors:
                        if successor not in tovisit and successor not in visited:
                            tovisit.append(successor)
                    self.flows = [x for x in self.flows if x not in self.outgoing[entry]]
                    self.outgoing[entry] = []

                    crawlers = []

                    for successor in direct_successors:
                        crawler = DiagramCrawler()
                        crawler.add_past(successor)

                        for future_successor in direct_successors:
                            if successor == future_successor:
                                continue
                            if self.are_concurrent(successor, future_successor):
                                crawler.add_future(future_successor)
                        crawler.stringify()
                        crawlers.append(crawler)
                    final_crawler = CrawlerMerger.merge_crawlers(crawlers)

                    self.generate_splits_hierarchy(entry, final_crawler)

                else:
                    try:
                        next_node = self.outgoing[entry].pop(0).tgt
                    except IndexError as e:
                        print("Error for: ", entry)
                    if next_node not in tovisit and next_node not in visited:
                        tovisit.append(next_node)

    def generate_simple_joins(self):
        self.discover_incoming_flows()
        self.discover_outgoing_flows()

        visited = []
        tovisit = [self.end]

        while len(tovisit) > 0:
            print(visited, len(visited))
            entry = tovisit.pop(0)
            visited.append(entry)
            if not entry.is_gateway:
                if len(self.incoming[entry]) > 1:
                    predecessors = self.get_direct_predecessors(entry)
                    if len(self.incoming[entry]) == 2:
                        print("TWO LENGTH ", entry, predecessors)
                        join = None
                        for predecessor in predecessors:
                            if predecessor not in tovisit and predecessor not in visited:
                                tovisit.append(predecessor)
                        self.flows = [x for x in self.flows if x not in self.incoming[entry]]
                        for predecessor in predecessors:
                            for compare_predecessor in predecessors:
                                if not predecessor.is_gateway and not compare_predecessor.is_gateway:
                                    if self.are_concurrent(predecessor, compare_predecessor):
                                        join_name = 'AND' + str(self.and_counter)
                                        self.and_counter += 1
                                        join = BPMNNode(join_name, is_gateway=True, gateway_type='AND')
                                    else:
                                        join_name = 'XOR' + str(self.xor_counter)
                                        self.xor_counter += 1
                                        join = BPMNNode(join_name, is_gateway=True, gateway_type='XOR')
                                if join is not None:
                                    break
                            if join is not None:
                                break
                        if join is None:
                            join_name = 'OR' + str(self.or_counter)
                            self.or_counter += 1
                            join = BPMNNode(join_name, is_gateway=True, gateway_type='OR')
                        self.gateways.append(join)
                        self.flows.append(BPMNEdge(join, entry))
                        for predecessor in predecessors:
                            flow = BPMNEdge(predecessor, join)
                            self.flows.append(flow)
                    else:
                        for predecessor in predecessors:
                            if predecessor not in tovisit and predecessor not in visited:
                                tovisit.append(predecessor)

                        self.flows = [x for x in self.flows if x not in self.incoming[entry]]

                        crawlers = []

                        for predecessor in predecessors:
                            crawler = DiagramCrawler()
                            crawler.add_future(predecessor)
                            for compare_predecessor in predecessors:
                                if predecessor == compare_predecessor:
                                    continue
                                elif self.are_concurrent(predecessor, compare_predecessor):
                                    crawler.add_past(compare_predecessor)
                            crawler.stringify()
                            crawlers.append(crawler)
                        final_crawler = CrawlerMerger.merge_join_crawlers(crawlers)

                        self.generate_joins_hierarchy(entry, final_crawler)
                else:
                    src = None
                    try:
                        src = self.incoming[entry].pop(0).src
                    except IndexError as e:
                        print("no incomings for", entry)
                    if src not in visited and src not in tovisit and src is not None:
                        tovisit.append(src)
            else:
                predecessors = self.get_direct_predecessors(entry)
                for predecessor in predecessors:
                    if predecessor not in visited and predecessor not in tovisit:
                        tovisit.append(predecessor)

    def generate_splits_hierarchy(self, entry, next_item):

        gateway_type = next_item.get_gateway_type()

        if next_item in self.candidate_joins:
            candidate_join = self.candidate_joins[next_item]
            flow = BPMNEdge(entry, candidate_join)
            self.flows.append(flow)
            return

        if gateway_type is None:
            node = next_item.get_node()
            if node is not None:
                self.flows.append(BPMNEdge(entry, node))
            else:
                print("ERROR - crawler witohuh brother and more tha tone elemtn int past")
            return

        if gateway_type == 'XOR':
            gate_name = gateway_type + str(self.xor_counter)
            self.xor_counter += 1
        elif gateway_type == 'AND':
            gate_name = gateway_type + str(self.and_counter)
            self.and_counter += 1

        gateway = BPMNNode(gate_name, is_gateway=True, gateway_type=gateway_type)
        self.gateways.append(gateway)
        flow = BPMNEdge(entry, gateway)
        self.flows.append(flow)

        for item in next_item.xor_siblings:
            self.generate_splits_hierarchy(gateway, item)
        for item in next_item.and_siblings:
            self.generate_splits_hierarchy(gateway, item)

        self.candidate_joins[next_item] = gateway

    def generate_joins_hierarchy(self, entry, next_item):
        gateway_type = next_item.get_gateway_type()
        if gateway_type is None:
            node = next_item.get_join_node()
            if node is not None:
                self.flows.append(BPMNEdge(node, entry))
            else:
                print("ERROR - crawler witohuh brother and more tha tone elemtn int past")
            return

        if gateway_type == 'XOR':
            gate_name = gateway_type + str(self.xor_counter)
            self.xor_counter += 1
        elif gateway_type == 'AND':
            gate_name = gateway_type + str(self.and_counter)
            self.and_counter += 1

        gateway = BPMNNode(gate_name, is_gateway=True, gateway_type=gateway_type)
        self.gateways.append(gateway)
        flow = BPMNEdge(gateway, entry)
        self.flows.append(flow)

        for item in next_item.xor_siblings:
            self.generate_joins_hierarchy(gateway, item)
        for item in next_item.and_siblings:
            self.generate_joins_hierarchy(gateway, item)

    def remove_join_splits(self):
        self.discover_incoming_flows()
        self.discover_outgoing_flows()
        new_gates = []
        for gate in self.gateways:
            # Introduce a new gateway and connect them
            if gate in new_gates:
                continue
            if len(self.incoming[gate]) > 1 and len(self.outgoing[gate]) > 1:
                print("JOINSPLIT: ", gate)
                print(self.incoming[gate])
                print(self.outgoing[gate])
                self.flows = [x for x in self.flows if x not in self.outgoing[gate]]
                if gate.gateway_type == 'XOR':
                    task_name = 'XOR' + str(self.xor_counter)
                if gate.gateway_type == 'AND':
                    task_name = 'AND' + str(self.and_counter)
                if gate.gateway_type == 'OR':
                    task_name = 'OR' + str(self.or_counter)
                new_gate = BPMNNode(task_name=task_name, is_gateway=True, gateway_type=gate.gateway_type)
                self.gateways.append(new_gate)
                new_gates.append(new_gate)
                connection = BPMNEdge(gate, new_gate)
                self.flows.append(connection)
                for flow in self.outgoing[gate]:
                    flow.src = new_gate
                    self.flows.append(flow)

    def prepare_diagram_for_export(self):
        if self.bpmn_model is not None:
            self.bpmn_model = None
        bpmn_model = BpmnDiagramGraph()
        bpmn_model.create_new_diagram_graph("Diagram1")
        process_id = bpmn_model.add_process_to_diagram("Process1")

        task_mapping = {}

        for task in self.tasks:
            if task.is_start:
                new_task_id, new_task = bpmn_model.add_start_event_to_diagram(process_id=process_id,
                                                                              start_event_name=task.task_name)
            elif task.is_end:
                new_task_id, new_task = bpmn_model.add_end_event_to_diagram(process_id=process_id,
                                                                            end_event_name=task.task_name)
            else:
                new_task_id, new_task = bpmn_model.add_task_to_diagram(process_id=process_id, task_name=task.task_name)
            task_mapping[task] = new_task_id

        for gate in self.gateways:
            if gate.gateway_type == 'XOR':
                gate_id, gateway = bpmn_model.add_exclusive_gateway_to_diagram(process_id=process_id,
                                                                               gateway_name=gate.task_name)
            elif gate.gateway_type == 'AND':
                gate_id, gateway = bpmn_model.add_parallel_gateway_to_diagram(process_id=process_id,
                                                                              gateway_name=gate.task_name)
            elif gate.gateway_type == 'OR':
                gate_id, gateway = bpmn_model.add_inclusive_gateway_to_diagram(process_id=process_id,
                                                                               gateway_name=gate.task_name)
            task_mapping[gate] = gate_id

        flow_mapping = {}
        for flow in self.flows:
            flow_id, new_flow = bpmn_model.add_sequence_flow_to_diagram(process_id=process_id,
                                                                        source_ref_id=task_mapping[flow.src],
                                                                        target_ref_id=task_mapping[flow.tgt])
            flow_mapping[flow] = flow_id
        generate_layout(bpmn_model)

        self.bpmn_model = bpmn_model

    def export_as_png(self, filename):
        self.prepare_diagram_for_export()
        bpmn_diagram_to_png(bpmn_diagram=self.bpmn_model, file_name=filename)

    def export_as_xml(self, directory, filename):
        self.prepare_diagram_for_export()
        self.bpmn_model.export_xml_file(directory, filename)

    def visualize(self):
        self.prepare_diagram_for_export()
        visualize_diagram(self.bpmn_model)
