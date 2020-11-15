# Messenger Counter
**Messenger Counter** is python script that counts messages from Facebook Messenger and shows various statistics.

### The most important features:
##### Counter
Use `count` to count all messages and save summary to *messages.json*\
Alternatively command `chars` counts all characters and saves to *messages_chars.json*

##### Statistics
Use `stats` to display statistics for all counted messages.\
You can specify a conversation to which apply command: `stats [conversation]`.\
Add `-c` at the end to  display detailed character statistics.

Use `user [name]` for detailed statistics for specific user.

`yearly` – displays summary and chart of messages grouped by year.\
Specify user by using `yearly [name]`.

`daily` – displays summary and chart of daily messages from the beginning of all conversations.\
Specify messages with one user by using `daily [name]`.\
Add `-h` at the end to shift the chart by the certain number of hours.

Use `hours [name, -h]` to show hour distribution of messages\
          specific user, hours difference\
Type `help` to display help prompt.\
Use `exit` to exit the program.

# Licence
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**Messenger Counter** is licenced under [Gnu Public Licence v3](https://www.gnu.org/licenses/gpl-3.0).
