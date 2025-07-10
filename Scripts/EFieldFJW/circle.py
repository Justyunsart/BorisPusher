import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Create a figure and axis
fig, ax = plt.subplots()

# Create a small circle at (1, 1) with a specified radius
circle = patches.Circle((1, 1), radius=0.1, color='blue', fill=True)

# Add the circle to the axes
ax.add_patch(circle)

# Set limits and aspect
ax.set_xlim(0, 2)
ax.set_ylim(0, 2)
ax.set_aspect('equal', adjustable='box')

# Show the plot
plt.title('Circle at (1, 1)')
plt.grid()
plt.show()
