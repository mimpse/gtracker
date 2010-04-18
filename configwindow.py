import gtk
import pygtk
import gettext

_ = gettext.gettext

class ConfigWindow(gtk.Window):
   def __init__(self,manager):
      super(ConfigWindow,self).__init__()
      self.set_title(_("Gtracker configuration"))
      self.set_modal(True)
   
      self.manager      = manager
      self.gconf        = self.manager.gconf
      self.resp         = None
      table             = gtk.Table(2,2,True)

      userStr         = gtk.Label(_("User name"))
      self.userTxt    = gtk.Entry()
      self.userTxt.set_text(str(self.manager.username))

      passStr         = gtk.Label(_("Password"))
      self.passTxt    = gtk.Entry()
      self.passTxt.set_visibility(False)
      self.passTxt.set_text(str(self.manager.password))

      intervalStr        = gtk.Label(_("Interval"))
      self.intervalTxt   = gtk.Entry()
      self.intervalTxt.set_text(str(self.manager.interval))

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

      table.attach(showPasswd,1,2,3,4)

      table.attach(self.ok,0,1,5,6)
      table.attach(self.cancel,1,2,5,6)
      
      self.add(table)
      self.show_all()

   def show_passwd(self,widget,data=None):
      self.passTxt.set_visibility(data.get_active())

   def save(self,widget):
      username = self.userTxt.get_text()
      self.manager.gconf.set_string("/apps/gtracker/username",username)
      self.manager.username = username

      password = self.passTxt.get_text()
      self.manager.gconf.set_string("/apps/gtracker/password",password)
      self.manager.password = password

      interval = int(self.intervalTxt.get_text())
      self.manager.gconf.set_int("/apps/gtracker/interval",interval)
      self.manager.interval = interval

      self.destroy()

   def dontsave(self,widget):
      self.destroy()
