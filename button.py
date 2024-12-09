import sys
import termios
import tty
import select

class Button:
        def __init__(
            self,
            x,
            y,
            Is_grid=False,
            grid=None,  
            border_color='\x1b[1;32m',
            border_color_when_hovered='\x1b[1;38;5;208m',
            label_color='\x1b[1;32m',
            label_color_when_hovered='\x1b[1;38;5;208m',
            label='Nothing yet',
            label_when_clicked='Clicked!',
            yes_label='Yes',
            no_label='No',
            padding=15,
            callback=None  
        ):
            """
            Params:
            x: button's x position
            y: button's y position
            Is_grid: Whether the button(s) will be part of a grid.
            grid: Dictionary containing button-specific settings and callbacks.
            callback: Optional function to call on button click (global for non-grid mode).
            """
            self.x = x
            self.y = y
            self.Is_grid = Is_grid
            self.grid = grid if grid else {}  
            self.border_color = border_color
            self.border_color_when_hovered = border_color_when_hovered
            self.label_color = label_color
            self.label_color_when_hovered = label_color_when_hovered
            self.label = label
            self.label_when_clicked = label_when_clicked
            self.y_label = yes_label
            self.n_label = no_label
            self.padding = padding
            self.callback = callback  

        def get_mouse_event(self):
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                while True:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        ch = sys.stdin.read(1)
                        if ch == '\x1b':
                            ch = sys.stdin.read(1)
                            if ch == '[':
                                ch = sys.stdin.read(1)
                                if ch == 'M':
                                    b = sys.stdin.read(1)
                                    x = sys.stdin.read(1)
                                    y = sys.stdin.read(1)
                                    return ord(b), ord(x) - 32, ord(y) - 32
                                elif ch == '<':
                                    event = ''
                                    while True:
                                        ch = sys.stdin.read(1)
                                        if ch in ['m', 'M']:
                                            event += ch
                                            break
                                        event += ch
                                    b, x, y = event.split(';')
                                    b = int(b)
                                    x = int(x)
                                    y = int(y.rstrip('mM'))
                                    return b, x, y
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        def draw_button(self,x, y, label, width,hovered=False):
            height = 3  

            if hovered:
                border_top_right = '╮'
                border_top_left = '╭'
                border_bottom_left = '╰'
                border_bottom_right = '╯'
                horizontal_border = '─'
                vertical_border = '│'
                border_color = self.border_color_when_hovered 
                label_color = self.label_color_when_hovered 
            else:
                border_top_left = '┌'
                border_top_right = '┐'
                border_bottom_right = '┘'
                border_bottom_left = '└'
                horizontal_border = '─'
                vertical_border = '│'
                border_color = self.border_color
                label_color = self.label_color 

            reset_color = '\x1b[0m'
            center_position = ((width - (len(label))) // 2) + x 
            sys.stdout.write(f"\x1b[{y};{x}H{border_color}{border_top_left}{horizontal_border * (width - 2)}{border_top_right}{reset_color}")
            for i in range(1, height - 1):
                sys.stdout.write(f"\x1b[{y + i};{x}H{border_color}{vertical_border}{' ' * (width - 2)}{vertical_border}{reset_color}")
                if i == 1:  
                    sys.stdout.write(f"\x1b[{y + i};{center_position}H{label_color}{label}{reset_color}")
            sys.stdout.write(f"\x1b[{y + height - 1};{x}H{border_color}{border_bottom_left}{horizontal_border * (width - 2)}{border_bottom_right}{reset_color}")
            sys.stdout.flush()
        def create_yes_or_no(self):
            """
            Returns True if the yes button is clicked and vice-versa
            """
            button_x = self.x
            button_y = self.y
            padding = self.padding
            yes_label = self.y_label
            no_label = self.n_label
            sys.stdout.write("\x1b7")
            sys.stdout.flush()
            sys.stdout.write("\033[?25l")
            sys.stdout.flush()
            sys.stdout.write("\x1b[?1000h")
            sys.stdout.write("\x1b[?1003h")
            sys.stdout.write("\x1b[?1006h") 
            sys.stdout.write("\x1b[?1015h") 
            sys.stdout.flush()
            yes_width = len(yes_label) + 4 
            no_width = len(no_label) + 4
            self.draw_button(button_x, button_y, yes_label,yes_width)
            self.draw_button(button_x + len(yes_label) + 4 + padding, button_y, no_label,no_width)
            try:
                hovered_yes = False
                hovered_no = False
                clicked_yes = False
                clicked_no = False
                while True:
                    b, x, y = self.get_mouse_event()
                    height = 3
                    if button_x <= x < button_x + yes_width and button_y <= y < button_y + height:
                        if not clicked_yes and not hovered_yes:
                            self.draw_button(button_x, button_y, '👍',yes_width,hovered=True)
                            hovered_yes = True
                        if b == 0 or b == 32:
                            clicked_yes = True
                            self.draw_button(button_x, button_y, "👍", yes_width,hovered=False)
                            return True
                    else:
                        if not clicked_yes and hovered_yes:
                            self.draw_button(button_x, button_y, yes_label,  yes_width,hovered=False)
                            hovered_yes = False
                    if button_x + yes_width + padding <= x < button_x + yes_width + padding + no_width and button_y <= y < button_y + height:
                        if not clicked_no and not hovered_no:
                            self.draw_button(button_x + yes_width + padding, button_y, '👎',  no_width,hovered=True)
                            hovered_no = True
                        if b == 0 or b == 32:
                            clicked_no = True
                            self.draw_button(button_x + yes_width + padding, button_y, "👎",  no_width,hovered=False)
                            return False
                    else:
                        if not clicked_no and hovered_no:
                            self.draw_button(button_x + yes_width + padding, button_y, no_label,  no_width,hovered=False)
                            hovered_no = False
            finally:
                sys.stdout.write("\x1b[?1000l")
                sys.stdout.write("\x1b[?1003l")
                sys.stdout.write("\x1b[?1006l")
                sys.stdout.write("\x1b[?1015l")
                print("\n\033[2K\r",end='')

        def create(self, callback=None):
            """
            Renders the button(s), handles clicks, and executes optional callbacks.
            - Clears old button areas to prevent leftover characters.
            - Ensures the cursor is placed one line below the bottom-most button or grid.
            - Supports per-button and global callbacks.
            """
            height = 3  
            vertical_spacing = height + 1  

            def clear_button_area(x, y, width):
                """Fills the button area with spaces to prevent leftover characters."""
                for i in range(height):
                    sys.stdout.write(f"\x1b[{y + i};{x}H" + ' ' * width)  
                sys.stdout.flush()

            def move_cursor_below(last_y):
                """Moves the cursor to one line below the bottom edge of the button(s)."""
                new_y = last_y + 1  
                sys.stdout.write(f"\x1b[{new_y};0H")  
                sys.stdout.flush()

            if self.Is_grid:
                grid_buttons = list(self.grid.values())
                button_count = min(len(grid_buttons), 4)  # Limit to the first 4 buttons
                spacing = 10  
                buttons = []  

                sys.stdout.write("\x1b7")  
                sys.stdout.flush()
                sys.stdout.write("\033[?25l")  
                sys.stdout.flush()
                sys.stdout.write("\x1b[?1000h")  
                sys.stdout.write("\x1b[?1003h")  
                sys.stdout.write("\x1b[?1006h")  
                sys.stdout.write("\x1b[?1015h")  
                sys.stdout.flush()

                max_y = self.y  

                # Iterate only over the first 4 buttons
                for idx, button in enumerate(grid_buttons[:4]):
                    label = button.get('label', 'Button')
                    button_callback = button.get('callback', None)  

                    if button_count == 4:
                        new_x = self.x + (idx % 2) * (len(label) + spacing)
                        new_y = self.y + (idx // 2) * vertical_spacing
                    elif button_count == 3 or button_count == 2:
                        new_x = self.x + idx * (len(label) + spacing)
                        new_y = self.y
                    else:
                        new_x = self.x
                        new_y = self.y + idx * vertical_spacing

                    width = len(label) + 4
                    buttons.append((new_x, new_y, width, label, button_callback))
                    self.draw_button(new_x, new_y, label, width)

                    max_y = max(max_y, new_y + height - 1)  


                try:
                    hovered_buttons = [False] * button_count

                    while True:
                        b, x, y = self.get_mouse_event()

                        for idx, (btn_x, btn_y, btn_width, btn_label, btn_callback) in enumerate(buttons):
                            if btn_x <= x < btn_x + btn_width and btn_y <= y < btn_y + height:
                                if not hovered_buttons[idx]:
                                    self.draw_button(btn_x, btn_y, btn_label, btn_width, hovered=True)
                                    hovered_buttons[idx] = True

                                if b == 0 or b == 32:  
                                    new_label = "Clicked!"
                                    new_width = len(new_label) + 4

                                    clear_button_area(btn_x, btn_y, btn_width)
                                    self.draw_button(btn_x, btn_y, new_label, new_width, hovered=False)

                                    move_cursor_below(max_y)

                                    if btn_callback is not None:
                                        print()  
                                        btn_callback()
                                        sys.stdout.flush()  
                                    elif self.callback is not None:
                                        print()  
                                        self.callback()
                                        sys.stdout.flush()  

                                    return
                            else:
                                if hovered_buttons[idx]:
                                    self.draw_button(btn_x, btn_y, btn_label, btn_width, hovered=False)
                                    hovered_buttons[idx] = False

                finally:
                    sys.stdout.write("\x1b[?1000l")
                    sys.stdout.write("\x1b[?1003l")
                    sys.stdout.write("\x1b[?1006l")
                    sys.stdout.write("\033[?25h")
                    sys.stdout.flush()
                    sys.stdout.write("\x1b[?1015l")
                    print("\n\033[2K\r", end='')

            else:
                width = len(self.label) + 4  

                sys.stdout.write("\x1b7")
                sys.stdout.flush()
                sys.stdout.write("\033[?25l")
                sys.stdout.flush()
                sys.stdout.write("\x1b[?1000h")
                sys.stdout.write("\x1b[?1003h")
                sys.stdout.write("\x1b[?1006h")
                sys.stdout.write("\x1b[?1015h")
                sys.stdout.flush()

                self.draw_button(self.x, self.y, self.label, width)

                try:
                    hovered = False

                    while True:
                        b, x, y = self.get_mouse_event()

                        if self.x <= x < self.x + width and self.y <= y < self.y + height:
                            if not hovered:
                                self.draw_button(self.x, self.y, self.label, width, hovered=True)
                                hovered = True

                            if b == 0 or b == 32:  
                                new_label = self.label_when_clicked
                                new_width = len(new_label) + 4

                                clear_button_area(self.x, self.y, width)
                                self.draw_button(self.x, self.y, new_label, new_width, hovered=False)

                                move_cursor_below(self.y + height - 1)

                                if self.callback is not None:
                                    print()  
                                    self.callback()
                                    sys.stdout.flush()  

                                return
                        else:
                            if hovered:
                                self.draw_button(self.x, self.y, self.label, width, hovered=False)
                                hovered = False

                finally:
                    sys.stdout.write("\x1b[?1000l")
                    sys.stdout.write("\x1b[?1003l")
                    sys.stdout.write("\x1b[?1006l")
                    sys.stdout.write("\033[?25h")
                    sys.stdout.flush()
                    sys.stdout.write("\x1b[?1015l")
                    print("\n\033[2K\r", end='')
