import math
import arcade
import pymunk
from game_logic import ImpulseVector

class Bird(arcade.Sprite):
    """
    Bird class. This represents an angry bird. All the physics is handled by Pymunk,
    the init method only set some initial properties
    """
    def __init__(
        self,
        image_path: str,
        impulse_vector: ImpulseVector,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 5,
        radius: float = 12,
        max_impulse: float = 100,
        power_multiplier: float = 50,
        elasticity: float = 0.8,
        friction: float = 1,
        collision_layer: int = 0,
    ):
        super().__init__(image_path, 1)
        # body
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)

        if impulse_vector:
            impulse = min(max_impulse, impulse_vector.impulse) * power_multiplier
            impulse_pymunk = impulse * pymunk.Vec2d(1, 0)
            body.apply_impulse_at_local_point(impulse_pymunk.rotated(impulse_vector.angle))
            
        shape = pymunk.Circle(body, radius)
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer

        space.add(body, shape)

        self.body = body
        self.shape = shape

    def update(self):
        """
        Update the position of the bird sprite based on the physics body position
        """
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle


class Pig(arcade.Sprite):
    def __init__(
        self,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 2,
        elasticity: float = 0.8,
        friction: float = 0.4,
        collision_layer: int = 0,
    ):
        super().__init__("assets/img/pig_failed.png", 0.1)
        moment = pymunk.moment_for_circle(mass, 0, self.width / 2 - 3)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        shape = pymunk.Circle(body, self.width / 2 - 3)
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer
        space.add(body, shape)
        self.body = body
        self.shape = shape

    def update(self):
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y


class Column(arcade.Sprite):
    def __init__(
        self,
        x: float,
        y: float,
        space: pymunk.Space,
        width: float = 60,
        height: float = 200,
        mass: float = 10,
        elasticity: float = 0.8,
        friction: float = 0.5,
        collision_layer: int = 0,
    ):
        super().__init__("assets/img/column.png", 1)
        moment = pymunk.moment_for_box(mass, (width, height))
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        shape = pymunk.Poly.create_box(body, (width, height))
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer
        space.add(body, shape)
        self.body = body
        self.shape = shape

    def update(self):
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y

class YellowBird(Bird):
    def __init__(self, *args, impulse_multiplier=2, **kwargs):
        super().__init__(*args, **kwargs)
        self.impulse_multiplier = impulse_multiplier
        self.increase_speed_on_click = False

    def on_click(self):
        # Aplica un impulso adicional en la dirección actual del pájaro
        impulse = self.impulse_multiplier * self.body.velocity.length
        impulse_vector = pymunk.Vec2d(impulse, 0).rotated(self.body.angle)
        self.body.apply_impulse_at_local_point(impulse_vector)

    def update(self):
        super().update()
        if self.increase_speed_on_click:
            self.on_click()
            self.increase_speed_on_click = False


class BlueBird(Bird):
    """
    Blue bird class. When the space key is pressed while the bird is in flight,
    it will split into three birds.
    """
    def __init__(self, image_path: str, impulse_vector: ImpulseVector, x: int, y: int, space: pymunk.Space, sprite_list: arcade.SpriteList, bird_list: arcade.SpriteList):
        super().__init__(image_path, impulse_vector, x, y, space)
        self.has_split = False  # Asegura que solo se divida una vez
        self.sprite_list = sprite_list
        self.bird_list = bird_list

    def on_click(self):
        if not self.has_split:
            # Crear dos nuevos pájaros
            for angle_offset in (-30, 30):
                angle = math.radians(angle_offset) + math.atan2(self.body.velocity.y, self.body.velocity.x)
                new_impulse = 200 * pymunk.Vec2d(math.cos(angle), math.sin(angle))
                new_bird = Bird("assets/img/blue.png", ImpulseVector(angle, new_impulse.length), self.body.position.x, self.body.position.y, self.space)
                self.sprite_list.append(new_bird)
                self.bird_list.append(new_bird)

            # Establecer el estado de dividido
            self.has_split = True
