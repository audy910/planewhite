# ScreenSaver

from kivy.logger import Logger

from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.app import App

from kivy.clock import Clock
from kivy.animation import Animation

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

#from kivy.core.audio import SoundLoader
import kivy.core.image
import kivy.uix.image

from kivy.graphics import *

from lib.utils import ZoneOfInterest
import lib.config, lib.kwargs

# Configuration
SCAN_IMG_PATH = 'images/scan.png' # scanner image
SCAN_DURATION = 5.0 # scan duration, by screen
NETWORK_DELAY = 0 # increase this value if you want to anticipate sync between two screens
TRIGGER_POINTS_THRESHOLD = 300 # amount of point to reveal to switch mode

########################################################################
class ScreenSaver(Widget):
  
  def __init__(self, **kwargs):

    lib.kwargs.set_kwargs(self, **kwargs)

    super(ScreenSaver, self).__init__(**kwargs)  
    
    self.pos = (lib.config.viewport[self.clientIdIndex][0], 0)
    self.width = abs(lib.config.viewport[self.clientIdIndex][0] - lib.config.viewport[self.clientIdIndex][1])

    self.scan_duration = SCAN_DURATION / Window.width * (self.width)

    self.points = []
    self.trigger_points = []
        
    # ZoneOfInterest
    self.shapes = []
    
    for zi in lib.config.zones_of_interest[self.clientIdIndex]:
      self.shapes.append( ZoneOfInterest( img=kivy.core.image.Image(zi[0]),
                                          pos=zi[1],
                                          alpha_index=1.0) )

    # Scaner
    self.scan_endMessageSent = False
    self.screensaver_touchedMessageSent = False
    self.fadeInMessageReceived = False
      
    self.scanner = kivy.uix.image.Image(source=SCAN_IMG_PATH, size=(218,768), color=(1,1,1,1), pos=(0 - 218,0))
    self.scanner.pos = (self.pos[0] - self.scanner.width,0)
        
    
    self.mask = Widget()
    self.mask.canvas.add(Color(0,0,0,1,mode="rgb"))
    if self.clientIdIndex == 0:
      self.mask.canvas.add(Rectangle(size=self.scanner.size, pos=(self.pos[0] - self.scanner.width,0)))
    else:
      self.mask.canvas.add(Rectangle(size=self.scanner.size, pos=(self.pos[0] + self.width,0)))    
    
    # cartel
#    self.cartel = Label(text="PlaneWhite", pos=(600,650), font_size=60, color=(1,1,1,1), halign="right")
#    self.touch_me = Label(text="by Carina Ow uber star", pos=(600,600), font_size=20, color=(1,1,1,1), halign="right")
#    self.add_widget(self.cartel)
#    self.add_widget(self.touch_me)
    

# basis
  def start(self, dt=False):
    # start is called on each scan, not only when changin mode.
    print ("ScreenSaver start() called")
    self.scan_endMessageSent = False
    self.scan()


  def stop(self):
    print( "ScreenSaver stop() called")
    self.reset()

    
  def reset(self):
    self.screensaver_touchedMessageSent = False    
    self.fadeInMessageReceived = False
    self.points = []
    self.trigger_points = []
    
    # remove shapes widgets
    for shape in self.shapes:
      self.remove_widget(shape)

    self.draw_ellipse()
    

  def fadein(self):
    self.fadeInMessageReceived = True
    print ("ScreenSaver fadeIn() called")
    self.points = []
    self.draw_ellipse()

    for shape in self.shapes:
      shape.alpha = 0.0
      shape.fadeIn()
      self.add_widget(shape)


# Custom methods
  def scan(self, dt=False):        
    self.scanner.pos = (self.pos[0] - self.scanner.width,0) # hide it outside the viewport

    a1 = Animation(pos=(self.pos[0] + self.width, 0), duration=self.scan_duration)
    a1.bind(on_start=self.add_scanner)
    a1.bind(on_progress=self.syncServerCommunication)
    a1.bind(on_complete=self.remove_scanner)
    a1.start(self.scanner)    


  def add_scanner(self, target=False, dt=False):
    if self.children.count(self.scanner) == 0:

      self.add_widget(self.scanner)
      self.add_widget(self.mask)


  def remove_scanner(self, target=False, dt=False):
#    self.scanner.pos = (self.pos[0] - self.scanner.width,0) # hide it outside the viewport    

    if self.children.count(self.scanner) > 0:  
      while self.children.count(self.scanner) > 0:
        self.remove_widget(self.scanner)

      self.remove_widget(self.mask)


  def draw_ellipse(self):
    self.remove_scanner()
    
    self.canvas.clear()
       
    with self.canvas:
      StencilPush()
      
      for pos in self.points:
        diameter = 100
        Ellipse(pos=(pos[0] - diameter / 2, pos[1] - diameter / 2), size=(diameter, diameter))
      
      StencilUse()      
      for shape in self.shapes:
        shape.object
        Rectangle(texture=shape.img.texture, size=shape.img.size, pos=shape.pos)
      
      StencilPop()

    self.add_scanner()
    

  def add_trigger_point(self, touch):
    for shape in self.shapes:
      if shape.collide_point(*touch.pos):
        self.trigger_points.append(touch.pos)


# Custom Callbacks
  def syncServerCommunication(self, animation, target, progression):
    if target.x >= (self.pos[0] + self.width - target.width - NETWORK_DELAY):
      if not self.scan_endMessageSent:
        if not self.fadeInMessageReceived:
          print ("Scan reached right of screen.")
          self.controller.sendMessage("scan_end") # sync next client
          self.scan_endMessageSent = True


# Kivy Callbacks
  def on_touch_down(self, touch):
    if not self.screensaver_touchedMessageSent:
      self.points.append(touch.pos)
      self.draw_ellipse()
      self.add_trigger_point(touch)


  def on_touch_move(self, touch):
    if not self.screensaver_touchedMessageSent:
      self.points.append(touch.pos)
      self.draw_ellipse()
      self.add_trigger_point(touch)


  def on_touch_up(self, touch):        
    if len(self.trigger_points) > TRIGGER_POINTS_THRESHOLD:
      if not self.screensaver_touchedMessageSent:
        print ("Screensaver touched. ", len(self.trigger_points))
        
        self.controller.sendMessage("screensaver_touched") # go to next mode
        self.screensaver_touchedMessageSent = True



########################################################################      
if __name__ == '__main__':
  class ScreenSaverApp(App):
      def build(self):
        base = Widget()
        ss = ScreenSaver()
        Clock.schedule_interval(ss.start, 2)
        base.add_widget(ss)
        
        return base
  ScreenSaverApp().run()
