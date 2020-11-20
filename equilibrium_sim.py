import random
from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.layouts import column, layout, row
from bokeh.models import CustomJS, Slider, Spinner, Button, ColumnDataSource

def make_new_state(old_state, fwd, bwd):
    new_state = ''
    for item in old_state:
        if item == 'R':
            if random.choice(fwd):
                new_state += 'P'
            else:
                new_state += 'R'
        else:
            if random.choice(bwd):
                new_state += 'R'
            else:
                new_state += 'P'
    return new_state

def make_new_state_gas(old_state, fwd, bwd):
    new_state = ''
    for item in old_state:
        if item == 'R':
            if random.choice(fwd):
                new_state += 'P'
            else:
                new_state += 'R'
        elif item == 'P':
            if random.choice(bwd):
                new_state += 'R'
            else:
                new_state += 'G'
        else:
            new_state += 'G'
    return new_state

def count(state):
    rs = 0
    ps = 0
    gs = 0
    for item in state:
        if item == 'R':
            rs += 1
        elif item == 'P':
            ps += 1
        else:
            gs += 1
    try:
        ratio = ps/rs
    except ZeroDivisionError:
        ratio = None
    return rs, ps, gs, ratio

def plot_equilibrium(state, fwd, bwd, rounds, gas=False):
    data = []
    for i in range(rounds):
        data.append(count(state))
        if gas:
            state = make_new_state_gas(state, fwd, bwd)
        else:
            state = make_new_state(state, fwd, bwd)
    x = range(rounds)
    y1 = []
    y2= []
    y3 = []
    for row in data:
        y1.append(row[0])
        y2.append(row[1])
        y3.append(row[2])
    plt.plot(x, y1)
    plt.plot(x, y2)
    if gas:
        plt.plot(x, y3)
    return plt

def plot_equilibrium_sub(state, fwd, bwd, rounds):
    data = []
    for i in range(rounds):
        data.append(count(state))
        state = make_new_state(state, fwd, bwd)
    fig, axs = plt.subplots(2)
    x = range(rounds)
    y1 = []
    y2 = []
    ratio = []
    for row in data:
        y1.append(row[0])
        y2.append(row[1])
        ratio.append(row[3])
    axs[0].plot(x, y1)
    axs[0].plot(x, y2)
    axs[1].plot(x, ratio)
    return plt


class Equilibrium:

    def shift_equil(self, shift):
        shift = self.state[-1] + shift
        self.state.append(shift)

    def make_new_state(self, rounds=1):

        if not self.state:
            self.state = [int(self.startR.value) * 'R' + int(self.startP.value) * 'P']
        rs, ps ,*_ = count(self.state[-1])
        rs += self.addR.value
        ps += self.addP.value
        self.state[-1] = rs*'R' + ps*'P'


        self.addR.value = 0
        self.addP.value = 0
        for round in range(rounds):
            new_state = ''
            for item in self.state[-1]:
                if item == 'R':
                    new_state += random.choices('PR', [self.fwd.value, 1 - self.fwd.value])[0]
                else:
                    new_state += random.choices('RP', [self.bwd.value, 1 - self.bwd.value])[0]
            self.state.append(new_state)
        x = list(range(len(self.state)))
        y1 = []
        y2 = []
        ratio = []
        for state in self.state:
            y1.append(count(state)[0])
            y2.append(count(state)[1])
            ratio.append(count(state)[3])

        print(x)
        print(y1)
        print(y2)
        self.source.data = dict(x=x, y1=y1, y2=y2, ratio=ratio)

            #self.plot_equilibrium()

    def __init__(self):
        self.fwd = Slider(start=0, end=1, value=0.5, step=.01, title="Initial Forward Rate")
        self.bwd = Slider(start=0, end=1, value=0.25, step=.01, title="Initial Reverse Rate")
        self.startR = Spinner(title="Starting Reactants", low=0, high=100000, step=1000, value=10000, width=150)
        self.startP = Spinner(title="Starting Products", low=0, high=1000000, step=1000, value=0, width=150)
        self.state = []
        self.addR = Spinner(title="Add or remove Reactants", low=-100000, high=100000, step=1000, value=0, width=150)
        self.addP = Spinner(title="Add or remove Products", low=-100000, high=1000000, step=1000, value=0, width=150)

        p1 = figure(plot_width=400, plot_height=400)
        p2 = figure(plot_width=400, plot_height=200)
        y1 = []
        y2 = []
        ratio = []

        x = []

        self.source = ColumnDataSource(data=dict(x=x, y1=y1, y2=y2, ratio=ratio))

        p1.line('x', 'y1', source=self.source, color="firebrick", line_width=3, legend_label="[R]")
        p1.line('x', 'y2', source=self.source, color='navy', line_width=3, legend_label="[P]")
        p2.line('x', 'ratio', source=self.source, color='green', legend_label="[P]/[R]", line_width=3)
        p2.legend.location = "bottom_right"

        button = Button(label="Advance State", button_type="success")
        button.on_click(self.make_new_state)
        row1 = row(self.startR, self.startP)
        row2 = row(self.addR, self.addP)

        curdoc().add_root(layout([row1], [row2], self.fwd, self.bwd, p1, p2, button))



Equilibrium()


