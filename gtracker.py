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
import time
import gobject
import pygtk
import gconf
import locale
import gettext
import datetime
import threading

pygtk.require('2.0')

from configwindow import *
from pivotal import *
from story import *
from state import *
from task import *

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

class InitThread(threading.Thread):
   def __init__(self,gui):
      super(InitThread,self).__init__()
      self.gui = gui

   def run(self):
      self.gui.init()

class Gtracker:
   
   def __init__(self):
      self.gconf     = gconf.client_get_default()
      self.started   = datetime.datetime.now()
      self.username  = None
      self.password  = None
      self.pivotal   = None
      self.projects  = {}
      self.stories   = {}
      self.working   = False

      self.interval   = self.gconf.get_int("/apps/gtracker/interval")
      if self.interval<1:
         self.interval = 15
         self.gconf.set_int("/apps/gtracker/interval",self.interval)

      self.username   = self.gconf.get_string("/apps/gtracker/username")
      if self.username==None or len(self.username)<1:
         self.username = ""
         self.gconf.set_string("/apps/gtracker/username","")

      self.password  = self.gconf.get_string("/apps/gtracker/password")
      if self.password==None or len(self.password)<1:
         self.password = ""
         self.gconf.set_string("/apps/gtracker/password",self.password)

      self.menu         = gtk.Menu()
      self.config_menu  = gtk.Menu()

      self.configItem   = None
      self.checkItem    = None
      self.statItem     = None
      self.aboutItem    = None
      self.quitItem     = None

      self.statusIcon = gtk.StatusIcon()
      self.statusIcon.set_from_file(self.get_icon("gtracker.png"))
      self.statusIcon.set_visible(True)
      self.statusIcon.connect('activate'  , self.left_click , self.menu)
      self.statusIcon.connect('popup-menu', self.right_click, self.config_menu)
      self.statusIcon.set_visible(1)

      self.make_control_menu()
      self.set_tooltip("Gtracker - Control your Pivotal Tracker stories from the tray bar")

      if notify>0:
         pynotify.init("Gtracker")

      t = InitThread(self)
      t.start()

      gtk.main()

   def make_config_item(self):
      if self.configItem==None:
         self.configItem = gtk.MenuItem(_("Authentication"))
         self.configItem.connect('activate', self.config)
      self.config_menu.append(self.configItem)
      return self.configItem

   def make_check_item(self):
      if self.checkItem==None:
         self.checkItem = gtk.MenuItem(_("Check now!"))
         self.checkItem.connect('activate', self.check_now)
      self.config_menu.append(self.checkItem)
      return self.checkItem

   def make_stat_item(self):
      if self.statItem==None:
         self.statItem = gtk.MenuItem(_("Statistics"))
         self.statItem.connect('activate', self.stats)
      self.config_menu.append(self.statItem)
      return self.statItem

   def make_about_item(self):
      if self.aboutItem==None:
         self.aboutItem = gtk.MenuItem(_("About"))
         self.aboutItem.connect('activate', self.about)
      self.config_menu.append(self.aboutItem)
      return self.aboutItem

   def make_quit_item(self):
      if self.quitItem==None:
         self.quitItem = gtk.MenuItem(_("Quit"))
         self.quitItem.connect('activate', self.quit)
      self.config_menu.append(self.quitItem)
      return self.quitItem

   def make_control_menu(self):
      self.make_config_item()
      self.make_check_item()
      self.make_stat_item()
      self.make_about_item()
      self.make_quit_item()

   def have_authentication_info(self):
      return self.username!=None and self.password!=None and len(self.username)>0 and len(self.password)>0

   def show_auth_message(self):
      self.set_tooltip(_("Please configure your username and password and try again"))
      self.blinking(True)

   def init(self):
      self.set_tooltip(_("Authenticating and verifying stories ..."))
      if not self.have_authentication_info():
         self.show_auth_message()
         return
      self.check_stories()

   def clear_menu(self):
      for menuitem in self.menu.get_children():
         self.menu.remove(menuitem)

   def check_stories(self):
      if not self.have_authentication_info():
         self.show_auth_message()
         self.show_error(_("Please configure your username and password and try again"))
         return

      self.working = True
      self.blinking(True)
      self.clear_menu()

      try:
         self.pivotal = Pivotal(self)
         if not self.pivotal.auth():
            self.set_tooltip(_("Could not authenticate. Please verify your username and password and try again."))
            self.working = False
            return
      except Exception as exc:
         self.set_tooltip(_("Error authenticating. Please try again."))
         self.working = False
         return

      self.set_tooltip(_("Retrieving projects info ..."))
      projs = self.pivotal.get_projects()
      count = 0

      for proj in projs:
         proj_id, proj_name = proj
         self.projects[proj_id] = proj_name

         self.set_tooltip(_("Retrieving stories for project %s ...") % proj_name)
         stories = self.pivotal.get_stories(proj_id)

         if len(stories)<1:
            continue

         self.stories[proj_id] = {}

         proj_item = gtk.MenuItem(proj_name)
         self.menu.append(proj_item)

         submenu = gtk.Menu()
         proj_item.set_submenu(submenu)

         for story in stories:
            sobj = Story(*story)
            self.stories[proj_id][sobj.id] = sobj             
            tasks       = self.pivotal.get_tasks(proj_id,sobj.id,sobj.name,True)
            sobj.tasks  = tasks
            task_size   = len(tasks)

            if task_size>0:
               menu_item = gtk.MenuItem("%s (%d tasks)" % (sobj,task_size))
            else:
               menu_item = gtk.MenuItem("%s" % sobj)
            sobj.menu_item = menu_item
            
            if task_size>0:
               task_submenu = gtk.Menu()
               for task in tasks:
                  task_menuitem = gtk.MenuItem("%s" % task)
                  task_menuitem.connect("activate",self.complete_task_from_menu,task)
                  task.menu_item = task_menuitem
                  task_submenu.append(task_menuitem)
               menu_item.set_submenu(task_submenu)

            submenu.append(menu_item)
            count += 1

      self.set_tooltip(_("%d stories retrieved.") % count)
      self.blinking(False)
      self.working = False

   def complete_task_from_menu(self,widget,task):
      self.complete_task(task,False)

   def complete_task(self,task,silent=False):
      if not silent and self.ask(_("Are you sure you want to mark task '%s' as completed?") % task.description)!=gtk.RESPONSE_YES:
         return

      # extra checking
      task = self.pivotal.get_task(task)
      if task.complete!="false":
         return False
      
      # if not completed, try to complete now
      rst = self.pivotal.complete_task(task)
      if rst and not silent:
         self.show_info(_("Task '%s' marked as completed.") % task.description)

      # voided here ! get before!
      print task.menu_item
      print task.menu_item.parent
      task.menu_item.parent.remove(task.menu_item)
      story = self.stories[task.proj_id][task.story_id]
      story.remove_task(task)
      # TODO: update task description
      return rst

   def blinking(self,blink):
      self.statusIcon.set_blinking(blink)

   def get_icon(self,icon):
      for base in DATA_DIRS:
         path = os.path.join(base,"images",icon)
         if os.path.exists(path):
            return path
      return None  

   def right_click(self, widget, button, time, data = None):
      if self.working:
         return
      self.blinking(False)
      data.show_all()
      data.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusIcon)

   def set_tooltip(self,text):
      self.statusIcon.set_tooltip(text)

   def left_click(self,widget,data):
      if self.working:
         return
      self.blinking(False)
      data.show_all()
      data.popup(None,None,None,3,0)

   def check_now(self,widget,data=None):
      t = InitThread(self)
      t.start()

   def config(self, widget, data = None):
      ConfigWindow(self)

   def stats(self,widget,data):
      pass

   def about(self,widget,data=None):
      self.about = gtk.AboutDialog()
      self.about.set_name(__appname__)
      self.about.set_program_name(__appname__)
      self.about.set_version(__version__)
      self.about.set_copyright(__copyright__)
      self.about.set_license(__license__)
      self.about.set_website(__website__)
      self.about.set_website_label(__website__)
      self.about.set_authors(["%s <%s>" % (__author__,__email__)])
      self.about.set_logo(gtk.gdk.pixbuf_new_from_file(self.get_icon("gtracker.png")))
      self.about.run()
      self.about.destroy()
      pass

   def quit(self,widget,data=None):
      gtk.main_quit()

   def show_error(self,msg):
      self.show_dialog(gtk.MESSAGE_ERROR,msg)

   def show_info(self,msg):
      self.show_dialog(gtk.MESSAGE_INFO,msg)

   def show_dialog(self,msg_type,msg):    
      dialog = gtk.MessageDialog(None,gtk.DIALOG_MODAL,msg_type,gtk.BUTTONS_OK,msg)
      dialog.run()
      dialog.destroy()

   def ask(self,msg):
      dialog = gtk.MessageDialog(None,gtk.DIALOG_MODAL,gtk.MESSAGE_QUESTION,gtk.BUTTONS_YES_NO,msg)
      rsp = dialog.run()
      dialog.destroy()
      return rsp

if __name__ == "__main__":
   gtracker = Gtracker()
