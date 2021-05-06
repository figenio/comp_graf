import time

class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y

P = [Coord(0,0),Coord(6,0),Coord(10,3),Coord(8,9),Coord(0,9),Coord(5,5)]
# for c in P:
#     print("({:d},{:d})".format(c.x, c.y), end=" ")
# print("")

output = []

for k in range(len(P)):
    l = -1 if (k + 1) >= len(P) else (k + 1)

    print("L:", l)
    dda = P[k]

    while (dda.x != P[l].x and dda.x != P[l].x):
        m = (P[l].y - dda.y)/(P[l].x - dda.x)
        print("On ({:d},{:d}) to ({:d},{:d}) with M: {:.2f}".format(dda.x, dda.y, P[l].x, P[l].y, m))

        output.append(Coord(dda.x, dda.y))

        
            

        if abs(m) > 1:
            if m >= 0:
                dda.y += 1
            else:
                dda.y -= 1
        elif abs(m) < 1:
            if m >= 0:
                dda.x += 1
            else:
                dda.x -= 1
        else:
            if m >= 0:
                dda.y += 1
                dda.x += 1
            else:
                dda.y -= 1
                dda.x -= 1
        
        time.sleep(0.5)

for c in output:
    print("({:d},{:d})".format(c.x, c.y))