"""The model classes maintain the state and logic of the simulation."""

from __future__ import annotations
from typing import List
from random import random
from projects.pj02 import constants
from math import sin, cos, pi, sqrt


__author__ = "730389239"


class Point:
    """A model of a 2-d cartesian coordinate Point."""
    x: float
    y: float

    def __init__(self, x: float, y: float):
        """Construct a point with x, y coordinates."""
        self.x = x
        self.y = y

    def add(self, other: Point) -> Point:
        """Add two Point objects together and return a new Point."""
        x: float = self.x + other.x
        y: float = self.y + other.y
        return Point(x, y)
    
    def distance(self, other: Point) -> float:
        """Calculate the distance between two points."""
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class Cell:
    """An individual subject in the simulation."""
    location: Point
    direction: Point
    sickness: int = constants.VULNERABLE

    def __init__(self, location: Point, direction: Point):
        """Construct a cell with its location and direction."""
        self.location = location
        self.direction = direction

    def tick(self) -> None:
        """Reassign the object's location attribute with its direction."""
        self.location = self.location.add(self.direction)
        if self.is_infected():
            self.sickness += 1
            if self.sickness >= constants.RECOVERY_PERIOD:
                self.immunize()
        
    def color(self) -> str:
        """Return the color representation of a cell."""
        if self.is_infected():
            return "red"
        elif self.is_immune():
            return "blue"
        else:
            return "gray"

    def contract_disease(self) -> None:
        """Assign the INFECTED constant to the sickness attribute."""
        self.sickness = constants.INFECTED
    
    def is_vulnerable(self) -> bool:
        """Returns True if the cell's sickness attributes is equal to VULNERABLE and False otherwise."""
        if self.sickness == constants.VULNERABLE:
            return True
        else:
            return False
    
    def is_infected(self) -> bool:
        """Returns True when the cell’s sickness attribute is equal to INFECTED and False otherwise."""
        if self.sickness >= constants.INFECTED:
            return True
        else:
            return False
    
    def contact_with(self, other: Cell) -> None:
        """If either of the Cell objects is infected and the other is vulnerable, then the other become infected."""
        if self.is_infected() and other.is_vulnerable():
            other.contract_disease()
        elif self.is_vulnerable() and other.is_infected():
            self.contract_disease()
    
    def immunize(self) -> None:
        """Assigns the constant IMMUNE to the sickness attribute of the Cell."""
        self.sickness = constants.IMMUNE

    def is_immune(self) -> bool:
        """Returns True when the Cell object’s sickness attribute is equal to the IMMUNE constant."""
        if self.sickness == constants.IMMUNE:
            return True
        else:
            return False


class Model:
    """The state of the simulation."""

    population: List[Cell]
    time: int = 0

    def __init__(self, cells: int, speed: float, start_infected: int, start_immune: int = 0):
        """Initialize the cells with random locations and directions."""
        self.population = []
        if start_infected >= cells or start_infected <= 0:
            raise ValueError("Some number of the Cell objects must begin infected.")
        if start_immune >= cells or start_immune < 0:
            raise ValueError("Immune cells must be less than the number of Cell objects.")
        if start_immune + start_infected >= cells:
            raise ValueError("Immune and Infected cells must be less than the number of Cell objects.")
        for _ in range(0, cells - start_infected - start_immune):
            start_loc = self.random_location()
            start_dir = self.random_direction(speed)
            self.population.append(Cell(start_loc, start_dir))
        for cell in range(0, start_infected):
            start_loc = self.random_location()
            start_dir = self.random_direction(speed)
            infected_cell: Cell = Cell(start_loc, start_dir)
            infected_cell.sickness = constants.INFECTED
            self.population.append(infected_cell)
        for immune in range(0, start_immune):
            start_loc = self.random_location()
            start_dir = self.random_direction(speed)
            immune_cell: Cell = Cell(start_loc, start_dir)
            immune_cell.sickness = constants.IMMUNE
            self.population.append(immune_cell)

    def tick(self) -> None:
        """Update the state of the simulation by one time step."""
        self.time += 1
        for cell in self.population:
            cell.tick()
            self.enforce_bounds(cell)
        self.check_contacts()

    def random_location(self) -> Point:
        """Generate a random location."""
        start_x = random() * constants.BOUNDS_WIDTH - constants.MAX_X
        start_y = random() * constants.BOUNDS_HEIGHT - constants.MAX_Y
        return Point(start_x, start_y)

    def random_direction(self, speed: float) -> Point:
        """Generate a 'point' used as a directional vector."""
        random_angle = 2.0 * pi * random()
        dir_x = cos(random_angle) * speed
        dir_y = sin(random_angle) * speed
        return Point(dir_x, dir_y)

    def enforce_bounds(self, cell: Cell) -> None:
        """Cause a cell to 'bounce' if it goes out of bounds."""
        if cell.location.x > constants.MAX_X:
            cell.location.x = constants.MAX_X
            cell.direction.x *= -1
        elif cell.location.x < constants.MIN_X:
            cell.location.x = constants.MIN_X
            cell.direction.x *= -1
        elif cell.location.y > constants.MAX_Y:
            cell.location.y = constants.MAX_Y
            cell.direction.y *= -1
        elif cell.location.y < constants.MIN_Y:
            cell.location.y = constants.MIN_Y
            cell.direction.y *= -1
    
    def check_contacts(self) -> None:
        """Compare the distance between every two Cell objects’ location attributes in the population."""
        used_cells: List[Cell] = []
        for cell in self.population:
            used_cells.append(cell)
            i: int = 0
            while i < len(self.population):
                if cell == self.population[i] or self.population[i] in used_cells:
                    i += 1
                else:
                    if cell.location.distance(self.population[i].location) < constants.CELL_RADIUS:
                        cell.contact_with(self.population[i])
                        i += 1
                    else:
                        i += 1

    def is_complete(self) -> bool:
        """Method to indicate when the simulation is complete."""
        for cell in self.population:
            if cell.is_infected():
                return False
        return True