import math
import sys

import pygame
import pygame.font
import pygame.time


class Body:
    def __init__(
        self,
        name: str,
        mass: float,
        density: float,
        position_x: float,
        position_y: float,
        velocity_x: float = 0.0,
        velocity_y: float = 0.0,
        color: tuple = (255, 255, 255),
    ):
        self.name = name
        self.mass = mass
        self.density = density
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
        self.radius = math.cbrt((3 * self.mass) / (4 * math.pi * self.density))
        return self

    def update_force(self, bodies: list["Body"]):
        """Updates the force applied to this body for each body in `bodies`."""
        for second_body in bodies:
            if self != second_body:
                self._update_force(second_body, bodies)
        return self

    def _update_force(self, second_body: "Body", bodies: list["Body"]):
        # G is the gravitational constant.
        G = 6.674e-11

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
        self.position_x = (self.position_x + second_body.position_x) / 2
        self.position_y = (self.position_y + second_body.position_y) / 2

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

    def get_scaled_position(
        self,
        scale: int | float,
        window_size: tuple[int, int],
    ) -> tuple[float, float]:
        """Returns the position, centred, with a scale factor applied."""
        position_x = (self.position_x / scale) + (window_size[0] / 2)
        position_y = (self.position_y / scale) + (window_size[1] / 2)
        return (position_x, position_y)

    def get_scaled_radius(self, scale: int | float):
        """Returns the radius, with a scale factor applied"""
        return math.pow(self.radius, scale)

    def get_scaled_trail(
        self,
        scale: int | float,
        window_resolution: tuple[int, int],
    ) -> list[tuple[float, float]]:
        """Returns the trail, centred, with a scale factor applied."""
        trail = [
            (
                (position_x / scale) + (window_resolution[0] / 2),
                (position_y / scale) + (window_resolution[1] / 2),
            )
            for (position_x, position_y) in self.trail
        ]
        return trail


def main() -> None:
    def preset_solar_system() -> list["Body"]:
        bodies = [
            # The density of the Sun is much higher than in the real world so that you
            # can see it in the same frame as the other bodies.
            Body(
                "Sun",
                mass=1.989e30,
                density=1.622e5,
                position_x=0.0,
                position_y=0.0,
                color=(255, 255, 0),
            ),
            Body(
                "Mercury",
                mass=0.330e24,
                density=5429,
                position_x=-57.9e9,
                position_y=0.0,
                velocity_x=0,
                velocity_y=47.4e3,
                color=(168, 168, 168),
            ),
            Body(
                "Venus",
                mass=4.87e24,
                density=5243,
                position_x=-108.2e9,
                position_y=0.0,
                velocity_x=0,
                velocity_y=35.0e3,
                color=(255, 228, 181),
            ),
            Body(
                "Earth",
                mass=5.97e24,
                density=5514,
                position_x=-149.6e9,
                position_y=0.0,
                velocity_x=0,
                velocity_y=29.8e3,
                color=(0, 0, 255),
            ),
            Body(
                "Mars",
                mass=0.642e24,
                density=3934,
                position_x=-228e9,
                position_y=0.0,
                velocity_x=0,
                velocity_y=24.1e3,
                color=(255, 99, 71),
            ),
            Body(
                "Jupiter",
                mass=1898e24,
                density=1326,
                position_x=-778.5e9,
                position_y=0.0,
                velocity_x=0,
                velocity_y=13.1e3,
                color=(255, 192, 0),
            ),
            Body(
                "Saturn",
                mass=568e24,
                density=687,
                position_x=-1432.0e9,
                position_y=0.0,
                velocity_x=0,
                velocity_y=9.7e3,
                color=(255, 215, 0),
            ),
            Body(
                "Uranus",
                mass=86.8e24,
                density=1270,
                position_x=-2867.0e9,
                position_y=0.0,
                velocity_x=0,
                velocity_y=6.8e3,
                color=(173, 216, 230),
            ),
            Body(
                "Neptune",
                mass=102e24,
                density=1638,
                position_x=-4515.0e9,
                position_y=0.0,
                velocity_x=0,
                velocity_y=5.4e3,
                color=(0, 0, 139),
            ),
            Body(
                "Pluto",
                mass=0.0130e24,
                density=1850,
                position_x=-5906.4e9,
                position_y=0.0,
                velocity_x=0,
                velocity_y=4.7e3,
                color=(139, 134, 130),
            ),
        ]
        return bodies

    WINDOW_SIZE = (1280, 1280)
    FRAMERATE_MAX = 120
    SCALE_POSITION = 10e9
    SCALE_RADIUS = 1 / 12

    pygame.init()
    pygame.font.init()
    font_consolas = pygame.font.SysFont("Consolas", 20)

    window = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Gravity Simulator")

    # Enter the preset you wish to use.
    bodies: list["Body"] = preset_solar_system()

    clock = pygame.time.Clock()
    timestep = 60 * 60 * 24

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
                body.get_scaled_position(SCALE_POSITION, WINDOW_SIZE),
                body.get_scaled_radius(SCALE_RADIUS),
            )
            if len(body.trail) > 2:
                pygame.draw.aalines(
                    window,
                    body.color,
                    False,
                    body.get_scaled_trail(SCALE_POSITION, WINDOW_SIZE),
                )

        pygame.display.flip()

        clock.tick(FRAMERATE_MAX)


if __name__ == "__main__":
    main()
