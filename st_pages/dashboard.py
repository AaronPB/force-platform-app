import streamlit as st
import pandas as pd
import time

from src.enums.configPaths import ConfigPaths

from loguru import logger


@st.fragment(run_every="1s")
def test_info(container) -> None:
    times: list = st.session_state.test_mngr.getTestTimes()
    metric_title_amount = "Test data amount"
    metric_title_time = "Test duration"
    if not times or len(times) < 2:
        with container.container():
            metric_col_1, metric_col_2 = st.columns(2)
            metric_col_1.metric(label=metric_title_time, value="00:00")
            metric_col_2.metric(label=metric_title_amount, value="0")
        return
    minutes, seconds = divmod((times[-1] - times[0]) / 1000, 60)
    with container.container():
        metric_col_1, metric_col_2 = st.columns(2)
        metric_col_1.metric(
            label=metric_title_time, value=f"{int(minutes):02}:{int(seconds):02}"
        )
        metric_col_2.metric(label=metric_title_amount, value=len(times))


def control_panel():
    # Variables states
    if "butter_fs_value" not in st.session_state:
        st.session_state.butter_fs_value = float(
            1000
            / st.session_state.config_mngr.getConfigValue(
                ConfigPaths.RECORD_INTERVAL_MS.value, 100
            )
        )
    if "butter_fc_value" not in st.session_state:
        # wn bounds: 0 < wn < 1
        # wn = fc / (0.5*fs)
        st.session_state.butter_fc_value = float(
            (st.session_state.butter_fs_value - 0.02) / 2
        )
    if "butter_order_value" not in st.session_state:
        st.session_state.butter_order_value = 6

    # Load page
    st.subheader("Control panel")

    test_unavailable = not st.session_state.test_mngr.getSensorConnected()
    if test_unavailable:
        st.warning(
            "Need to connect sensors! Go to the settings page.",
            icon=":material/offline_bolt:",
        )

    if st.session_state.get("btn_test_start", False):
        st.session_state.test_recording = True
    elif st.session_state.get("btn_test_stop", False):
        st.session_state.test_recording = False

    panel_col_1, panel_col_2, panel_col_3 = st.columns(3)
    btn_test_start = panel_col_1.button(
        label="Start test",
        key="btn_test_start",
        type="primary",
        use_container_width=True,
        disabled=test_unavailable or st.session_state.test_recording,
    )
    btn_test_stop = panel_col_2.button(
        label="Stop test",
        key="btn_test_stop",
        type="primary",
        use_container_width=True,
        disabled=test_unavailable or not st.session_state.test_recording,
    )
    btn_test_tare = panel_col_3.button(
        label="Tare sensors",
        key="btn_test_tare",
        type="secondary",
        use_container_width=True,
        disabled=test_unavailable or not st.session_state.test_recording,
    )

    # Test information
    test_status = st.empty()

    test_details_col_1, test_details_col_2 = st.columns(2, gap="large")
    test_metrics_container = test_details_col_1.empty()
    auto_stop_col_1, auto_stop_col_2 = test_details_col_2.columns(
        2, vertical_alignment="bottom"
    )

    auto_stop_col_1.toggle(
        label="Auto stop test",
        value=False,
        key="test_toggle_auto_stop",
        disabled=st.session_state.test_recording,
    )
    auto_stop_time = auto_stop_col_2.number_input(
        label="After specified seconds",
        min_value=1.0,
        max_value=6000.0,
        value=3.0,
        disabled=not st.session_state.test_toggle_auto_stop
        or st.session_state.test_recording,
    )

    if st.session_state.test_recording:
        if st.session_state.test_toggle_auto_stop:
            test_status.info(
                f"A current test is running! The test will end automatically in **{auto_stop_time} seconds**."
                + " Do NOT leave this page during the test recording.",
                icon=":material/motion_photos_auto:",
            )
        else:
            test_status.info(
                "A current test is running! Click on **Stop test** when finished.",
                icon=":material/play_circle:",
            )

    if btn_test_start:
        st.session_state.test_mngr.testStart(
            st.session_state.config_mngr.getConfigValue(
                ConfigPaths.RECORD_INTERVAL_MS.value, 100
            )
        )
    if btn_test_stop:
        st.session_state.test_mngr.testStop()
        st.session_state.data_mngr.loadData(
            st.session_state.test_mngr.getTestTimes(),
            st.session_state.sensor_mngr.getGroups(only_available=True),
        )
        st.session_state.data_mngr.applyButterFilter(
            st.session_state.butter_fs_value,
            st.session_state.butter_fc_value,
            st.session_state.butter_order_value,
        )
    if btn_test_tare:
        amount = st.session_state.config_mngr.getConfigValue(
            ConfigPaths.RECORD_TARE_AMOUNT.value, 300
        )
        interval_ms = st.session_state.config_mngr.getConfigValue(
            ConfigPaths.RECORD_INTERVAL_MS.value, 100
        )
        st.session_state.test_mngr.tareSensors(
            st.session_state.sensor_mngr, amount, interval_ms
        )

    # Update test duration and data amount
    test_info(test_metrics_container)

    # Show/download dataframes
    dataframes = [pd.DataFrame(), pd.DataFrame(), pd.DataFrame()]
    if not st.session_state.test_recording:
        dataframes = [
            st.session_state.data_mngr.getCalibrateDataframe(),
            st.session_state.data_mngr.getFilteredDataframe(),
            st.session_state.data_mngr.getRawDataframe(),
        ]

    st.subheader("Recorded data")
    file_name = st.text_input(
        label="Test name",
        value=st.session_state.config_mngr.getConfigValue(
            ConfigPaths.TEST_NAME.value, "Test"
        ),
        help="Set a file name for the downloaded file.",
    )
    if file_name:
        st.session_state.config_mngr.setConfigValue(
            ConfigPaths.TEST_NAME.value, file_name
        )
    df_tabs = st.tabs(["Calibrated data", "Filtered data", "Raw data"])
    file_suffixes = ["_CALIBRATED", "_FILTERED", "_RAW"]
    for i, df in enumerate(dataframes):
        with df_tabs[i]:
            if df.empty:
                st.error(
                    "There is no data recorded. Start a test!",
                    icon=":material/report:",
                )
                st.button(
                    label="Download CSV",
                    key=f"btn_download_df_{i}",
                    # use_container_width=True,
                    help="Download the following dataframe in CSV format.",
                    disabled=True,
                )
                st.dataframe(
                    data=pd.DataFrame({"timestamp": [0], "sensor_data": [0]}),
                    use_container_width=True,
                )
                continue
            st.download_button(
                label="Download CSV",
                key=f"btn_download_df_{i}",
                icon=":material/download:",
                data=df.to_csv(index=False).encode("utf-8"),
                mime="text/csv",
                file_name=f"{file_name+file_suffixes[i]}.csv",
                help="Download the following dataframe in CSV format.",
            )
            st.dataframe(data=df, use_container_width=True)

    # If auto stop test is enabled, add stop process to a thread
    if st.session_state.test_toggle_auto_stop and st.session_state.test_recording:
        time.sleep(auto_stop_time)
        st.session_state.test_mngr.testStop()
        st.session_state.data_mngr.loadData(
            st.session_state.test_mngr.getTestTimes(),
            st.session_state.sensor_mngr.getGroups(only_available=True),
        )
        st.session_state.data_mngr.applyButterFilter(
            st.session_state.butter_fs_value,
            st.session_state.butter_fc_value,
            st.session_state.butter_order_value,
        )
        st.session_state.test_recording = False
        st.rerun()


def data_visualization():
    # Variables states
    if "butter_fs_value" not in st.session_state:
        st.session_state.butter_fs_value = float(
            1000
            / st.session_state.config_mngr.getConfigValue(
                ConfigPaths.RECORD_INTERVAL_MS.value, 100
            )
        )
    if "butter_fc_value" not in st.session_state:
        # wn bounds: 0 < wn < 1
        # wn = fc / (0.5*fs)
        st.session_state.butter_fc_value = float(
            (st.session_state.butter_fs_value - 0.02) / 2
        )
    if "butter_order_value" not in st.session_state:
        st.session_state.butter_order_value = 6

    st.subheader("Data visualization")

    sensor_options = st.session_state.data_mngr.getSensorFigureOptions()
    platform_options = st.session_state.data_mngr.getPlatformFigureOptions()

    with st.expander("Figure and filter settings", icon=":material/dataset:"):
        settings_col_1, settings_col_2 = st.columns(2)
        settings_col_1.subheader("Recorded data")
        figure_type = settings_col_1.radio(
            label="Figure type",
            options=["Sensor", "Platform"],
            captions=["Individual sensors", "A force platform"],
            horizontal=True,
        )
        if figure_type == "Sensor":
            figure_option = settings_col_1.selectbox(
                label="Select sensor",
                options=sensor_options,
                index=None,
                placeholder="Choose a sensor",
            )
        else:
            figure_option = settings_col_1.selectbox(
                label="Select platform",
                options=platform_options,
                index=None,
                placeholder="Choose a platform",
            )
        settings_col_2.subheader("Butterworth filter")
        butter_col_1, butter_col_2 = settings_col_2.columns(2)
        butter_fs = butter_col_1.number_input(
            label="Sampling rate (Hz)",
            key="number_input_butter_fs",
            value=float(
                1000
                / st.session_state.config_mngr.getConfigValue(
                    ConfigPaths.RECORD_INTERVAL_MS.value, 100
                )
            ),  # Reading frequency: f = 1/t
            disabled=True,
        )
        # Check if butter_fc is out of bounds, if butter_fs has been modified
        fs_value = st.session_state.butter_fc_value
        if (butter_fs - 0.01) < fs_value:
            fs_value = float((butter_fs - 0.02) / 2)
        butter_fc = butter_col_2.number_input(
            label="Cutoff frequency (Hz)",
            key="number_input_butter_fc",
            min_value=1.0,
            max_value=butter_fs - 0.01,  # Max rate: f = 1/t - 0.01
            value=fs_value,
        )
        butter_order = settings_col_2.number_input(
            label="Filter order",
            key="number_input_butter_order",
            min_value=2,
            max_value=6,
            value=st.session_state.butter_order_value,
        )
        if (
            butter_fs != st.session_state.butter_fs_value
            or butter_fc != st.session_state.butter_fc_value
            or butter_order != st.session_state.butter_order_value
        ):
            logger.debug(
                f"Editing Butterworth filter with: fs={butter_fs} Hz, fc={butter_fc} Hz and order={butter_order}"
            )
            st.session_state.butter_fs_value = butter_fs
            st.session_state.butter_fc_value = butter_fc
            st.session_state.butter_order_value = butter_order
            st.session_state.data_mngr.applyButterFilter(
                butter_fs, butter_fc, butter_order
            )

    # Generate figure with selected option
    if figure_type == "Sensor":
        st.plotly_chart(st.session_state.data_mngr.getSensorFigure(figure_option))
    else:
        st.plotly_chart(st.session_state.data_mngr.getPlatformFigure(figure_option))
