# File Infobar

This [Sublime Text](http://www.sublimetext.com/) plugin displays the
path and modification time of the current file in the status bar.

## Features

  * Detection and resolution of [symlinks](https://en.wikipedia.org/wiki/Symbolic_link).
  * **Toggle Relative Path** [command](FileInfobar.sublime-commands) (toggles the
    display of file paths between absolute and relative to the window's folders).
  * "Today" and "Yesterday" relative days for displaying the modification time.
  * Customisable /
    [localisable](https://en.wikipedia.org/wiki/Internationalization_and_localization)
    display (see the [settings](FileInfobar.sublime-settings)),
    including custom date / time formatting using
    [`strftime()`](https://docs.python.org/2.6/library/datetime.html#datetime.datetime.strftime).

## Compatibility

File Infobar was developed for [ST2](http://www.sublimetext.com/2), and is designed
to also be compatible with [ST3](http://www.sublimetext.com/3).

## License

File Infobar is licensed under the
[MIT License (Expat)](http://en.wikipedia.org/wiki/MIT_License).
