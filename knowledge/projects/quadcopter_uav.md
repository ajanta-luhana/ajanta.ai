# Lightweight Quadcopter UAV

## Overview
Dec 2022 to Nov 2023. A lightweight quadcopter UAV (drone) prototype for aerial surveillance, real-time monitoring, site surveying, agriculture, environmental inspection and emergency response. It was Ajanta's Bachelor of Engineering final-year thesis at MUET Jamshoro, supervised by Dr. Fahim Aziz Umrani. It was funded by Ignite and shortlisted for NGIRI 2022-23.

## Hardware and approach
Built on a 250 mm carbon-fibre frame with an APM 2.8 flight controller, u-blox 7 GPS, 433 MHz telemetry and a 1.5 GHz video link. Ajanta developed the flight-dynamics model and PID control (altitude, roll, pitch, yaw) in MATLAB/Simulink, then converted it to C firmware on Arduino IDE.

## Results
Testing showed simulated hovering and position response, roll-pitch-yaw response to control inputs, and live video transmission.

## Technologies
MATLAB/Simulink, PID control, Embedded C, Arduino IDE, GPS and telemetry, live video.
