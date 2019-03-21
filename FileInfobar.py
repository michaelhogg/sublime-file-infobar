# @author  Michael Hogg
# @license MIT
# @see     github.com/michaelhogg/sublime-file-infobar


import datetime  # docs.python.org/2.6/library/datetime.html
import os        # docs.python.org/2.6/library/os.html

import sublime         # sublimetext.com/docs/2/api_reference.html#sublime
import sublime_plugin  # sublimetext.com/docs/2/api_reference.html#sublime_plugin


# @type {bool}
relativePathEnabled = True


# Get the plugin's settings.
#
# @return {sublime.Settings}
# @see    sublimetext.com/docs/2/api_reference.html#sublime -- load_settings()
# @see    sublimetext.com/docs/2/api_reference.html#sublime.Settings
def getPluginSettings():

    return sublime.load_settings('FileInfobar.sublime-settings')


# An extended version of datetime.strftime().
# Python only guarantees it to support the format codes from the 1989 C standard.
# This function implements the following additional format codes from other standards:
#    %e   Day of the month (range 1 to 31) without a leading 0
#    %l   Hour (12-hour clock: range 1 to 12) without a leading 0
#    %P   Lowercase "am" or "pm" (or a corresponding string for the current locale)
#
# @param  {datetime.datetime} dt
# @param  {unicode}           format
# @return {str}
# @see    docs.python.org/2.6/library/datetime.html#datetime.datetime.strftime
# @see    docs.python.org/2.6/library/datetime.html#strftime-and-strptime-behavior
# @see    linux.die.net/man/3/strftime
def extendedStrftime(dt, format):

    day  = dt.strftime('%d').lstrip('0')
    hour = dt.strftime('%I').lstrip('0')
    ampm = dt.strftime('%p').lower()

    format = format.replace('%e', day)
    format = format.replace('%l', hour)
    format = format.replace('%P', ampm)

    return dt.strftime(format)


# @param  {datetime.datetime} dt
# @return {unicode}
# @see    docs.python.org/2.6/library/datetime.html#datetime.datetime.today
# @see    docs.python.org/2.6/library/datetime.html#timedelta-objects
def formatDatetime(dt):

    settings = getPluginSettings()

    dateFormatString = settings.get('date_format_string', '%a %e %b %Y')
    timeFormatString = settings.get('time_format_string', '%l:%M:%S %P')

    today     = datetime.datetime.today()
    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)

    todayString     = extendedStrftime(today,     dateFormatString)
    yesterdayString = extendedStrftime(yesterday, dateFormatString)

    dateString = extendedStrftime(dt, dateFormatString)
    dateString = dateString.replace(todayString,     settings.get('today',     'Today'))
    dateString = dateString.replace(yesterdayString, settings.get('yesterday', 'Yesterday'))

    timeString = extendedStrftime(dt, timeFormatString)

    return dateString + ' @ ' + timeString


# This command can be executed by the user (see the FileInfobar.sublime-commands file).
#
# @see sublimetext.com/docs/2/api_reference.html#sublime_plugin.WindowCommand
class FileInfobarToggleRelativePathCommand(sublime_plugin.WindowCommand):

    # @param {FileInfobar.FileInfobarToggleRelativePathCommand} self
    # @see   sublimetext.com/docs/2/api_reference.html#sublime_plugin.WindowCommand -- run()
    def run(self):

        global relativePathEnabled

        relativePathEnabled = not relativePathEnabled

        if relativePathEnabled == True:
            sublime.status_message('<File Infobar: relative path enabled>')
        else:
            sublime.status_message('<File Infobar: relative path disabled>')

        self.window.run_command('file_infobar_render')


# @see sublimetext.com/docs/2/api_reference.html#sublime_plugin.EventListener
class FileInfobarEventListener(sublime_plugin.EventListener):

    # Called when a view gains input focus.
    #
    # @param {FileInfobar.FileInfobarEventListener} self
    # @param {sublime.View}                         view
    # @see   sublimetext.com/docs/2/api_reference.html#sublime_plugin.EventListener -- on_activated()
    def on_activated(self, view):

        # Only render the Infobar if the view is contained in a window (false when creating a new file)
        if view.window() != None:
            view.window().run_command('file_infobar_render')

    # Called after a view has been saved.
    #
    # @param {FileInfobar.FileInfobarEventListener} self
    # @param {sublime.View}                         view
    # @see   sublimetext.com/docs/2/api_reference.html#sublime_plugin.EventListener -- on_post_save()
    def on_post_save(self, view):

        view.window().run_command('file_infobar_render')


# @see sublimetext.com/docs/2/api_reference.html#sublime_plugin.WindowCommand
class FileInfobarRenderCommand(sublime_plugin.WindowCommand):

    # @param  {FileInfobar.FileInfobarRenderCommand} self
    # @param  {unicode}                              path
    # @return {unicode}
    def formatPath(self, path):

        windowFolders = self.window.folders()

        if relativePathEnabled == True:
            if len(windowFolders) == 1:
                folderPath = windowFolders[0] + os.sep  # docs.python.org/2.6/library/os.html#os.sep
                path       = path.replace(folderPath, '', 1)
            else:
                for folderPath in windowFolders:
                    folderName = os.path.split(folderPath)[1]  # docs.python.org/2.6/library/os.path.html#os.path.split
                    path       = path.replace(folderPath, folderName, 1)

        userHomeDirectory = os.path.expanduser('~')  # docs.python.org/2.6/library/os.path.html#os.path.expanduser

        if userHomeDirectory != '~':  # If expansion of ~ succeeded
            path = path.replace(userHomeDirectory, '~', 1)

        return path

    # @param {FileInfobar.FileInfobarRenderCommand} self
    # @see   sublimetext.com/docs/2/api_reference.html#sublime_plugin.WindowCommand -- run()
    def run(self):

        settings = getPluginSettings()
        view     = self.window.active_view()
        filePath = view.file_name()

        if filePath == None:  # For example, when viewing a new unsaved file
            return

        markerStringFilepathStart = settings.get('filepath_start_marker', '[[ ')
        markerStringFilepathEnd   = settings.get('filepath_end_marker',   ' ]]')
        markerStringSymlink       = settings.get('symlink_marker',        '-->')
        statusBarKey              = settings.get('status_bar_key',        'zFileInfobar')

        # Unix timestamp of last modification
        # docs.python.org/2.6/library/os.path.html#os.path.getmtime
        fileModUnixTimestamp = os.path.getmtime(filePath)

        # docs.python.org/2.6/library/datetime.html#datetime.datetime.fromtimestamp
        fileModDTLocal = datetime.datetime.fromtimestamp(fileModUnixTimestamp)

        fileModFormatted  = formatDatetime(fileModDTLocal)
        filePathFormatted = self.formatPath(filePath)

        if os.path.islink(filePath):                        # docs.python.org/2.6/library/os.path.html#os.path.islink
            symlinkTarget     = os.path.realpath(filePath)  # docs.python.org/2.6/library/os.path.html#os.path.realpath
            symlinkTarget     = self.formatPath(symlinkTarget)
            filePathFormatted = filePathFormatted + ' ' + markerStringSymlink + ' ' + symlinkTarget

        filePathFormatted = markerStringFilepathStart + filePathFormatted + markerStringFilepathEnd

        # "The value will be displayed in the status bar, in a comma separated list of all status values, ordered by key."
        # sublimetext.com/docs/2/api_reference.html#sublime.View -- set_status()
        view.set_status(statusBarKey, fileModFormatted + ' ' + filePathFormatted)
