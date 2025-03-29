<p align="center">
  <a href="#readme"><img alt="Force platform reader logo" src="images/force_platform_logo.png"></a>
</p>
<p align="center">
  <a href="#readme"><img alt="Python tested versions" src="https://img.shields.io/badge/python-3.10_3.11-blue?style=flat-square"></a>
  <a href="https://github.com/psf/black"><img alt="Python formatter" src="https://img.shields.io/badge/code%20style-black-000000?style=flat-square"></a>
  <a href="https://github.com/AaronPB/force-platform-app/actions/workflows/project_test.yaml"><img alt="Project test status" src="https://img.shields.io/github/actions/workflow/status/AaronPB/force-platform-app/project_test.yaml?branch=master&logo=github&label=project_test&style=flat-square"></a>
  <a href="https://aaronpb.github.io/force_platform/"><img alt="Documentation link" src="https://img.shields.io/badge/main_project_docs-available-44CC11?logo=materialformkdocs&logoColor=white&style=flat-square"></a>
  <a href="https://streamlit.io/"><img alt="Streamlit support" src="https://img.shields.io/badge/Powered_with_Streamlit-FF4B4B?logo=streamlit&logoColor=white&style=flat-square"></a>
</p>

## Information

A python software for synchronized data management of specific force platforms sensors compatible with Phidget API and other sensor types such as IMUs.

> [!note]
> This repository contains a dockerized streamlit version of the [force_platform](https://aaronpb.github.io/force_platform/) project, available on [this repository](https://github.com/AaronPB/force_platform).

This project is licensed under de GNU General Public License v3.0.

## Documentation

The documentation is available within the software, making it convenient to check out while learning how to use it. It has useful tips and internal links to the software tools.

## Simple setup

1. Install [Docker](https://docs.docker.com/engine/install/)
2. Pull the docker image from DockerHub or the GitHub Container Registry.
3. Start the container and try it out by going to the specified port.

Here is a setup example to run it locally through commands, in a Linux-based distro:

```bash
docker pull WIP
docker run -d --name example_app --device /dev/usb:/dev/usb -p 8501:8501 force-platform-app
```

And done! Check it out on [http://localhost:8501](http://localhost:8501).

> [!warning]
> It is recommended to connect the sensors before starting the container, as the container cannot detect new USB ports while running.
> Additionally, reconnecting devices during runtime may cause errors or connection failures.
>
> To avoid these issues, you can use the `--privileged` flag when running the container, though this is not recommended due to security concerns:
> ```bash
> docker run -d --name example_app --privileged -p 8501:8501 force-platform-app
> ```
