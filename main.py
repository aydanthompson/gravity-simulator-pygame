import sys
import math
import random
import pygame
import pygame.font
import pygame.time


class Body:
    def __init__(
        self,
        name: str,
        mass: int | float,
        pos_x: int | float,
        pos_y: int | float,
        vel_x: int | float = 0,
        vel_y: int | float = 0,
        color: tuple = (255, 255, 255),
    ):
        self.name = name
        self.mass = mass
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color

        self.force_x = 0.0
        self.force_y = 0.0

        self.trail = []

        self.update_radius()

    def update_radius(self):
        self.radius = math.sqrt(self.mass) * 2
        return self

    def update_force(self, other_body: "Body", bodies: list):
        gravitational_constant = 0  # 6.67430e-11

        dx = self.pos_x - other_body.pos_x
        dy = self.pos_y - other_body.pos_y
        distance = math.sqrt(dx**2 + dy**2)

        if distance <= self.radius + other_body.radius:
            force = 0
            # self.combine(other_body, bodies)
        else:
            force = -(gravitational_constant * self.mass * other_body.mass) / (
                distance**2
            )

        angle = math.atan2(dy, dx)
        self.force_x += force * math.cos(angle)
        self.force_y += force * math.sin(angle)
        return self

    def reset_force(self):
        self.force_x = 0.0
        self.force_y = 0.0
        return self

    def update_position(self, timestep: float = 1):
        # a = F / m
        self.accel_x = self.force_x / self.mass
        self.accel_y = self.force_y / self.mass

        # v = at
        # v2 = v1 + at
        self.vel_x += self.accel_x * timestep
        self.vel_y += self.accel_y * timestep

        # s = vt
        # s2 = s1 + vt
        self.pos_x += self.vel_x * timestep
        self.pos_y += self.vel_y * timestep
        return self

    def combine(self, other_body: "Body", bodies: list):
        self.mass += other_body.mass
        self.radius = math.sqrt(self.radius**2 + other_body.radius**2)
        self.pos_x = (self.pos_x + other_body.pos_x) / 2
        self.pos_y = (self.pos_y + other_body.pos_y) / 2
        self.vel_x = (self.vel_x + other_body.vel_x) / 2
        self.vel_y = (self.vel_y + other_body.vel_y) / 2
        self.color = tuple(
            [int(self.color[i] + other_body.color[i]) / 2 for i in range(3)]
        )
        bodies.remove(other_body)

    def update_trail(self):
        self.trail.append((self.pos_x, self.pos_y))

        if len(self.trail) > 2**6:
            self.trail.pop(0)
        return self

    def get_pos(self):
        return (self.pos_x, self.pos_y)

    def get_vel(self):
        return (self.vel_x, self.vel_y)

    def get_accel(self):
        return (self.accel_x, self.accel_y)

    def get_force(self):
        return (self.force_x, self.force_y)


def main() -> None:
    WINDOW_SIZE = (1920, 1080)

    pygame.init()
    pygame.font.init()
    font_consolas = pygame.font.SysFont("Consolas", 20)

    window = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Gravity Simulator")

    # Add the various bodies.
    bodies: list["Body"] = []

    bodies.append(
        Body(
            "a",
            mass=10,
            pos_x=(WINDOW_SIZE[0] / 2) - 100,
            pos_y=WINDOW_SIZE[1] / 2,
            color=(255, 0, 0),
            vel_x=0.1,
        )
    )
    bodies.append(
        Body(
            "b",
            mass=10,
            pos_x=(WINDOW_SIZE[0] / 2) + 100,
            pos_y=WINDOW_SIZE[1] / 2,
            color=(0, 0, 255),
            vel_x=-0.1,
        )
    )

    clock = pygame.time.Clock()
    timestep = 1

    # Game loop.
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        window.fill((0, 0, 0))

        # Update the force applied to each body.
        for primary_body in bodies:
            for secondary_body in bodies:
                if primary_body != secondary_body:
                    primary_body.update_force(secondary_body, bodies)

        for body in bodies:
            # Update the position and trail.
            body.update_position(timestep=timestep)
            body.update_trail()

            # Redraw the body and trail.
            pygame.draw.circle(
                window,
                body.color,
                (body.pos_x, body.pos_y),
                body.radius,
            )
            if len(body.trail) > 2:
                pygame.draw.aalines(
                    window,
                    body.color,
                    False,
                    body.trail,
                )
            body.reset_force()

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

        pygame.display.flip()

        clock.tick()


if __name__ == "__main__":
    main()
