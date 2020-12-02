import random
from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.layouts import column, layout, row
from bokeh.models import CustomJS, Slider, Spinner, Button, ColumnDataSource


def count(state):
    """Takes a state Returns the reactant count, product count and ratio of product over reactants."""
    rs = 0
    ps = 0
    for item in state:
        if item == 'R':
            rs += 1
        elif item == 'P':
            ps += 1
    try:
        ratio = ps/rs
    except ZeroDivisionError:
        ratio = None
    return rs, ps, ratio


class Equilibrium:
    """Equilibrium class sets up a Bokeh plot of an Equilibrium system"""

    def __init__(self):
        # Setup sliders and spinners
        self.fwd = Slider(start=0, end=1, value=0.5, step=.01, title="Initial Forward Rate")
        self.bwd = Slider(start=0, end=1, value=0.25, step=.01, title="Initial Reverse Rate")
        self.startR = Spinner(title="Starting Reactants", low=0, high=10000, step=1000, value=10000, width=150)
        self.startP = Spinner(title="Starting Products", low=0, high=10000, step=1000, value=0, width=150)
        self.state = []
        self.addR = Spinner(title="Add or remove Reactants", low=-5000, high=5000, step=1000, value=0, width=150)
        self.addP = Spinner(title="Add or remove Products", low=-5000, high=50000, step=1000, value=0, width=150)
        # Setup bokeh plots
        p1 = figure(plot_width=400, plot_height=400)
        p2 = figure(plot_width=400, plot_height=400)
        y1 = []
        y2 = []
        ratio = []
        x = []
        # Setup Data source
        self.source = ColumnDataSource(data=dict(x=x, y1=y1, y2=y2, ratio=ratio))
        # Plot the data and setup plot
        p1.line('x', 'y1', source=self.source, color="blue", line_width=3, legend_label="[R]")
        p1.line('x', 'y2', source=self.source, color='red', line_width=3, legend_label="[P]")
        p2.line('x', 'ratio', source=self.source, color='green', legend_label="[P]/[R]", line_width=3)
        p2.legend.location = "bottom_right"
        p1.legend.location = "bottom_right"
        state_button = Button(label="Advance State", button_type="primary")
        state_button.on_click(self.make_new_state)

        main_col = column(row(self.fwd,), row(self.bwd,), row(p1, p2), row(self.addR, self.addP), row(state_button, ))
        curdoc().add_root(layout([
                                [self.startR,  self.startP],
                                [main_col]
                               ]))

    def shift_equil(self, shift):
        shift = self.state[-1] + shift
        self.state.append(shift)

    def make_new_state(self, rounds=1):
        """ Advances the state and determines the reactants and products based on the rate"""
        if not self.state:
            self.state = [int(self.startR.value) * 'R' + int(self.startP.value) * 'P']
        rs, ps, _ = count(self.state[-1])
        rs += self.addR.value
        ps += self.addP.value
        # converts the rs and ps to a string
        self.state[-1] = rs*'R' + ps*'P'
        # reset buttons to 0
        self.addR.value = 0
        self.addP.value = 0
        # advance the requisite number of round
        for round in range(rounds):
            new_state = ''
            # Determine state based on the initial rates
            for item in self.state[-1]:
                if item == 'R':
                    new_state += random.choices('PR', [self.fwd.value, 1 - self.fwd.value])[0]
                else:
                    new_state += random.choices('RP', [self.bwd.value, 1 - self.bwd.value])[0]
            self.state.append(new_state)
        # Setup variables for graphing
        x = list(range(len(self.state)))
        y1 = []
        y2 = []
        ratios = []
        for state in self.state:
            rs, ps, ratio = count(state)
            y1.append(rs)
            y2.append(ps)
            ratios.append(ratio)
        # update datashource
        self.source.data = dict(x=x, y1=y1, y2=y2, ratio=ratios)


Equilibrium()


