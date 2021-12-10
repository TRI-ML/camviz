# Copyright 2021 Toyota Research Institute.  All rights reserved.

import pygame


class DrawInput:
    """Draw subclass containing input controls"""
    def __init__(self):
        # Initialize basic keys
        self.UP = self.DOWN = self.LEFT = self.RIGHT = False
        self.RCTRL = self.LCTRL = self.RALT = self.LALT = self.RSHIFT = self.LSHIFT = False
        self.SPACE = self.RETURN = self.PGUP = self.PGDOWN = False
        # Initialize letter keys
        self.KEY_Q = self.KEY_W = self.KEY_E = self.KEY_R = self.KEY_T = False
        self.KEY_A = self.KEY_S = self.KEY_D = self.KEY_F = self.KEY_G = False
        self.KEY_Z = self.KEY_X = self.KEY_C = self.KEY_V = self.KEY_B = False
        # Initialize number keys
        self.KEY_0 = self.KEY_1 = self.KEY_2 = self.KEY_3 = self.KEY_4 = self.KEY_5 = \
            self.KEY_6 = self.KEY_7 = self.KEY_8 = self.KEY_9 = False
        # Initialize mouse keys
        self.mouse_pos = self.motion_type = None
        self.tmp_screen, self.tmp_focus = None, False
        self.mouse_down = False

    def change_keys(self, key, flag):
        """
        Change key to flag value

        Parameters
        ----------
        key : pygame key
            Key in consideration
        flag : bool
            State to set the key [True or False]
        """
        if key == pygame.K_UP:
            self.UP = flag
        if key == pygame.K_DOWN:
            self.DOWN = flag
        if key == pygame.K_LEFT:
            self.LEFT = flag
        if key == pygame.K_RIGHT:
            self.RIGHT = flag

        if key == pygame.K_RCTRL:
            self.RCTRL = flag
        if key == pygame.K_LCTRL:
            self.LCTRL = flag
        if key == pygame.K_RALT:
            self.RALT = flag
        if key == pygame.K_LALT:
            self.LALT = flag
        if key == pygame.K_RSHIFT:
            self.RSHIFT = flag
        if key == pygame.K_LSHIFT:
            self.LSHIFT = flag
        if key == pygame.K_PAGEUP:
            self.PGUP = flag
        if key == pygame.K_PAGEDOWN:
            self.PGDOWN = flag

        if key == pygame.K_SPACE:
            self.SPACE = flag
        if key == pygame.K_RETURN:
            self.RETURN = flag

        if key == pygame.K_s:
            self.KEY_S = flag
        if key == pygame.K_q:
            self.KEY_Q = flag
        if key == pygame.K_w:
            self.KEY_W = flag
        if key == pygame.K_e:
            self.KEY_E = flag
        if key == pygame.K_r:
            self.KEY_R = flag
        if key == pygame.K_t:
            self.KEY_T = flag
        if key == pygame.K_a:
            self.KEY_A = flag
        if key == pygame.K_s:
            self.KEY_S = flag
        if key == pygame.K_d:
            self.KEY_D = flag
        if key == pygame.K_f:
            self.KEY_F = flag
        if key == pygame.K_g:
            self.KEY_G = flag

        if key == pygame.K_0:
            self.KEY_0 = flag
        if key == pygame.K_1:
            self.KEY_1 = flag
        if key == pygame.K_2:
            self.KEY_2 = flag
        if key == pygame.K_3:
            self.KEY_3 = flag
        if key == pygame.K_4:
            self.KEY_4 = flag
        if key == pygame.K_5:
            self.KEY_5 = flag
        if key == pygame.K_6:
            self.KEY_6 = flag
        if key == pygame.K_7:
            self.KEY_7 = flag
        if key == pygame.K_8:
            self.KEY_8 = flag
        if key == pygame.K_9:
            self.KEY_9 = flag

    def input(self):
        """
        Parse keyboard and mouse input
        """
        events = pygame.event.get()     # Get events
        pos = pygame.mouse.get_pos()    # Get mouse position

        # If mouse is not pressing down
        if self.mouse_down is False:
            # Get current screen based on mouse position
            screen = None
            for key, scr in self.screens.items():
                if scr.inside(pos):
                    screen = scr
                    break
            # Set screen focus based on mouse position
            focus = screen is not None and pygame.mouse.get_focused()
            if not focus:
                self.mouse_pos = None
        else:
            # Use stored screen and focus
            screen, focus = self.tmp_screen, self.tmp_focus

        # For each event
        for event in events:
            # If x button is pressed
            if event.type == pygame.QUIT:
                return False
            # If key has been presed down
            if event.type == pygame.KEYDOWN:
                # If escape has been pressed, exit
                if event.key == pygame.K_ESCAPE:
                    return False
                # If p has been pressed, return virtual camera pose
                if event.key == pygame.K_p:
                    if self.currScreen().viewer is not None:
                        print('(%7.5f, %7.5f, %7.5f, %1.5f, %1.5f, %1.5f, %1.5f)' %
                              self.currScreen().viewer.current7())
                # Change key to pressed
                self.change_keys(event.key, True)
            # If key has been released
            if event.type == pygame.KEYUP:
                self.change_keys(event.key, False)
            # If mouse button has been pressed down
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_down = True
                self.tmp_screen, self.tmp_focus = screen, focus
                # If it's a 3D world screen
                if focus and screen.mode is '3D_WORLD':
                    if event.button == 4:   # Wheel forward
                        if self.RALT: # Going for rotation in Z
                            screen.viewer.rotateZ(5.0 if self.RCTRL else 0.05 if self.LCTRL else 0.5)
                        else: # Going for translation in Z
                            screen.viewer.translateZ(+(5.0 if self.RCTRL else 0.2 if self.LCTRL else 1.0))
                    if event.button == 5:   # Wheel backwards
                        if self.RALT: # Going for rotation in Z
                            screen.viewer.rotateZ(-5.0 if self.RCTRL else -0.05 if self.LCTRL else -0.5)
                        else: # Going for translation in Z
                            screen.viewer.translateZ(-(5.0 if self.RCTRL else 0.2 if self.LCTRL else 1.0))
                    if event.button == 1:   # Left button
                        self.motion_type, self.mouse_pos = 1, pos
                    if event.button == 3:   # Right button
                        self.motion_type, self.mouse_pos = 3, pos
                    if event.button == 2:   # Wheel press
                        screen.reset()
                # If it's a 2D image screen
                if focus and screen.mode is '2D_IMAGE':
                    if event.button == 1:   # Left button
                        self.motion_type, self.mouse_pos = 1, pos
                    if event.button == 2:   # Wheel press
                        screen.res = list(screen.orig_res)
                    else:
                        # Change resolution
                        rel = [(pos[0] - screen.luwh[0]) / screen.luwh[2] * screen.res[2] + screen.res[0],
                               (pos[1] - screen.luwh[1]) / screen.luwh[3] * screen.res[3] + screen.res[1]]
                        # Get speed multiplier
                        mlt = 1.20 if self.RSHIFT else 1.05
                        # Wheel forward
                        if event.button == 4:
                            if screen.res[0] < 0.95 * screen.res[2] and \
                               screen.res[1] < 0.95 * screen.res[3]:
                                screen.res[2] = (screen.res[0] + screen.res[2] - rel[0])/mlt + rel[0] - screen.res[0]
                                screen.res[0] = (screen.res[0] - rel[0])/mlt + rel[0]
                                screen.res[3] = (screen.res[1] + screen.res[3] - rel[1])/mlt + rel[1] - screen.res[1]
                                screen.res[1] = (screen.res[1] - rel[1])/mlt + rel[1]
                        # Wheel backwards
                        elif event.button == 5:
                            screen.res[2] = (screen.res[0] + screen.res[2] - rel[0])*mlt + rel[0] - screen.res[0]
                            screen.res[0] = (screen.res[0] - rel[0])*mlt + rel[0]
                            screen.res[3] = (screen.res[1] + screen.res[3] - rel[1])*mlt + rel[1] - screen.res[1]
                            screen.res[1] = (screen.res[1] - rel[1])*mlt + rel[1]
                        # Change resolution
                        screen.res[0] = max(screen.res[0], screen.orig_res[0])
                        screen.res[1] = max(screen.res[1], screen.orig_res[1])
                        screen.res[2] = min(screen.res[2], screen.orig_res[2])
                        screen.res[3] = min(screen.res[3], screen.orig_res[3])
            # If mouse button has been released
            if event.type == pygame.MOUSEBUTTONUP:
                self.mouse_down = False
                self.mouse_pos = None
        # If screen has focus
        if focus:
            # If it's a 3D world screen
            if screen.mode == '3D_WORLD':
                # Get new mouse position
                if self.mouse_pos is not None:
                    dX = pos[0] - self.mouse_pos[0]
                    dY = pos[1] - self.mouse_pos[1]
                    self.mouse_pos = pos
                    # If left button
                    if self.motion_type == 1:
                        mlin = 1.00 if self.RCTRL else 0.02 if self.LCTRL else 0.10
                        screen.viewer.translateX(- dX * mlin)
                        screen.viewer.translateY(- dY * mlin)
                    # If right button
                    elif self.motion_type == 3:
                        mang = 0.25 if self.RCTRL else 0.01 if self.LCTRL else 0.05
                        if screen.ref == 'cam':     # Rotation in camera reference
                            screen.viewer.rotateX(- dY * mang)
                            screen.viewer.rotateY(+ dX * mang)
                        elif screen.ref == 'lidar': # Rotation in lidar reference
                            screen.viewer.rotateX(- dY * mang)
                            screen.viewer.rotateZ(- dX * mang)
            # If it's a 2D image screen
            elif screen.mode == '2D_IMAGE':
                # Get new mouse position
                if self.mouse_pos is not None:
                    mlin = 5.00 if self.RCTRL else 1.00
                    dX = pos[0] - self.mouse_pos[0]
                    dY = pos[1] - self.mouse_pos[1]
                    self.mouse_pos = pos
                    # Resize and move screen center around
                    screen.res[0] -= dX * mlin
                    screen.res[2] -= dX * mlin
                    if screen.res[0] < screen.orig_res[0] or \
                       screen.res[2] > screen.orig_res[2]:
                        screen.res[0] += dX * mlin
                        screen.res[2] += dX * mlin
                    screen.res[1] -= dY * mlin
                    screen.res[3] -= dY * mlin
                    if screen.res[1] < screen.orig_res[1] or \
                       screen.res[3] > screen.orig_res[3]:
                        screen.res[1] += dY * mlin
                        screen.res[3] += dY * mlin
        # Continue and return True
        return True

    @staticmethod
    def update(wait):
        """Update window after every wait milisseconds"""
        pygame.display.flip()
        pygame.time.wait(wait)

    @staticmethod
    def control(obj):
        """Control an object with keyboard"""
        # Get velocity values
        dlin, dang = 0.2, 5.0
        # Get keys
        keys = pygame.key.get_pressed()
        # Check for changes
        change = False
        # Translate in +Z if UP
        if keys[pygame.K_UP]:
            change = True
            obj.translateZ(+dlin)
        # Translate in -Z if DOWN
        if keys[pygame.K_DOWN ]:
            change = True
            obj.translateZ(-dlin)
        # Translate in -X if LEFT
        if keys[pygame.K_LEFT]:
            change = True
            obj.translateX(-dlin)
        # Translate in +X if RIGHT
        if keys[pygame.K_RIGHT]:
            change = True
            obj.translateX(+dlin)
        # Translate in -Y if Q
        if keys[pygame.K_q]:
            change = True
            obj.translateY(-dlin)
        # Translate in +Y if A
        if keys[pygame.K_a]:
            change = True
            obj.translateY(+dlin)
        # Rotate in +Y if S
        if keys[pygame.K_s]:
            change = True
            obj.rotateY(+dang)
        # Rotate in -Y if F
        if keys[pygame.K_f]:
            change = True
            obj.rotateY(-dang)
        # Rotate in -X if E
        if keys[pygame.K_e]:
            change = True
            obj.rotateX(-dang)
        # Rotate in +X if D
        if keys[pygame.K_d]:
            change = True
            obj.rotateX(+dang)
        # Rotate in +Z if W
        if keys[pygame.K_w]:
            change = True
            obj.rotateZ(+dang)
        # Rotate in -Z if R
        if keys[pygame.K_r]:
            change = True
            obj.rotateZ(-dang)
        # Return change value
        return change
