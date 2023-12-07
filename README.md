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

1. Count your messages using (insert path for your .zip file)
```shell
python -m mc count "facebook-YourName.zip"
```
2. Add flag `--chars` or `-c` to count characters (optional)
```shell
python -m mc count -c "facebook-YourName.zip"
```
3. Use following commands for different statistics (examples below)
```shell
python -m mc [-h] command [options]
```
Available commands:
* `count [-c] file` &mdash; Counts all messages/characters and saves
  to _messages.json_ or _messages_chars.json_ file.
* `stats [-c] [converstion]` &mdash; Displays statistics for counted messages.
  You can specify conversation for detailed statistics
  and use -c for character statistics.
* `user name` &mdash; Detailed statistics for specific person
* `yearly file [conversation]` &mdash; Number of messages per year.
  (please specify path to .zip file as for counting messages)
  You can specify conversation for more precise statistics. 
* `daily [-d DIFF] file [conversation]` &mdash; Number of messages daily.
  (use `-d` or `--difference` flag to time shift by some number
  of hours and show statistics differently)
* `hours [-d DIFF] file [conversation]` &mdash; Average number of messages
  by hour throughout the day. (additional options as above)

## Examples

Show general statistics of all conversations
```shell
python -m mc stats
```

Show messages statistics for specific conversation.
(you can list all conversations by running previous example) 
```shell
python -m mc stats JohnDoe
```

Program allows you to write only the beginning of the conversation name.
It will return first matching occurrence. (Works exactly as the previous example)
```shell
python -m mc stats Joh
```

Shows how many messages did the person send grouped by conversation.
```shell
python -m mc user "John Doe"
```

Shows how many messages on average have you send and received grouped by time of the day.
```shell
python -m mc daily "facebook-YourName.zip"
```

Similar to previous one, but limited to one conversation.
```shell
python -m mc daily "facebook-YourName.zip" John
```

## Basic module usage

Get started:

```python
import counter as mc

mc.set_source('facebook-YourName.zip') # insert path for your .zip file
mc.count()
mc.count('chars', save=True)
data = mc.get_data()
mc.statistics(*data)
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
