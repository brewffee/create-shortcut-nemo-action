#! /usr/bin/python3 -OOt
#
# Usage: main.py '[target_file]'
#
# This script was originally designed to be run only when given a target file,
# but has been adapted to be run without a target file.
#
# Bugs are to be expected.

import mimetypes
import os
import shutil

import gi

gi.require_version("Gtk", "3.0")

# Get command line arguments
from sys import argv

from gi.repository import Gtk
from PIL import Image


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Create Launcher")
        self.set_resizable(False)
        self.set_border_width(16)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Create the content boxes
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.add(vbox)

        hbox = Gtk.Box(spacing=16)
        vbox.pack_start(hbox, True, True, 0)

        lbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        hbox.pack_start(lbox, True, True, 0)

        cbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16, margin_left=36)
        hbox.pack_start(cbox, True, True, 0)

        rbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        rbox.set_size_request(456, -1)
        hbox.pack_end(rbox, True, True, 0)

        # Create a label for type
        typeLabel = Gtk.Label()
        typeLabel.set_markup("<b>Type:</b>")
        typeLabel.set_halign(Gtk.Align.END)

        # Create a type combo box
        typeCombo = Gtk.ComboBoxText()

        # Disable until full support is added
        typeCombo.set_sensitive(False)
        typeCombo.set_tooltip_text("(Coming soon) Select the type of launcher you want to create")

        typeCombo.append_text("Application")
        typeCombo.append_text("Link")
        typeCombo.append_text("Directory")
        typeCombo.set_active(0)
        typeCombo.set_hexpand(True)
    
        self.typeCombo = typeCombo

        cbox.pack_start(typeLabel, True, True, 0)
        rbox.pack_start(typeCombo, False, True, 0)

        # Get the executable name and working directory
        if len(argv) > 1:
            executable = os.path.basename(argv[1]).split(".")[0]        
            directory = os.path.dirname(argv[1])
        else:
            # Open a file chooser and ask for a folder to create the launcher in
            fileChooser = Gtk.FileChooserDialog("Please choose a folder", self, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
            response = fileChooser.run()
            if response == Gtk.ResponseType.OK:
                print("Open clicked")
                print("Folder selected: " + fileChooser.get_filename())
                executable = ""
                directory = fileChooser.get_filename()
            elif response == Gtk.ResponseType.CANCEL:
                print("Cancel clicked")
            fileChooser.destroy()

        # If there is no directory after asking for a folder, abort
        if directory == "":
            print("No directory specified")
            exit()

        self.executable = executable
        self.directory = directory

        # Get the file's mime type for determining defaults
        if len(argv) > 1:
            mimeType = mimetypes.MimeTypes().guess_type(argv[1])[0] 
            print(mimeType)

            if mimeType is None:
                mimeType = 'unknown'  

        else:
            mimeType = 'unknown'
        self.mime = mimeType

        # Create a label for name
        nameLabel = Gtk.Label()
        nameLabel.set_markup("<b>Name:</b>")
        nameLabel.set_halign(Gtk.Align.END)

        # Create a name entry
        nameEntry = Gtk.Entry()
        nameEntry.set_input_purpose(Gtk.InputPurpose.ALPHA)
        nameEntry.set_tooltip_text("Enter the name of the launcher")

        # If the executable name is alpha-numeric, set nameEntry text to the executable name
        if executable.isalnum():
            nameEntry.set_text(executable.capitalize())
        elif mimeType.startswith(("inode/directory", "image", "video", "audio", "text", "application")):
            nameEntry.set_text(mimeType.split("/")[0].capitalize())
        
        nameEntry.set_hexpand(True)
        self.nameEntry = nameEntry

        cbox.pack_start(nameLabel, True, True, 0)
        rbox.pack_start(nameEntry, False, True, 0)

        # Create a label for the command
        commandLabel = Gtk.Label()
        commandLabel.set_markup("<b>Command:</b>")
        commandLabel.set_halign(Gtk.Align.END)

        # Create a command entry
        commandEntry = Gtk.Entry()
        commandEntry.set_tooltip_text("Enter the command to run")
        self.commandEntry = commandEntry

        def set_command(self, item): # Gonna need this later
            print(item)
            selMimeType = mimetypes.MimeTypes().guess_type(item)[0] 

            if selMimeType is None:
                selMimeType = 'unknown'  

            if selMimeType.startswith(("inode/directory", "image", "video", "audio", "text", "application")) and not selMimeType.startswith("application/x-"):
                self.commandEntry.set_text("xdg-open " + "'" + item + "'")
            else:
                print("Other")
                self.commandEntry.set_text("'" + item + "'")

        self.set_command = set_command

        # Set the command to the executable if there is one
        if len(argv) > 1:
           set_command(self, argv[1])

        commandEntry.set_hexpand(True)

        # Create a browse button
        commandBrowseButton = Gtk.Button.new_with_label("...")
        commandBrowseButton.set_hexpand(False)
        commandBrowseButton.connect("clicked", self.on_browse_button_clicked)

        commandEntryBox = Gtk.Box(spacing=6)
        commandEntryBox.pack_start(commandEntry, True, True, 0)
        commandEntryBox.pack_end(commandBrowseButton, False, True, 0)

        cbox.pack_start(commandLabel, True, True, 0)
        rbox.pack_start(commandEntryBox, False, True, 0)

        # Create a label for the icon
        iconLabel = Gtk.Label()
        iconLabel.set_markup("<b>Icon:</b>")
        iconLabel.set_halign(Gtk.Align.END)

        # Create an icon entry
        iconEntry = Gtk.Entry()
        iconEntry.set_tooltip_text("Enter the icon name or file to use")
        
        # Check if an icon name matches the executable name
        if executable in Gtk.IconTheme.get_default().list_icons():
            iconEntry.set_text(executable)
        
        iconEntry.set_hexpand(True)
        self.iconEntry = iconEntry

        # Create a browse button
        iconBrowseButton = Gtk.Button.new_with_label("...")
        iconBrowseButton.set_hexpand(False)
        iconBrowseButton.connect("clicked", self.on_icon_button_clicked)

        iconEntryBox = Gtk.Box(spacing=6)
        iconEntryBox.pack_start(iconEntry, True, True, 0)
        iconEntryBox.pack_end(iconBrowseButton, False, True, 0)

        cbox.pack_start(iconLabel, True, True, 0)
        rbox.pack_start(iconEntryBox, False, True, 0)

        # Create a label for comment
        commentLabel = Gtk.Label()
        commentLabel.set_markup("<b>Comment:</b>")
        commentLabel.set_halign(Gtk.Align.END)

        # Create a comment entry
        commentEntry = Gtk.Entry()
        commentEntry.set_hexpand(True)
        self.commentEntry = commentEntry
        commentEntry.set_tooltip_text("Enter a comment for the launcher")

        cbox.pack_start(commentLabel, True, True, 0)
        rbox.pack_start(commentEntry, False, True, 0)

        # Create a terminal check button
        terminalCheck = Gtk.CheckButton().new_with_label("Run in terminal")
        terminalCheck.set_hexpand(True)
        self.terminalCheck = terminalCheck
        terminalCheck.set_tooltip_text("Check to run launcher in the terminal")

        cbox.pack_start(Gtk.Label(), True, True, 0)
        rbox.pack_start(terminalCheck, False, True, 0)

        # Create a button box to hold the OK and Cancel buttons
        buttonBox = Gtk.Box(spacing=6)
        vbox.pack_start(buttonBox, True, True, 0)

        # Create Help, cancel, and OK buttons
        helpButton = Gtk.Button.new_with_label("Help")
        helpButton.connect("clicked", self.on_help_button_clicked)
        helpButton.set_hexpand(False)

        cancelButton = Gtk.Button.new_with_label("Cancel")
        cancelButton.connect("clicked", self.on_cancel_button_clicked)
        cancelButton.set_hexpand(False)

        okButton = Gtk.Button.new_with_label("OK")
        okButton.connect("clicked", self.on_ok_button_clicked) 
        okButton.set_hexpand(False)

        # buttonBox.pack_start(helpButton, False, True, 0)
        buttonBox.pack_end(okButton, False, True, 0)
        buttonBox.pack_end(cancelButton, False, True, 0)

        # Create a preview for the launcher icon
        iconPreview = Gtk.Image()

        # Define methods to update the preview
        def set_icon_defaults(self):
            if typeCombo.get_active_text() == "Application":
                # Set to generic executable icon OR file type if opening a file
                if mimeType.startswith(("image", "video", "audio", "text")):
                    iconPreview.set_from_icon_name(mimeType.split("/")[0], Gtk.IconSize.DIALOG)
                else:
                    iconPreview.set_from_icon_name("application-x-executable", Gtk.IconSize.DIALOG)
            elif typeCombo.get_active_text() == "Link":
                iconPreview.set_from_icon_name("browser", Gtk.IconSize.DIALOG)                    
            elif typeCombo.get_active_text() == "Directory":
                iconPreview.set_from_icon_name("folder", Gtk.IconSize.DIALOG)

        def set_icon(self):
            if iconEntry.get_text() != "":
                # If iconEntry matches an icon name, set it to that
                if iconEntry.get_text() in Gtk.IconTheme.get_default().list_icons():
                    iconPreview.set_from_icon_name(iconEntry.get_text(), Gtk.IconSize.DIALOG)
                    print("Matches icon name: " + iconEntry.get_text())
                # If iconEntry matches a file, set it to that
                elif os.path.isfile(iconEntry.get_text()):
                    # Resize the image to fit the button using PIL
                    try:
                        Image.open(iconEntry.get_text())
                    except IOError:
                        print("idk messagebox isnt showing")
                        return
                    # Open the image and resize it
                    img = Image.open(iconEntry.get_text())                                   
                    img = img.resize((48, 48), Image.ANTIALIAS)
                    print("resized image")
                    img.save("/tmp/icon.png")
                    print("saved image")
                    img.close()
                    print("closed image")
                    iconPreview.set_from_file("/tmp/icon.png")
                    print("set image")
                    print("Matches file: " + iconEntry.get_text())
                # If iconEntry isnt valid, set it to a default
                else:
                    print("Doesnt match anything:" + iconEntry.get_text())
                    set_icon_defaults(self)
            else:
                set_icon_defaults(self)

        # Perform the set_icon function when the iconEntry or typeCombo text changes and on startup
        iconEntry.connect("changed", set_icon)
        typeCombo.connect("changed", set_icon)
        set_icon(self)

        # Create a button to hold the GtkImage
        iconButton = Gtk.Button()
        iconButton.set_size_request(64, 64)
        iconButton.set_image(iconPreview)
        iconButton.set_always_show_image(True)
        iconButton.connect("clicked", self.on_icon_button_clicked)
        lbox.pack_start(iconButton, False, True, 0)

        # Create a clear button
        clearButton = Gtk.Button.new_with_label("Clear")
        clearButton.connect("clicked", self.on_clear_button_clicked)
        clearButton.set_hexpand(False)
        lbox.pack_start(clearButton, False, True, 0)

    def on_browse_button_clicked(self, widget):
        print("Browse button clicked")
        # Open a file chooser dialog and set the commandEntry text to the selected file
        fileChooser = Gtk.FileChooserDialog("Please choose a file", self, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = fileChooser.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + fileChooser.get_filename())
            self.set_command(self, fileChooser.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        fileChooser.destroy()

    def on_cancel_button_clicked(self, widget):
        print("Cancel button clicked")
        self.destroy()

    def on_ok_button_clicked(self, widget):
        print("OK button clicked")
        print("Creating desktop file")
        # Create a .desktop file at directory
        dest = self.directory + "/" + self.nameEntry.get_text() + ".desktop"
        # Check if dest already exists
        if os.path.isfile(dest):
            # Create another file and add (2) to the end of the name
            dest = self.directory + "/" + self.nameEntry.get_text() + "(2).desktop"
            # Check if dest already exists again
            if os.path.isfile(dest):
                # Increase the number until it doesnt
                i = 2
                while os.path.isfile(dest):        
                    i+=1
                    dest = self.directory + "/" + self.nameEntry.get_text() + "(" + str(i) + ").desktop"        
                    print("File already exists, increasing number")
        # Create the file
        desktopFile = open(dest, "w")
        # Write the desktop file header
        desktopFile.write("[Desktop Entry]\n")
        # Write the name of the application
        desktopFile.write("Name=" + self.nameEntry.get_text() + "\n")
        # Write the comment of the application
        desktopFile.write("Comment=" + self.commentEntry.get_text() + "\n")
        # Write the type of the application
        desktopFile.write("Type=" + self.typeCombo.get_active_text() + "\n")
        # Write the command of the application
        if self.iconEntry.get_text() in Gtk.IconTheme.get_default().list_icons():
            desktopFile.write("Icon=" + self.iconEntry.get_text() + "\n")
        # Check if iconEntry matches a file, if so, move and the file
        elif os.path.isfile(self.iconEntry.get_text()):
            # Move /tmp/icon.png to ~/.local/share/shortcuts/icon.png
            # Firstly, check if ~/.local/share/shortcuts exists
            if not os.path.isdir(os.path.expanduser("~") + "/.local/share/shortcuts"):
                print("Creating ~/.local/share/shortcuts")
                os.mkdir(os.path.expanduser("~") + "/.local/share/shortcuts")
            # Then move the file
            shutil.move("/tmp/icon.png", os.path.expanduser("~/.local/share/shortcuts/" + self.nameEntry.get_text() + ".png"))
            # Write the icon of the application
            desktopFile.write("Icon=" + os.path.expanduser("~/.local/share/shortcuts/" + self.nameEntry.get_text() + ".png") + "\n")
        # If iconEntry isnt valid, set it to a default depending on the type
        else:
            if self.typeCombo.get_active_text() == "Application":
                if self.mime.startswith(("image", "video", "audio", "text")):
                    desktopFile.write("Icon=" + self.mime.split("/")[0] + "\n")
                else:
                    desktopFile.write("Icon=application-x-executable\n")
            elif self.typeCombo.get_active_text() == "Link":
                desktopFile.write("Icon=browser\n")
            elif self.typeCombo.get_active_text() == "Directory":
                desktopFile.write("Icon=folder\n")
        # Write the executable of the application
        desktopFile.write("Exec=" + self.commandEntry.get_text() + "\n")
        # Write the terminal option of the application
        if self.terminalCheck.get_active():
            desktopFile.write("Terminal=true\n")
        # Save the desktop file
        desktopFile.close()
        print("Desktop file created")
        # Make the desktop file executable
        os.chmod(dest, 0o755)
        print("Desktop file made executable")
        # Destroy the window
        self.destroy()
    
    def on_icon_button_clicked(self, widget):
        print("Icon button clicked")
        # Open a file chooser dialog and set the iconEntry text to the selected file
        fileChooser = Gtk.FileChooserDialog("Please choose a file", self, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        # Filter for only image files
        fileFilter = Gtk.FileFilter()
        fileFilter.set_name("Image files")
        fileFilter.add_mime_type("image/*")
        fileChooser.add_filter(fileFilter)
        
        response = fileChooser.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + fileChooser.get_filename())
            self.iconEntry.set_text(fileChooser.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        fileChooser.destroy()

    def on_help_button_clicked(self, widget):
        print("Help button clicked")
    
    def on_clear_button_clicked(self, widget):
        print("Clear button clicked")
        self.iconEntry.set_text("")


win = MainWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()


# <3 
