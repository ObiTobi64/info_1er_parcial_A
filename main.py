import logging
import random
import arcade
import pymunk

from game_object import Bird, Column, Pig, YellowBird, BlueBird
from game_logic import get_impulse_vector, Point2D

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("arcade").setLevel(logging.WARNING)
logging.getLogger("pymunk").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

logger = logging.getLogger("main")

WIDTH = 1800
HEIGHT = 800
TITLE = "Angry Birds"
GRAVITY = -900

class App(arcade.Window):

    def __init__(self):
        super().__init__(WIDTH, HEIGHT, TITLE)
        self.background = arcade.load_texture("assets/img/background3.png")
        
        # Crear espacio de pymunk
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)

        # Agregar piso
        floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        floor_shape = pymunk.Segment(floor_body, [0, 15], [WIDTH, 15], 0.0)
        floor_shape.friction = 10
        self.space.add(floor_body, floor_shape)

        self.sprites = arcade.SpriteList()
        self.birds = arcade.SpriteList()
        self.world = arcade.SpriteList()
        self.add_columns()  # Llamada al método add_columns
        self.add_pigs()     # Llamada al método add_pigs
        self.add_moving_obstacles()  # Llamada al método add_moving_obstacles
        self.add_fragile_blocks()  # Llamada al método add_fragile_blocks

        # Cargar imagen de la resortera y establecer posición fija
        self.sling_image = arcade.load_texture("assets/img/sling-3.png")
        self.sling_position = (250, HEIGHT / 12)

        self.start_point = Point2D()
        self.end_point = Point2D()
        self.distance = 0
        self.draw_line = False

        # Agregar un collision handler
        self.handler = self.space.add_default_collision_handler()
        self.handler.post_solve = self.collision_handler

        # Inicializar el tipo de pájaro seleccionado
        self.selected_bird_type = "red"
        self.keys_pressed = set()

    def add_columns(self):
        # Columnas de diferentes alturas y anchos
        for x in range(WIDTH // 2, WIDTH, 300):
            height = random.randint(100, 300)
            column = Column(x, 50, self.space, width=60, height=height)
            self.sprites.append(column)
            self.world.append(column)
        
        # Añadir plataformas flotantes
        for x in range(WIDTH // 2 + 150, WIDTH, 450):
            y = random.randint(300, 500)
            platform = Column(x, y, self.space, width=200, height=20, mass=5)
            self.sprites.append(platform)
            self.world.append(platform)

    def add_moving_obstacles(self):
        for x in range(WIDTH // 2, WIDTH, 400):
            y = random.randint(100, 300)
            moving_obstacle = Column(x, y, self.space, width=50, height=50, mass=8)
            self.sprites.append(moving_obstacle)
            self.world.append(moving_obstacle)
            moving_obstacle.body.velocity = pymunk.Vec2d(random.choice([-50, 50]), 0)

    def add_fragile_blocks(self):
        for x in range(WIDTH // 2 + 100, WIDTH, 350):
            y = random.randint(100, 200)
            fragile_block = Column(x, y, self.space, width=100, height=50, mass=2)
            fragile_block.shape.elasticity = 0.1  # Menos elástico, más frágil
            self.sprites.append(fragile_block)
            self.world.append(fragile_block)

    def collision_handler(self, arbiter, space, data):
        impulse_norm = arbiter.total_impulse.length
        if impulse_norm < 100:
            return True
        logger.debug(impulse_norm)
        if impulse_norm > 1200:
            for obj in self.world:
                if obj.shape in arbiter.shapes:
                    obj.remove_from_sprite_lists()
                    self.space.remove(obj.shape, obj.body)

        return True

    def add_pigs(self):
        pig1 = Pig(WIDTH / 2, 100, self.space)
        self.sprites.append(pig1)
        self.world.append(pig1)

    def on_update(self, delta_time: float):
        self.space.step(1 / 60.0)  # Actualiza la simulación de las físicas
        self.update_collisions()
        self.sprites.update()

        # Verificar si algún pájaro necesita ejecutar su acción especial
        for bird in self.birds:
            if isinstance(bird, YellowBird) and arcade.key.SPACE in self.keys_pressed:
                bird.on_click()

            if isinstance(bird, BlueBird) and arcade.key.SPACE in self.keys_pressed and not bird.has_split:
                bird.on_click()

    def update_collisions(self):
        pass

    def on_key_press(self, key, modifiers):
        if key == arcade.key.KEY_1:
            self.selected_bird_type = "red"
        elif key == arcade.key.KEY_2:
            self.selected_bird_type = "yellow"
        elif key == arcade.key.KEY_3:
            self.selected_bird_type = "blue"
        elif key == arcade.key.SPACE:
            # Capturar la tecla espacio
            self.keys_pressed.add(key)

    def on_key_release(self, key, modifiers):
        if key == arcade.key.SPACE:
            # Eliminar la tecla espacio del set cuando se suelta
            self.keys_pressed.discard(key)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Ajusta la posición de inicio al punto fijo de la resortera
            self.start_point = Point2D(self.sling_position[0], self.sling_position[1])
            self.end_point = Point2D(x, y)
            self.draw_line = True
            logger.debug(f"Start Point: {self.start_point}")

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if buttons == arcade.MOUSE_BUTTON_LEFT:
            self.start_point = Point2D(self.sling_position[0], self.sling_position[1])
            self.start_point = Point2D(x, y)
            logger.debug(f"Dragging to: {self.start_point}")

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            logger.debug(f"Releasing from: {self.start_point}")
            self.draw_line = False
            impulse_vector = get_impulse_vector(self.start_point, self.end_point)
            
            # Crear el pájaro seleccionado
            if self.selected_bird_type == "red":
                bird = Bird("assets/img/red.png", impulse_vector, self.sling_position[0], self.sling_position[1], self.space)
            elif self.selected_bird_type == "yellow":
                bird = YellowBird("assets/img/chuck.png", impulse_vector, self.sling_position[0], self.sling_position[1], self.space)
            elif self.selected_bird_type == "blue":
                bird = BlueBird("assets/img/blue.png", impulse_vector, self.sling_position[0], self.sling_position[1], self.space, self.sprites, self.birds)
            
            self.sprites.append(bird)
            self.birds.append(bird)
            self.keys_pressed = set()  # Restablecer teclas presionadas

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, WIDTH, HEIGHT, self.background)
        # Dibujar la resortera
        arcade.draw_texture_rectangle(self.sling_position[0], self.sling_position[1], self.sling_image.width, self.sling_image.height, self.sling_image)
        self.sprites.draw()
        if self.draw_line:
            arcade.draw_line(self.start_point.x, self.start_point.y, self.end_point.x, self.end_point.y,
            arcade.color.BLACK, 3)

def main():
    app = App()
    arcade.run()

if __name__ == "__main__":
    main()
