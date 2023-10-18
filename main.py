import math
from random import randint, random, lognormvariate, normalvariate
import sys

import pygame
import pygame.font
import pygame.time


class Body:
    def __init__(
        self,
        name: str,
        mass: int | float,
        position_x: int | float,
        position_y: int | float,
        velocity_x: int | float = 0,
        velocity_y: int | float = 0,
        color: tuple = (255, 255, 255),
    ):
        self.name = name
        self.mass = mass
        self.position_x = position_x
        self.position_y = position_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.color = color

        self.force_x = 0.0
        self.force_y = 0.0

        self.trail = []

        self._update_radius()
        self._update_momentum()

    def _update_radius(self):
        # Using a combined formula for the volume of a sphere and the density.
        density = 1.0
        self.radius = math.cbrt((3 * self.mass) / (4 * math.pi * density))
        return self

    def update_force(self, bodies: list["Body"]):
        """Updates the force applied to this body for each body in `bodies`."""
        for second_body in bodies:
            if self != second_body:
                self._update_force(second_body, bodies)
        return self

    def _update_force(self, second_body: "Body", bodies: list["Body"]):
        # In our universe, G (gravitational constant) is equal to 6.67430e-11, but in
        # this simulation G can be set to different values to change the proportionality
        # of the force applied to each body.
        G = 1.0

        dx = self.position_x - second_body.position_x
        dy = self.position_y - second_body.position_y
        d = math.sqrt(dx**2 + dy**2)

        if d <= (self.radius + second_body.radius):
            force = 0
            self.combine(second_body, bodies)
        else:
            # Newton's Universal Law of Gravitation:
            # https://phys.libretexts.org/Bookshelves/Conceptual_Physics/Introduction_to_Physics_(Park)/02%3A_Mechanics_I_-_Motion_and_Forces/02%3A_Dynamics/2.09%3A_Newtons_Universal_Law_of_Gravitation
            force = -(G * self.mass * second_body.mass) / (d**2)

        angle = math.atan2(dy, dx)
        self.force_x += force * math.cos(angle)
        self.force_y += force * math.sin(angle)
        return self

    def update_position(self, timestep: float = 1.0):
        # a = F / m
        self.acceleration_x = self.force_x / self.mass
        self.acceleration_y = self.force_y / self.mass

        # v = at
        # v2 = v1 + at
        self.velocity_x += self.acceleration_x * timestep
        self.velocity_y += self.acceleration_y * timestep

        # s = vt
        # s2 = s1 + vt
        self.position_x += self.velocity_x * timestep
        self.position_y += self.velocity_y * timestep

        self._reset_force()
        self._update_momentum()
        return self

    def _reset_force(self):
        self.force_x = 0.0
        self.force_y = 0.0
        return self

    def _update_momentum(self) -> "Body":
        self.momentum_x = self.mass * self.velocity_x
        self.momentum_y = self.mass * self.velocity_y
        return self

    def combine(self, second_body: "Body", bodies: list["Body"]):
        # Combine mass.
        self.mass += second_body.mass
        self._update_radius()

        # Combine position.
        self.position_x = (self.position_x * (self.mass / (self.mass + second_body.mass)) + second_body.position_x * (second_body.mass / (self.mass + second_body.mass)))
        self.position_y = (self.position_y * (self.mass / (self.mass + second_body.mass)) + second_body.position_y * (second_body.mass / (self.mass + second_body.mass)))

        # Combine momentum and update velocity.
        self.momentum_x += second_body.momentum_x
        self.momentum_y += second_body.momentum_y
        self.velocity_x = self.momentum_x / self.mass
        self.velocity_y = self.momentum_y / self.mass

        # Combine colors.
        self.color = tuple(
            (color_1 + color_2) // 2
            for _, (color_1, color_2) in enumerate(zip(self.color, second_body.color))
        )

        bodies.remove(second_body)

        # Reset trail.
        self.trail = []

    def update_trail(self, framerate):
        """Adds the current position to the trail and removes the oldest position from
        the trail if the number of points in the trail is too high.
        """
        trail_max = framerate

        self.trail.append((self.position_x, self.position_y))

        # Remove the oldest position from the trail if
        # the number of points exceeds `trail_max`.
        if len(self.trail) > trail_max:
            self.trail.pop(0)
        return self


def main() -> None:
    def preset_momentum_demo() -> list["Body"]:
        bodies = [
            Body(
                "red",
                mass=10000,
                position_x=(WINDOW_SIZE[0] / 2) - 100,
                position_y=WINDOW_SIZE[1] / 2,
                color=(255, 0, 0),
                velocity_x=1,
            ),
            Body(
                "blue",
                mass=10,
                position_x=(WINDOW_SIZE[0] / 2) + 100,
                position_y=WINDOW_SIZE[1] / 2,
                color=(0, 0, 255),
            ),
        ]
        return bodies

    def preset_random(body_count: int) -> list["Body"]:
        bodies = [
            Body(
                i,
                mass=randint(1, 100),
                position_x=randint(0, WINDOW_SIZE[0]),
                position_y=randint(0, WINDOW_SIZE[1]),
                color=(randint(0, 255), randint(0, 255), randint(0, 255)),
            )
            for i in range(body_count)
        ]
        return bodies

    def preset_circle(body_count: int, velocity: int, radius: int, width: int) -> list["Body"]:
        def generate_point_on_circle(velocity: int, radius: int, width: float) -> tuple[float, float, float, float]:
            centre_x = WINDOW_SIZE[0] / 2
            centre_y = WINDOW_SIZE[1] / 2

            r = radius + width * random()
            theta = random() * 2 * math.pi

            x = centre_x + r * math.cos(theta)
            y = centre_y + r * math.sin(theta)

            velocity = normalvariate(velocity, 4)
            velocity_x = velocity * math.cos(theta + math.pi / 2)
            velocity_y = velocity * math.sin(theta + math.pi / 2)
            return x, y, velocity_x, velocity_y

        bodies = []
        bodies.append(
            Body(
                'centre',
                mass=1000000,
                position_x=WINDOW_SIZE[0] / 2,
                position_y=WINDOW_SIZE[1] / 2,
            )
        )
        for i in range(body_count):
            x, y, velocity_x, velocity_y = generate_point_on_circle(radius, width)
            bodies.append(
                Body(
                    i,
                    mass=lognormvariate(4, 0.9),
                    position_x=x,
                    position_y=y,
                    velocity_x=velocity_x,
                    velocity_y=velocity_y,
                    color=(randint(0, 255), randint(0, 255), randint(0, 255)),
                )
            )
        return bodies

    WINDOW_SIZE = (1080, 1080)
    FRAMERATE_MAX = 120

    pygame.init()
    pygame.font.init()
    font_consolas = pygame.font.SysFont("Consolas", 20)

    window = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Gravity Simulator")

    # Enter the preset you wish to use.
    bodies: list["Body"] = preset_circle(25, 65, 250, 100)

    clock = pygame.time.Clock()
    timestep = 0.1

    # Game loop.
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        window.fill((0, 0, 0))

        # Draw the framerate, frametime, and the number of
        # bodies in the top-left corner of the window.
        framerate = clock.get_fps()
        framerate_text = font_consolas.render(
            f"Framerate: {int(framerate)} FPS", True, (255, 255, 255)
        )
        window.blit(framerate_text, (10, 10))
        frametime = clock.get_time()
        frametime_text = font_consolas.render(
            f"Frametime: {int(frametime)}ms", True, (255, 255, 255)
        )
        window.blit(frametime_text, (10, 30))
        bodies_text = font_consolas.render(
            f"Bodies: {int(len(bodies))}", True, (255, 255, 255)
        )
        window.blit(bodies_text, (10, 50))

        # Update the force applied to each body.
        for body in bodies:
            body.update_force(bodies)

        # Update the position of the body and redraw.
        for body in bodies:
            # Update the position and trail.
            body.update_position(timestep=timestep)
            body.update_trail(framerate)

            # Draw the body and trail.
            pygame.draw.circle(
                window,
                body.color,
                (body.position_x, body.position_y),
                body.radius,
            )
            if len(body.trail) > 2:
                pygame.draw.aalines(
                    window,
                    body.color,
                    False,
                    body.trail,
                )

        pygame.display.flip()

        clock.tick(FRAMERATE_MAX)


if __name__ == "__main__":
    main()
