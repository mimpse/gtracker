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
import locale
import gettext
import datetime
import threading

pygtk.require('2.0')

from configwindow import *
from pivotal import *
from config import *
from story import *
from state import *
from task import *

try:
   import pynotify
   notify = 1
except:
   notify = 0

try:
   from dbus_server import *
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
      self.started   = datetime.datetime.now()
      self.username  = None
      self.password  = None
      self.pivotal   = None
      self.projects  = {}
      self.stories   = {}
      self.working   = False
      self.stats     = {}
      self.manual    = False
      self.config    = Config()
      self.interval  = self.config.interval
      self.username  = self.config.username
      self.password  = self.config.password
      self.pivotal   = Pivotal(self)

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

      if dbus_enabled>0:
         bus = dbus.SessionBus()
         bus_name = dbus.service.BusName('com.Gtracker',bus=bus)
         bus_obj = DbusServer(bus_name,'/')
         bus_obj.set_manager(self)

      gtk.main()

   def make_config_item(self):
      if self.configItem==None:
         self.configItem = gtk.MenuItem(_("Configuration"))
         self.configItem.connect('activate', self.config_from_menu)
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
         self.statItem.connect('activate', self.statistic)
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
      self.checkItem.set_sensitive(False)
      if not self.have_authentication_info():
         self.show_auth_message()
         return
      self.check_stories()
      self.checkItem.set_sensitive(True)

   def check_stories(self):
      if self.manual:
         self.manual = False
         self.schedule_next_check()
         return

      if not self.have_authentication_info():
         self.show_auth_message()
         self.show_error(_("Please configure your username and password and try again"))
         return

      self.working = True
      self.blinking(True)

      try:
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
         proj_id, proj_name, proj_last = proj
         proj_found = None

         # if there's already a project, check the last activity time
         if proj_id in self.projects:
            proj_found = self.projects[proj_id]
            if proj_found["last_activity"]==proj_last:
               continue

         # check if there are stories for this project
         self.set_tooltip(_("Retrieving stories for project %s ...") % proj_name)
         stories = self.pivotal.get_stories(proj_id)

         # no stories, move on
         if len(stories)<1:
            # but if there is a menu item, remove it
            if proj_found!=None and proj_found["menu_item"]!=None:
               self.menu.remove(proj_found["menu_item"])
            continue

         # if there isn't a project, we need to create a dictionary entry
         proj_item = None
         if proj_found==None:
            proj_item = gtk.MenuItem(proj_name,False)
            self.menu.append(proj_item)
         # if there is a project with some activity, clear the stories submenu             
         else:
            proj_found["menu_item"].remove_submenu()
            proj_item = proj_found["menu_item"]

         # update project info
         self.projects[proj_id] = {"name":proj_name,"menu_item":proj_item,"last_activity":proj_last}

         submenu = gtk.Menu()
         proj_item.set_submenu(submenu)
         self.stories[proj_id] = {}

         for story in stories:
            self.stories[proj_id][story.id] = story             
            tasks       = self.pivotal.get_tasks(proj_id,story.id,story.name,True)
            story.tasks = tasks
            task_size   = len(tasks)

            story.multiline = self.config.multiline
            menu_item = gtk.MenuItem(("%s" % story),False)
            story.menu_item = menu_item

            if story.done or int(story.points)<0:
               story.menu_item.set_sensitive(False)
            
            if task_size>0:
               task_submenu = gtk.Menu()
               for task in tasks:
                  task_menuitem = gtk.MenuItem(("%s" % task),False)
                  task_menuitem.connect("activate",self.complete_task_from_menu,task)
                  task.menu_item = task_menuitem
                  task_submenu.append(task_menuitem)
               menu_item.set_submenu(task_submenu)
            else:
               menu_item.connect("activate",self.update_story_state_from_menu,story)

            submenu.append(menu_item)
            if self.config.separator and story!=stories[-1]:
               submenu.append(gtk.SeparatorMenuItem())
            count += 1

      self.set_tooltip(_("%d stories retrieved.") % count)
      self.blinking(False)
      self.working = False
      self.schedule_next_check()

   def schedule_next_check(self):
      gobject.timeout_add(1000*60*self.interval,self.check_thread)

   def update_story_state_from_menu(self,widget,story):
      self.update_story_state(story,False)

   def choose_from_states(self,states):
      image = gtk.Image()
      image.set_from_file(self.get_icon("gtracker.png"))
      dialog = gtk.Dialog(_("Please choose"),None,gtk.DIALOG_MODAL,(_(states[0].verb),1000,_(states[1].verb),1001,_("Cancel"),gtk.RESPONSE_CANCEL))
      label = gtk.Label(_("Please choose what you want\nto do with your story."))
      dialog.vbox.pack_start(label,padding=10,expand=True,fill=True)
      dialog.vbox.pack_end(image,padding=10)
      dialog.show_all()
      resp = dialog.run()
      dialog.destroy()
      return resp

   def update_story_state(self,story,silent=False):
      # choose state
      next_states = story.next_states()
      if len(next_states)>1:
         states = [States.get_state(next_states[0]),States.get_state(next_states[1])]
         rsp    = self.choose_from_states(states)
         if rsp==gtk.RESPONSE_CANCEL:
            self.show_error(_("Story update canceled!"))
            return False
         next_state = next_states[rsp-1000]
      else:
         next_state = next_states[0]

      state_obj      = States.get_state(next_state)
      present_verb   = _(state_obj.verb)
      past_verb      = _(state_obj.past)
      if not silent and self.ask(_("Are you sure you want to %(verb)s '%(name)s'?") % {"verb":present_verb.lower(),"name":story.name})!=gtk.RESPONSE_YES:
         return False

      rsp = self.pivotal.update_story_state(story,next_state)
      if not silent and not rsp:
         self.show_error(_("Could not start to work on '%s'") % story.name)
         return False

      story.menu_item.set_label(story.__str__())
      if story.done:
         story.menu_item.set_sensitive(False)
      if not silent:
         self.show_info(_("'%(name)s' %(verb)s.") % {"name":story.name,"verb":past_verb.lower()})

      count = 0
      key   = past_verb.lower()
      try:
         count = self.stats[key]
         count += 1
      except:
         count = 1
      self.stats[key] = count
      return True

   def stats_str(self):
      s = ""
      for k,v in self.stats.items():
         s += k.capitalize()+": "+str(v)+"\n"
      return s

   def statistic(self,widget):
      self.show_info(_("About this session\n\nStarted on %(start)s\n\n%(str)s") % {"start":self.started.strftime(_("%m/%d/%Y %H:%M:%S")),"str":self.stats_str()})

   def find_task_by_id(self,id):
      for proj_id,stories in self.stories.items():
         for story_id,story in stories.items():
            for task in story.tasks:
               if task.id==id:
                  return task
      return None               

   def find_story_by_id(self,id):
      for proj_id,stories in self.stories.items():
         for story_id,story in stories.items():
            if story.id==id:
               return story
      return None            

   def complete_task_from_menu(self,widget,task):
      self.complete_task(task,False)

   def complete_task(self,task,silent=False):
      if not silent and self.ask(_("Are you sure you want to mark task '%s' as completed?") % task.description)!=gtk.RESPONSE_YES:
         return

      task_menu_item    = task.menu_item
      task_menu_parent  = task.menu_item.parent

      # extra checking
      task = self.pivotal.get_task(task)
      if task.complete!="false":
         return False
      
      # if not completed, try to complete now
      rst = self.pivotal.complete_task(task)

      # remove from menu
      task_menu_parent.remove(task_menu_item)

      story = self.stories[task.proj_id][task.story_id]
      story.remove_task(task)
      story.menu_item.set_label(story.__str__())

      # remove submenu
      if(len(story.tasks)<1):
         story.menu_item.remove_submenu()
         story.menu_item.connect("activate",self.update_story_state_from_menu,story)
     
      # start story, if status different from started
      state = States.get_state(story.state)
      if not state.started:
         self.pivotal.update_story_state(story,"started")
         story.menu_item.set_label(story.__str__())

      if rst and not silent:
         self.show_info(_("Task '%s' marked as completed.") % task.description)
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
      self.check_thread()
      self.manual = True

   def check_thread(self):
      t = InitThread(self)
      t.start()

   def config_from_menu(self, widget, data = None):
      ConfigWindow(self)

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

   # dbus
   def story_count(self):
      count = 0
      for proj_id in self.stories:
         count += len(self.stories[proj_id])
      return count 

   def get_story(self,pos):
      all = []
      for proj_id,stories in self.stories.items():
         proj = self.projects[proj_id]["name"]
         for story_id,story in stories.items():
            tasks = story.tasks
            if len(tasks)<1:
               all.append([story.id,proj,story.name,story.points,"",""])
               continue

            for task in tasks:
               all.append([story.id,proj,story.name,story.points,task.id,task.description])

      if len(all)<pos:
         return [None,None,None,None]
      return all[pos]

if __name__ == "__main__":
   gtracker = Gtracker()
