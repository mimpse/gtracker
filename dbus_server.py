import dbus, dbus.glib, dbus.service

class DbusServer(dbus.service.Object):
   def set_manager(self,manager):
      self.manager = manager

   @dbus.service.method(dbus_interface="com.Gtracker.Interface",in_signature="",out_signature="i")
   def story_count(self):
      return self.manager.story_count()

   @dbus.service.method(dbus_interface="com.Gtracker.Interface",in_signature="",out_signature="ssss")
   def get_story(self,pos):
      return self.manager.get_story(pos)

   @dbus.service.method(dbus_interface="com.Gtracker.Interface",in_signature="",out_signature="b")
   def complete_story(self,id,silent=False):
      return False
      #story = self.manager.find_story_by_id(id)
      #if story==None:
         #return False
      #return self.manager.complete(None,story,silent)
