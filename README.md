# Messenger Counter

![Dependency status](https://img.shields.io/librariesio/github/kmchris/messenger-counter?style=flat-square)
![PyPI version](https://img.shields.io/pypi/v/messenger-counter?style=flat-square)
![PyPI downloads](https://img.shields.io/pypi/dm/messenger-counter?style=flat-square)

**Messenger Counter** is a python script that counts messages from Facebook Messenger and shows various statistics.

If you are interested in contributing to this repository, pull requests are much appreciated.

Note: To use this software you need to download your data directly from Facebook (in JSON format).
[How to download my data?](https://github.com/KMChris/messenger-counter#how-to-download-messages)

## Installation 

```shell
pip install messenger-counter
```

## CLI usage

1. Run the following command to open CLI. You can provide path to .zip file (or extracted folder) as an argument.
```shell
python -m mc facebook-YourName.zip
```
2. Wait for `>` to appear and use following commands for different statistics (examples below)
```shell
>command [options]
```
Available commands:
* `count [mcw] [s]` &mdash; Counts messages, characters and words. 
  You can use `s` to save data to .json file.
* `stats [converstion] [-c]` &mdash; Displays statistics for counted messages.
  You can specify conversation for detailed statistics
  and use -c for character statistics.
* `user [name]` &mdash; Detailed statistics for specific person
* `yearly [conversation]` &mdash; Number of messages per year.
  You can specify conversation for more precise statistics. 
* `daily [conversation]` &mdash; Number of messages daily.
* `hours [conversation]` &mdash; Average number of messages
  by hour throughout the day.

## Examples

Show general statistics of all conversations
```shell
stats
```

Show messages statistics for specific conversation.
(you can list all conversations by running previous example) 
```shell
stats JohnDoe
```

Program allows you to write only the beginning of the conversation name.
It will return first matching occurrence. (Works exactly as the previous example)
```shell
stats Joh
```

Shows how many messages did the person send grouped by conversation.
```shell
user "John Doe"
```

Shows how many messages on average have you send and received grouped by time of the day.
```shell
daily
```

Similar to previous one, but limited to one conversation.
```shell
daily John
```

## Basic module usage

Get started:

```python
import counter as mc

# Available soon
```

## How to download messages

1. Select Settings & Privacy in the top right of Facebook, then click Settings.
1. In the left column, click Your Facebook Information.
1. Click on Download Your Information.
![fb1](https://user-images.githubusercontent.com/17026216/99185953-4e075300-274d-11eb-99f1-eb475a465652.png)
1. Deselect all and select "Messages" category by clicking the box on the right side.
1. It is necessary to choose JSON format of your download request.
![fb2](https://user-images.githubusercontent.com/17026216/99186010-b2c2ad80-274d-11eb-8684-4077192373f0.png)
1. Click Create File to confirm the download request.
1. Facebook will notify you when your copy will be ready to download.
1. Go to the Available Files section.
1. Click Download and enter your password.

# Licence
![Licence](https://img.shields.io/github/license/kmchris/messenger-counter?style=flat-square)

**Messenger Counter** is licenced under [MIT Licence](https://opensource.org/licenses/MIT).
