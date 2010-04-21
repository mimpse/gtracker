import glib
import gconf

keyring = False
try:
   import  gnomekeyring as gk
   #keyring = True
except:
   pass

class Config:
   def __init__(self):
      self.username  = None
      self.password  = None
      self.gconf     = gconf.client_get_default()

      self.username_key   = "/apps/gtracker/username"
      self.password_key   = "/apps/gtracker/password"
      self.interval_key   = "/apps/gtracker/interval"

      self.interval = self.gconf.get_int(self.interval_key)
      if self.interval<1:
         self.interval = 15
         self.gconf.set_int(self.interval_key,self.interval)

      if not keyring:
         self.username = self.gconf.get_string(self.username_key)
         if self.username==None or len(self.username)<1:
            self.username = ""
            self.gconf.set_string(self.username_key,"")

         self.password = self.gconf.get_string(self.password_key)
         if self.password==None or len(self.password)<1:
            self.password = ""
            self.gconf.set_string(self.password_key,self.password)
      else:
         self.gconf.unset(self.username_key)
         self.gconf.unset(self.password_key)
         self.gconf.unset(self.interval_key)
         glib.set_application_name("Gtracker")

   def save(self,username,password,interval):
      try:
         self.gconf.set_int(self.interval_key,interval)

         if not keyring:
            self.gconf.set_string(self.username_key,username)
            self.gconf.set_string(self.password_key,password)
         else:
            pass
      except:
         return False
      return True
