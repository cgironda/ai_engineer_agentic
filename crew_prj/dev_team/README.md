# DevTeam Crew

Welcome to the DevTeam Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. The goal is to enable agents to collaborate effectively on complex tasks.

## Prerequisites

Mke sure you have the following installed on your system:

1. Python version 3.10 to 3.13
2. [UV](https://docs.astral.sh/uv/), for dependency management and package handling

### Installation

If you haven't already, install uv:

```bash
pip install uv
```

Navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```

## Quick Start

```bash
$ cd crew_prj/dev_team
$ uv sync
$ unset DOCKER_HOST
$ uv run --active crewai run
```

Ensure `OPENAI_API_KEY` is set in `crew_prj/dev_team/.env` before running.

### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/dev_team/config/agents.yaml` to define your agents
- Modify `src/dev_team/config/tasks.yaml` to define your tasks
- Modify `src/dev_team/crew.py` to add your own logic, tools and specific args
- Modify `src/dev_team/main.py` to add custom inputs for your agents and tasks

## Running the Project

To start your crew of AI agents and begin task execution, run this from the root folder of the project:

```bash
$ cd crew_prj/dev_team
$ uv run --active crewai run
```

This command initializes the dev_team Crew, assembles the agents, and assigns them tasks as defined in the configuration.

This unmodified example will create a `report.md` file with the output of research on LLMs in the root folder.

### Outputs

The crew writes generated artifacts to the file `output/`:

- `output/{module_name}_design.md`: Design doc for the backend module.
- `output/{module_name}`: Generated backend module.
- `output/app.py`: Gradio UI for the backend.
- `output/test_{module_name}`: Unit tests for the backend.

### Troubleshooting: Docker + Code Interpreter

If you see a Code Interpreter error about fetching the server API version, check that:

- Docker Desktop is running
- `OPENAI_API_KEY` is set in `crew_prj/dev_team/.env`
- `DOCKER_HOST` is not set to a stale socket
- The project `.venv` is active

Quick reset:

```bash
$ cd crew_prj/dev_team
$ unset DOCKER_HOST
$ uv run --active crewai run
```

## Understanding Your Crew

The dev_team Crew includes several AI agents, each with their own roles, goals, and tools. They work together on tasks listed in `config/tasks.yaml`, using their combined skills to handle complex projects. The `config/agents.yaml` file describes what each agent can do and how they are set up.

### Agents Overview

- Engineering Lead: Translates requirements into a detailed module design with class and function signatures.
- Backend Engineer: Implements the designed Python module that satisfies the requirements.
- Frontend Engineer: Creates a simple Gradio UI in `app.py` to demonstrate the backend module.
- Test Engineer: Writes unit tests for the backend module in `test_{module_name}`.

### Agent → Task Mapping

- Engineering Lead → `design_task` (writes `output/{module_name}_design.md`)
- Backend Engineer → `code_task` (writes `output/{module_name}`)
- Frontend Engineer → `frontend_task` (writes `output/app.py`)
- Test Engineer → `test_task` (writes `output/test_{module_name}`)

### Testing

After a run generates the backend and tests:

```bash
$ cd crew_prj/dev_team/output
$ python -m unittest test_accounts.py
```

### Running the UI

After a run generates `app.py`:

```bash
$ cd crew_prj/dev_team/output
$ python app.py
```

## Support

If you need help, have questions, or want to share feedback about DevTeam Crew check:
- Visit [documentation](https://docs.crewai.com)
- Reach out to [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with the docs](https://chatg.pt/DWjSBZn)