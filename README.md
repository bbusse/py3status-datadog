# py3status-datadog
A [py3status](https://github.com/ultrabug/py3status) module for querying Datadog metrics and monitors

## Installation
### py3status
[Install py3status](https://ultrabug.github.io/py3status/user-guide/installation/)
```
# Debian / Ubuntu / macOS / Fedora / FreeBSD
$ apt/brew/dnf/pkg install py3status
# Alpine
$ apk add py3status
```
### py3status-datadog
Clone the repository
```
$ git clone https://github.com/bbusse/py3status-datadog
```
Copy module file to a module folder recognised by py3status
```
$ mkdir -p ~/.config/py3status/modules
$ cp src/py3status-datadog/datadog.py ~/.config/py3status/modules/
```

## Usage
Like any py3status module, py3status-datadog can be tested standalone
```
$ python src/py3status-datadog/datadog.py
```

## Resources
[py3status](https://github.com/ultrabug/py3status)  
[py3status docs](https://py3status.readthedocs.io/en/latest/)  
[py3status Installation](https://ultrabug.github.io/py3status/user-guide/installation/)  
[Datadog](https://www.datadoghq.com/)  
[Datadog API](https://docs.datadoghq.com/api/latest/)
