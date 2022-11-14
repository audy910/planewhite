# Credits
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.app import App

from kivy.clock import Clock, ClockBase
from kivy.animation import Animation

from kivy.uix.boxlayout import BoxLayout
from kivy.core.image import Image
from kivy.uix.label import Label

from kivy.graphics import *

from lib.utils import ZoneOfInterest
import lib.config, lib.kwargs

# Configuration
TOUCH_DELAY = 15.0 # seconds before a touch switch to mode 1
PERSPECTIVE_DELAY = 10.0 # seconds before switching the background to perspective
CREDIT_DELAY = 10.0 # seconds before it displays credits
SCREENSAVER_DELAY = 30.0 # before jumping to next mode, mode 1

########################################################################
class Credits(Widget):
  
  def __init__(self, **kwargs):

    lib.kwargs.set_kwargs(self, **kwargs)

    super(Credits, self).__init__(**kwargs)  

    self.credits_touchedMessageSent = False
    self.credits_timeoutMessageSent = False

    self.last_runtime = 0.0

    self.credits = ZoneOfInterest(img=Image("images/credits.png"), pos=(11, 200))
    self.credits.alpha = 0.99
    
    self.label = Label(text="Composition VIII, Kandinsky",
                        font_size=25, 
                        color=(0,0,0,1), 
                        pos=(600,25), 
                        font_name="fonts/Akkurat.ttf")

    self.background_path = "images/bgs/" + str(self.clientIdIndex + 1) + ".jpg"
    self.perspective_path = "images/perspectives/" + str(self.clientIdIndex + 1) + ".jpg"

    self.background = ZoneOfInterest(img=Image(self.background_path))
    self.perspective = ZoneOfInterest(img=Image(self.perspective_path))

# basis
  def start(self):
    print ("Credits start() called")    

    self.background.alpha = 0.0
    self.perspective.alpha = 0.0
    
    self.add_widget(self.background)
    self.add_widget(self.perspective)

    self.background.fadeIn()
    if self.clientIdIndex == 0:
      self.add_widget(self.label)
    
    Clock.schedule_once(self.switchToPerspective, PERSPECTIVE_DELAY)

    if self.clientIdIndex == 3:
      Clock.schedule_once(self.displayCredits, CREDIT_DELAY)
    
    Clock.schedule_once(self.announceTheEnd, SCREENSAVER_DELAY) # restart screensaver
    self.last_runtime = Clock.get_boottime()
    

  def stop(self):
    print ("Credits stop() called")    
    self.remove_widget(self.background)
    self.remove_widget(self.perspective)
    self.remove_widget(self.credits)

    self.reset()
    Clock.unschedule(self.switchToPerspective)
    Clock.unschedule(self.displayCredits)
    Clock.unschedule(self.announceTheEnd) 
    

  def reset(self):
    self.credits_touchedMessageSent = False
    self.credits_timeoutMessageSent = False

# Custom methods

# Custom callbacks  
  def switchToPerspective(self, instance=False):
    self.remove_widget(self.label)
    
    self.background.alpha = 0.99
    self.background.fadeOut()
    
    self.perspective.alpha = 0.0
    self.perspective.fadeIn()


      
  def displayCredits(self, instance=False):
    self.add_widget(self.credits)


  def announceTheEnd(self, instance=False):
    if not self.credits_timeoutMessageSent:
      print ("This is the end.")
      self.controller.sendMessage("credits_timeout") # go back to mode1, ScreenSaver
      self.credits_timeoutMessageSent = True
    

# Kivy callbacks    
  def on_touch_down(self, touch):
    # Doesn't do anything if touched within the tenth first seconds.
    if abs(Clock.get_boottime() - self.last_runtime) > TOUCH_DELAY:
      if not self.credits_touchedMessageSent:
        print ("Credits touched at, ", Clock.get_boottime())
        self.controller.sendMessage("credits_touched") # go back to mode2, Learning
        self.credits_touchedMessageSent = True



########################################################################

      
if __name__ == '__main__':
  class CreditsApp(App):
    def build(self):      
      base = Widget()
      credit = Credits()
      base.add_widget(credit)
      credit.start()
      return base
      
  CreditsApp().run()
