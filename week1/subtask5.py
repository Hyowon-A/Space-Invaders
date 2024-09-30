# Create a program that displays the surface area of a cylinder given the height and the radius.

from math import pi

h = 6
r = 4

surface = 2 * pi * r * h + 2 * pi * (r ** 2)

print("The surface area of a cylinder: " + str(surface))