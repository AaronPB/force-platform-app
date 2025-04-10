import streamlit as st
import pandas as pd

from src.enums.sensorTypes import STypes
from src.handlers.sensorGroup import SensorGroup
from src.enums.configPaths import ConfigPaths

from loguru import logger


def connectSensors():
    st.session_state.sensor_connection_available = False
    with st.spinner("Connecting sensors..."):
        st.session_state.test_mngr.checkConnection(
            st.session_state.sensor_mngr.getGroups()
        )
    st.session_state.sensor_connection_available = True


def newConfigFile(file_path: str):
    pass


def config_settings():
    st.subheader("Configuration file")

    file_upload = st.file_uploader(
        label="Load a custom configuration file",
        type=".yaml",
        accept_multiple_files=False,
        help="The app will update all sensors and general settings with the new custom configuration.",
    )
    if file_upload is not None:
        st.session_state.config_mngr.updateCustomConfig(file_upload)
        st.session_state.sensor_mngr.setup(st.session_state.config_mngr)

    with st.expander(
        "Configuration file information", icon=":material/document_scanner:"
    ):
        st.write("File name")
        file_info_col_1, file_info_col_2 = st.columns(2, vertical_alignment="bottom")
        file_info_col_1.text_input(
            label="File name",
            value=st.session_state.config_mngr.getConfigValue(
                ConfigPaths.CONFIG_NAME.value, "Default file"
            ),
            disabled=True,
            label_visibility="collapsed",
        )
        config_file_name = "config.yaml"
        if st.session_state.config_mngr.isCustomConfig():
            with open("custom.yaml", "r") as file:
                config_file = file.read()
            config_file_name = "custom_config.yaml"
        else:
            with open("config.yaml", "r") as file:
                config_file = file.read()
        file_info_col_2.download_button(
            label="Download file",
            type="secondary",
            use_container_width=True,
            file_name=config_file_name,
            help="Download the configuration file",
            data=config_file,
            mime="text/yaml",
        )

        st.write("Loaded sensors")
        st.info(
            "For more information, go to the :material/tune: **Sensor management** page.",
            icon=":material/info:",
        )
        sensor_groups: list[SensorGroup] = st.session_state.sensor_mngr.getGroups()
        if not sensor_groups:
            st.error(
                "There is no sensor group information available!",
                icon=":material/report:",
            )
        else:
            sensors_info: dict[str, list[int]] = {}
            for group in sensor_groups:
                sensors_info[group.getName()] = [
                    len(group.getSensors(sensor_type=STypes.SENSOR_LOADCELL)),
                    len(group.getSensors(sensor_type=STypes.SENSOR_ENCODER)),
                    len(group.getSensors(sensor_type=STypes.SENSOR_IMU)),
                ]
            sensors_df = pd.DataFrame(
                {
                    "Sensor group": list(sensors_info.keys()),
                    "Load cells": [
                        sensor_info[0] for sensor_info in sensors_info.values()
                    ],
                    "Encoders": [
                        sensor_info[1] for sensor_info in sensors_info.values()
                    ],
                    "IMUs": [sensor_info[2] for sensor_info in sensors_info.values()],
                }
            )
            st.dataframe(sensors_df, use_container_width=True, hide_index=True)

    # Test settings
    st.subheader("Test settings")
    config_col_1, config_col_2 = st.columns(2)
    config_tare = config_col_1.number_input(
        label="Tare amount",
        key="number_input_tare_amount",
        min_value=10,
        max_value=500,
        value=st.session_state.config_mngr.getConfigValue(
            ConfigPaths.RECORD_TARE_AMOUNT.value, 300
        ),
        step=1,
        help="Number of values to be taken to tare sensors.",
    )
    if config_tare:
        st.session_state.config_mngr.setConfigValue(
            ConfigPaths.RECORD_TARE_AMOUNT.value, config_tare
        )
    config_interval = config_col_2.number_input(
        label="Record interval (ms)",
        key="number_input_record_freq",
        min_value=10,
        max_value=1000,
        value=st.session_state.config_mngr.getConfigValue(
            ConfigPaths.RECORD_INTERVAL_MS.value, 100
        ),
        step=1,
        help="Timeframe between registered values in milliseconds.",
    )
    if config_interval:
        st.session_state.config_mngr.setConfigValue(
            ConfigPaths.RECORD_INTERVAL_MS.value, config_interval
        )


def sensor_settings():
    if "sensor_connection_available" not in st.session_state:
        # TODO Maybe False if there are errors with config loads?
        st.session_state.sensor_connection_available = True

    if st.session_state.get("btn_sensor_connect", False):
        st.session_state.sensor_connection_available = False

    st.subheader("Sensor management")

    connect_col_1, connect_col_2 = st.columns(2)
    connect_sensors_btn = connect_col_1.button(
        label="Connect sensors",
        key="btn_sensor_connect",
        type="primary",
        disabled=not st.session_state.sensor_connection_available,
    )
    if connect_sensors_btn:
        connectSensors()
        st.rerun()
    if st.session_state.test_mngr.getSensorConnected():
        connect_col_2.success("Sensors connected!", icon=":material/check_circle:")
    else:
        connect_col_2.warning(
            "Need to connect sensors!", icon=":material/offline_bolt:"
        )

    sensor_groups = st.session_state.sensor_mngr.getGroups()
    if not sensor_groups:
        st.error(
            "There is no sensor group information available!", icon=":material/report:"
        )
    elif len(sensor_groups) == 1:
        group = sensor_groups[0]
        df = pd.DataFrame(
            {
                "ID": [sensor.getID() for sensor in group.getSensors().values()],
                "Connect": [sensor.getRead() for sensor in group.getSensors().values()],
                "Name": [sensor.getName() for sensor in group.getSensors().values()],
                "Type": [
                    sensor.getType().value for sensor in group.getSensors().values()
                ],
                "Status": [
                    sensor.getStatus().value for sensor in group.getSensors().values()
                ],
            }
        )
        st.toggle(
            label="Disable entire sensor group",
            key=f"group_toggle",
            value=not group.getRead(),
            help="Ignores and does not connect to enabled sensors of this group.",
        )
        if group.getRead() == st.session_state[f"group_toggle"]:
            st.session_state.sensor_mngr.setSensorRead(
                not group.getRead(), group.getID()
            )
            st.rerun()
        edited_df = st.data_editor(
            data=df,
            key=f"edited_df",
            use_container_width=True,
            hide_index=True,
            column_order=("Connect", "Name", "Type", "Status"),
            disabled=("Name", "Type", "Status"),
        )
        changed_sensors = df[df["Connect"] != edited_df["Connect"]]
        if not changed_sensors.empty:
            for index, row in changed_sensors.iterrows():
                st.session_state.sensor_mngr.setSensorRead(
                    not row["Connect"], group.getID(), row["ID"]
                )
            st.rerun()
        return

    tab_names = [group.getName() for group in sensor_groups]
    tabs = st.tabs(tab_names)
    for i, group in enumerate(sensor_groups):
        df = pd.DataFrame(
            {
                "ID": [sensor.getID() for sensor in group.getSensors().values()],
                "Connect": [sensor.getRead() for sensor in group.getSensors().values()],
                "Name": [sensor.getName() for sensor in group.getSensors().values()],
                "Type": [
                    sensor.getType().value for sensor in group.getSensors().values()
                ],
                "Status": [
                    sensor.getStatus().value for sensor in group.getSensors().values()
                ],
            }
        )
        with tabs[i]:
            st.toggle(
                label="Disable entire sensor group",
                key=f"group_toggle_{i}",
                value=not group.getRead(),
                help="Ignores and does not connect to enabled sensors of this group.",
            )
            if group.getRead() == st.session_state[f"group_toggle_{i}"]:
                st.session_state.sensor_mngr.setSensorRead(
                    not group.getRead(), group.getID()
                )
                st.rerun()
            edited_df = st.data_editor(
                data=df,
                key=f"edited_df_{i}",
                use_container_width=True,
                hide_index=True,
                column_order=("Connect", "Name", "Type", "Status"),
                disabled=("Name", "Type", "Status"),
            )
            changed_sensors = df[df["Connect"] != edited_df["Connect"]]
            if not changed_sensors.empty:
                for index, row in changed_sensors.iterrows():
                    st.session_state.sensor_mngr.setSensorRead(
                        not row["Connect"], group.getID(), row["ID"]
                    )
                st.rerun()
