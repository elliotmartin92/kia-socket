from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
import numpy as np

y_axle = 9.279
z_axle = 11.190
r_hub = 2.10

hub_circle = Point(y_axle, z_axle).buffer(r_hub)

# Let's test a true tangential upper profile:
# Top apex is at (y_axle, z_axle + r_hub) = (9.279, 13.290).
# A smooth transition from top of hub to (6.80, 10.80):
# Instead of a straight line from (9.279, 13.29) to (6.80, 10.80) that cuts into the circle,
# We can follow the circle arc from 90 deg (9.279, 13.290) to the tangent point to (6.80, 10.80)
# OR a smooth curve / fillet!

# Let's find the tangent line from (6.80, 10.80) to the hub circle:
# Center C = (y_axle, z_axle), P = (6.80, 10.80)
# Vector CP = P - C = (-2.479, -0.390)
# Dist = sqrt(2.479^2 + 0.390^2) = 2.509 mm
# Since dist > r_hub (2.10 mm), there exist two tangents from P to the circle!
# The upper tangent:
P = np.array([6.80, 10.80])
C = np.array([y_axle, z_axle])
d = np.linalg.norm(P - C)
theta_CP = np.arctan2(P[1] - C[1], P[0] - C[0]) # angle of CP
alpha = np.arccos(r_hub / d) # angle offset to tangent points

# Upper tangent angle from center:
phi_tan_upper = theta_CP + alpha
T_upper = C + r_hub * np.array([np.cos(phi_tan_upper), np.sin(phi_tan_upper)])
print("Upper tangent point on hub:", T_upper, "angle deg:", np.degrees(phi_tan_upper))

# If we follow the circle from 90 deg down to phi_tan_upper, and then take the straight tangent to P:
# Let's check angles:
# 90 deg = pi/2 = 1.5708 rad
# phi_tan_upper:
print(f"90 deg = (9.279, 13.290), T_upper = ({T_upper[0]:.3f}, {T_upper[1]:.3f})")

# Let's also check the bottom return:
# Point 7 is at (y_axle - 1.50, z_axle - 2.50) = (7.779, 8.690)
# Can we also find the tangent from (4.50, 5.30) or Point 7 to the bottom of the hub circle?
P_bot = np.array([4.50, 5.30])
d_bot = np.linalg.norm(P_bot - C)
theta_bot = np.arctan2(P_bot[1] - C[1], P_bot[0] - C[0])
alpha_bot = np.arccos(r_hub / d_bot)
phi_tan_lower = theta_bot - alpha_bot
T_lower = C + r_hub * np.array([np.cos(phi_tan_lower), np.sin(phi_tan_lower)])
print(f"Lower tangent from (4.50, 5.30) to hub: T_lower = ({T_lower[0]:.3f}, {T_lower[1]:.3f}), angle deg: {np.degrees(phi_tan_lower):.1f}")
