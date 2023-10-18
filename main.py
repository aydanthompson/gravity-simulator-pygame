import math
from random import randint, random, lognormvariate, normalvariate
import sys

import pygame
import pygame.font
import pygame.time

from body import Body


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

    def preset_circle(
        body_count: int, velocity: int, radius: int, width: int
    ) -> list["Body"]:
        def generate_point_on_circle(
            velocity: int, radius: int, width: float
        ) -> tuple[float, float, float, float]:
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
                "centre",
                mass=1000000,
                position_x=WINDOW_SIZE[0] / 2,
                position_y=WINDOW_SIZE[1] / 2,
            )
        )
        for i in range(body_count):
            x, y, velocity_x, velocity_y = generate_point_on_circle(
                velocity, radius, width
            )
            bodies.append(
                Body(
                    i,
                    mass=lognormvariate(2, 0.9),
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
    bodies: list["Body"] = preset_circle(25, 50, 250, 100)

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
