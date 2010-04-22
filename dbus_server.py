import dbus, dbus.glib, dbus.service
from state import *

class DbusServer(dbus.service.Object):
   def set_manager(self,manager):
      self.manager = manager

   @dbus.service.method(dbus_interface="com.Gtracker.Interface",in_signature="",out_signature="i")
   def story_count(self):
      return self.manager.story_count()

   @dbus.service.method(dbus_interface="com.Gtracker.Interface",in_signature="",out_signature="ssssss")
   def get_story(self,pos):
      return self.manager.get_story(pos)

   @dbus.service.method(dbus_interface="com.Gtracker.Interface",in_signature="",out_signature="b")
   def complete_task(self,id,silent=False):
      task = self.manager.find_task_by_id(id)
      if task==None:
         return False
      return self.manager.complete_task(task,True)

   @dbus.service.method(dbus_interface="com.Gtracker.Interface",in_signature="",out_signature="b")
   def update_story(self,id,starting=False,silent=False):
      story = self.manager.find_story_by_id(id)
      if story==None:
         return False
      # if story doesn't answer to a start event, get out
      state = States.get_state(story.state)
      if starting and not state.starting_trigger:
         return True
      # if we need to choose, cant update story, go to web page
      if len(state.next_states)>1:
         return False
      return self.manager.update_story_state(story,silent)
