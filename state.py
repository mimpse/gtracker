import gettext

_ = gettext.gettext

class State:
   def __init__(self,state,next_states,verb,past):
      self.state = state
      self.next_states = next_states
      self.verb = verb
      self.past = past

class States:
   states = {}
   states["unscheduled"] = State("unscheduled"  ,["started"],_("Unscheduling"),_("Voided")) # this one will never show
   states["unstarted"]   = State("unstarted"    ,["started"],_("Unscheduling"),_("Voided")) # this one will never show
   states["started"]     = State("started"      ,["finished"],_("Start"),_("Started"))
   states["finished"]    = State("finished"     ,["delivered"],_("Finish"),_("Finished"))
   states["delivered"]   = State("delivered"    ,["accepted","rejected"],_("Deliver"),_("Delivered"))
   states["accepted"]    = State("accepted"     ,[],_("Accept"),_("Accepted"))
   states["rejected"]    = State("rejected"     ,["started"],_("Reject"),_("Rejected"))

   @classmethod
   def get_state(cls,id):
      return cls.states[id]
