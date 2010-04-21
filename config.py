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

      self.interval = self.gconf.get_int("/apps/gtracker/interval")
      if self.interval<1:
         self.interval = 15
         self.gconf.set_int("/apps/gtracker/interval",self.interval)

      if not keyring:
         self.username = self.gconf.get_string("/apps/gtracker/username")
         if self.username==None or len(self.username)<1:
            self.username = ""
            self.gconf.set_string("/apps/gtracker/username","")

         self.password = self.gconf.get_string("/apps/gtracker/password")
         if self.password==None or len(self.password)<1:
            self.password = ""
            self.gconf.set_string("/apps/gtracker/password",self.password)

   def save(self,username,password,interval):
      try:
         self.gconf.set_int("/apps/gtracker/interval",interval)

         if not keyring:
            self.gconf.set_string("/apps/gtracker/username",username)
            self.gconf.set_string("/apps/gtracker/password",password)
         else:
            pass
      except:
         return False
      return True
