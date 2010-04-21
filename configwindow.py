import gtk
import pygtk
import gobject
import gettext

from config import *

_ = gettext.gettext

class ConfigWindow(gtk.Window):
   def __init__(self,manager):
      super(ConfigWindow,self).__init__()
      self.set_title(_("Gtracker configuration"))
      self.set_modal(True)
   
      self.manager      = manager
      self.config       = Config()
      self.resp         = None
      table             = gtk.Table(2,2,True)

      userStr         = gtk.Label(_("Username"))
      self.userTxt    = gtk.Entry()
      self.userTxt.set_text(str(self.config.username))

      passStr         = gtk.Label(_("Password"))
      self.passTxt    = gtk.Entry()
      self.passTxt.set_visibility(False)
      self.passTxt.set_text(str(self.config.password))

      intervalStr        = gtk.Label(_("Interval"))
      self.intervalTxt   = gtk.Entry()
      self.intervalTxt.set_text(str(self.config.interval))

      self.multiline = gtk.CheckButton(_("Show stories using two lines"))
      self.multiline.set_active(self.config.multiline)

      showPasswd = gtk.CheckButton(_("Show password"));
      showPasswd.connect("toggled", self.show_passwd,showPasswd)

      self.ok  = gtk.Button(_("Ok"))
      self.ok.connect("clicked",self.save)

      self.cancel = gtk.Button(_("Cancel"))
      self.cancel.connect("clicked",self.dontsave)

      table.attach(userStr,0,1,0,1)
      table.attach(self.userTxt,1,2,0,1)

      table.attach(passStr,0,1,1,2)
      table.attach(self.passTxt,1,2,1,2)

      table.attach(intervalStr,0,1,2,3)
      table.attach(self.intervalTxt,1,2,2,3)

      table.attach(self.multiline ,1,2,3,4)
      table.attach(showPasswd,1,2,4,5)

      table.attach(self.ok,0,1,6,7)
      table.attach(self.cancel,1,2,6,7)
      
      self.add(table)
      self.show_all()

   def show_passwd(self,widget,data=None):
      self.passTxt.set_visibility(data.get_active())

   def save(self,widget):
      username  = self.userTxt.get_text()
      password  = self.passTxt.get_text()
      interval  = int(self.intervalTxt.get_text())
      multiline = self.multiline.get_active()

      if not self.config.save(username,password,interval,multiline):
         self.manager.show_error(_("Could not save configuration info!"))
         return False

      self.manager.interval = interval
      self.manager.config.multiline = multiline

      if len(username)>0 and len(password)>0 and (username!=self.manager.username or password!=self.manager.password):
         self.manager.username = username
         self.manager.password = password
         gobject.idle_add(self.manager.check_thread)

      self.destroy()
      return True

   def dontsave(self,widget):
      self.destroy()
