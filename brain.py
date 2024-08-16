from math import tanh


class Brain:
    """
    Brain of the cell.
    """
    
    def __init__(self):
        self.input_neurons = ['rand', 'age', 'Px', 'Py', 'BD', 'BDr', 'BDl', 'BDu', 'BDd']
        self.action_neurons = ['Mrand', 'Mr', 'Ml', 'Mu', 'Md']
        self.internal_neurons = 4
        
        self.inputs = len(self.input_neurons)
        self.outputs = len(self.action_neurons)
        
        self.internal_inputs = []
        self.action_inputs = []

        self.internal_outputs = [0 for _ in range(self.internal_neurons)]
        self.action_outputs = [0 for _ in range(self.outputs)]

    def wire_up(self, genome):
        """
        Wire up the brain according to the specified genome.
        """
        sources = [self.inputs, self.internal_neurons]
        sinks = [self.outputs, self.internal_neurons]

        self.internal_inputs = [[] for _ in range(self.internal_neurons)]
        self.action_inputs = [[] for _ in range(self.outputs)]

        for gene in genome:
            source = format(eval('0x'+gene[:2]), '08b')
            sink = format(eval('0x'+gene[2:4]), '08b')
            weight = int(eval('0x'+gene[4:]))
            if weight >= 32768:  # Signed bit, convert to negative
                weight = 32768 - (weight % 32768)
                weight *= -1
            weight /= 8192

            src_type = int(source[0])
            sink_type = int(sink[0])

            src = int(eval('0b'+source[1:])) % sources[src_type]
            snk = int(eval('0b'+sink[1:])) % sinks[sink_type]
            
            if not sink_type:  # If the sink is an action neuron
                self.action_inputs[snk].append((src_type, src, weight))
            else:  # If the sink is an internal neuron
                self.internal_inputs[snk].append((src_type, src, weight))

    def process(self, sensory_inputs):
        """
        Process the given sensory inputs through the brain wiring.
        """
        internal_outputs = [0 for _ in range(self.internal_neurons)]
        action_outputs = [0 for _ in range(self.outputs)]

        for internal in range(self.internal_neurons):
            inputs = []
            for src_type, src, w in self.internal_inputs[internal]:
                if src_type == 0:  # Input Neuron -> Internal Neuron
                    inputs.append(sensory_inputs[src] * w)
                else:  # Internal Neuron -> Internal Neuron
                    inputs.append(self.internal_outputs[src] * w)
            internal_outputs[internal] = tanh(sum(inputs))

        for action in range(self.outputs):
            inputs = []
            for src_type, src, w in self.action_inputs[action]:
                if src_type == 0:  # Input Neuron -> Action Neuron
                    inputs.append(sensory_inputs[src] * w)
                else:  # Internal Neuron -> Action Neuron
                    inputs.append(internal_outputs[src] * w)
            action_outputs[action] = max(0.0001, tanh(sum(inputs)))  # Using ReLU to avoid negative

        self.internal_outputs = internal_outputs
        self.action_outputs = action_outputs
