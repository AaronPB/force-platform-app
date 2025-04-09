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

1. Install [Docker](https://docs.docker.com/engine/install/).
2. Pull the docker image from [DockerHub](https://hub.docker.com/r/aaronrpb/force-platform-app) or the GitHub Container Registry.
3. Start the container and try it out by going to the specified port.

> [!tip]
> Need more detailed information? Check out the setup steps for [Linux distros](https://aaronpb.github.io/force_platform/software/docker_streamlit/setup/project_linux/) or [Windows](https://aaronpb.github.io/force_platform/software/docker_streamlit/setup/project_windows/).

Here is a setup example to run it with phidgetbridge-based sensors and IMUs:

Pull the image.

```bash
docker pull aaronrpb/force-platform-app:latest
```

Create a new container called `example_app` and link the required device paths.

> Make sure you have USB sensors connected to the delivered paths in `--device`, or the daemon will throw a `no such file or directory` error.
> If you want just to check the container content without sensors, remove the `--device` options from de `docker run` command.

```bash
docker run -d --name example_app \
  --device /dev/bus/usb \
  --device /dev/ttyUSB0 \
  --device /dev/ttyUSB1 \
  -p 8501:8501 \
  aaronrpb/force-platform-app
```

And done! Check it out on [http://localhost:8501](http://localhost:8501).

> [!warning]
> It is recommended to connect the sensors before starting the container, as the container cannot detect new USB ports while running.
> Additionally, reconnecting devices during runtime may cause errors or connection failures.
>
> To avoid these issues, you can use the `--privileged` flag when running the container, though this is not recommended due to security concerns:
>
> ```bash
> docker run -d --name example_app --privileged -p 8501:8501 aaronrpb/force-platform-app
> ```

## Managing the Application

Once you run `docker run`, you can stop the app with `docker stop <container_name>` and restart it with `docker start <container_name>`.

You can algo check the app [logs](https://docs.docker.com/reference/cli/docker/container/logs/), with `docker logs <container_name>`.

More information about docker CLI commands: [https://docs.docker.com/reference/cli/docker/](https://docs.docker.com/reference/cli/docker/).
