# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from scipy.spatial.transform import Rotation
from scipy.signal import butter, filtfilt

from src.figures.generalFigure import GeneralFigure
from src.figures.platformFigures import PlatformForcesFigure, PlatformCOPFigure
from src.handlers import SensorGroup, Sensor

from src.enums.sensorTypes import SGTypes, STypes
from src.enums.sensorStatus import SGStatus

from loguru import logger


class DataManager:
    def __init__(self):
        # Time
        self.timestamp_list: list = []
        self.timeincr_list: list = []
        # Data frames
        self.df_raw: pd.DataFrame = pd.DataFrame()
        self.df_calibrated: pd.DataFrame = pd.DataFrame()
        self.df_filtered: pd.DataFrame = pd.DataFrame()
        # Data structures for figures
        self.sensor_figure_structs: dict[str, tuple[list[str], str]] = {}
        self.platform_figure_structs: dict[
            str, tuple[list[str], list[str], list[str]]
        ] = {}
        # Sensor header suffixes
        self.imu_ang_headers: list[str] = ["qx", "qy", "qz", "qw"]
        self.imu_vel_headers: list[str] = ["wx", "wy", "wz"]
        self.imu_acc_headers: list[str] = ["x_acc", "y_acc", "z_acc"]
        # Platform loadcell required strings for platform figures
        self.platform_fx_names: list[str] = ["X_1", "X_2", "X_3", "X_4"]
        self.platform_fy_names: list[str] = ["Y_1", "Y_2", "Y_3", "Y_4"]
        self.platform_fz_names: list[str] = ["Z_1", "Z_2", "Z_3", "Z_4"]

    def clearDataFrames(self) -> None:
        self.df_raw: pd.DataFrame = pd.DataFrame()
        self.df_calibrated: pd.DataFrame = pd.DataFrame()
        self.df_filtered: pd.DataFrame = pd.DataFrame()

    # Data load methods

    def loadData(self, time_list: list, sensor_groups: list[SensorGroup]) -> None:
        self.clearDataFrames()
        self.timestamp_list = time_list
        self.timeincr_list = [(t - time_list[0]) / 1000 for t in time_list]
        for group in sensor_groups:
            # Check group status
            if not group.getRead():
                continue
            if group.getStatus() == SGStatus.ERROR:
                continue
            # Check if group is a platform for specific plots
            if group.getType() == SGTypes.GROUP_PLATFORM:
                valid_sensors = self.getPlatformGroupValidSensors(group)
                if any(len(sensor_forces) > 0 for sensor_forces in valid_sensors):
                    self.platform_figure_structs[group.getName() + "_FORCES"] = (
                        valid_sensors
                    )
                # Check 2 Fx, 2 Fy and 4 Fz sensors available for valid COP
                if (
                    len(valid_sensors[0]) == 2
                    and len(valid_sensors[1]) == 2
                    and len(valid_sensors[2]) == 4
                ):
                    self.platform_figure_structs[group.getName() + "_COP"] = (
                        valid_sensors
                    )
            # Store available sensor data from group
            for sensor in group.getSensors(only_available=True).values():
                if sensor.getType() == STypes.SENSOR_IMU:
                    values_list = self.getListedData(sensor)
                    for i, suffix in enumerate(
                        self.imu_ang_headers
                        + self.imu_vel_headers
                        + self.imu_acc_headers
                    ):
                        imu_name = sensor.getName() + "_" + suffix
                        self.df_raw[imu_name] = values_list[i]
                        # No need to calibrate IMUs
                        self.df_calibrated[imu_name] = values_list[i]
                    # Store imu structures for figures. Could be done inside the previous for loop for better performance.
                    self.sensor_figure_structs[sensor.getName() + "_ANGLES"] = (
                        [
                            sensor.getName() + "_" + suffix
                            for suffix in self.imu_ang_headers
                        ],
                        "Angle (deg)",
                    )
                    self.sensor_figure_structs[sensor.getName() + "_VELOCITIES"] = (
                        [
                            sensor.getName() + "_" + suffix
                            for suffix in self.imu_vel_headers
                        ],
                        "Angular velocity (deg/s)",
                    )
                    self.sensor_figure_structs[sensor.getName() + "_ACCELERATIONS"] = (
                        [
                            sensor.getName() + "_" + suffix
                            for suffix in self.imu_acc_headers
                        ],
                        "Linear acceleration (m/s2)",
                    )
                    continue
                self.df_raw[sensor.getName()] = sensor.getValues()
                slope = sensor.getSlope()
                intercept = sensor.getIntercept()
                self.df_calibrated[sensor.getName()] = [
                    value * slope + intercept for value in sensor.getValues()
                ]
                # Store into figure option
                units = "Force (N)"
                if sensor.getType() == STypes.SENSOR_ENCODER:
                    units = "Displacement (mm)"
                self.sensor_figure_structs[sensor.getName()] = (
                    [sensor.getName()],
                    units,
                )

    # Transforms values lists into separate variable lists.
    # Ex: [ti [gx, gy, gz]] -> [gx[ti], gy[ti], gz[ti]]
    def getListedData(self, sensor: Sensor) -> list[list[float]]:
        main_list = sensor.getValues()
        new_main_list: list[list[float]] = [[] for _ in range(len(main_list[0]))]
        for value_list in main_list:
            for i, value in enumerate(value_list):
                new_main_list[i].append(value)
        return new_main_list

    def isRangedPlot(self, idx1: int, idx2: int) -> bool:
        if idx1 != 0 or idx2 != 0:
            if idx2 > idx1 and idx1 >= 0 and idx2 <= len(self.df_filtered):
                return True
        return False

    def getPlatformGroupValidSensors(
        self, group: SensorGroup
    ) -> tuple[list[str], list[str], list[str]]:
        fx_sensors = []
        fy_sensors = []
        fz_sensors = []
        sensors = group.getSensors(
            only_available=True, sensor_type=STypes.SENSOR_LOADCELL
        ).values()
        if not sensors:
            return ([], [], [])
        for sensor in sensors:
            if any(name in sensor.getName() for name in self.platform_fx_names):
                fx_sensors.append(sensor.getName())
            elif any(name in sensor.getName() for name in self.platform_fy_names):
                fy_sensors.append(sensor.getName())
            elif any(name in sensor.getName() for name in self.platform_fz_names):
                fz_sensors.append(sensor.getName())
        return (fx_sensors, fy_sensors, fz_sensors)

    # Getters

    def getDataSize(self) -> int:
        return len(self.df_raw)

    def getSensorFigureOptions(self) -> list[str]:
        return self.sensor_figure_structs.keys()

    def getPlatformFigureOptions(self) -> list[str]:
        return self.platform_figure_structs.keys()

    def getRawDataframe(self, idx1: int = 0, idx2: int = 0) -> pd.DataFrame:
        return self.formatDataframe(self.df_raw.copy(deep=True), idx1, idx2)

    def getCalibrateDataframe(self, idx1: int = 0, idx2: int = 0) -> pd.DataFrame:
        return self.formatDataframe(self.df_calibrated.copy(deep=True), idx1, idx2)

    def getFilteredDataframe(self, idx1: int = 0, idx2: int = 0) -> pd.DataFrame:
        return self.formatDataframe(self.df_filtered.copy(deep=True), idx1, idx2)

    def formatDataframe(
        self, df: pd.DataFrame, idx1: int = 0, idx2: int = 0
    ) -> pd.DataFrame:
        timestamp = self.timestamp_list.copy()
        if self.isRangedPlot(idx1, idx2):
            timestamp = timestamp[idx1:idx2]
            df = df.iloc[idx1:idx2]
        # Format dataframe values to 0.000000e+00
        df = df.map("{:.6e}".format)
        # Add timestamp values
        df.insert(0, "timestamp", timestamp)
        return df

    # Data process methods

    # ButterWorth filter
    def applyButterFilter(self, fs: float = 100, fc: float = 5, order: int = 6):
        b, a = butter(order, fc / (0.5 * fs), btype="low", analog=False)
        self.df_filtered = pd.DataFrame()
        for col in self.df_calibrated:
            self.df_filtered[col] = filtfilt(b, a, self.df_calibrated[col])

    # - Sensor specific methods

    def getIMUAngles(self, headers: list[str]) -> pd.DataFrame:
        # Get dataframe and sensor name
        df_quat = self.df_filtered[headers]
        sensor_name = ""
        for suffix in self.imu_ang_headers:
            if headers[0].endswith(f"_{suffix}"):
                sensor_name = headers[0].replace(f"_{suffix}", "")
                break

        rot = Rotation.from_quat(df_quat.to_numpy())
        euler_ang_deg = np.degrees(rot.as_euler("xyz"))

        df_euler = pd.DataFrame(
            euler_ang_deg,
            columns=[
                sensor_name + "_yaw",
                sensor_name + "_pitch",
                sensor_name + "_roll",
            ],
        )

        return df_euler

    # - Platform group methods

    def getPlatformCOP(
        self, df_fx: pd.DataFrame, df_fy: pd.DataFrame, df_fz: pd.DataFrame
    ) -> tuple[pd.Series, pd.Series]:
        # Platform dimensions
        lx = 506  # mm
        ly = 306  # mm
        h = 50.6  # mm
        # Get sum forces
        fx = df_fx.iloc[:, 0] - df_fx.iloc[:, 1]
        fy = df_fy.iloc[:, 0] - df_fy.iloc[:, 1]
        fz = df_fz.sum(axis=1)
        # Operate
        mx = (
            ly
            / 2
            * (
                -df_fz.iloc[:, 0]
                - df_fz.iloc[:, 1]
                + df_fz.iloc[:, 2]
                + df_fz.iloc[:, 3]
            )
            + h * fy
        )
        my = (
            lx
            / 2
            * (
                df_fz.iloc[:, 0]
                - df_fz.iloc[:, 1]
                - df_fz.iloc[:, 2]
                + df_fz.iloc[:, 3]
            )
            - h * fx
        )
        # Get COP
        cop_x = -my / fz
        cop_y = mx / fz
        # Get relative COP
        cop_x = cop_x - np.mean(cop_x)
        cop_y = cop_y - np.mean(cop_y)
        return [cop_x, cop_y]

    def getEllipseFromCOP(
        self, cop: tuple[pd.Series, pd.Series]
    ) -> tuple[pd.Series, pd.Series, float]:

        cov_matrix = np.cov(cop[0], cop[1])

        # Eigen vectors and angular rotation
        D, V = np.linalg.eig(cov_matrix)
        theta = np.arctan2(V[1, 0], V[0, 0])

        ellipse_axis = np.sqrt(D)

        # Ellipse params
        a = ellipse_axis[0]
        b = ellipse_axis[1]
        area = np.pi * a * b / 100  # In cm2
        x0 = np.mean(cop[0])
        y0 = np.mean(cop[1])

        # Ellipse coords
        phi = np.linspace(0, 2 * np.pi, 100)
        x = x0 + a * np.cos(phi) * np.cos(theta) - b * np.sin(phi) * np.sin(theta)
        y = y0 + a * np.cos(phi) * np.sin(theta) + b * np.sin(phi) * np.cos(theta)

        return pd.Series(x), pd.Series(y), area

    # Figure getters
    def getSensorFigure(self, sensor_name: str = None) -> go.Figure:
        if sensor_name is None:
            return GeneralFigure("Sensor figure", "Not specified").getFigure(
                pd.Series([0]), pd.Series([0])
            )
        if sensor_name not in self.getSensorFigureOptions():
            logger.error(
                f"There is no sensor data tagged as {sensor_name}! Return empty figure."
            )
            return GeneralFigure("Sensor figure", "Not specified").getFigure(
                pd.Series([0]), pd.Series([0])
            )

        # Build dataframe
        df = self.df_filtered[self.sensor_figure_structs[sensor_name][0]]
        if "_ANGLES" in sensor_name:
            # Extra process to get angle values
            df = self.getIMUAngles(self.sensor_figure_structs[sensor_name][0])

        # Build figure
        figure = GeneralFigure(
            f"Figure of {sensor_name}", self.sensor_figure_structs[sensor_name][1]
        )
        return figure.getFigure(df, pd.Series(self.timeincr_list))

    def getPlatformFigure(self, platform_name: str = None) -> go.Figure:
        if platform_name is None:
            return GeneralFigure("Platform figure", "Not specified").getFigure(
                pd.Series([0]), pd.Series([0])
            )
        if platform_name not in self.getPlatformFigureOptions():
            logger.error(
                f"There is no platform data tagged as {platform_name}! Return empty figure."
            )
            return GeneralFigure("Platform figure", "Not specified").getFigure(
                pd.Series([0]), pd.Series([0])
            )
        keys_tuple = self.platform_figure_structs[platform_name]
        df_fx = self.df_filtered[keys_tuple[0]]
        df_fy = self.df_filtered[keys_tuple[1]]
        df_fz = self.df_filtered[keys_tuple[2]]
        if platform_name.endswith("_COP"):
            [copx, copy] = self.getPlatformCOP(df_fx, df_fy, df_fz)
            [ellipx, ellipy, area] = self.getEllipseFromCOP([copx, copy])
            figure = PlatformCOPFigure(f"Platform figure {platform_name}")
            return figure.getFigure(copx, copy, ellipx, ellipy, area)
        if platform_name.endswith("_FORCES"):
            figure = PlatformForcesFigure(f"Platform figure {platform_name}")
            return figure.getFigure(df_fx, df_fy, df_fz, pd.Series(self.timeincr_list))
