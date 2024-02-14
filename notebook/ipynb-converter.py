import os
import jupytext

file_path = os.path.dirname(__file__)

source_name = 'app'
source = jupytext.read(os.path.join(file_path, f'{source_name}.py'))
jupytext.write(source, os.path.join(file_path, f'{source_name}.ipynb'), fmt='.ipynb')
