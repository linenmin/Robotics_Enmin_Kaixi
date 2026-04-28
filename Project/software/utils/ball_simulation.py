import numpy as np

GRAVITY = np.array([0, 0, -9.81])  # Gravity vector in m/s^2


class BallSimulation:
    ball_radius = 0.12

    def __init__(self, num_balls=1):
        self.num_balls = num_balls

        self.positions = np.array([[5.0, 0, 2.0]] * num_balls)
        self.velocities = np.zeros((num_balls, 3))
        self.goal_points = np.zeros((num_balls, 3))

        # goal area is square parallel to ground plane
        goal_area_center = np.array([0.8, 0.15, 0.5])
        goal_area_radius = np.array([0.5, 1.0, 0])
        self.velocities[:, 2] = 6.0
        for i in range(num_balls):
            # pick random point in goal area
            goal_point = goal_area_center + (0.5 - np.random.rand(3)) * goal_area_radius
            self.goal_points[i] = goal_point

            a = self.positions[i, 2] - goal_point[2]
            b = self.velocities[i, 2]
            c = 0.5 * GRAVITY[2]

            t_air = (-b - np.sqrt(b**2 - 4 * c * a)) / (2 * c)

            self.velocities[i, 0] = (goal_point[0] - self.positions[i, 0]) / t_air
            self.velocities[i, 1] = (goal_point[1] - self.positions[i, 1]) / t_air

    def update(self, dt: float):
        """
        Updates the positions and velocities of the balls based on the time step dt.
        """
        self.positions += self.velocities * dt + 0.5 * GRAVITY * dt**2
        self.velocities += GRAVITY * dt

        # Check for collisions with the ground (z=0) and reflect the velocity if a collision occurs
        for i in range(self.num_balls):
            if self.positions[i, 2] < self.ball_radius:
                self.positions[i, 2] = self.ball_radius
                self.velocities[i, 2] *= -0.8
                if self.velocities[i, 2] < 0.05:
                    self.velocities[i, 2] = 0

    def get_positions(self) -> np.ndarray:
        """
        Computes the positions of the balls at time t based on their initial positions and velocities.
        """
        mean = 0.0
        standard_deviation = 1.0 * 1e-3
        return self.positions + np.random.normal(
            mean, standard_deviation, self.positions.shape
        )