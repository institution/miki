#!/usr/bin/python
import gtk
from functools import partial
import gobject, os, re
from subprocess import call
import time

import os
#from stat import *
import mimetypes
#import mimeapps
import subprocess
import sys



def get_path(r): return r[0]
def get_text(r): return r[1]
def get_mime(r): return r[2]
def get_type(r): return r[2]
def get_size(r): return r[3]
def get_rank(r): return r[4]
def get_fulltext(r): return 'type:' + r[2] + ' ' + r[1].lower()

def get_row(p):
	path,size = p.split('|||')
	mt,_ = mimetypes.guess_type(path)
	return path, ' '.join(re.findall('[a-zA-Z0-9_]+', path)) + ' ' + ('+'*path.count('+')), str(mt), int(size), path.count('+')

def buffered_stdin_lines():	
	while 1:
		try:
			x = raw_input()	
			
		except EOFError: 
			break
		
		yield x




# long list filter app
class LLFApp(object):

	def hello(self, widget):
		print "Hello World"

	def delete_event(self, widget, event):
		print "delete event occurred"
		# Change FALSE to TRUE and the main window will not be destroyed
		# with a "delete_event".
		return False

	def destroy(self):
		gtk.main_quit()

	
	def idle_refresh_list(self):
		if self.need_refresh:			
			if self.last_activity + 0.300 <= time.time():
				self.force_refresh_list()
			
		gobject.timeout_add(100, self.idle_refresh_list)
		
	def refresh_list(self):		
		self.last_activity = time.time()
		if not self.need_refresh:
			self.need_refresh = True
			
	def force_refresh_list(self):
		self.need_refresh = False
		
		ts = self.entry.get_text().split()
		
		ts = filter(lambda r: all(t in get_fulltext(r) for t in ts), self.store)
		if self.get_sort_val_func:
			def cmp_func(x,y):
				return cmp(
					self.get_sort_val_func(x), 
					self.get_sort_val_func(y)
				)				
			ts2 = sorted(ts, cmp = cmp_func, reverse = self.is_rev_sort)
			
		else:
			if self.is_rev_sort:
				ts2 = reversed(ts)
			else:
				ts2 = ts
		
		self.liststore.clear()	
		for r in ts2:
			self.liststore.append([get_text(r), get_path(r)])
		
		self.status.push(0, '{0} items'.format(len(self.liststore)))

	def get_selected_path(self):
		treeview = self.files_list
		
		treemodel, treepaths = treeview.get_selection().get_selected_rows()
		
		tp = treepaths[0]
		fpath, = treemodel.get(treemodel.get_iter(tp), 1)
		return fpath
		
	
	def open_file(self, menuitem): 
		
		##listmodel = treeview.get_model()
		#fpath = get_path(listmodel.get(listmodel.get_iter(selection), 1))
		fpath = self.get_selected_path()
	
		call(['xdg-open', os.path.join(self.root, fpath)])
	
		
		
	def open_folder(self, menuitem): 
		dirr,_ = os.path.split(self.get_selected_path())
		
		call(['xdg-open', os.path.join(self.root, dirr)])

		
	def open_with(self, menuitem): pass
	def rename_file(self, menuitem): pass

	def set_sort(self, sender, func): 
		self.get_sort_val_func = func
		self.refresh_list()
	
	def set_only(self, sender, what): 
		pass
		
	def rev_sort(self, sender): 
		self.is_rev_sort = not self.is_rev_sort
		self.refresh_list()
		
	def __init__(self, gen_data, root):
		self.root = root
		self.store = list(gen_data())
		self.need_refresh = False
		
		self.last_activity = 0
		
		self.get_sort_val_func = None
		self.is_rev_sort = False
		
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_default_size(600, 800)
		window.connect("delete_event", self.delete_event)
		window.connect("destroy", lambda _: self.destroy() )
		window.set_border_width(0)
		window.show()
		
		self.window = window
		
		entry = gtk.Entry()
		self.entry = entry
		entry.connect("changed", lambda editable: self.refresh_list() )
		entry.show()
		
		
		#button = gtk.Button("Hello World")
		#button.connect("clicked", self.hello)
		#button.connect("clicked", lambda _: self.window.destroy() )
		#button.show()
		
		liststore = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
		self.liststore = liststore
		
		tags_store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
		self.tags_store = tags_store
		
		#window.connect('change', self.refresh_list)
		
		files_list = gtk.TreeView(model=liststore)
		files_list.set_headers_visible(True)
		files_list.append_column(
			gtk.TreeViewColumn(None, gtk.CellRendererText(), text=0)
		)
		files_list.set_property('headers-visible', False)
		files_list.set_property("fixed-height-mode", True)		
		files_list.set_property('rubber-banding', True)
		files_list.set_property("enable-search", False)
		files_list.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
		files_list.connect("row-activated", self.activate)
		files_list.show()
		self.files_list = files_list
		
				
		def construct_right_click_menu(self):
			
			menu = gtk.Menu()
			x = gtk.MenuItem("Open")
			x.connect('activate', self.open_file)
			menu.append(x)
			
			x = gtk.MenuItem("Open folder")
			x.connect('activate', self.open_folder)
			menu.append(x)
						
			x = gtk.SeparatorMenuItem()
			menu.append(x)

			s = gtk.RadioMenuItem(None, 'Sort by path')		
			s.connect('activate', self.set_sort, get_path)
			menu.append(s)
			
			x = gtk.RadioMenuItem(s, 'Sort by type')
			x.connect('activate', self.set_sort, get_type)
			menu.append(x)
			
			x = gtk.RadioMenuItem(s, 'Sort by size')
			x.connect('activate', self.set_sort, get_size)
			menu.append(x)
			
			x = gtk.RadioMenuItem(s, 'Sort by rank')
			x.connect('activate', self.set_sort, get_rank)
			menu.append(x)
			
			
			x = gtk.RadioMenuItem(s, 'Do not sort')
			x.connect('activate', self.set_sort, None)
			menu.append(x)	
			x.set_active(True)
	
			x = gtk.SeparatorMenuItem()
			menu.append(x)
			
			x = gtk.CheckMenuItem('Reverse sort order')
			x.connect('activate', self.rev_sort)
			menu.append(x)
			
			menu.show_all()

			return menu

		menu = construct_right_click_menu(self)
		menu.attach_to_widget(files_list, detach_func=None)
		self.menu = menu

		def button_press_event(treeview, event):
			if event.button == 3: # right click
				# print treeview.get_path_at_pos(int(event.x), int(event.y))
				self.menu.popup(None, None, None, event.button, event.time)

		files_list.connect('button-press-event' , button_press_event)

		def handle_window_key_press(window, event):
			if event.keyval == gtk.gdk.keyval_from_name("Escape"):
				gtk.main_quit()
			
		window.connect("key-press-event", handle_window_key_press)
		    
		    		
		status = gtk.Statusbar()
		self.status = status
		status.set_property("has-resize-grip", False)
		status.push(0, 'aaa')
		status.show()
	
		files_scroll = gtk.ScrolledWindow()
		files_scroll.add(files_list)
		files_scroll.show()		
				
		
		vbox = gtk.VBox()
		vbox.pack_start(entry, expand=False, fill=True, padding=0)
		vbox.pack_start(status, expand=False, fill=True, padding=0)
		vbox.pack_start(files_scroll, expand=True, fill=True, padding=0)
		vbox.show()
		
		window.add(vbox)
		
		# ```---- init ----'''
		self.refresh_list()
		entry.grab_focus()
		
		accelgroup = gtk.AccelGroup()
		key, modifier = gtk.accelerator_parse('F2')
		accelgroup.connect_group(key, modifier, gtk.ACCEL_VISIBLE, self.ttt)
		window.add_accel_group(accelgroup)

		self.force_refresh_list()
		
		gobject.idle_add(self.idle_refresh_list)

		return
		
		#s = area.get_selection()
		#s.set_mode(gtk.SELECTION_SINGLE)
		#s.select_iter(store.get_iter_first())
		#gtk.gdk.KEY_PRESS
		#vbox = gtk.VBox(homogeneous=False, spacing=0)
		
		
	def ttt(self, *args):
		print args
		
		ids = self.get_selected_ids()

		rt = self.run_edit_text_dialog('aaa')
		
		if rt != 'aaa':
			# set tag
			pass
			
		
		
		return True
	
	
	def get_selected_ids(self):
		ls, ps = self.area.get_selection().get_selected_rows()
		
		rs = []
		# indeksy obiektow w store
		for path in ps:
			rs.append(ls.get(ls.get_iter(path), 1))
			
		return rs
	
	
	def activate(self, treeview, selection, view_column):
	
		listmodel = treeview.get_model()
		fpath = get_path(listmodel.get(listmodel.get_iter(selection), 1))
		print fpath
	
		
		call(['xdg-open', os.path.join(self.root, fpath)])
		
	def run_edit_text_dialog(self):
			
		entry = gtk.Entry()
		entry.show()

		#edit = gtk.Window()
		#edit.set_border_width(0)
		#edit.add(edit_entry)
		#edit.show()
		
		cancel = gtk.Button("Cancel")
		cancel.show()
		
		button = gtk.Button("OK")
		#button.connect("clicked", self.hello)
		#button.connect("clicked", lambda _: self.window.destroy() )
		button.show()
		
		
		dialog = gtk.Dialog("Edit tags", self.window)
		dialog.get_content_area().add(entry)
		dialog.get_action_area().add(cancel)
		dialog.get_action_area().add(button)
		dialog.run()

		
		

	def run_event_loop(self):
		gtk.main()







import subprocess
import sys

def main():
		
	mimetypes.init()
	# mimeapps.init()
		
		
	if len(sys.argv) > 1:
		root = sys.argv[1]
	else:
		root = '.'
		#gen = buffered_stdin_lines()
	
	def gen_rows():
		p = subprocess.Popen(['find', root, '-type', 'f', '-printf', '%P|||%s\n'], stdout=subprocess.PIPE)
		out,err = p.communicate()
		lines = out.split('\n')
		return [get_row(l) for l in lines if l]

	a = LLFApp(gen_rows, root)
	a.run_event_loop()
	

	

if __name__ == "__main__":
	main()

	
	
	
	
	
	
	

