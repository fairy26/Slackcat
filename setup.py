from setuptools import setup

setup(
    name="slackcat",
    version="1.0",
    install_requires=["pytz", "requests", "slack_sdk", "fire", "tkcalendar", "tqdm",],
    extras_requires={},
    entry_points={"console_scripts": ["slackcat=src:run",]},
    python_requires=">=3.7",
)
