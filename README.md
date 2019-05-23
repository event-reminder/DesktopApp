## Event Reminder

##### Desktop application which helps to finish all tasks in time.

### Download an Application
You can try this app on your computer, install `Python3` and after success, run the next command:
```bash
$ pip install erdesktop
```

### Development

To start with this project (development), run the following:
```bash
# create a virtual environment if required
$ virtualenv -p python3 venv
$ source venv/bin/activate

# Install requirements and run the server
$ pip install -r requirements.txt

# if running on Windows machine:
$ pip install -r windows_requirements.txt

$ make resources
$ python ./erdesktop/app_main.py
```

#### Author:
[Yuriy Lisovskiy](https://github.com/YuriyLisovskiy)

#### License
This project is licensed under the GNU General Public License, Version 3 software license - see the [LICENSE](LICENSE) file for details.
