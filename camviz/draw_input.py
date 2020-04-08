
import pygame


class DrawInput:

    def __init__(self):

        self.UP = self.DOWN = self.LEFT = self.RIGHT = False
        self.RCTRL = self.LCTRL = self.RALT = self.LALT = self.RSHIFT = self.LSHIFT = False
        self.SPACE = self.RETURN = False

        self.mouse_pos = self.motion_type = None
        self.tmp_screen, self.tmp_focus = None, False
        self.mouse_down = False

    def input(self):

        events = pygame.event.get()
        pos = pygame.mouse.get_pos()

        if self.mouse_down is False:
            screen = None
            for key, scr in self.screens.items():
                if scr.inside(pos):
                    screen = scr; break

            focus = screen is not None and pygame.mouse.get_focused()
            if not focus: self.mouse_pos = None
        else:
            screen, focus = self.tmp_screen, self.tmp_focus

        for event in events:

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_p:
                    print('(%7.5f, %7.5f, %7.5f, %1.5f, %1.5f, %1.5f, %1.5f)' %
                          self.currScreen().viewer.current7())

                if event.key == pygame.K_UP:     self.UP     = True
                if event.key == pygame.K_DOWN:   self.DOWN   = True
                if event.key == pygame.K_LEFT:   self.LEFT   = True
                if event.key == pygame.K_RIGHT:  self.RIGHT  = True
                if event.key == pygame.K_RCTRL:  self.RCTRL  = True
                if event.key == pygame.K_LCTRL:  self.LCTRL  = True
                if event.key == pygame.K_RALT:   self.RALT   = True
                if event.key == pygame.K_LALT:   self.LALT   = True
                if event.key == pygame.K_RSHIFT: self.RSHIFT = True
                if event.key == pygame.K_LSHIFT: self.LSHIFT = True
                if event.key == pygame.K_SPACE:  self.SPACE  = True
                if event.key == pygame.K_RETURN: self.RETURN = True

            if event.type == pygame.KEYUP:

                if event.key == pygame.K_UP:     self.UP     = False
                if event.key == pygame.K_DOWN:   self.DOWN   = False
                if event.key == pygame.K_LEFT:   self.LEFT   = False
                if event.key == pygame.K_RIGHT:  self.RIGHT  = False
                if event.key == pygame.K_RCTRL:  self.RCTRL  = False
                if event.key == pygame.K_LCTRL:  self.LCTRL  = False
                if event.key == pygame.K_RALT:   self.RALT   = False
                if event.key == pygame.K_LALT:   self.LALT   = False
                if event.key == pygame.K_RSHIFT: self.RSHIFT = False
                if event.key == pygame.K_LSHIFT: self.LSHIFT = False
                if event.key == pygame.K_SPACE:  self.SPACE  = False
                if event.key == pygame.K_RETURN: self.RETURN = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_down = True
                self.tmp_screen, self.tmp_focus = screen, focus

                if focus and screen.mode is '3D_WORLD':

                    if event.button == 4:
                        screen.viewer.translateZ(+(5.0 if self.RCTRL else 0.5))
                    if event.button == 5:
                        screen.viewer.translateZ(-(5.0 if self.RCTRL else 0.5))
                    if event.button == 1:
                        self.motion_type, self.mouse_pos = 1, pos
                    if event.button == 3:
                        self.motion_type, self.mouse_pos = 3, pos
                    if event.button == 2:
                        screen.reset()

                if focus and screen.mode is '2D_IMAGE':

                    if event.button == 1:
                        self.motion_type, self.mouse_pos = 1, pos
                    if event.button == 2:
                        screen.res = list(screen.orig_res)
                    else:
                        rel = [(pos[0] - screen.luwh[0]) / screen.luwh[2] * screen.res[2] + screen.res[0],
                               (pos[1] - screen.luwh[1]) / screen.luwh[3] * screen.res[3] + screen.res[1]]
                        mlt = 1.20 if self.RSHIFT else 1.05

                        if event.button == 4:
                            if screen.res[0] < 0.95 * screen.res[2] and \
                               screen.res[1] < 0.95 * screen.res[3]:
                                screen.res[2] = (screen.res[0] + screen.res[2] - rel[0])/mlt + rel[0] - screen.res[0]
                                screen.res[0] = (screen.res[0] - rel[0])/mlt + rel[0]
                                screen.res[3] = (screen.res[1] + screen.res[3] - rel[1])/mlt + rel[1] - screen.res[1]
                                screen.res[1] = (screen.res[1] - rel[1])/mlt + rel[1]

                        elif event.button == 5:
                            screen.res[2] = (screen.res[0] + screen.res[2] - rel[0])*mlt + rel[0] - screen.res[0]
                            screen.res[0] = (screen.res[0] - rel[0])*mlt + rel[0]
                            screen.res[3] = (screen.res[1] + screen.res[3] - rel[1])*mlt + rel[1] - screen.res[1]
                            screen.res[1] = (screen.res[1] - rel[1])*mlt + rel[1]

                        screen.res[0] = max(screen.res[0], screen.orig_res[0])
                        screen.res[1] = max(screen.res[1], screen.orig_res[1])
                        screen.res[2] = min(screen.res[2], screen.orig_res[2])
                        screen.res[3] = min(screen.res[3], screen.orig_res[3])

            if event.type == pygame.MOUSEBUTTONUP:
                self.mouse_down = False
                self.mouse_pos = None

        if focus:

            if screen.mode == '3D_WORLD':
                if self.mouse_pos is not None:
                    dX = pos[0] - self.mouse_pos[0]
                    dY = pos[1] - self.mouse_pos[1]
                    self.mouse_pos = pos

                    if self.motion_type == 1:
                        mlin = 1.00 if self.RCTRL else 0.10
                        screen.viewer.translateX( - dX * mlin )
                        screen.viewer.translateY( - dY * mlin )
                    elif self.motion_type == 3:
                        mang = 0.25 if self.RCTRL else 0.05
                        if screen.ref == 'cam':
                            screen.viewer.rotateX( - dY * mang )
                            screen.viewer.rotateJ( + dX * mang )
                        elif screen.ref == 'lid':
                            screen.viewer.rotateX( - dY * mang )
                            screen.viewer.rotateK( - dX * mang )

            elif screen.mode == '2D_IMAGE':
                if self.mouse_pos is not None:
                    mlin = 5.00 if self.RCTRL else 1.00
                    dX = pos[0] - self.mouse_pos[0]
                    dY = pos[1] - self.mouse_pos[1]
                    self.mouse_pos = pos

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

        return True

    @staticmethod
    def update(wait):

        pygame.display.flip()
        pygame.time.wait( wait )

    @staticmethod
    def control( obj ):

        dlin, dang = 0.2, 5.0
        keys = pygame.key.get_pressed()

        change = False

        if keys[pygame.K_UP]:
            change = True
            obj.translateZ(+dlin)
        if keys[pygame.K_DOWN ]:
            change = True
            obj.translateZ(-dlin)
        if keys[pygame.K_LEFT]:
            change = True
            obj.translateX(-dlin)
        if keys[pygame.K_RIGHT]:
            change = True
            obj.translateX(+dlin)
        if keys[pygame.K_q]:
            change = True
            obj.translateY(-dlin)
        if keys[pygame.K_a]:
            change = True
            obj.translateY(+dlin)
        if keys[pygame.K_s]:
            change = True
            obj.rotateY(+dang)
        if keys[pygame.K_f]:
            change = True
            obj.rotateY(-dang)
        if keys[pygame.K_e]:
            change = True
            obj.rotateX(-dang)
        if keys[pygame.K_d]:
            change = True
            obj.rotateX(+dang)
        if keys[pygame.K_w]:
            change = True
            obj.rotateZ(+dang)
        if keys[pygame.K_r]:
            change = True
            obj.rotateZ(-dang)

        return change