# MultiMega

Interface for a multiaccount [MEGA](https://mega.nz/) cloud service.

## Getting Started

### Prerequisites

You'll need Python 3 and a couple of MEGA accounts.

### Installation

1. Clone the repository
2. Install the Python dependencies (see *requirements.txt*)
3. Add your account to the program database with `python main.py account create` and following the procedure
4. Voilà!

### Usage

Here is a list of possible commands:

Object    | Action   | Description
--------- | -------- | -----------
`account` | `create` | Add a new account to the database
`account` | `list`   | List all accounts in the database and their quota usage
`account` | `sync`   | Manual forced files synchronization for a user
`file`    | `upload` | Upload a file
`file`    | `list`   | List all uploaded files
`file`    | `delete` | Delete an uploaded file
`file`    | `find`   | Find an uploaded file

See `python main.py [object] [action] --help` for more details.

## Mechanics

Built with [richardARPANET/mega.py](https://code.richard.do/richardARPANET/mega.py).

A folder is first zipped, renamed, and re-zipped with a password. That way, the
files AND THE FILENAMES within the folder can not be accessed without the
password, preventing any automated parsing from the file hoster. Note that other
compression protocols allow for doing this directly, though zip being the most
supported format, this way of doing ensures a large number of people will be
able to access the files.

Then files are uploaded to one of the available MEGA accounts, which returns the
download link. The program can also generate an index file gathering uploaded
files with their link, their size, and their hash. Storing hash also enables
post-download authenticity verifications.
