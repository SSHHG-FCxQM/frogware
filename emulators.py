"""The emulator class is made in the hopes that I just have to debug utilities.py
when I first connect to hardware."""

import numpy as np
import time
import PyQt5.QtCore as qtc


pool = qtc.QThreadPool.globalInstance()


class Motor:
    def __init__(self):
        pass

        self._position = 5
        self.is_in_motion = False
        self._stop = False

    @property
    def position(self):
        # In the GUI, I assumed that they give the position in mm
        return self._position

    @position.setter
    def position(self, value_mm):
        self.move_to(value_mm)

    def create_runnable(self, pos_mm):
        self.runnable = MotorRunnable(self, pos_mm)

    def move_to(self, value_mm):
        self.create_runnable(value_mm)
        pool.start(self.runnable)

    def move_by(self, value_mm, blocking=False):
        self._position += value_mm

    def move_home(self, blocking):
        self.move_to(0.)

    def stop_profiled(self):
        self._stop = True

    def get_stage_axis_info(self):
        return 0, 10, "mm", 0.


class MotorRunnable(qtc.QRunnable):
    def __init__(self, motor, pos_mm):
        motor: Motor
        self.motor = motor
        self.pos_mm = pos_mm
        super().__init__()

    def run(self):
        dx = 1e-4
        if self.motor.position < self.pos_mm:
            self.motor.is_in_motion = True

            while self.motor.position < self.pos_mm:
                if self.motor._stop:
                    self.motor._stop = False
                    return

                self.motor._position += dx
                time.sleep(.005)

            self.motor.is_in_motion = False

        elif self.motor.position > self.pos_mm:
            self.motor.is_in_motion = True

            while self.motor.position > self.pos_mm:
                if self.motor._stop:
                    self.motor._stop = False
                    return

                self.motor._position -= dx
                time.sleep(.005)

            self.motor.is_in_motion = False

        else:
            return


class Spectrometer:
    def __init__(self):
        self.int_time_micros = 1000
        self.integration_time_micros_limits = [1, 10e6]

    def spectrum(self):
        wavelengths = np.linspace(350, 1150, 5000)
        lambda0 = 25 + 5 * np.random.random()
        intensities = 1 / np.cosh((wavelengths - 750) / lambda0)
        return wavelengths, intensities

    def integration_time_micros(self, time_micros):
        self.int_time_micros = time_micros
