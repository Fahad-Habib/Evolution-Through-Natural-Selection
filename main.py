from kivy.config import Config

WIDTH, HEIGHT = 830, 480  # 1680, 960

Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', WIDTH)
Config.set('graphics', 'height', HEIGHT)

from kivy.app import App
from kivy.clock import mainthread
from kivy.core.window import Window

from kivy.graphics import Color, Rectangle, Line, Ellipse, Triangle

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen

from random import random, choices, randint, shuffle
from math import ceil
from time import sleep
from threading import Thread


GRID_WIDTH, GRID_HEIGHT = 800, 800
GRID_POS = 60

POPULATION = 1000
GENOME_LENGTH = 8

CELL = 5
SPEED = 1
STEPS_GEN = 200
SIZE = GRID_WIDTH // CELL
SIZE_ = SIZE - 2  # Reduce 1 from both ends due to grid border

GRID = [
    [
        0 for _ in range(SIZE)
    ] for _ in range(SIZE)
]


class Cell:
    """
    The anatomy of the cell.
    """

    def __init__(self, parent, genome):
        # self.brain = Brain()
        
        self.action_outputs = {
            'Mr': (1, 0), 
            'Ml': (-1, 0), 
            'Mu': (0, 1), 
            'Md': (0, -1)
        }

        with parent.canvas.before:
            self.color = Color((0,0,0,0))
            self.label = Ellipse(size=(CELL, CELL))

        self.reset(genome)
        self.update()

    def move_step(self):
        """Move one step on the grid according to the brain's output signal."""
        BDs = [
            1 - (self.x / SIZE_), 
            self.x / SIZE_, 
            self.y / SIZE_, 
            1 - (self.y / SIZE_)
        ]
        sensory_inputs = [
            random(), 
            self.age / STEPS_GEN, 
            self.x / SIZE_, 
            self.y / SIZE_, 
            min(BDs), 
            *BDs
        ]

        # self.brain.process(sensory_inputs)
        
        # out = choices(
        #     ['Mrand', 'Mr', 'Ml', 'Mu', 'Md'],
        #     weights = self.brain.action_outputs, 
        #     k = 1
        # )[0]
        
        # if out == 'Mrand':
        #     out = (randint(-1, 1), randint(-1, 1))
        # else:
        #     out = self.action_outputs[out]

        out = (randint(-1, 1), randint(-1, 1))

        x = self.x + SPEED * out[0]
        y = self.y + SPEED * out[1]

        GRID[self.x][self.y] = 0

        if 1 <= x <= SIZE_ and 1 <= y <= SIZE_:
            if not GRID[x][y]:
                self.x = x
                self.y = y
            elif not GRID[self.x][y]:
                self.y = y
            elif not GRID[x][self.y]:
                self.x = x
        elif 1 <= x <= SIZE_:
            if not GRID[x][self.y]:
                self.x = x
        elif 1 <= y <= SIZE_:
            if not GRID[self.x][y]:
                self.y = y

        GRID[self.x][self.y] = 1
        self.age += 1

    @mainthread
    def update(self):
        """
        Update label position.
        """
        self.label.pos = (GRID_POS + self.x * CELL, GRID_POS + self.y * CELL)

    @mainthread
    def assign_random_color(self):
        """
        Assign a random color on reset.
        """
        self.color.rgba = (randint(0, 255)/255, randint(0, 255)/255, randint(0, 255)/255, 1)

    def reset(self, genome):
        """
        Reset the brain wiring of the cell according to the given genome.
        """
        self.age = 0
        self.genome = genome
        # self.brain.wire_up(genome)

        self.assign_random_color()

        self.x = randint(1, SIZE_)
        self.y = randint(1, SIZE_)

        while GRID[self.x][self.y]:
            self.x = randint(1, SIZE_)
            self.y = randint(1, SIZE_)

        GRID[self.x][self.y] = 1


class CustomLabel(Label):
    """
    Customize the kivy label class to initialize some standard values.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.size_hint = (None, None)
        self.font_size = 45
        self.color = 'black'
        self.bold = True


class CustomButton(Button):
    """
    Customize the kivy button class to initialize some standard values.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.size_hint = (None, None)
        self.font_size = 20


class MainWindow(Screen):
    """
    Main window of the simulator.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.grid = Rectangle(size=(GRID_WIDTH, GRID_HEIGHT), pos=(GRID_POS, GRID_POS))

        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.grid_border = Line(width=2.5, rectangle=(GRID_POS, GRID_POS, GRID_WIDTH, GRID_HEIGHT))

        self.gen = 0
        self.genomes = [
            [
                format(randint(0, (16**8)-1), '08x') for _ in range(GENOME_LENGTH)
            ] for _ in range(POPULATION)
        ]
        self.cells = [Cell(self, genome) for genome in self.genomes]
        self.survivors = []
        self.children_ = self.genomes[:]

        self.label = CustomLabel(text='Gen 0', size=(800, 70), pos=(GRID_POS, 860))
        self.size_label = CustomLabel(text='World Size: 160x160', size=(820, 70), pos=(860, 790))
        self.pop_label = CustomLabel(text=f'Population: {POPULATION}', size=(820, 70), pos=(860, 720))
        self.step_label = CustomLabel(text=f'Steps / Gen: {STEPS_GEN}', size=(820, 70), pos=(860, 650))
        self.genome_label = CustomLabel(text=f'Genome Length: {GENOME_LENGTH} genes', size=(820, 70), pos=(860, 580))
        self.survive_label = CustomLabel(text='', size=(820, 70), pos=(860, 440))

        self.simulate = CustomButton(text='Simulate Current', size=(180, 50), pos=(1100, 320))
        self.next_gen = CustomButton(text='Next Generation', size=(180, 50), pos=(1300, 320))
        self.skip_next_gen = CustomButton(text='Skip to Next Generation', size=(380, 50), pos=(1100, 250))
        self.skip_next_gen_10 = CustomButton(text='Skip to Next 10 Generations', size=(380, 50), pos=(1100, 180))

        self.simulate.bind(on_release=self.simulate_current)
        self.next_gen.bind(on_release=self.get_next_gen)
        self.skip_next_gen.bind(on_release=self.skip_to_next_gen)
        # self.skip_next_gen_10.bind(on_release=self.skip_to_next_n_gen)

        self.add_widget(self.label)
        self.add_widget(self.size_label)
        self.add_widget(self.pop_label)
        self.add_widget(self.step_label)
        self.add_widget(self.genome_label)
        self.add_widget(self.survive_label)

        self.add_widget(self.simulate)
        self.add_widget(self.next_gen)
        self.add_widget(self.skip_next_gen)
        self.add_widget(self.skip_next_gen_10)

        self.next_gen.disabled = True

    def simulate_current(self, *args):
        """
        Disable the buttons and start the simulation thread.
        """
        self.next_gen.disabled = True
        self.simulate.disabled = True
        self.skip_next_gen.disabled = True
        self.skip_next_gen_10.disabled = True
        Thread(target=self.__simulate_current).start()

    def __simulate_current(self):
        """
        Thread to simulate one generation.
        """
        for _ in range(STEPS_GEN):
            for cell in self.cells:
                cell.move_step()
            for cell in self.cells:
                cell.update()
            sleep(0.00001)

        # self.update()

    def update(self):
        """
        Update the survival rate.
        """
        # survivors = []
        # for cell in self.cells:
        #     if self.selection_criteria(cell):
        #         survivors.append(cell.genome)
        
        # rate = int((len(survivors) / POPULATION) * 100)
        # self.survive_label.text = f'Survival Rate: {rate}%'
        # self.boundary_color.rgba = (0, 1, 0, 1)
        # self.boundary_fill.rgba = (0, 1, 0, 0.2)
        self.next_gen.disabled = False

    def get_next_gen(self, *args):
        """Get the next generation and update the labels."""
        self.gen += 1
        self.label.text = f'Gen {self.gen}'
        self.survive_label.text = ''
        # self.boundary_color.rgba = (0, 0, 0, 0)
        # self.boundary_fill.rgba = (0, 0, 0, 0)

        for i in range(SIZE):
            for j in range(SIZE):
                GRID[i][j] = 0

        self.reproduce()

        for cell in self.cells:
            cell.update()

        # pool = [cell.out for cell in self.cells]
        # self.diverse_label.text = 'Genetic Diversity: {:.2f}'.format(self.calculate_diversity(pool))

        self.simulate.disabled = False
        self.skip_next_gen.disabled = False
        self.skip_next_gen_10.disabled = False

    def skip_to_next_gen(self, *args):
        """
        Skip to the next generation without the simulation.
        """
        for _ in range(STEPS_GEN):
            for cell in self.cells:
                cell.move_step()

        self.get_next_gen()

    def reproduce(self):
        """
        Take the survivors and reproduce the children for the next generation.
        """
        return
        self.survivors = []
        for cell in self.cells:
            if self.selection_criteria(cell):
                self.survivors.append(cell.genome)

        rate = len(self.survivors) / POPULATION
        factor = ceil(1 / rate)

        self.survivors = self.survivors * factor
        shuffle(self.survivors)

        self.children_ = []

        for i in range(0, POPULATION, 2):
            for _ in range(2):  # Get 2 children from every 2 parents
                self.children_.append(choices(self.survivors[i]+self.survivors[i+1], k=8))

        for genome, cell in zip(self.children_, self.cells):
            cell.reset(genome)


class ScreenManagement(ScreenManager):
    """
    Screen Manager.
    """

    def __init__(self, **kwargs):
        super(ScreenManagement, self).__init__(**kwargs)

        self.add_widget(MainWindow(name="main"))


class EvolutionApp(App):
    """
    App class.
    """

    def build(self):
        Window.clearcolor = (211/255, 211/255, 211/255, 1)
        self.manager = ScreenManagement()
        return self.manager


if __name__ == '__main__':
    EvolutionApp().run()