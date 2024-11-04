import streamlit as st
from st_pages import home, settings, dashboard

from src.managers.configManager import ConfigManager
from src.managers.sensorManager import SensorManager
from src.managers.testManager import TestManager
from src.managers.dataManager import DataManager


def main():
    # Global session states
    # - Managers
    if "config_mngr" not in st.session_state:
        st.session_state.config_mngr = ConfigManager()
    if "sensor_mngr" not in st.session_state:
        st.session_state.sensor_mngr = SensorManager()
        st.session_state.sensor_mngr.setup(st.session_state.config_mngr)
    if "test_mngr" not in st.session_state:
        st.session_state.test_mngr = TestManager()
    if "data_mngr" not in st.session_state:
        st.session_state.data_mngr = DataManager()
    # - Status
    if "test_available" not in st.session_state:
        st.session_state.test_available = False
    if "test_recording" not in st.session_state:
        st.session_state.test_recording = False

    # Page configuration
    st.set_page_config(
        page_title="Force Platform Reader",
        page_icon="images/app_icon.png",
        # layout="wide",
        initial_sidebar_state="expanded",
    )

    # Logo
    st.logo(
        image="images/app_logo.png",
        icon_image="images/app_icon.png",
        link="https://github.com/AaronPB",
    )

    # Pages
    # - Home page
    home_pg = st.Page(
        home.homePage,
        title="Home",
        icon=":material/home:",
    )
    # - Settings pages
    config_stgs_pg = st.Page(
        settings.config_settings,
        title="Configuration file",
        icon=":material/description:",
    )
    sensor_stgs_pg = st.Page(
        settings.sensor_settings,
        title="Sensor management",
        icon=":material/tune:",
    )
    # - Dashboard pages
    control_panel_pg = st.Page(
        dashboard.control_panel,
        title="Control panel",
        icon=":material/monitor:",
    )
    data_visualization_pg = st.Page(
        dashboard.data_visualization,
        title="Data visualization",
        icon=":material/ssid_chart:",
    )
    pg = st.navigation(
        {
            "Force Platform Reader": [home_pg],
            "Settings": [config_stgs_pg, sensor_stgs_pg],
            "Dashboard": [control_panel_pg, data_visualization_pg],
        }
    )
    pg.run()


if __name__ == "__main__":
    main()
