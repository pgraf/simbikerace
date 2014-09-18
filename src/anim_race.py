
import pygame, sys, time
from pygame.locals import *

# set up pygame
pygame.init()


rrdat = file("race.out").readlines()
nriders = int(rrdat[0].split()[2])
print "there are %d riders" % (nriders)

race_dat = []
ifull = 2
maxpos = 0
while ifull < len(rrdat):
    frame = []
    for irider in range(nriders):
        rdat = rrdat[ifull+irider]
        rdat = [float(x) for x in rdat.split()]
        frame.append(rdat)
        maxpos = max(maxpos, rdat[1])
    race_dat.append(frame)
    ifull += nriders

# set up the window
WINDOWWIDTH = 800
WINDOWHEIGHT = nriders * 10 + 10
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Animation')

BLACK=(0,0,0)

# run the game loop
keydown = False
i = 0
reverse = False
#while (i < len(race_dat)):
while True:
    # check for the QUIT event
    if keydown:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYUP:
                keydown = False
    else:
        advance = False
        while (not advance):
    #        pygame.event.wait()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    advance = True
                if event.type == KEYDOWN:
                    if (event.key == K_q):
                        pygame.quit()
                        sys.exit()
                    if (event.key == K_a or event.key == K_LEFT):
                        reverse = True
                    else:
                        reverse = False
                    keydown = True
                    advance = True
        
    # draw the black background onto the surface
    windowSurface.fill(BLACK)

    frame = race_dat[i]
    for rider in frame:
        # move the block data structure
        # (set b['rect'])
        p = rider[1]
        gnum = rider[4]
        rnum = rider[5]
        r = pygame.Rect(1+(WINDOWWIDTH-10)*p/maxpos, 5+10*rnum, 10, 10)

        # draw the block onto the surface
#        c = (int(50 +13*rnum), int(100 + 10*rnum),0)
        c = (int(255*(rnum%3==0)), int(255*(rnum%3==1)), int(255*(rnum%3==2)))
#        print c
        pygame.draw.rect(windowSurface, c, r)

    # draw the window onto the screen
    pygame.display.update()
    time.sleep(0.025)

    if reverse:
        i = max(0,i-1)
    else:
        i = min(i+1,len(race_dat)-1)
