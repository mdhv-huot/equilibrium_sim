from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.layouts import column, layout, row
from bokeh.models import CustomJS, Slider, Spinner, Button, ColumnDataSource
import numpy as np

class Equil_vals():
    def __init__(self, rs, ps, fwd, bwd):
        self.rs = rs
        self.ps = ps
        self.fwd = fwd
        self.bwd = bwd
        try:
            self.ratio = self.ps / self.rs
        except ZeroDivisionError:
            self.ratio = np.nan

    def advance_state(self):
        newps = round(self.rs * self.fwd)
        oldrs = self.rs - newps
        newrs = round(self.ps * self.bwd)
        oldps = self.ps - newrs
        rs = newrs + oldrs
        ps = newps + oldps
        return(Equil_vals(rs, ps, self.fwd, self.bwd))

class Equilibrium:
    """Equilibrium class sets up a Bokeh plot of an Equilibrium system"""

    def __init__(self):
        # Setup sliders and spinners
        self.fwd = Slider(start=0, end=1, value=0.5, step=.01, title="Initial Forward Rate")
        self.bwd = Slider(start=0, end=1, value=0.25, step=.01, title="Initial Reverse Rate")
        self.startR = Spinner(title="Starting Reactants", low=0, high=1000000, step=1000, value=10000, width=150)
        self.startP = Spinner(title="Starting Products", low=0, high=1000000, step=1000, value=0, width=150)
        self.state = []
        self.addR = Spinner(title="Add or remove Reactants", low=-500000, high=5000000, step=1000, value=0, width=150)
        self.addP = Spinner(title="Add or remove Products", low=-500000, high=5000000, step=1000, value=0, width=150)
        # Setup bokeh plots
        p1 = figure(plot_width=400, plot_height=400)
        p2 = figure(plot_width=350, plot_height=400)
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

    def make_new_state(self, rounds=1):
        """ Advances the state and determines the reactants and products based on the rate"""
        if not self.state:
            self.state = [Equil_vals(int(self.startR.value), int(self.startP.value), self.fwd.value, self.bwd.value)]
        self.state[-1].rs += self.addR.value
        self.state[-1].ps += self.addP.value
        # reset buttons to 0
        self.addR.value = 0
        self.addP.value = 0
        # advance the requisite number of round
        for round in range(rounds):
            # Determine state based on the initial rates
            self.state.append(self.state[-1].advance_state())
        # Setup variables for graphing
        x = list(range(len(self.state)))
        y1 = []
        y2 = []
        ratios = []
        for state in self.state:
            y1.append(state.rs)
            y2.append(state.ps)
            ratios.append(state.ratio)
        # update datashource
        self.source.data = dict(x=x, y1=y1, y2=y2, ratio=ratios)


Equilibrium()


