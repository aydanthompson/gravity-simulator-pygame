import math


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
        self.position_x = self.position_x * (
            self.mass / (self.mass + second_body.mass)
        ) + second_body.position_x * (second_body.mass / (self.mass + second_body.mass))
        self.position_y = self.position_y * (
            self.mass / (self.mass + second_body.mass)
        ) + second_body.position_y * (second_body.mass / (self.mass + second_body.mass))

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
