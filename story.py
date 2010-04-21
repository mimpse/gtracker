from state import *
import gettext

_ = gettext.gettext

class Story:
   def __init__(self,proj_id,id,name,state,owner,points=0,menu_item=None):
      self.proj_id   = proj_id
      self.id        = id
      self.name      = name
      self.state     = state
      self.owner     = owner
      self.points    = points
      self.tasks     = []
      self.menu_item = menu_item
      self.done      = False

   def __str__(self):
      next_states = self.next_states()
      state_desc  = _(" or ").join([States.get_state(st).verb for st in next_states])
      state_desc  = state_desc.lower().capitalize()

      # nothing more to do here
      if len(state_desc)<1:
         state_desc  = "Done"
         self.done   = True

      name = self.name.replace(self.name[0],self.name[0].lower(),1)

      points = _("Unestimated") if int(self.points)<0 else ("%s points" % self.points)
      if len(self.tasks)>0:
         return _("%s %s (%s) (%s) (%d tasks)") % (state_desc,name,points,self.owner,len(self.tasks))
      else:
         return _("%s %s (%s) (%s)") % (state_desc,name,points,self.owner)

   def next_states(self):
      return States.get_state(self.state).next_states

   def remove_task(self,task):
      found = None
      for t in self.tasks:
         if task.id==t.id:
            found = t
            break
      if found==None:
         return False
      self.tasks.remove(t)
      return True
