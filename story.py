from state import *
import gettext

_ = gettext.gettext

class Story:
   def __init__(self,proj_id,id,name,state,owner,points=0,type="undertermined",menu_item=None):
      self.proj_id   = proj_id
      self.id        = id
      self.name      = name
      self.state     = state
      self.owner     = owner
      self.points    = points
      self.type      = type
      self.tasks     = []
      self.menu_item = menu_item
      self.done      = False
      self.multiline = True

   def __str__(self):
      next_states = self.next_states()
      state_desc  = _(" or ").join([_(States.get_state(st).verb) for st in next_states])
      state_desc  = state_desc.lower().capitalize()

      # nothing more to do here
      if len(state_desc)<1:
         state_desc  = _("Done")
         self.done   = True

      name     = self.name.replace(self.name[0],self.name[0].lower(),1)
      points   = _("Unestimated") if int(self.points)<0 else (_("%s points") % self.points)
      multi    = "\n" if self.multiline else " - "
      type     = _(self.type).lower().capitalize()
      values   = {"desc":state_desc,"name":name,"multi":multi,"points":points,"owner":self.owner,"tasks_len":len(self.tasks),"type":type}

      if len(self.tasks)>0:
         return _("%(desc)s %(name)s%(multi)s%(type)s - s%(points)s - %(owner)s - %(tasks_len)d tasks") % values
      else:
         return _("%(desc)s %(name)s%(multi)s%(type)s - %(points)s - %(owner)s") % values

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
