# Create a program that displays the area and the circumference of a circle given the radius.

from math import pi

r = 4

area = pi * (r ** 2)
circumference = 2 * r * pi

print("The area of the circle: " + str(area))
print("The circumference of the circle " + str(circumference))