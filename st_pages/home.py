import streamlit as st
import pandas as pd

from st_pages import settings, dashboard


def generalSensorsDocs() -> None:
    st.subheader(":material/code_blocks: Configure compatible sensors", divider="blue")
    st.markdown(
        """
        There are three available sensor types:
        - **Loadcells**: all sensors that are compatible with the [PhidgetBridge 4-input](https://www.phidgets.com/?tier=3&catid=98&pcid=78&prodid=1027) device.
        - **Encoders**: all sensors that are compatible with the [PhidgetEncoder HighSpeed 4-input](https://www.phidgets.com/?tier=3&catid=4&pcid=2&prodid=1199) device.
        - **IMUs**: the current version only supports [Taobotics IMUs](https://www.taobotics.com/).
        All sensors are defined in a global settings file, in `YAML` format, called the **configuration file**.
        
        To load compatible sensors within the software, the sensor needs to be defined into the `sensors` configuration section, 
        and be listed into a valid **sensor group**, in the `sensor_groups` configuration section.
        """
    )
    st.info(
        "Go to the :material/upload_file: **Load a custom configuration file** expander to get more information about configuration sections and required parameters for each sensor.",
        icon=":material/info:",
    )
    st.markdown(
        """
        ### Customize the default configuration file
        
        It is possible to make a different set of sensors and sensor_groups, uploading a modified `config.yaml` file to the app
        in the :material/description: **Configuration file** page.
        """
    )
    st.page_link(
        st.Page(
            settings.config_settings,
            title="Click here to go to the :material/description: **configuration file** page",
        )
    )
    st.info(
        "You can download the current configuration file by clicking at the :material/document_scanner: **Configuration file information** expander.",
        icon=":material/info:",
    )
    with open("config.yaml", "r") as file:
        config_file = file.read()
    st.download_button(
        label="Or download the default config file",
        key="download_btn_default_config",
        type="secondary",
        use_container_width=True,
        file_name="config.yaml",
        help="Download the default config file to customize it",
        data=config_file,
        mime="text/yaml",
    )
    st.subheader(":material/discover_tune: Enable and connect sensors", divider="blue")
    st.write(
        "Once the configuration file has loaded successfully, go to the :material/tune: **sensor management** page to handle and connect the loaded sensors."
    )
    st.page_link(
        st.Page(
            settings.sensor_settings,
            title="Click here to go to the :material/tune: **sensor management** page",
        )
    )
    st.markdown(
        """
        You can enable and disable sensors and sensor groups from the loaded configuration file, marking or unmarking the corresponding checkbox.
        - **Enable a sensor**: The app will attempt to connect to this sensor, at the specified `serial` (and `channel` if needed) in the configuration file.
        - **Disable a sensor**: The sensor will be ignored. This means the app will not attempt a connection with the sensor.
        - **Enable a sensor group**: The app will try to connect only to enabled sensors. Disabled sensors inside an enabled sensor group are still ignored.
        - **Disable a sensor group**: The complete sensor list will be ignored, avoiding connection attempts even if there are enabled sensors.
        """
    )
    st.warning(
        "All sensors inside a disabled sensor group will be ignored.",
        icon=":material/warning:",
    )
    st.markdown(
        """
        Click the `Connect sensors` button in order to check the enabled sensors connections.
        Once the connection check is done, the tab list below will update with the new sensor status.
        """
    )
    st.subheader(":material/check_circle: Check sensor status", divider="blue")
    st.write(
        "Each sensor can have one out of the following status, depending on the connection results."
    )
    st.dataframe(
        pd.DataFrame(
            {
                "Status": ["Ignored", "Not found", "Available"],
                "Description": [
                    "No connection attempted.",
                    "Connection could not be established.",
                    "Connection successfully established.",
                ],
            }
        ),
        hide_index=True,
        use_container_width=True,
    )
    st.info(
        "To be able to preform tests, at least one sensor must be available.",
        icon=":material/info:",
    )


def generalTestDocs() -> None:
    st.subheader(":material/tune: Adjust the test settings", divider="blue")
    st.write(
        "Verify the loaded configuration file and its parameters are set accordingly in the :material/description: **configuration file** page."
    )
    st.page_link(
        st.Page(
            settings.config_settings,
            title="Click here to go to the :material/description: **configuration file** page",
        )
    )
    st.dataframe(
        pd.DataFrame(
            {
                "Option": ["Recording interval", "Tare amount"],
                "Min value": [10, 10],
                "Max value": [1000, 500],
                "Description": [
                    "Timeframe between each data recording in milliseconds.",
                    "Amount of values to be taken for sensor new intercepts.",
                ],
            }
        ),
        hide_index=True,
        use_container_width=True,
    )
    st.info(
        "When settings are modified, the changes are also saved in the configuration file.",
        icon=":material/info:",
    )
    st.subheader(
        ":material/conversion_path: Connect and check your sensors", divider="blue"
    )
    st.write(
        "Connect the desired sensors also in the :material/tune: **sensor management** page. Check their connection status are `Available`."
    )
    st.page_link(
        st.Page(
            settings.sensor_settings,
            title="Click here to go to the :material/tune: **sensor management** page",
        )
    )
    st.warning(
        "To be able to preform tests, at least one sensor must be available.",
        icon=":material/warning:",
    )
    st.subheader(":material/play_circle: Start a test", divider="blue")
    st.write(
        "Once sensors are connected, move to the :material/monitor: **control panel** page to start the test."
    )
    st.page_link(
        st.Page(
            dashboard.control_panel,
            title="Click here to go to the :material/monitor: **control panel** page",
        )
    )
    st.markdown(
        """
        There are three self-explanatory buttons at the top of the page: 
        - **Start test**: run a new test with available sensors.
        - **Stop test**: stop a current test.
        - **Tare sensors**: update intercept parameters of `SENSOR_LOADCELL` and `SENSOR_ENCODER` sensor types.
        
        When starting a new test, stop test and tare buttons will be enabled. An information box will also appear below.
        """
    )
    with st.popover("Information box"):
        st.info(
            "A current test is running! Click on **Stop test** when finished.",
            icon=":material/play_circle:",
        )
    st.markdown(
        """
        Each sensor data is recorded in separate threads.
        The record process is also driven in a thread, which handles all sensor threads in a synchronous way, using barriers.
        """
    )
    st.info(
        "When recording, you can still move to other pages in the app. "
        + "Modifying test or sensors settings during a test recording is **not recommended**. It may affect data post-processing.",
        icon=":material/info:",
    )
    st.markdown(
        """
        #### Tare sensors
        You can tare `SENSOR_LOADCELL` and `SENSOR_ENCODER` sensor types, once a test has started.
        The tare process goes as follows. Let $b$ be the new intercept, $b_0$ the previous intercept, 
        $V_f(t)$ the recorded sensor values by a given timeframe $(t)$, and $m$ the sensor slope.
        """
    )
    st.latex(
        r"""
        b = b_0 - \text{mean}\left(m \cdot V_f(t) + b_0\right)
        """
    )
    st.write(
        "The new intercept value will be saved in the configuration file and used into the data post-processing."
    )
    st.markdown(
        """
        #### Enable automatic stop test
        It is also possible to enable an automatic stop trigger after certain time.
        Enable the toggle below the control panel buttons, and define the desired recording time in seconds.

        When starting a new test in **auto stop** mode, stop test and tare buttons **will not be enabled**. A different information box will also appear below.
        """
    )
    with st.popover("Information box in auto stop mode"):
        st.info(
            f"A current test is running! The test will end automatically in **5.00 seconds**."
            + " Do NOT leave this page during the test recording.",
            icon=":material/motion_photos_auto:",
        )
    st.warning(
        "When recording with **auto stop test** enabled, you **cannot** move to other pages in the app, tare or manually stop the test. "
        + "If you move to other pages, the automatic stop will be disabled, having to stop the running test manually.",
        icon=":material/warning:",
    )
    st.subheader(":material/stop_circle: Stop a test", divider="blue")
    st.markdown(
        """
        To finish a test, click on the **stop test** button. The test manager will wait the test thread to complete, so it could have some delay.
        When stopped, the recorded data will be processed, filtered with a Butterworth filter and stored in dataframes.

        This dataframes can be checked and downloaded in the **Recorded data** section, below the control panel buttons.

        At the top, the test name can be changed. This will be the name of the`.csv` file, when downloaded.

        Below this option, there are three tabs showing different dataframe types:
        - **Raw data**: A dataframe with the recorded values without any post-processings.
        - **Calibrated data**: This dataframe applies the calibration params to `SENSOR_LOADCELL` and `SENSOR_ENCODER` sensor types, using a linear approach: $y = m \cdot x + b$
        - **Filtered data**: It is a filtered version of the **calibration data**, using a Butterworth filter.
        """
    )
    st.info(
        "The Butterworh filter params can be modified in the :material/ssid_chart: **data visualization** page.",
        icon=":material/info:",
    )
    st.markdown(
        """
        Depending on the selected tab, the downloaded file will have an extra suffix indicating the data type: `_RAW`, `_CALIBRATED` or `_FILTERED`.

        Also, the filtered data can be shown as figures, going to the :material/ssid_chart: **data visualization** page.
        """
    )
    st.page_link(
        st.Page(
            dashboard.control_panel,
            title="Click here to go to the :material/ssid_chart: **data visualization** page",
        )
    )
    st.info(
        "For more information about sensor and platform figures, read the :material/bar_chart: **Check and visualize the results** expander below.",
        icon=":material/info:",
    )


def configDetails() -> None:
    with open("config.yaml", "r") as file:
        config_file = file.read()
    st.download_button(
        label="Download the default config file",
        key="download_button_default_config",
        type="secondary",
        use_container_width=True,
        file_name="config.yaml",
        help="Download the default config file to customize it",
        data=config_file,
        mime="text/yaml",
    )
    st.subheader("Configuration structure")
    st.markdown(
        """
        The configuration file follows a certain structure in order to be loaded correctly.
        
        - All sensors must be defined under the `sensors` configuration section.
        - To register data from a sensor, its `id` needs to be included in a `sensor_list` of a defined sensor group, under the `sensor_groups` configuration section.
        """
    )
    st.warning(
        "Sensors that are not included in a `sensor_list` are ignored and not loaded.",
        icon=":material/warning:",
    )
    st.info(
        "There are some requirements for certain sensor and group types. Check the info below.",
        icon=":material/info:",
    )
    code_config_struct = """
        %YAML 1.2.2
        general_settings:
          config:
            name: Custom config
            version: 2.0
          test:
            name: Test name
          recording:
            data_interval_ms: 10
            tare_data_amount: 300
          filter:
            fc_hz: 5.00
            order: 6
        sensor_groups:
          group_id:
            name: Group name
            type: GROUP_TYPE
            read: true
            sensor_list: [sensor_id]
        sensors:
          sensor_id:
            name: Sensor name
            type: SENSOR_TYPE
            read: true
            connection:
              channel: 0
              serial: path/to/usb
            properties: []
            calibration:
              slope: 1
              intercept: 0
        """
    st.code(code_config_struct, language="yaml")
    # Sensor types
    st.subheader("Sensor types")
    sensor_tab_loadcell, sensor_tab_encoder, sensor_tab_imu = st.tabs(
        ["`SENSOR_LOADCELL`", "`SENSOR_ENCODER`", "`SENSOR_IMU`"]
    )
    ## Loadcell sensors
    sensor_loadcell_col_1, sensor_loadcell_col_2 = sensor_tab_loadcell.columns(2)
    sensor_loadcell_col_1.markdown(
        """
        #### Section example
        ```yaml
        name: P1_LoadCell_Z_1
        type: SENSOR_LOADCELL
        read: true
        connection:
          channel: 0
          serial: 583477
        properties: []
        calibration:
          slope: 1460645.82
          intercept: 0
        ```
        """
    )
    sensor_loadcell_col_2.markdown(
        """
        #### Compatible sensors
        All sensors that are compatible with the [PhidgetBridge 4-input](https://www.phidgets.com/?tier=3&catid=98&pcid=78&prodid=1027).
        It has been tested with the following sensors:
        - [Zemic L6P Planar Load Cell](https://www.zemiceurope.com/es/categories/celulas-de-carga/l6p.html) (main sensors).
        - [Phidgets S-Type Load Cell](https://www.phidgets.com/?tier=3&catid=9&pcid=7&prodid=229)
        - [Phidgets Single Point Load Cell](https://www.phidgets.com/?tier=3&catid=9&pcid=7&prodid=226)
        """
    )
    sensor_tab_loadcell.write("Required keys information:")
    sensor_tab_loadcell.dataframe(
        pd.DataFrame(
            {
                "Key": [
                    "name",
                    "type",
                    "read",
                    "connection.channel",
                    "connection.serial",
                    "properties",
                    "calibration.slope",
                    "calibration.intercept",
                ],
                "Type": [
                    "STRING",
                    "STRING",
                    "BOOL",
                    "INT",
                    "INT",
                    "LIST",
                    "INT",
                    "INT",
                ],
                "Description": [
                    "Sensor name.",
                    "Sensor type: SENSOR_LOADCELL.",
                    "Enable or disable sensor data recording. Can be modified in GUI.",
                    "Channel number (0 to 3) in Phidget device.",
                    "USB serial number of Phidget device.",
                    "(Could be empty) Configuration section to provide more information.",
                    "Slope parameter.",
                    "Intercept parameter.",
                ],
            }
        ),
        hide_index=True,
        use_container_width=True,
    )
    ## Encoder sensors
    sensor_encoder_col_1, sensor_encoder_col_2 = sensor_tab_encoder.columns(2)
    sensor_encoder_col_1.markdown(
        """
        #### Section example
        ```yaml
        name: Encoder_Z_1
        type: SENSOR_ENCODER
        read: true
        connection:
          channel: 0
          serial: 641800
        initial_position: 0
        properties: []
        calibration:
          slope: 0.01875
          intercept: 0.0
        ```
        """
    )
    sensor_encoder_col_2.markdown(
        """
        #### Compatible sensors
        All sensors that are compatible with the [PhidgetEncoder HighSpeed 4-input](https://www.phidgets.com/?tier=3&catid=4&pcid=2&prodid=1199).
        
        It has been tested with the following sensors:
        - [Draw Wire Encoder](https://www.phidgets.com/?prodid=1001) (main sensors).
        """
    )
    sensor_tab_encoder.write("Required keys information:")
    sensor_tab_encoder.dataframe(
        pd.DataFrame(
            {
                "Key": [
                    "name",
                    "type",
                    "read",
                    "connection.channel",
                    "connection.serial",
                    "initial_position",
                    "properties",
                    "calibration.slope",
                    "calibration.intercept",
                ],
                "Type": [
                    "STRING",
                    "STRING",
                    "BOOL",
                    "INT",
                    "INT",
                    "INT",
                    "LIST",
                    "INT",
                    "INT",
                ],
                "Description": [
                    "Sensor name.",
                    "Sensor type: SENSOR_ENCODER.",
                    "Enable or disable sensor data recording. Can be modified in GUI.",
                    "Channel number (0 to 3) in Phidget device.",
                    "USB serial number of Phidget device.",
                    "The initial value of the encoder state if it provides incremental values.",
                    "(Could be empty) Configuration section to provide more information.",
                    "Slope parameter.",
                    "Intercept parameter.",
                ],
            }
        ),
        hide_index=True,
        use_container_width=True,
    )
    ## IMU sensors
    sensor_imu_col_1, sensor_imu_col_2 = sensor_tab_imu.columns(2)
    sensor_imu_col_1.markdown(
        """
        #### Section example
        ```yaml
        name: IMU_Leg_Right
        type: SENSOR_IMU
        read: true
        connection:
          serial: /dev/ttyUSB0
        properties:
          tag: IMU_1
        ```
        """
    )
    sensor_imu_col_2.markdown(
        """
        #### Compatible sensors
        The current version only supports [Taobotics IMUs](https://www.taobotics.com/).
        """
    )
    sensor_tab_imu.write("Required keys information:")
    sensor_tab_imu.dataframe(
        pd.DataFrame(
            {
                "Key": ["name", "type", "read", "connection.serial", "properties"],
                "Type": ["STRING", "STRING", "BOOL", "STRING", "LIST"],
                "Description": [
                    "Sensor name.",
                    "Sensor type: SENSOR_IMU.",
                    "Enable or disable sensor data recording. Can be modified in GUI.",
                    "USB path. Use: `ll /dev/serial/by-path/` to assure symlinks to ttyUSB, if provided.",
                    "(Could be empty) Configuration section to provide more information.",
                ],
            }
        ),
        hide_index=True,
        use_container_width=True,
    )
    st.subheader("Sensor group types")
    group_tab_default, group_tab_platform = st.tabs(
        ["`GROUP_DEFAULT`", "`GROUP_PLATFORM`"]
    )
    ## Default group
    group_default_col_1, group_default_col_2 = group_tab_default.columns(2)
    group_default_col_1.markdown(
        """
        #### Section example
        ```yaml
        name: Body IMUs
        type: GROUP_DEFAULT
        read: true
        sensor_list:
        - imu_1
        - imu_2
        - imu_3
        ```
        """
    )
    group_default_col_2.markdown(
        """
        #### Group description
        This group can be defined with multiple sensors from different types.
        """
    )
    group_tab_default.dataframe(
        pd.DataFrame(
            {
                "Key": ["name", "type", "read", "sensor_list"],
                "Type": ["STRING", "STRING", "BOOL", "LIST"],
                "Description": [
                    "Group name.",
                    "Group type: GROUP_DEFAULT.",
                    "Enable or disable entire group data recording. Can be modified in GUI.",
                    "A string list of sensor IDs, declared in the sensors section.",
                ],
            }
        ),
        hide_index=True,
        use_container_width=True,
    )
    ## Platform group
    group_platform_col_1, group_platform_col_2 = group_tab_platform.columns(2)
    group_platform_col_1.markdown(
        """
        #### Section example
        ```yaml
        name: Platform 1
        type: GROUP_PLATFORM
        read: true
        sensor_list:
        - p1_z1
        - p1_z2
        - p1_z3
        - p1_z4
        - p1_x1
        - p1_x2
        - p1_x3
        - p1_x4
        - p1_y1
        - p1_y2
        - p1_y3
        - p1_y4
        ```
        """
    )
    group_platform_col_1.warning(
        "Less sensors could be defined, with the specified key strings. In that case, **COP graphs** are not available.",
        icon=":material/warning:",
    )
    group_platform_col_1.error(
        "If sensor names does not include key strings, **total forces** and **COP graphs** are not available. The sensor group will be treated as a default one.",
        icon=":material/error:",
    )
    group_platform_col_2.markdown(
        """
        #### Group description
        Configure a platform with the `GROUP_PLATFORM` type. This group type only expects  `SENSOR_LOADCELL` type sensors, with a maximum of 12 (4 sensors on each axis).
        To obtain platform graphs such as **total forces** or **COP values**; sensors must have the following strings included in their names:
        - The 4 X-axis sensors: `_X_n`.
        - The 4 Y-axis sensors: `_Y_n`.
        - The 4 Z-axis sensors: `_Z_n`.
        Being $n = \{1, 2, 3, 4\}$ depending on the sensor location in the platform:
        """
    )
    group_platform_col_2.image(
        image="images/platform.png",
        caption="Platform sensor locations",
        use_container_width=True,
    )
    group_tab_platform.dataframe(
        pd.DataFrame(
            {
                "Key": ["name", "type", "read", "sensor_list"],
                "Type": ["STRING", "STRING", "BOOL", "LIST"],
                "Description": [
                    "Group name.",
                    "Group type: GROUP_PLATFORM.",
                    "Enable or disable entire group data recording. Can be modified in GUI.",
                    "A string list of sensor IDs, declared in the sensors section.",
                ],
            }
        ),
        hide_index=True,
        use_container_width=True,
    )


def figureDetails() -> None:
    st.subheader("Sensor and sensor groups figures")
    st.markdown(
        """
        The software provides graphical data visualization. There are two types:
        - Sensor figures: individual sensor data display. There are some figures, such as IMU data, which contains grouped data.
        - Sensor group figures: these figures are build depending on the group context.
        For instance, a `PLATFORM_GROUP` sensor group offers two figure types: global forces and COP displacement.
        """
    )
    st.subheader("Customize the figures")
    st.markdown(
        """
        Thanks to `plotly` [configuration options](https://plotly.com/python/configuration-options/),
        you can zoom into a specific range and even include extra forms such as rectangles, circles or free lines
        (credit to [Juan Miguel Serrano](https://github.com/juan11iguel)).
        Check out the available options at the modebar, at the upper-right corner of the figure.
        """
    )
    st.subheader("Export the generated figures")
    st.markdown(
        """
        Above the figure you can modify the file export name and format. To export it, clic the :material/photo_camera: camera option in the figure modebar, at the upper-right corner.
        """
    )


def homePage():
    _, img_col, _ = st.columns([0.2, 0.6, 0.2])
    img_col.image(
        image="images/force_platform_logo.png",
        use_container_width=True,
    )
    st.title("Welcome to Force Platform Reader")
    st.write(
        "Check the following documentation if you are not familiar with the application."
    )
    with st.expander("About the software", icon=":material/privacy_tip:"):
        st.markdown(
            f"""
            This app is made by [AaronPB](https://github.com/AaronPB) with streamlit version {st.__version__}, 
            under the [3-Clause BSD](https://opensource.org/license/bsd-3-clause) 
            and [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.html) licenses.

            A preliminary version of this software with QT (for Linux distros only) can be installed, going to the  
            [force_platform](https://github.com/AaronPB/force_platform) public repository.
            """
        )

    st.header("General overview")

    with st.expander("Connect sensors", icon=":material/cable:"):
        generalSensorsDocs()

    with st.expander("Run a test", icon=":material/play_circle:"):
        generalTestDocs()

    st.header("Settings")

    with st.expander("Load a custom config file", icon=":material/upload_file:"):
        configDetails()

    st.header("Dashboard")

    with st.expander("Check and visualize the results", icon=":material/bar_chart:"):
        figureDetails()
