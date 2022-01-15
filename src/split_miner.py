from pm4py.objects.log.importer.xes import importer as xes_importer


class SplitMiner:
    def __init__(self, event_log, concurrency_threshold=0.6, filtering_percentile=50):
        self.log = self.parse_log(event_log)
        self.concurrency_threshold = concurrency_threshold
        self.filtering_percentile = filtering_percentile
        self.dfg = None
        self.self_loops = None
        self.short_loops = None
        self.short_loop_frequency = None
        self.event_labels = None
        self.incoming_edges = None
        self.outgoing_edges = None

    def __repr__(self):
        return f''

    @staticmethod
    def parse_log(path_to_log):
        parsed_log = xes_importer.apply(path_to_log)
        return parsed_log

    def run(self):
        self.dfg_and_loops_discovery()
        self.remove_loops()
        self.discover_concurrency(self.concurrency_threshold)
        self.filter_pdfg(self.filtering_percentile)

    def dfg_and_loops_discovery(self):
        self.discover_dfg()
        self.self_loop_discovery()
        self.extract_event_labels()
        self.discover_short_loops()

    def discover_incoming_and_outgoing_edges(self):
        self.discover_incoming_edges()
        self.discover_outgoing_edges()

    def discover_dfg(self):
        # Directly-Follows Graph construction
        the_dfg = {}
        for trace in self.log:
            for idx in range(len(trace) - 1):
                the_tuple = (trace[idx]['concept:name'], trace[idx + 1]['concept:name'])
                if the_tuple in the_dfg:
                    the_dfg[the_tuple] += 1
                else:
                    the_dfg[the_tuple] = 1
        self.dfg = the_dfg

    def self_loop_discovery(self):
        self_loops = []
        for edge in self.dfg:
            node_from = edge[0]
            node_to = edge[1]
            if node_from == node_to:
                if node_from not in self_loops:
                    self_loops.append(node_from)
        self.self_loops = self_loops

    def extract_event_labels(self):
        events = []
        for edge in self.dfg:
            if edge[0] not in events:
                events.append(edge[0])
            if edge[1] not in events:
                events.append(edge[1])
        self.event_labels = events

    def discover_short_loops(self):
        short_loop_frequency = {}
        short_loops = []
        for trace in self.log:
            for idx, event in enumerate(trace):
                if idx + 2 == len(trace):
                    break
                else:
                    a = trace[idx]['concept:name']
                    b = trace[idx + 1]['concept:name']
                    c = trace[idx + 2]['concept:name']
                    if a == c and a != b:
                        if a not in self.self_loops and b not in self.self_loops:
                            if (a, b) in short_loop_frequency:
                                short_loop_frequency[(a, b)] += 1
                            else:
                                short_loop_frequency[(a, b)] = 1
                            if (a, b) not in short_loops:
                                short_loops.append((a, b))
        self.short_loops = short_loops
        self.short_loop_frequency = short_loop_frequency

    def discover_incoming_edges(self):
        incoming = {}
        for current_event in self.event_labels:
            incoming[current_event] = {}
            for edge in self.dfg:
                if edge[1] == current_event and edge not in incoming[current_event]:
                    if edge not in incoming[current_event]:
                        incoming[current_event][edge] = self.dfg[edge]
            incoming[current_event] = {k: v for k, v in
                                       sorted(incoming[current_event].items(), key=lambda item: item[1], reverse=True)}
        self.incoming_edges = incoming

    def discover_outgoing_edges(self):
        outgoing = {}
        for current_event in self.event_labels:
            outgoing[current_event] = {}
            for edge in self.dfg:
                if edge[0] == current_event and edge not in outgoing[current_event]:
                    if edge not in outgoing[current_event]:
                        outgoing[current_event][edge] = self.dfg[edge]
            outgoing[current_event] = {k: v for k, v in sorted(outgoing[current_event].items(), key=lambda item: item[1], reverse=True)}
        self.outgoing_edges = outgoing

    def get_most_frequent_edges_set(self):
        most_frequent_edges = []
        for task in self.event_labels:
            print(f"OUTGOING FOR {task}: {self.outgoing_edges[task]}")
            print(f"INCOMING FOR {task}: {self.incoming_edges[task]}")
            most_freq_out = None
            most_freq_in = None
            if len(self.outgoing_edges[task]) > 0:
                high_out_value = list(self.outgoing_edges[task].values())[0]
                for edge in self.outgoing_edges[task]:
                    if self.outgoing_edges[task][edge] == high_out_value:
                        most_freq_out = edge
            if len(self.incoming_edges[task]) > 0:
                high_in_value = list(self.incoming_edges[task].values())[0]
                for edge in self.incoming_edges[task]:
                    if self.incoming_edges[task][edge] == high_in_value:
                        most_freq_in = edge
            if most_freq_in and most_freq_out:
                most_frequent_edges.append(most_freq_out)
                most_frequent_edges.append(most_freq_in)
            elif most_freq_in:
                most_frequent_edges.append(most_freq_in)
            elif most_freq_out:
                most_frequent_edges.append(most_freq_out)
        return most_frequent_edges

    def remove_loops(self):
        to_remove = []
        for edge in self.dfg:
            if edge in self.short_loops and edge not in to_remove:
                to_remove.append(edge)
            elif edge[0] == edge[1] and edge[0] in self.self_loops and edge not in to_remove:
                to_remove.append(edge)
        for edge in to_remove:
            del self.dfg[edge]

    def discover_concurrency(self, concurrency_threshold):
        # First, see if events can occur two ways i.e. a -> b, b -> a
        to_remove = []
        for edge in self.dfg:
            for inner_edge in self.dfg:
                if edge[0] == inner_edge[1] and edge[1] == inner_edge[0]:
                    # When this occurs, 1st condition is fulfilled
                    # Now check if those tasks do not form a short loop - all short loops have been removed
                    # So condition 2 is fulfilled
                    concurrency_index = abs(self.dfg[edge] - self.dfg[inner_edge]) / (self.dfg[edge] + self.dfg[inner_edge])
                    if concurrency_index < concurrency_threshold:
                        # If true, we remove both edges from the DFG
                        if edge not in to_remove:
                            to_remove.append(edge)
                        if inner_edge not in to_remove:
                            to_remove.append(inner_edge)
                    else:
                        # Else, we remove least frequent edge of the two
                        if self.dfg[edge] > self.dfg[inner_edge] and inner_edge not in to_remove:
                            to_remove.append(inner_edge)
                        elif self.dfg[edge] < self.dfg[inner_edge] and edge not in to_remove:
                            to_remove.append(edge)
        print(f"Removing {len(to_remove)} edges given threshold: {self.concurrency_threshold}")
        for edge in to_remove:
            del self.dfg[edge]

    def filter_pdfg(self, filtering_percentile):
        self.discover_incoming_and_outgoing_edges()
        most_frequent_edges = self.get_most_frequent_edges_set()
        percentile_locator = (len(most_frequent_edges) + 1)*(filtering_percentile/100)

    def discover_splits(self):
        pass

    def discover_joins(self):
        pass
