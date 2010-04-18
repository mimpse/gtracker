class Story:
   def __init__(self,proj_id,id,name,state,owner,points=0,menu_item=None):
      self.proj_id   = proj_id
      self.id        = id
      self.name      = name
      self.state     = state
      self.owner     = owner
      self.points    = points
      self.menu_item = menu_item
