import pygame
from pygame import gfxdraw
from scipy.spatial import distance
from copy import deepcopy
from collections import deque
import numpy as np

class Window:
    def __init__(self, sim, config={}):
        # Simulation to draw
        self.sim = sim

        # Set default configurations
        self.set_default_config()

        # Update configurations
        for attr, val in config.items():
            setattr(self, attr, val)
        
    def set_default_config(self):
        """Set default configuration"""
        self.width = 600
        self.height = 600
        self.bg_color = (250, 250, 250)

        self.fps = 60
        self.zoom = 2
        self.offset = (0, 0)

        self.mouse_last = (0, 0)
        self.mouse_down = False
        
        self.pos = 0
        self.step_size = 1/5
        self.currentIndex = 0
        self.step = 1;

        self.tfstate = [(0,0,0),(0,0,0)]


    def loop(self, loop=None):
        """Shows a window visualizing the simulation and runs the loop function."""
        
        # Create a pygame window
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.flip()

        # Fixed fps
        clock = pygame.time.Clock()

        # To draw text
        pygame.font.init()
        self.text_font = pygame.font.SysFont('Lucida Console', 16)

        # Draw loop
        running = True
        while running and self.step <2000:
            # Update simulation
            if loop: loop(self.sim)

            # Draw simulation
            self.draw()

            # Update window
            pygame.display.update()
            clock.tick(self.fps)

            # Handle all events
            for event in pygame.event.get():
                # Quit program if window is closed
                if event.type == pygame.QUIT:
                    running = False
            self.step = self.step + 1
           # print(self.step)
        pygame.quit()
        
    def run(self, steps_per_update=1):
        """Runs the simulation by updating in every loop."""
        def loop(sim):
            sim.run(steps_per_update)
        self.loop(loop)

    def convert(self, x, y=None):
        """Converts simulation coordinates to screen coordinates"""
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (
            int(self.width/2 + (x + self.offset[0])*self.zoom),
            int(self.height/2 + (y + self.offset[1])*self.zoom)
        )

    def inverse_convert(self, x, y=None):
        """Converts screen coordinates to simulation coordinates"""
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (
            int(-self.offset[0] + (x - self.width/2)/self.zoom),
            int(-self.offset[1] + (y - self.height/2)/self.zoom)
        )


    def background(self, r, g, b):
        """Fills screen with one color."""
        self.screen.fill((r, g, b))

    def line(self, start_pos, end_pos, color):
        """Draws a line."""
        gfxdraw.line(
            self.screen,
            *start_pos,
            *end_pos,
            color
        )

    def rect(self, pos, size, color):
        """Draws a rectangle."""
        gfxdraw.rectangle(self.screen, (*pos, *size), color)

    def box(self, pos, size, color):
        """Draws a rectangle."""
        gfxdraw.box(self.screen, (*pos, *size), color)

    def circle(self, pos, radius, color, filled=True):
        gfxdraw.aacircle(self.screen, *pos, radius, color)
        if filled:
            gfxdraw.filled_circle(self.screen, *pos, radius, color)



    def polygon(self, vertices, color, filled=True):
        gfxdraw.aapolygon(self.screen, vertices, color)
        if filled:
            gfxdraw.filled_polygon(self.screen, vertices, color)

    def rotated_box(self, pos, size, angle=None, cos=None, sin=None, centered=True, color=(0, 0, 255), filled=True):
        """Draws a rectangle center at *pos* with size *size* rotated anti-clockwise by *angle*."""
        x, y = pos
        l, h = size

        if angle:
            cos, sin = np.cos(angle), np.sin(angle)
        
        vertex = lambda e1, e2: (
            x + (e1*l*cos + e2*h*sin)/2,
            y + (e1*l*sin - e2*h*cos)/2
        )

        if centered:
            vertices = self.convert(
                [vertex(*e) for e in [(-1,-1), (-1, 1), (1,1), (1,-1)]]
            )
        else:
            vertices = self.convert(
                [vertex(*e) for e in [(0,-1), (0, 1), (2,1), (2,-1)]]
            )

        self.polygon(vertices, color, filled=filled)

    def rotated_rect(self, pos, size, angle=None, cos=None, sin=None, centered=True, color=(0, 0, 255)):
        self.rotated_box(pos, size, angle=angle, cos=cos, sin=sin, centered=centered, color=color, filled=False)

    def arrow(self, pos, size, angle=None, cos=None, sin=None, color=(150, 150, 190)):
        if angle:
            cos, sin = np.cos(angle), np.sin(angle)
        
        self.rotated_box(
            pos,
            size,
            cos=(cos - sin) / np.sqrt(2),
            sin=(cos + sin) / np.sqrt(2),
            color=color,
            centered=False
        )

        self.rotated_box(
            pos,
            size,
            cos=(cos + sin) / np.sqrt(2),
            sin=(sin - cos) / np.sqrt(2),
            color=color,
            centered=False
        )


    def draw_axes(self, color=(100, 100, 100)):
        x_start, y_start = self.inverse_convert(0, 0)
        x_end, y_end = self.inverse_convert(self.width, self.height)
        self.line(
            self.convert((0, y_start)),
            self.convert((0, y_end)),
            color
        )
        self.line(
            self.convert((x_start, 0)),
            self.convert((x_end, 0)),
            color
        )

    def draw_grid(self, unit=50, color=(150,150,150)):
        x_start, y_start = self.inverse_convert(0, 0)
        x_end, y_end = self.inverse_convert(self.width, self.height)

        n_x = int(x_start / unit)
        n_y = int(y_start / unit)
        m_x = int(x_end / unit)+1
        m_y = int(y_end / unit)+1

        for i in range(n_x, m_x):
            self.line(
                self.convert((unit*i, y_start)),
                self.convert((unit*i, y_end)),
                color
            )
        for i in range(n_y, m_y):
            self.line(
                self.convert((x_start, unit*i)),
                self.convert((x_end, unit*i)),
                color
            )

    def draw_roads(self):
        for road in self.sim.roads:
            # Draw road background
            self.rotated_box(
                road.start,
                (road.length, 3.7),
                cos=road.angle_cos,
                sin=road.angle_sin,
                color=(180, 180, 220),
                centered=False
            )
            # Draw road lines
            # self.rotated_box(
            #     road.start,
            #     (road.length, 0.25),
            #     cos=road.angle_cos,
            #     sin=road.angle_sin,
            #     color=(0, 0, 0),
            #     centered=False
            # )

            # Draw road arrow
            if road.length > 5: 
                for i in np.arange(-0.5*road.length, 0.5*road.length, 10):
                    pos = (
                        road.start[0] + (road.length/2 + i + 3) * road.angle_cos,
                        road.start[1] + (road.length/2 + i + 3) * road.angle_sin
                    )

                    self.arrow(
                        pos,
                        (-1.25, 0.2),
                        cos=road.angle_cos,
                        sin=road.angle_sin
                    )   
            


            # TODO: Draw road arrow
     
    def draw_traffic_lights(self):
        i = 0
        for light in self.sim.lights:
            self.circle(light.position, 4, light.state)
            self.tfstate[i] = light.state;
            i += 1

    def draw_status(self):
        text_fps = self.text_font.render(f't={self.sim.t:.5}', False, (0, 0, 0))
        text_frc = self.text_font.render(f'n={self.sim.frame_count}', False, (0, 0, 0))
        
        self.screen.blit(text_fps, (0, 0))
        self.screen.blit(text_frc, (100, 0))


    def draw(self):
        # Fill background
        self.background(*self.bg_color)

        # Major and minor grid and axes
        # self.draw_grid(10, (220,220,220))
        # self.draw_grid(100, (200,200,200))
        # self.draw_axes()

        self.draw_roads()
        self.draw_traffic_lights()

        #self.draw_vehicles()
        #self.draw_signals()

        # Draw status info
        self.draw_status()
        
        road_index = self.currentIndex 
        road2take = [0 , 1, 2, 5, 7, 12, 3, 9]
        longitud = self.sim.roads[road2take[self.currentIndex]].length
        
        if (self.pos > longitud):
            self.pos = 0
            self.currentIndex += 1
        
        sin, cos = self.sim.roads[road2take[self.currentIndex]].angle_sin,self.sim.roads[road2take[self.currentIndex]].angle_cos
        h=3
        l=3
        x = self.sim.roads[road2take[self.currentIndex]].start[0] + cos * self.pos
        y = self.sim.roads[road2take[self.currentIndex]].start[1] + sin * self.pos 
        
        
        self.rotated_box((x, y), (l, h), cos=cos, sin=sin, centered=True)
          
        self.pos = self.pos + self.step_size
        
from copy import deepcopy

class Simulation:
    def __init__(self, config={}):
        # Set default configuration
        self.set_default_config()

        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)

    def set_default_config(self):
        self.t = 0.0            # Time keeping
        self.frame_count = 0    # Frame count keeping
        self.dt = 1/300          # Simulation time step
        self.roads = []         # Array to store roads
        self.lights = []        # Array to store traffic lights


    def create_road(self, start, end):
        road = Road(start, end)
        self.roads.append(road)
        return road

    def create_roads(self, road_list):
        for road in road_list:
            self.create_road(*road)


    def update(self):
        # Update every road
        for road in self.roads:
            road.update(self.dt)

        
        # Increment time
        self.t += self.dt
        self.frame_count += 1


    def create_traffic_lights(self, light_list):
       for light in light_list:
           self.lights.append(TrafficLight(*light))

    def update(self):
        # Update every road
        for road in self.roads:
            road.update(self.dt)

        for light in self.lights:
            light.update(self.t)

        # Increment time
        self.t += self.dt
        self.frame_count += 1


    def run(self, steps):
        for _ in range(steps):
            self.update()

class Road:
    def __init__(self, start, end):
        self.start = start
        self.end = end

        self.vehicles = deque()

        self.init_properties()

    def init_properties(self):
        self.length = distance.euclidean(self.start, self.end)
        self.angle_sin = (self.end[1]-self.start[1]) / self.length
        self.angle_cos = (self.end[0]-self.start[0]) / self.length
        

    def update(self, dt):
        n = len(self.vehicles)


class TrafficLight:
    def __init__(self, position, route):
        self.cicle = cicles[route]  # Actual Cicle
        self.index = 0  # Index in array
        # The index on the colors array
        self.stateIndex = self.cicle[self.index]
        self.state = colors[self.stateIndex]  # The State's Color
        self.time = 0
        self.position = position

    def checkState(self):
        if (self.time != 0 and self.time % 9 < 0.01666666666674388):
            self.index += 1
            self.stateIndex = self.cicle[self.index]
            self.state = colors[self.stateIndex]
            if (self.index == 4):
                self.index = 0

    def getState(self):
        return self.state

    def update(self, t):
        self.time = t
        self.checkState()


cicles = [
        [0, 0, 1, 2, 2],
        [2, 2, 2, 0, 1] ]  

colors = [(0, 255, 0), (255, 255, 0), (255, 0, 0)]  
        

sim = Simulation()


# Add multiple roads
sim.create_roads([
    ((50, -50), (0 , -50)), #0
    ((0, -50), (0, 0)),#1
    ((0, 0), (50,0)), #2
    ((50,-50),(50,0)), #3
    ((0,0),(0,50)),#4
    ((50, 0), (100,0)), #5
    ((0,50),(0,100)),#6
    ((100, 0), (100 , -50)),#7
    ((100, 0), (100, 50)),#8
    ((50, 0), (50, 50)),#9
    ((100, 50), (50 , 50)), #10
    ((50, 50), (0 , 50)), #11   
    ((100, -50), (50,-50)) #12
])

# Add multiple traffic lights
sim.create_traffic_lights([
    ((300, 290), 1),
    ((400, 300), 0)
])

# Start simulation
win = Window(sim)
win.offset = (0, 0)
win.run(steps_per_update=5)
  
  