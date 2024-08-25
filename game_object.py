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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_impulse_multiplier = 2
        self.increase_speed_on_click = False

    def on_click(self):
        impulse = self.default_impulse_multiplier
        self.body.apply_impulse_at_local_point(pymunk.Vec2d(impulse, 0))

    def update(self):
        super().update()
        if self.increase_speed_on_click and self.body.velocity.x < 200:
            self.body.velocity.x += 50

class BlueBird(Bird):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_birds = 3
        self.angle_offset = 30

    def split(self):
        for i in range(self.num_birds):
            angle = i * self.angle_offset
            new_bird = BlueBird("assets/img/blue.png", None, self.body.position.x, self.body.position.y, self.space)
            new_bird.body.apply_impulse_at_local_point(pymunk.Vec2d(100, 0).rotated(math.radians(angle)))
            self.space.add(new_bird.body, new_bird.shape)
            self.sprites.append(new_bird)
        self.remove_from_sprite_lists()
