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
      self.menu_item = menu_item

   def __str__(self):
      state_info  = States.get_state(self.state)
      next_state  = States.get_state(state_info.next_states[0])
      points      = _("Unestimated") if int(self.points)<0 else ("%s points" % self.points)
      return _("%s: %s (%s) (%s)") % (next_state.verb,self.name,points,self.owner)
