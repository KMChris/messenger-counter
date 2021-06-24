# Messenger Counter
**Messenger Counter** is python script that counts messages from Facebook Messenger and shows various statistics.

If you are interested in contributing to this repository, pull requests are much appreciated.

To perform calculations on your messages you need to download data directly from Facebook (in JSON format).

### The most important features
##### Counter
Use `count` to count all messages and save summary to *messages.json*\
Alternatively command `chars` counts all characters and saves to *messages_chars.json*.

##### Statistics
Use `stats` to display statistics for all counted messages.\
You can specify a conversation to which apply command: `stats [conversation]`.\
Add `-c` at the end to  display detailed character statistics.

Use `user [name]` for detailed statistics for specific user.

`yearly` &mdash; displays summary and chart of messages grouped by year.\
Specify user by using `yearly [name]`.

`daily` &mdash; displays summary and chart of daily messages from the beginning of all conversations.\
Specify messages with one user by using `daily [name]`.\
Add `-d [hours]` at the end to shift the chart by the certain number of hours.

Use `hours` to show hour distribution of messages\
Specify messages with one user by using `hours [name]`.\
Add `-d [hours]` at the end to shift the chart by the certain number of hours.

Type `help` to display help prompt.\
Use `exit` to exit the program.

### How to download messages
1. Select Settings & Privacy in the top right of Facebook, then click Settings.
1. In the left column, click Your Facebook Information.
1. Click on Download Your Information.
![fb1](https://user-images.githubusercontent.com/17026216/99185953-4e075300-274d-11eb-99f1-eb475a465652.png)
1. Deselect all and select Messages category by clicking the box on the right side.
1. It is necessary to choose JSON format of your download request.
![fb2](https://user-images.githubusercontent.com/17026216/99186010-b2c2ad80-274d-11eb-8684-4077192373f0.png)
1. Click Create File to confirm the download request.
1. Facebook will notify you when your copy will be ready to download.
1. Go to the Available Files section.
1. Click Download and enter your password.

# Licence
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**Messenger Counter** is licenced under [Gnu Public Licence v3](https://www.gnu.org/licenses/gpl-3.0).
