import urllib
import urllib2
import xml.dom.minidom

AUTH_URL       = "https://www.pivotaltracker.com/services/v3/tokens/active"
PROJECTS_URL   = "http://www.pivotaltracker.com/services/v3/projects"

class Pivotal:
   def __init__(self,gui):
      self.gui       = gui
      self.token     = None
      self.username  = None
      self.password  = None

   def auth(self):
      data  = urllib.urlencode((('username',self.gui.username),('password',self.gui.password)))
      xml   = self.get_xml("guid",AUTH_URL,"GET",data)
      if len(xml)<1:
         return False
      self.token = xml[0].firstChild.data
      return True

   def get_token(self):
      return self.token

   def get_projects(self):
      headers = {}
      headers['X-TrackerToken'] = self.token

      data  = []
      projs = self.get_xml("project",PROJECTS_URL,"GET",None,headers)

      if len(projs)<1:
         return data

      for proj in projs:
         id    = proj.getElementsByTagName("id")[0].firstChild.data
         name  = proj.getElementsByTagName("name")[0].firstChild.data
         data.append([id,name])
      return data         

   def get_stories(self,proj_id):
      headers = {}
      headers['X-TrackerToken'] = self.token

      filter   = urllib.urlencode({'filter': 'state:unstarted,unscheduled,started'})
      url      = "%s/%s/stories?%s" % (PROJECTS_URL,proj_id,filter)
      stories  = self.get_xml("story",url,"GET",None,headers)
      data     = []

      if len(stories)<1:
         return data

      for story in stories:
         data.append(self.make_story(proj_id,story))
      return data         

   def get_tasks(self,proj_id,story_id,story_name,only_completed):
      data     = []
      headers  = {}
      headers['X-TrackerToken'] = self.token

      try:
         url   = "%s/%s/stories/%s/tasks" % (PROJECTS_URL,proj_id,story_id)
         tasks = self.get_xml("task",url,"GET",None,headers)

         if len(tasks)<1:
            return data

         for task in tasks:
            otask = self.make_task(proj_id,story_id,story_name,task)
            if only_completed and otask[6]!="true":
               data.append(otask)
      except:
         pass
      return data

   def make_story(self,proj_id,data):
      id       = data.getElementsByTagName("id")[0].firstChild.data
      name     = data.getElementsByTagName("name")[0].firstChild.data
      state    = data.getElementsByTagName("current_state")[0].firstChild.data
      points   = data.getElementsByTagName("estimate")[0].firstChild.data
      owner    = data.getElementsByTagName("owned_by")
      if len(owner)>0:
         owner = owner[0].firstChild.data
      else:
         owner = "nobody"
      return [proj_id,id,name,state,owner,points]

   def make_task(self,proj_id,story_id,story_name,data):
      id       = data.getElementsByTagName("id")[0].firstChild.data
      desc     = data.getElementsByTagName("description")[0].firstChild.data
      position = data.getElementsByTagName("position")[0].firstChild.data
      complete = data.getElementsByTagName("complete")[0].firstChild.data
      return [proj_id,story_id,story_name,id,desc,position,complete]

   def walk_story(self,id):
      pass

   def start_story(self,story):
      return self.update_story_state(story,"started")

   def finish_story(self,story):
      return self.update_story_state(story,"finished")

   def deliver_story(self,story):
      return self.update_story_state(story,"delivered")

   def update_story_state(self,story,status):
      try:
         headers = {}
         headers["X-TrackerToken"]  = self.token
         headers["Content-type"]    = "application/xml"

         proj_id, id, name, state, owned = story
         url   = "%s/%s/stories/%s" % (PROJECTS_URL,proj_id,id)
         data  = ("<story><current_state>%s</current_state></story>" % status)
         story = self.get_xml("story",url,"PUT",data,headers)
         if len(story)<1:
            return False
         sid = story[0].getElementsByTagName("id")[0]
         if sid.firstChild.data!=id:
            return False
         return self.make_story(proj_id,story[0])
      except Exception as exc:
         print "Error updating story state: %s" % exc
         return False

   def get_xml(self,elem,url,method="GET",data=None,headers=None):
      if headers==None:
         req   = urllib2.Request(url,data)
      else:
         req   = urllib2.Request(url,data,headers)
      if method!="GET":
         req.get_method = lambda: method
      dom = xml.dom.minidom.parse(urllib2.urlopen(req))
      return dom.getElementsByTagName(elem)
