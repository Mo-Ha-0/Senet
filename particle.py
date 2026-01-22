"""Particle effects for visual feedback"""
import random


class Particle:
    """Particle for visual effects"""
    def __init__(self, x, y, color, velocity_x, velocity_y):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.life = 1.0
        self.size = random.uniform(3, 8)
        
    def update(self, dt):
        self.x += self.velocity_x * dt * 60
        self.y += self.velocity_y * dt * 60
        self.velocity_y -= 200 * dt  # Gravity
        self.life -= dt * 2
        return self.life > 0