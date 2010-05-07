import time
import urllib
import urllib2
import xml.dom.minidom

AUTH_URL       = "https://www.pivotaltracker.com/services/v3/tokens/active"
PROJECTS_URL   = "http://www.pivotaltracker.com/services/v3/projects"
PIVOTAL_HOME   = "http://www.pivotaltracker.com"

from story import *
from task  import *

class Pivotal:
   def __init__(self,gui):
      self.gui       = gui
      self.token     = None
      self.username  = None
      self.password  = None
      self.check     = True

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
         last  = proj.getElementsByTagName("last_activity_at")[0].firstChild.data
         data.append([id,name,last])
      return data         

   def get_story(self,story):
      headers = {}
      headers['X-TrackerToken'] = self.token

      url      = "%s/%s/stories/%s" % (PROJECTS_URL,story.proj_id,story.id)
      stories  = self.get_xml("story",url,"GET",None,headers)
      if len(stories)<1:
         return None
      return self.make_story(story.proj_id,stories[0])

   def get_stories(self,proj_id):
      headers = {}
      headers['X-TrackerToken'] = self.token

      filter   = urllib.urlencode({'filter': 'state:unstarted,unscheduled,started,finished,delivered,rejected'})
      url      = "%s/%s/stories?%s" % (PROJECTS_URL,proj_id,filter)
      stories  = self.get_xml("story",url,"GET",None,headers)
      data     = []

      if len(stories)<1:
         return data

      for story in stories:
         if story==None:
            continue
         st = self.make_story(proj_id,story)
         if st!=None:
            data.append(st)
      return data         

   def get_task(self,data):
      headers  = {}
      headers['X-TrackerToken'] = self.token
      
      try:
         url   = "%s/%s/stories/%s/tasks/%s" % (PROJECTS_URL,data.proj_id,data.story_id,data.id)
         tasks = self.get_xml("task",url,"GET",None,headers)

         if len(tasks)<1:
            return None
         return self.make_task(data.proj_id,data.story_id,data.story_name,tasks[0])
      except Exception as exc:
         print "get_task: %s" % exc 
         return None

   def complete_task(self,task):
      headers  = {}
      headers['X-TrackerToken']  = self.token
      headers["Content-type"]    = "application/xml"

      try:
         url   = "%s/%s/stories/%s/tasks/%s" % (PROJECTS_URL,task.proj_id,task.story_id,task.id)
         data  = "<task><complete>true</complete></task>"
         tasks = self.get_xml("task",url,"PUT",data,headers)

         if len(tasks)<1:
            return False

         task = self.make_task(task.proj_id,task.story_id,task.story_name,tasks[0])
         return task.complete=="true"
      except Exception as exc:
         print "complete_task: %s" % exc
         return False

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
            if only_completed and otask.complete!="true":
               data.append(otask)
      except Exception as exc:
         print "get_tasks: %s" % exc 
      return data

   def make_story(self,proj_id,data):
      try:
         id       = data.getElementsByTagName("id")[0].firstChild.data
         name     = data.getElementsByTagName("name")[0].firstChild.data
         state    = data.getElementsByTagName("current_state")[0].firstChild.data
         points   = data.getElementsByTagName("estimate")
         type     = data.getElementsByTagName("story_type")
         owner    = data.getElementsByTagName("owned_by")

         if len(points)>0:
            points = points[0].firstChild.data
         else:
            points = "0"
         
         if len(type)>0:
            type = type[0].firstChild.data
         else:
            type = "undertermined"

         if len(owner)>0:
            owner = owner[0].firstChild.data
         else:
            owner = "nobody"
         
         return Story(proj_id,id,name,state,owner,points,type)
      except Exception as exc:
         print "make_story: %s" % exc
         return None

   def make_task(self,proj_id,story_id,story_name,data):
      try:
         id       = data.getElementsByTagName("id")[0].firstChild.data
         desc     = data.getElementsByTagName("description")[0].firstChild.data
         position = data.getElementsByTagName("position")[0].firstChild.data
         complete = data.getElementsByTagName("complete")[0].firstChild.data
         return Task(proj_id,story_id,story_name,id,desc,position,complete)
      except Exception as exc:
         print "make_task: %s" % exc
         return None

   def update_story_state(self,story,state):
      try:
         # extra checking
         cstory = self.get_story(story)
         if story.state!=cstory.state:
            return False

         headers = {}
         headers["X-TrackerToken"]  = self.token
         headers["Content-type"]    = "application/xml"

         url      = "%s/%s/stories/%s" % (PROJECTS_URL,story.proj_id,story.id)
         data     = ("<story><current_state>%s</current_state></story>" % state)
         rstory   = self.get_xml("story",url,"PUT",data,headers)

         if len(rstory)<1:
            return False

         sid = rstory[0].getElementsByTagName("id")[0]
         if sid.firstChild.data!=story.id:
            return False

         story.state = state
         return True
      except Exception as exc:
         print "update_story_state: %s" % exc
         return False

   def connectivity(self):
      for i in range(30):
         print "Checking connectivity: %d" % i
         try:
            urllib.urlopen(PIVOTAL_HOME)
            print "Connected."
            return True
         except Exception as exc:
            print "Failed connectivity: %d %s" % (i,exc)
         time.sleep(5)
      return False

   def get_xml(self,elem,url,method="GET",data=None,headers=None):
      if self.check and not self.connectivity():
         raise Exception, "Failed to connect"
      self.check = False

      if headers==None:
         req   = urllib2.Request(url,data)
      else:
         req   = urllib2.Request(url,data,headers)
      if method!="GET":
         req.get_method = lambda: method
      dom = xml.dom.minidom.parse(urllib2.urlopen(req))
      return dom.getElementsByTagName(elem)
