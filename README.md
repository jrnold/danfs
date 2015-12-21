# Dictionary of American Naval Fighting Ships (DANFS)

Code to download data from the [Dictionary of American Naval Fighting Ships](http://www.history.navy.mil/research/histories/ship-histories/danfs.html) to a sqlite database.

Running
```shell
$ python danfs.py
```
creates a sqlite3 database named `danfs.sqlite3` with two tables: `danfs_ships` with all ships in the [DANFS](http://www.history.navy.mil/research/histories/ship-histories/danfs.html), and `confederate_ships` with all ships in the [Confederate ships](http://www.history.navy.mil/research/histories/ship-histories/confederate_ships.html) histories.

# Download

You can download a SQLite version of the DANFS database from https://s3.amazonaws.com/data.jrnold.me/danfs/danfs.sqlite3 .

