## Install Dependencies

> NOTE: 
> 1. Python >=3.10 is required.
> 2. All scripts in the repository are dependent on the following dependencies. If you want to run the scripts/jupyter notebooks in this repository, you need to install all dependencies first. In addition, you need to specify the python kernel in the jupyter notebook to the python environment you created when running a jupyter notebook in this repository.

We assume that you have download/clone this repository to your local machine. If not, please download/clone this repository to your local machine first.

```bash
# Clone the repository
git clone https://github.com/open-prophetdb/biomedgps-data

cd biomedgps-data
```

We recommend you to use [virtualenv](https://virtualenv.pypa.io/en/latest/) or [conda](https://docs.conda.io/en/latest/) to install the dependencies. If you don't have virtualenv or conda installed, you can install them by following the instructions in the official document.

```
# [Option 1] Install the dependencies with virtualenv
virtualenv -p python3 .env
source .env/bin/activate

# [Option 2] Install the dependencies with conda
conda create -n biomedgps-data python=3.10
conda activate biomedgps-data

# Install the dependencies
pip install -r requirements.txt
```
