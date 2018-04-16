#!/usr/bin/env python3


class Terminal:
    def __init__(self, owner, t_type):
        self.owner_ = owner
        self.t_type_ = t_type
        self.node_ = None

    def __str__(self):
        return str(self.node_)

    def __repr__(self):
        ret = f'<{self.__class__.__name__}>'+str(self.node_)+"\n"
        return ret

    def set_node(self, node):
        if self.node_:
            self.node_.remove_terminal(self)
        node.add_terminal(self)
        self.node_ = node

    def get_node(self):
        return self.node_

    def get_name(self):
        return self.node_.get_name()


class Transistor:
    terminal_type = dict(gate=0, drain=1, source=2)

    def __init__(self, name, t_type):
        self.name_ = name
        self.t_type_ = t_type
        if t_type == 'PMOS':
            self.buck_ = 'VDD PMOS'
        else:
            self.buck_ = 'GND NMOS'
        self.terminals = list()
        self.terminals.append(Terminal(self, 'gate'))
        self.terminals.append(Terminal(self, 'drain'))
        self.terminals.append(Terminal(self, 'source'))

    def get_terminal(self, t_type):
        return self.terminals[t_type]

    def set_name(self, name):
        self.name_ = name

    def get_name(self):
        return self.name_

    def get_type(self):
        return self.t_type_

    def get_description(self, reverse_diffusions=False):
        ret = ''
        if reverse_diffusions:
            terminal_idx = (2, 0, 1)
        else:
            terminal_idx = (1, 0, 2)
        for i in terminal_idx:
            ret += str(self.terminals[i]) + ' '

        ret = f"{self.name_} {ret}{self.buck_}\n"
        return ret

    def __str__(self):
        return self.get_description()

    def __repr__(self):
        ret = f'<{self.__class__.__name__}>'+self.name_+"\n"
        for tx in self.terminals:
            ret += "\t" + repr(tx)
        return ret+"\n"
