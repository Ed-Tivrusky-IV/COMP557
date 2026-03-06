# Hello Triangle and Hello Monkey

This is a set of bare-bones moderngl examples that can be used to understand how to draw geometry and apply simple transformations to geometry.

## Setup

Recommended to install [Anaconda3](https://www.anaconda.com/download), and start anaconda prompt with administrator privileges to be able to install modules.  

You should use a *clean* environment to help you avoid problems!  Create and activate an [environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment) specific to this course with the following commands, and note that you will be able to tell vscode (or your IDE of preference) to use this environment.  Use python 3.10 for best compatibility.

	conda create --name comp557f25 python=3.10
	conda activate comp557f24

Install required modules (may in future provide a requirements file with version numbers):

	python -m pip install moderngl
	python -m pip install PyQt5
	python -m pip install trimesh
