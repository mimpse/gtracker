#!/usr/bin/python
__appname__    = "Gtracker"
__author__     = "Eustaquio 'TaQ' Rangel"
__copyright__  = "2010 Eustaquio 'TaQ' Rangel"
__version__    = "0.0.1"
__license__    = "GPL"
__email__      = "eustaquiorangel@gmail.com"
__website__    = "http://github.com/taq/gtracker"
__date__       = "$Date: 2010/04/12 12:00:00$"

import os
import sys
import gtk
import glob
import gobject
import pygtk
import gconf
import locale
import gettext
import datetime
import threading

pygtk.require('2.0')

try:
   import pynotify
   notify = 1
except:
   notify = 0

try:
   import dbus, dbus.glib
   dbus_enabled = 1
except:
   dbus_enabled = 0

BASE_DIRS = [os.path.join(os.path.expanduser("~"), ".local", "share"),"/usr/share/pyshared","/usr/local/share", "/usr/share"]
DATA_DIRS = [os.path.abspath(sys.path[0])] + [os.path.join(d,__appname__.lower()) for d in BASE_DIRS]

gettext.bindtextdomain(__appname__.lower())
gettext.textdomain(__appname__.lower())
_ = gettext.gettext

gobject.threads_init()

class Gtracker:
   
   def __init__(self):
      self.gconf     = gconf.client_get_default()
      self.started   = datetime.datetime.now()

      self.timeout   = self.gconf.get_int("/apps/gtracker/timeout")
      if self.timeout<1:
         self.timeout = 15
         self.gconf.set_int("/apps/gtracker/timeout",self.timeout)

      self.menu = gtk.Menu()

      self.statusIcon = gtk.StatusIcon()
      self.statusIcon.set_from_file(self.get_icon("gtracker.png"))
      self.statusIcon.set_visible(True)
      self.statusIcon.connect('activate'  , self.left_click, self.menu)
      self.statusIcon.connect('popup-menu', self.right_click, self.menu)
      self.statusIcon.set_visible(1)

      self.configItem = gtk.MenuItem(_("Configuration"))
      self.configItem.connect('activate', self.config, self.statusIcon)
      self.menu.append(self.configItem)

      self.statItem = gtk.MenuItem(_("Statistics"))
      self.statItem.connect('activate', self.stats, self.statusIcon)
      self.menu.append(self.statItem)

      self.aboutItem = gtk.MenuItem(_("About"))
      self.aboutItem.connect('activate', self.about, self.statusIcon)
      self.menu.append(self.aboutItem)

      self.quitItem = gtk.MenuItem(_("Quit"))
      self.quitItem.connect('activate', self.quit, self.statusIcon)
      self.menu.append(self.quitItem)

      if notify>0:
         pynotify.init("Gtracker")

      self.set_tooltip("Gtracker - Control your Pivotal Tracker stories from the tray bar")
      gtk.main()

   def get_icon(self,icon):
      for base in DATA_DIRS:
         path = os.path.join(base,"images",icon)
         if os.path.exists(path):
            return path
      return None  

   def right_click(self, widget, button, time, data = None):
      data.show_all()
      data.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusIcon)

   def set_tooltip(self,text):
      self.statusIcon.set_tooltip(text)

   def left_click(self,widget,data):
      pass

   def config(self, widget, data = None):
      pass

   def stats(self,widget,data):
      pass

   def about(self,widget,data=None):
      pass

   def quit(self,widget,data=None):
      gtk.main_quit()

if __name__ == "__main__":
   gpomo = Gtracker()
