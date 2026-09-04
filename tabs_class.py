import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from tkinter import simpledialog

def update_recursive(target, source):
    """
    Recursively updates the target dictionary with data from the source.
    Nested dictionaries are merged, not replaced.
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            # If both values are dictionaries, recurse
            update_recursive(target[key], value)
        else:
            # Otherwise, update/add the value
            target[key] = value
    target = {key: target[key] for key in source.keys()}

    return target


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

        # Bind events
        widget.bind('<Enter>', self.show_tip, '+')
        widget.bind('<Leave>', self.hide_tip, '+')

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return

        # Get mouse coordinates
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        # Create tooltip window
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window borders
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Arial", 10))
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class NavigableNotebook(ttk.Notebook):
    def __init__(self, parent, order=None,
                 tooltip: bool = False,
                 enable_close: bool = True,         # Close button on tabs
                 cyclically: bool = False,          # Cyclical tab navigation
                 **kwargs):

        # Initialize state variables
        self.font = tkFont.Font(parent, font=kwargs.pop('font', ('Arial', 10)))
        self.color = kwargs.pop('color', {'bg': 'white', 'fg': 'gray40'})
        self.color_bg = kwargs.pop('color_bg', {'bg_in': '#f0f0f0', 'bg_out': 'white'})
        self.color_tab = kwargs.pop('color_tab',
                                    {'background': [('bgcolor', '#d9d9d9'), ('fgcolor', '#000000'), ('tabfg1', 'black')],
                                     'foreground': [('tabfg2', 'white'), ('tabbg1', '#d9d9d9'), ('tabbg2', 'gray40')]})

        super().__init__(parent, **kwargs)

        self.order = order or {
            'first': {'visible': True},   # "First" button
            'prev': {'visible': True},    # "Previous" button
            'counter': {'visible': True}, # "1/10" counter
            'close': {'visible': True},   # "Close" button
            'add': {'visible': True},     # "Add" button
            'menu': {'visible': True},    # "Menu" dropdown button
            'next': {'visible': True},    # "Next" button
            'last': {'visible': True}     # "Last" button
        }

        self._drag_start_index = None
        self._drag_tab_id = None
        self._is_dragging = False
        self._click_on_close = False
        self._is_processing = False

        self.tooltip = tooltip
        self.enable_close = enable_close
        self.cyclically = cyclically
        self.tab_counter = 0

        self.create_notebook_style()

        self.show = {
            'first': {'item': None, 'right': False, 'tooltip': 'First', 'visible': True,
                      'setting': {'text': '|<', 'command': self.go_to_first, **self.color, 'font': self.font}},
            'prev': {'item': None, 'right': False, 'tooltip': 'Previous', 'visible': True,
                     'setting': {'text': '<', 'command': self.go_to_prev, 'font': self.font, **self.color}},

            'counter': {'item': None, 'right': False, 'tooltip': 'Counter', 'visible': True,
                        'setting': {'text': f'{0:3}/{0:<3}', 'command': self.show_tabs_list, 'font': self.font, **self.color}},

            'next': {'item': None, 'right': False, 'tooltip': 'Next', 'visible': True,
                     'setting': {'text': '>', 'command': self.go_to_next, 'font': self.font, **self.color}},
            'last': {'item': None, 'right': False, 'tooltip': 'Last', 'visible': True,
                     'setting': {'text': '>|', 'command': self.go_to_last, 'font': self.font, **self.color}},
            'close': {'item': None, 'right': True, 'tooltip': 'Close tab', 'visible': True,
                      'setting': {'text': '✕', 'command': self.close_current_tab, 'font': self.font, **self.color}},
            'add': {'item': None, 'right': True, 'tooltip': 'Add tab', 'visible': True,
                    'setting': {'text': '+', 'command': self.add_new_tab, 'font': self.font, **self.color}},
            'menu': {'item': None, 'right': True, 'tooltip': 'Menu', 'visible': True,
                     'setting': {'text': '☰', 'command': self.show_menu, 'font': self.font, **self.color}}
        }

        self.show = update_recursive(self.show, self.order)

        # Create buttons (only selected ones)
        self._create_buttons()

        # Apply style and update margins
        self.configure(style=self.style_name)

        # Bind events
        self.bind('<Button-1>', self._on_mouse_down)
        self.bind('<ButtonRelease-1>', self._on_mouse_up)
        self.bind('<B1-Motion>', self._on_drag_motion)
        self.bind('<Motion>', self._mouse_over)
        self.bind('<Double-Button-1>', self.rename_current_tab)

        self.bind('<<NotebookTabChanged>>', self._update_buttons_state)
        self.bind('<MouseWheel>', self._on_mousewheel)
        self.bind('<Shift-MouseWheel>', self._on_mousewheel)
        self.bind('<Control-Tab>', self._on_mousewheel)
        self.bind('<Control-Shift-Tab>', self._on_mousewheel)

        self.bind('<Configure>', self._on_configure)

        # Initialize state
        self.after(100, self._update_buttons_state)
        self.tabs_width = self.winfo_width() - (self._calculate_left_margin() + self._calculate_right_margin())

    # === PROPERTIES ===
    @property
    def total_tabs(self):
        """Total number of tabs"""
        return len(self.tabs())

    @property
    def current_index(self):
        """Index of the current tab"""
        try:
            return self.index('current')
        except tk.TclError:
            return 0

    @property
    def has_tabs(self):
        """Whether there are any tabs"""
        return self.total_tabs > 0

    # === BUTTON CREATION METHODS ===

    def create_notebook_style(self):
        self.style = ttk.Style()
        self.style.theme_use('default')

        self.style_name = f"Custom.TNotebook.{id(self)}"
        self.style.configure(f"{self.style_name}.Tab", padding=0, font=self.font)

        if not self.enable_close:
            self.style.layout(self.style_name, self.style.layout('TNotebook'))
            return

        close_image_data = '''R0lGODlhDAAMAIQUADIyMjc3Nzk5OT09PT8/P0JCQkVFRU1NTU5OTlFRUVZWVmBgYGFhYWlpaXt7e6CgoLm5ucLCwszMzNbW1v//////////////////////////////////// ///////////yH5BAEKAB8ALAAAAAAMAAwAAAUt4CeOZGmaA5mSyQCIwhCUSwEIxHHW+fkxBgPiBDwshCWHQfc5KkoNUtRHpYYAADs='''
        close_white_image_data = '''R0lGODlhDAAMAPQfAM3NzcjIyMbGxsLCwsDAwL29vbq6urKysrGxsa6urqmpqZ+fn56enpaWloSEhF9fX0ZGRj09PTMzMykpKQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///yH5BAEKAB8ALAAAAAAMAAwAAAUt4CeOZGmaA5mSyQCIwhCUSwEIxHHW+fkxBgPiBDwshCWHQfc5KkoNUtRHpYYAADs='''
        close_active_image_data = '''R0lGODlhDAAMAIQcALwuEtIzFL46INY0Fdk2FsQ8IdhAI9pAIttCJNlKLtpLL9pMMMNTPcVTPdpZQOBbQd60rN+1rfCzp+zLxPbMxPLX0vHY0/fY0/rm4vvx8Pvy8fzy8P//////// ///////yH5BAEKAB8ALAAAAAAMAAwAAAVHYLQQZEkukWKuxEgg1EPCcilx24NcHGYWFhxP0zANBEEOhhFYGSocTsax2imDOdNtiez9JszjpEg4EAaA5jlNUEASLFICEgIAOw=='''
        close_pressed_image_data = '''R0lGODlhDAAMAIQeAJ8nD64qELErELMsEqIyG6cyG7U1HLY2HrY3HrhBKrlCK6pGM7lDLKtHM7pKNL5MNtiViNaon+GqoNSyq9WzrNyyqtuzq+O0que/t+bIwubJw+vJw+vTz+zTz////////yH5BAEKAB8ALAAAAAAMAAwAAAVJIMUMZEkylGKuwzgc0kPCcgl123NcHWYWFs6Gp2mYBIRgR7MIrAwVDifjWO2WwZzpxkxyfKVCpImMGAeIgQDgVLMHikmCRUpMQgA7'''

        self.img_close = tk.PhotoImage("img_close", data=close_image_data)
        self.img_close_white = tk.PhotoImage("img_close_white", data=close_white_image_data)
        self.img_closeactive = tk.PhotoImage("img_closeactive", data=close_active_image_data)
        self.img_closepressed = tk.PhotoImage("img_closepressed", data=close_pressed_image_data)

        if 'close' not in self.style.element_names():
            self.style.element_create("close", "image", self.img_close_white,
                                      ('active', 'pressed', self.img_closepressed),
                                      ('active', 'alternate', self.img_closeactive),
                                      ('selected', self.img_close),
                                      ('!selected', 'active', self.img_close),
                                      border=8, sticky='')

        self.style.layout(self.style_name, [("ClosetabNotebook.client", {"sticky": "nswe"})])
        self.style.layout(f"{self.style_name}.Tab", [
            ("ClosetabNotebook.tab",
             {"sticky": "nswe",
              "children": [
                  ("ClosetabNotebook.padding", {
                      "side": "top",
                      "sticky": "nswe",
                      "children": [
                          ("ClosetabNotebook.focus", {
                              "side": "top",
                              "sticky": "nswe",
                              "children": [
                                  ("ClosetabNotebook.label", {"side": "left", "sticky": ''}),
                                  ("ClosetabNotebook.close", {"side": "left", "sticky": ''}),
                              ]})]})]})])

        _bgcolor = '#d9d9d9'
        _fgcolor = '#000000'
        _tabfg1 = 'black'
        _tabfg2 = 'white'
        _tabbg1 = '#d9d9d9'
        _tabbg2 = 'gray40'

        self.style.map('ClosetabNotebook.Tab',
                       background=[('selected', _bgcolor), ('active', _tabbg1), ('!active', _tabbg2)],
                       foreground=[('selected', _fgcolor), ('active', _tabfg1), ('!active', _tabfg2)])

    def _create_label_button(self, **kwargs):
        """Creates a label with button functionality"""
        command = kwargs.pop('command', None)
        label = tk.Label(self, **kwargs)
        label._command = command

        label.bind('<Button-1>', lambda e: label._command(e) if label['state'] != 'disabled' else None)
        label.bind('<Enter>', lambda e: label.config(bg=self.color_bg['bg_in']) if label['state'] != 'disabled' else None)
        label.bind('<Leave>', lambda e: label.config(bg=self.color_bg['bg_out']) if label['state'] != 'disabled' else None)

        return label

    def _get_button_width(self, item):
        """Gets the actual width of a button"""
        if item is None:
            return 0
        item.update_idletasks()
        return item.winfo_width() + 2  # +2 for padding

    def _calculate_left_margin(self):
        """
        Calculates the left margin for the tab bar
        based on the actual width of visible left buttons
        """
        margin = 5  # base margin
        # Navigation buttons
        for btn_key in self.show.keys():
            if self.show[btn_key]['visible'] and not self.show[btn_key]['right']:
                margin += self._get_button_width(self.show[btn_key]['item'])
        return margin

    def _calculate_right_margin(self):
        """
        Calculates the right margin for the tab bar
        based on the actual width of visible right buttons
        """
        margin = 5  # base margin

        for btn_key in self.show.keys():
            if self.show[btn_key]['visible'] and self.show[btn_key]['right']:
                margin += self._get_button_width(self.show[btn_key]['item'])

        return margin

    def _get_widget_width(self, widget):
        """Gets the actual width of a widget"""
        if widget is None:
            return 0
        widget.update_idletasks()
        return widget.winfo_width() + 2  # +2 for padding

    def _update_margins(self):
        """Updates margins for the tab bar based on actual button sizes"""
        left_margin = self._calculate_left_margin()
        right_margin = self._calculate_right_margin()

        # Configure a unique style for this instance
        self.style.configure(self.style_name, tabmargins=[left_margin, 0, right_margin, 0])

    def _update_button_positions(self):
        """Updates positions of all buttons"""
        width = self.winfo_width()
        left_x = 5
        right_x = width - 5
        for btn_key in self.show.keys():
            if self.show[btn_key]['visible']:
                width = self._get_button_width(self.show[btn_key]['item'])
                if self.show[btn_key]['right']:
                    right_x -= width
                    self.show[btn_key]['item'].place_configure(x=right_x)
                else:
                    self.show[btn_key]['item'].place_configure(x=left_x)
                    left_x += width

    def _create_buttons(self):
        """Creates all buttons through loops"""
        width = self.winfo_width()
        left_x = 5
        right_x = width - 5
        for key in self.show.keys():
            if self.show[key]['visible']:
                # if key == 'counter':
                #     self.show[key]['item'] = tk.Label(self, **self.show[key]['setting'])
                # else:
                #     self.show[key]['item'] = self._create_label_button(**self.show[key]['setting'])

                self.show[key]['item'] = self._create_label_button(**self.show[key]['setting'])
                if self.tooltip and 'tooltip' in self.show[key]:
                    ToolTip(self.show[key]['item'], self.show[key]['tooltip'])

                geo = self._get_text_geo(self.show[key]['setting']['text'])
                if geo[0] < geo[1]:
                    geo = (geo[1], geo[1])

                if self.show[key]['right']:
                    right_x -= geo[0]
                    self.show[key]['item'].place(x=right_x, height=geo[1], width=geo[0])
                else:
                    self.show[key]['item'].place(x=left_x, height=geo[1], width=geo[0])
                    left_x += geo[0]

    def _on_configure(self, event):
        """Resize event handler"""
        self.tabs_width = self.winfo_width() - (self._calculate_left_margin() + self._calculate_right_margin())
        self._update_margins()
        self._update_button_positions()
        self._update_buttons_state()
        self._update_tab(event)

    def _update_buttons_state(self, event=None):
        """Updates button states"""

        if 'counter' not in self.show:
            return

        current = self.current_index
        total = self.total_tabs

        if current >= 0 and total > 0:
            # Update counter

            if self.show['counter']['visible']:
                self.show['counter']['item'].config(text=f"{current + 1:3}/{total:<3}")

        else:
            if self.show['counter']['visible']:
                self.show['counter']['item'].config(text=self.show['counter']['setting']['text'])

    def _return_break(self, event):
        return "break"

    def _on_mousewheel(self, event):
        """Mouse wheel event handler"""
        self._update_tab(event)
        return "break"  # Prevent further event processing

    def _update_tab(self, event):
        if self._is_processing:
            return "break"
        else:
            self._is_processing = True

        index = self.current_index
        len_tabs = self.total_tabs

        if event:
            if hasattr(event, 'keysym') and event.keysym == 'Tab':
                state = event.state
                shift_pressed = bool(state & 0x1)
                control_pressed = bool(state & 0x4)
                if control_pressed and shift_pressed:
                    # Ctrl+Shift+Tab - previous tab
                    if index > 0:
                        index = index - 1
                    else:
                        if self.cyclically:
                            index = len_tabs - 1
                        else:
                            self._is_processing = False
                            return None

                elif control_pressed:
                    if index < len_tabs - 1:
                        index = index + 1
                    else:
                        if self.cyclically:
                            index = 0
                        else:
                            self._is_processing = False
                            return None

            elif hasattr(event, 'delta'):
                if event.delta < 0:
                    if index < len_tabs - 1:
                        index = index + 1
                    else:
                        if self.cyclically:
                            index = 0
                        else:
                            self._is_processing = False
                            return None

                elif event.delta > 0:
                    if index > 0:
                        index = index - 1
                    else:
                        if self.cyclically:
                            index = len_tabs - 1
                        else:
                            self._is_processing = False
                            return None

            self.tab(index, state='normal')
            self.select(index)

        else:
            self._is_processing = False
            return None

        width_temp = self._get_text_geo(self.tab([index], 'text'))[0]
        if self.enable_close:
            width_temp += 15

        for i in range(1, len_tabs):
            if index + i < len_tabs:
                width_temp += self._get_text_geo(self.tab([index + i], 'text'))[0]
                if self.enable_close:
                    width_temp += 15
                if width_temp <= self.tabs_width:
                    self.tab(index + i, state='normal')
                else:
                    self.tab(index + i, state='hidden')

            if index - i >= 0:
                width_temp += self._get_text_geo(self.tab([index - i], 'text'))[0]
                if self.enable_close:
                    width_temp += 15
                if width_temp <= self.tabs_width:
                    self.tab(index - i, state='normal')
                else:
                    self.tab(index - i, state='hidden')

        self._is_processing = False
        return None

    def _get_text_geo(self, text):
        self.update()

        # Measure text width in pixels
        text_width = self.font.measure(text)

        # Add padding that the theme adds around the text
        # Usually about 10-15 pixels on each side
        padding = 4  # empirical value

        width = text_width + padding
        height = self.font.metrics('linespace') + 4
        return width, height

    # === EVENT HANDLERS ===
    def _on_mouse_down(self, event):
        """Mouse down event handler - determines what was clicked"""
        widget = event.widget
        element = widget.identify(event.x, event.y)

        # Check if click is on close button
        if "close" in element and self.total_tabs > 1:
            self._click_on_close = True
            index = self._get_tab_index_at_position(widget, event.x, event.y)
            widget.state(['pressed'])
            widget._active = index
            self._drag_start_index = None
            return

        self._click_on_close = False

        # Check if click is on a tab
        try:
            index = self._get_tab_index_at_position(widget, event.x, event.y)
            if index is not None and index < self.total_tabs:
                self._drag_start_index = index
                self._drag_tab_id = widget.tabs()[index]
                self._is_dragging = False
            else:
                self._drag_start_index = None
                self._drag_tab_id = None
        except (tk.TclError, IndexError):
            self._drag_start_index = None
            self._drag_tab_id = None

    def _on_mouse_up(self, event):
        """Mouse up event handler"""
        widget = event.widget

        # If click was on close button - handle closing
        if self._click_on_close:
            if widget.instate(['pressed']):
                element = widget.identify(event.x, event.y)
                index = self._get_tab_index_at_position(widget, event.x, event.y)
                if "close" in element and widget._active == index and index is not None:
                    if index < self.total_tabs:
                        widget.forget(index)
                        widget.event_generate("<<NotebookTabClosed>>")
                        self._update_tab('close_tab')
                widget.state(['!pressed'])
                widget._active = None
            self._click_on_close = False
            self._drag_start_index = None
            self._drag_tab_id = None
            self._is_dragging = False
            widget.config(cursor="")
            return

        # If there was a drag
        if self._is_dragging and self._drag_start_index is not None:
            index = self._get_tab_index_at_position(widget, event.x, event.y)
            if index is not None and index != self._drag_start_index:
                self._move_tab(self._drag_start_index, index)

        # Reset state
        self._drag_start_index = None
        self._drag_tab_id = None
        self._is_dragging = False
        widget.config(cursor="")

    def _on_drag_motion(self, event):
        """Mouse drag motion handler"""
        widget = event.widget
        widget.config(cursor="sb_h_double_arrow")

        if self._drag_start_index is None:
            return

        # Mark that dragging has started
        if not self._is_dragging:
            self._is_dragging = True
            widget.config(cursor="sb_h_double_arrow")

        index = self._get_tab_index_at_position(widget, event.x, event.y)

        if index is not None and index < self.total_tabs and index != self._drag_start_index:
            self._move_tab(self._drag_start_index, index)
            self._drag_start_index = index

    def _get_tab_index_at_position(self, widget, x, y):
        """Gets tab index at coordinates with error protection"""
        try:
            index = widget.index("@%d,%d" % (x, y))
            return index
        except (tk.TclError, IndexError):
            pass
        return None

    def _mouse_over(self, event):
        widget = event.widget
        element = widget.identify(event.x, event.y)
        if "close" in element:
            widget.state(['alternate'])
        else:
            widget.state(['!alternate'])

    def _move_tab(self, from_index, to_index):
        """Moves tab from from_index to to_index"""
        if from_index == to_index:
            return

        self.insert(to_index, self.tabs()[from_index], **self.tab(from_index))
        self.update_idletasks()

    # === BUTTON VISIBILITY MANAGEMENT METHODS ===

    def show_button_group(self, group_name, visible):
        """
        Shows or hides a group of buttons
        """
        for item in group_name.split('_'):
            if item in self.show:
                self.show[item]['visible'] = visible

        self._destroy_buttons()
        self._create_buttons()
        self._update_margins()
        self._update_button_positions()
        self._update_buttons_state()

    def _destroy_buttons(self):
        """Destroys all buttons"""
        for key in self.show.keys():
            if self.show[key]['item']:
                self.show[key]['item'].destroy()
                self.show[key]['item'] = None

    def get_button_state(self, group_name):
        """Returns the current state of a button group"""
        if group_name in self.show:
            return self.show[group_name]['visible']
        return None

    # === NAVIGATION METHODS ===

    def go_to_first(self, event=None):
        """Go to first tab"""
        if self.total_tabs > 0:
            self.select(0)
            self._update_tab('go_to_first')

    def go_to_prev(self, event=None):
        """Go to previous tab"""
        current = self.current_index
        if current > 0:
            self.select(current - 1)
            self._update_tab('go_to_prev')

    def go_to_next(self, event=None):
        """Go to next tab"""
        current = self.current_index
        if current < self.total_tabs - 1:
            self.select(current + 1)
            self._update_tab('go_to_next')

    def go_to_last(self, event=None):
        """Go to last tab"""
        if self.total_tabs > 0:
            self.select(self.total_tabs - 1)
            self._update_tab('go_to_last')

    # === TAB MANAGEMENT METHODS ===

    def add_new_tab(self, event=None, text=None, content=None):
        """Adds a new tab"""
        self.tab_counter += 1

        if text is None:
            text = f"Tab {self.tab_counter}"

        # Create tab
        tab = ttk.Frame(self)

        # Add default content
        if content is None:
            ttk.Label(tab, text=f"Content of {text}", font=('Arial', 14)).pack(pady=30)
            ttk.Label(tab, text=f"This is the content of tab {self.tab_counter}").pack(pady=10)
        else:
            content(tab)

        # Add to Notebook
        self.add(tab, text=text)
        self.select(tab)
        self._update_tab('add_new_tab')
        self._update_buttons_state()
        return tab

    def close_current_tab(self, event=None):
        """Closes the current tab"""
        current = self.current_index
        if current >= 0 and self.total_tabs > 1:
            self.forget(current)
            self._update_tab('close_current_tab')
            self._update_buttons_state()

    def close_tab(self, index):
        """Closes a tab by index"""
        if 0 <= index < self.total_tabs and self.total_tabs > 1:
            self.forget(index)
            self._update_tab('close_tab')
            self._update_buttons_state()

    def close_other_tabs(self):
        """Closes all tabs except the current one"""
        current = self.current_index
        if current >= 0:
            for i in range(self.total_tabs - 1, current, -1):
                self.forget(i)
            for i in range(current - 1, -1, -1):
                self.forget(i)
            self._update_buttons_state()

    def rename_current_tab(self, event=None):
        """Renames the current tab"""
        if event:
            index = self._get_tab_index_at_position(event.widget, event.x, event.y)
        else:
            index = self.current_index
        if index is not None and 0 <= index < self.total_tabs:
            self._show_rename_dialog(index)
            self._update_tab('rename_tab')

    def rename_tab(self, index, new_text):
        """Renames a tab by index"""
        if 0 <= index < self.total_tabs:
            self.tab(index, text=new_text)
            self._update_tab('rename_tab')

    def duplicate_current_tab(self):
        """Duplicates the current tab"""
        current = self.current_index
        if current >= 0:
            tab_id = self.tabs()[current]
            text = self.tab(tab_id, "text")

            # Create a copy tab
            new_tab = ttk.Frame(self)
            ttk.Label(new_tab, text=f"Copy: {text}", font=('Arial', 14)).pack(pady=30)
            ttk.Label(new_tab, text="This is a duplicate tab").pack(pady=10)

            self.add(new_tab, text=f"{text} (copy)")
            self.select(new_tab)
            self._update_buttons_state()
            self._update_tab('duplicate_current_tab')

    # === HELPER METHODS ===

    def _show_rename_dialog(self, index):
        """Shows the rename dialog"""
        new_name = simpledialog.askstring(
            "Rename Tab",
            "Enter new tab name:",
            initialvalue=self.tab(index, "text"),
            parent=self
        )

        if new_name is not None:
            new_name = new_name.strip()
            if new_name:
                self.tab(index, text=new_name)


    def show_tab(self, tab):
        index = self.index(tab)
        self.tab(index, state='normal')
        self.select(index)
        self._update_tab('show_tab')

    def show_tabs_list(self, event=None):
        """Shows the context menu for tabs list"""
        menu = tk.Menu(self, tearoff=0)
        for tab in self.tabs():
            menu.add_command(label=self.tab(tab, 'text'), command=lambda t=tab: self.show_tab(t))

        # Show menu below the button
        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty() + event.widget.winfo_height() + 2
        menu.post(x, y)

    def show_menu(self, event=None):
        """Shows the context menu"""
        if self.show['menu']['visible']:
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label="Add tab", command=self.add_new_tab)
            menu.add_command(label="Close current", command=self.close_current_tab)
            menu.add_command(label="Close others", command=self.close_other_tabs)
            menu.add_separator()
            menu.add_command(label="Rename", command=self.rename_current_tab)
            menu.add_command(label="Duplicate", command=self.duplicate_current_tab)
            menu.add_separator()
            menu.add_command(label="Go to first", command=self.go_to_first)
            menu.add_command(label="Go to last", command=self.go_to_last)

            # Show menu below the button
            x = event.widget.winfo_rootx()
            y = event.widget.winfo_rooty() + event.widget.winfo_height() + 2
            menu.post(x, y)

    def get_tabs_info(self):
        """Returns information about all tabs"""
        tabs_info = []
        for i, tab_id in enumerate(self.tabs()):
            tabs_info.append({
                'index': i,
                'text': self.tab(tab_id, "text"),
                'widget': self.nametowidget(tab_id)
            })
        return tabs_info

    def get_current_tab_info(self):
        """Returns information about the current tab"""
        current = self.current_index
        if current >= 0:
            tab_id = self.tabs()[current]
            return {
                'index': current,
                'text': self.tab(tab_id, "text"),
                'widget': self.nametowidget(tab_id)
            }
        return None

# === DEMONSTRATION CLASS ===
class DemoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Label buttons instead of ttk.Button")
        self.root.geometry("1000x800")

        # Dictionary with configurations for different Notebooks
        self.notebook_configs = {
            'full': {
                'name': 'Full set',
                'description': 'All buttons enabled - Label style',
                'params': {'font': ('Arial', 10), 'tooltip': True, 'cyclically': True},
                'tabs_count': 18,
                'tab_prefix': 'Tab'
            },
            'minimal': {
                'name': 'Minimal',
                'description': 'Only navigation and close - Label',
                'params': {'font': ('Tahoma', 15)},
                'tabs_count': 8,
                'tab_prefix': 'Tab'
            },
            'navigation_only': {
                'name': 'Navigation only',
                'description': 'Only navigation - Label',
                'params': {
                    'order': {
                        'first': {'visible': True},   # "First" button
                        'prev': {'visible': True},    # "Previous" button
                        'counter': {'visible': True},  # "1/10" counter
                        'close': {'visible': False},   # "Close" button
                        'add': {'visible': False},     # "Add" button
                        'menu': {'visible': False},    # "Menu" button
                        'next': {'visible': True},     # "Next" button
                        'last': {'visible': True}      # "Last" button
                    }
                },
                'tabs_count': 8,
                'tab_prefix': 'Tab'
            },
            'management_only': {
                'name': 'Management only',
                'description': 'Only tab management - Label',
                'params': {
                    'order': {
                        'first': {'visible': True},   # "First" button
                        # 'prev': {'visible': False},    # "Previous" button
                        # 'counter': {'visible': False},  # "1/10" counter
                        # 'close': {'visible': True},    # "Close" button
                        # 'add': {'visible': True},      # "Add" button
                        # 'menu': {'visible': True},     # "Menu" button
                        # 'next': {'visible': False},    # "Next" button
                        'last': {'visible': True, 'right': True}     # "Last" button
                    }
                },
                'tabs_count': 8,
                'tab_prefix': 'Tab'
            },
            'custom_only': {
                'name': 'Custom management',
                'description': 'Custom tab management - Label',
                'params': {
                    'order': {
                        'first': {'visible': True, 'setting': {'text': '|←|'}},
                        'prev': {'visible': False},    # "Previous" button
                        'menu': {'visible': True},     # "Menu" button
                        'add': {'visible': True, 'setting': {'text': '++'}},      # "Add" button
                        'close': {'visible': True, 'setting': {'text': '**'}},  # "Close" button
                        'last': {'visible': True, 'right': True, 'setting': {'text': '|→|'}},
                        'next': {'visible': False, 'right': True},   # "Next" button
                        'counter': {'visible': True, 'right': True},  # "1/10" counter
                    },
                    'font': ('Tahoma', 15, 'bold italic')
                },
                'tabs_count': 8,
                'tab_prefix': 'Tab'
            }
        }

        # Create main Notebook for demonstration
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(expand=True, fill='both')

        # Create all Notebooks from configurations
        self.created_notebooks = {}
        for config_key, config in self.notebook_configs.items():
            self._create_notebook_from_config(config_key, config)

        # Add info panel
        self._create_info_panel()

    def _create_notebook_from_config(self, key, config):
        """Creates a Notebook based on configuration from dictionary"""
        tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(tab, text=config['name'])

        # Create NavigableNotebook with parameters from dictionary
        notebook = NavigableNotebook(tab, **config['params'])
        notebook.pack(expand=True, fill='both')

        # Add tabs
        for i in range(config['tabs_count']):
            notebook.add_new_tab(text=f"{config['tab_prefix']} {i+1}")

        # Save reference
        self.created_notebooks[key] = notebook

        # Add description
        ttk.Label(tab, text=config['description'], font=('Arial', 10)).pack(pady=5)

        # Add button to add tabs
        ttk.Button(tab, text="Add tab", command=lambda n=notebook: n.add_new_tab()).pack(pady=5)

    def _create_info_panel(self):
        """Creates an info panel with control buttons"""
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(info_frame, text="Button visibility control (Label):",
                  font=('Arial', 10, 'bold')).pack(side='left', padx=5)

        # Button to toggle visibility across all Notebooks
        def toggle_all_groups(group_name):
            """Toggles visibility of a group across all Notebooks"""
            current_state = None
            for notebook in self.created_notebooks.values():
                state = notebook.get_button_state(group_name.split('_')[0])
                if current_state is None:
                    current_state = state
                # Toggle to the opposite state
                notebook.show_button_group(group_name, not current_state)

            # Update button text
            for btn in info_frame.winfo_children():
                if isinstance(btn, ttk.Button) and btn['text'].startswith(group_name):
                    new_state = "ON" if not current_state else "OFF"
                    btn.config(text=f"{group_name}: {new_state}")

        # Create buttons for each group
        for group in ['first_last', 'prev_next', 'counter', 'close', 'add', 'menu']:
            # Get initial state from the first Notebook
            first_notebook = next(iter(self.created_notebooks.values()))
            state = "ON" if first_notebook.get_button_state(group) else "OFF"

            btn = ttk.Button(
                info_frame,
                text=f"{group}: {state}",
                command=lambda g=group: toggle_all_groups(g)
            )
            btn.pack(side='left', padx=2)

        # Reset button
        def reset_all():
            """Resets all settings to original"""
            for key, notebook in self.created_notebooks.items():
                config = self.notebook_configs[key]
                # Update visibility of each group
                for group, value in config['params'].items():
                    # Convert show_first_last -> first_last
                    group_name = group.replace('show_', '')
                    notebook.show_button_group(group_name, value)

            # Update button text
            for btn in info_frame.winfo_children():
                if isinstance(btn, ttk.Button) and '_' in btn['text']:
                    group = btn['text'].split(':')[0]
                    first_notebook = next(iter(self.created_notebooks.values()))
                    state = "ON" if first_notebook.get_button_state(group) else "OFF"
                    btn.config(text=f"{group}: {state}")

        ttk.Button(info_frame, text="Reset all",
                   command=reset_all).pack(side='left', padx=10)

        # Information about number of Notebooks
        ttk.Label(info_frame,
                  text=f"Total Notebooks: {len(self.created_notebooks)}",
                  font=('Arial', 9)).pack(side='right', padx=5)

# Run the application
if __name__ == "__main__":
    app = DemoApp()
    app.root.mainloop()
