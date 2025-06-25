import math

DX = 0.03  # horizontal spacing in meters
DY = 0.03  # vertical spacing in meters
C = 343  # speed of sound in m/s

d = math.hypot(DX, DY)  # path length in m
t_sec = d / C  # time in seconds
t_ns = t_sec * 1e9  # time in nanoseconds

print(f"Distance = {d:.4f} m,  Time-of-flight = {t_ns:.0f} ns")
