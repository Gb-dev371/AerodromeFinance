## Prerequisites

:warning: 
You need to have [Python](https://python.org) installed on your machine



## How to run the application :arrow_forward:

### Git clone
In the terminal, clone the project: 

```
git clone https://github.com/Gb-dev371/AerodromeFinance.git
```

### Virtual environment
Run the following command:
```
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Installing the requirements
```
pip install -r requirements.txt
```

### Adding environment variables
Next, set up your .env file with the necessary environment variables:

```bash
NODE_URL = 'your_base_node_url'
API_KEY_BASE_SCAN = 'your_api_key_of_base_scan'
```

### Running the code
```
python main.py
```
