import numpy as np
import matplotlib.pyplot as plt
#
# # Example 2D array: a Gaussian
# x = np.linspace(-5, 5, 100)
# y = np.linspace(-5, 5, 100)
# X, Y = np.meshgrid(x, y)
# Z = np.exp(-(X**2 + Y**2))  # 2D Gaussian
#
# # Choose a line-out: e.g., horizontal line at center row
# center_row_index = Z.shape[0] // 2
# line_out = Z[center_row_index, :]
#
# # Plot
# plt.figure()
# plt.plot(x, line_out)
# plt.title("Line-out from center row")
# plt.xlabel("x")
# plt.ylabel("Value")
# plt.grid(True)
# plt.show()

# import numpy as np
# import matplotlib.pyplot as plt

# Create a sample 2D array
data = np.random.rand(100, 100)  # shape (rows, columns)

# Choose a line to extract: e.g., middle row or column
row_index = 50  # horizontal line
column_index = 75  # vertical line

# Horizontal line-out (constant row, varying column)
line_out_row = data[row_index, :]  # 1D array across columns
x_axis = np.arange(data.shape[1])  # x-coordinates (columns)

# Vertical line-out (constant column, varying row)
line_out_col = data[:, column_index]  # 1D array down rows
y_axis = np.arange(data.shape[0])  # y-coordinates (rows)

# Plot horizontal and vertical line-outs
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(x_axis, line_out_row)
plt.title(f"Line-out across Row {row_index}")
plt.xlabel("Column Index")
plt.ylabel("Value")

plt.subplot(1, 2, 2)
plt.plot(y_axis, line_out_col)
plt.title(f"Line-out across Column {column_index}")
plt.xlabel("Row Index")
plt.ylabel("Value")

plt.tight_layout()
plt.show()