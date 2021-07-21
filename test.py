#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author： 11360
# datetime： 2021/7/21 14:24 

import matplotlib.pyplot as plt
import numpy as np

N = 100
t_array = np.array([i for i in range(N)]) / 5
# control_y_array = np.sin(t_array)
control_y_array = np.ones(N) * 5


# control_y_array = [5 for i in range(1000)]

Kp = 0.4
Ki = 0.3
Kd = 0.2
init_y = 0

y_control_curve = []
intergral = 0
last_error = control_y_array[0] - init_y
y_i = init_y
mse = 0
max_control = 0
for i in range(N):
    error_i = control_y_array[i] - y_i
    proportion = Kp * error_i
    intergral += Ki * error_i
    # if abs(error_i) < 1:
    difference = Kd * (error_i - last_error)
    # else:
    #     difference = 0
    u_i = proportion + intergral + difference - 1
    y_i += u_i
    if y_i > max_control:
        max_control = y_i
    y_control_curve.append(y_i)
    last_error = error_i
    mse += (last_error / N)
overshoot = (max_control - 5) / 5 * 100
print("overshoot = {}%".format(overshoot))
plt.title("Kp = {}, Ki = {}, Kd = {}, \n "
          "mse = {:.3}, overshoot = {:.3}%".format(Kp, Ki, Kd, mse, overshoot))
plt.plot(t_array, control_y_array, c="r")
plt.plot(t_array, y_control_curve)
plt.xlabel("t")
plt.ylabel("control parameters")
plt.show()













