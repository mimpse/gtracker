import gettext

_ = gettext.gettext

class State:
   def __init__(self,state,next_states,verb):
      self.state = state
      self.next_states = next_states
      self.verb = verb

class States:
   states = {}
   states["unscheduled"] = State("unscheduled",["started"],_("Unscheduling")) # this one will never show
   states["started"]     = State("started",["finished"],_("Start"))
   states["finished"]    = State("finished",["delivered"],_("Finish"))
   states["delivered"]   = State("delivered",["accepted","rejected"],_("Deliver"))
   states["accepted"]    = State("accepted",[],_("Accept"))
   states["rejected"]    = State("rejected",[],_("Reject"))

   @classmethod
   def get_state(cls,id):
      return cls.states[id]
