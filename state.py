import gettext

_ = gettext.gettext

class State:
   def __init__(self,state,next_states,verb,past,started=False):
      self.state = state
      self.next_states = next_states
      self.verb = verb
      self.past = past
      self.started = started

class States:
   states = {}
   states["unscheduled"] = State("unscheduled"  ,["started"],_("Unscheduling"),_("Voided"),False) # this one will never show
   states["unstarted"]   = State("unstarted"    ,["started"],_("Unscheduling"),_("Voided"),False) # this one will never show
   states["started"]     = State("started"      ,["finished"],_("Start"),_("Started"),True)
   states["finished"]    = State("finished"     ,["delivered"],_("Finish"),_("Finished"),True)
   states["delivered"]   = State("delivered"    ,["accepted","rejected"],_("Deliver"),_("Delivered"),True)
   states["accepted"]    = State("accepted"     ,[],_("Accept"),_("Accepted"),True)
   states["rejected"]    = State("rejected"     ,["started"],_("Reject"),_("Rejected"),True)

   @classmethod
   def get_state(cls,id):
      return cls.states[id]
