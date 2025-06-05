---
description: Create a config file with env variables
---

# Objective

Create a config.py file in which all variables from .env file are imported to be used along the project.

Rules:
- Don't create the config.py if the .env file doesn't exist.
- If the .env file exists, use the variables inse of it to create the config.py file
- Make sure that variables are being loaded from the .env file and not from the operating system environment
- While installing the python-dotenv package using UV, please add it to the pyproject.toml