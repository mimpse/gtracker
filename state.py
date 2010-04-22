import gettext

_ = gettext.gettext

class State:
   def __init__(self,state,next_states,verb,past,started=False,starting_trigger=False):
      self.state = state
      self.next_states = next_states
      self.verb = verb
      self.past = past
      self.started = started
      self.starting_trigger = starting_trigger

class States:
   states = {}
   states["unscheduled"] = State("unscheduled"  ,["started"],_("Unscheduling"),_("Voided"),False,True) # this one will never show
   states["unstarted"]   = State("unstarted"    ,["started"],_("Unscheduling"),_("Voided"),False,True) # this one will never show
   states["started"]     = State("started"      ,["finished"],_("Start"),_("Started"),True,False)
   states["finished"]    = State("finished"     ,["delivered"],_("Finish"),_("Finished"),True,False)
   states["delivered"]   = State("delivered"    ,["accepted","rejected"],_("Deliver"),_("Delivered"),True,False)
   states["accepted"]    = State("accepted"     ,[],_("Accept"),_("Accepted"),True,False)
   states["rejected"]    = State("rejected"     ,["started"],_("Reject"),_("Rejected"),True,False)

   @classmethod
   def get_state(cls,id):
      return cls.states[id]
