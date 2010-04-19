import gettext

_ = gettext.gettext

class Task:
   def __init__(self,proj_id,story_id,story_name,id,desc,position,complete):
      self.proj_id      = proj_id
      self.story_id     = story_id
      self.story_name   = story_name
      self.id           = id
      self.description  = desc
      self.position     = position
      self.complete     = complete
      self.menu_item    = None

   def __str__(self):
      return _("Task %s") % (self.description)
