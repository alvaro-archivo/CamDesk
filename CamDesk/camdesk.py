#!/usr/bin/env python

import sys, os
import pygtk, gtk, gobject
import pygst
pygst.require("0.10")
import gst

class CamDesk(gtk.Window):
	
   def closeme(self, widget, event) :
	if event.keyval == gtk.keysyms.Escape :
	 gtk.main_quit()
	 
   def startme(self, widget, event) :
	if event.keyval == gtk.keysyms.F1 :
	 self.player.set_state(gst.STATE_PLAYING)
	 
   def stopme(self, widget, event) :
	if event.keyval == gtk.keysyms.F2 :
	 self.player.set_state(gst.STATE_NULL)
	 
   def properties(self, widget, event) :
	if event.keyval == gtk.keysyms.F5 :
	 self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
	 self.win.set_title("Properties")
	 self.win.set_size_request(320, 120)
	 self.win.set_resizable(False)
	 self.win.set_keep_above(True)
	 self.win.set_property('skip-taskbar-hint', True)
	 self.win.connect("destroy", self.closeproperties)
	 vbox = gtk.VBox(spacing=4)
	 hbox = gtk.HBox(spacing=4)
	 hbox2 = gtk.HBox(spacing=4)
	 
	 check = gtk.CheckButton("Pin")
	 check.set_active(True)
	 check.set_size_request(100, 35)
	 check.connect("clicked", self.pinning)
	 hbox.pack_start(check)
	 
	 scale = gtk.HScale()
	 scale.set_range(0, 100)
	 scale.set_value(100)
	 scale.set_size_request(320, 35)
	 scale.connect("value-changed", self.opac_slider)
	 
	 hbox.pack_start(scale)
	 
	 self.entry = gtk.Entry()
	 self.entry2 = gtk.Entry()
	 self.entry.set_text("width")
	 self.entry2.set_text("height")
	 hbox2.pack_start(self.entry)
	 hbox2.pack_start(self.entry2)
	 
	 hbox3 = gtk.HBox(spacing=4)
	 ok = gtk.Button("OK")
	 ok.connect("clicked", self.change_size)
	 hbox3.pack_start(ok)
	 exit = gtk.Button("Exit")
	 exit.connect("clicked", self.closeproperties)
	 hbox3.pack_start(exit)
	 
	 vbox.pack_start(hbox)
	 vbox.pack_start(hbox2)
	 vbox.pack_start(hbox3)
	  
	 self.win.add(vbox)
	 self.win.show_all()
	 
   def pinning(self, checkbox):
	if checkbox.get_active():
	  self.set_keep_above(True)
	else:
	  self.set_keep_above(False)
	 
   def opac_slider(self, w):
	 self.set_opacity(w.get_value()/100.0)
	
   def change_size(self, w):
	 width = int(self.entry.get_text())
	 height = int(self.entry2.get_text())
	 self.set_size_request(width,height)
	 
   def closeproperties(self, w):
	 self.win.hide()

   def __init__(self):
	super(CamDesk, self).__init__()
	
	self.set_position(gtk.WIN_POS_CENTER)
	self.set_title("CamDesk")
	self.set_decorated(False)
	self.set_has_frame(False)
	self.set_size_request(320, 240)
	self.set_resizable(False)
	self.set_keep_above(True)
	self.set_property('skip-taskbar-hint', True)
	gtk.window_set_default_icon_from_file('logo.png')
	self.connect("destroy", gtk.main_quit, "WM destroy")
	self.connect("key-press-event", self.closeme)
	self.connect("key-press-event", self.startme)
	self.connect("key-press-event", self.stopme)
	self.connect("key-press-event", self.properties)
	
	vbox = gtk.VBox(False, 0)
	self.add(vbox)
	
	self.movie_window = gtk.DrawingArea()
	vbox.add(self.movie_window)
	self.show_all()

	# Set up the gstreamer pipeline
	self.player = gst.parse_launch ("v4l2src ! autovideosink")

	bus = self.player.get_bus()
	bus.add_signal_watch()
	bus.enable_sync_message_emission()
	bus.connect("message", self.on_message)
	bus.connect("sync-message::element", self.on_sync_message)

   def on_message(self, bus, message):
      t = message.type
      if t == gst.MESSAGE_EOS:
	self.player.set_state(gst.STATE_NULL)
	self.startcam.set_label("Start")
      elif t == gst.MESSAGE_ERROR:
	err, debug = message.parse_error()
	print "Error: %s" % err, debug
	self.player.set_state(gst.STATE_NULL)
	self.startcam.set_label("Start")

   def on_sync_message(self, bus, message):
      if message.structure is None:
         return
      message_name = message.structure.get_name()
      if message_name == "prepare-xwindow-id":
	# Assign the viewport
	imagesink = message.src
	imagesink.set_property("force-aspect-ratio", True)
	imagesink.set_xwindow_id(self.movie_window.window.xid)
	
CamDesk()
gtk.gdk.threads_init()
gtk.main()
