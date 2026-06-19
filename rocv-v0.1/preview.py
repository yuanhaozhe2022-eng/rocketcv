from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter,QPen
from PyQt6.QtCore import Qt


class DXFPreview(QWidget):

    def __init__(self):
        super().__init__()

        self.body=[]
        self.fin=[]
        self.fin_count=0


    def set_body(self,data):

        self.body=data["lines"]
        self.update()


    def set_fin(self,data,count):

        self.fin=data["lines"]
        self.fin_count=count
        self.update()


    def paintEvent(self,event):

        painter=QPainter(self)

        painter.fillRect(
            self.rect(),
            Qt.GlobalColor.white
        )

        painter.setPen(
            QPen(Qt.GlobalColor.black,2)
        )


        if self.body:

            self.draw_centered(
                painter,
                self.body,
                0
            )


        if self.fin:

            for i in range(self.fin_count):

                self.draw_centered(
                    painter,
                    self.fin,
                    120+(i*40)
                )


    def draw_centered(self,painter,lines,offset):

        xs=[]
        ys=[]

        for line in lines:

            xs.append(line["start"].x)
            xs.append(line["end"].x)

            ys.append(line["start"].y)
            ys.append(line["end"].y)


        if not xs:
            return


        minx=min(xs)
        maxx=max(xs)

        miny=min(ys)
        maxy=max(ys)


        width=maxx-minx
        height=maxy-miny


        scale=min(
            (self.width()-100)/(width+1),
            (self.height()-100)/(height+1)
        )


        cx=self.width()/2
        cy=self.height()/2


        for line in lines:

            x1=(line["start"].x-(minx+width/2))*scale+cx+offset
            y1=(-(line["start"].y-(miny+height/2))*scale)+cy

            x2=(line["end"].x-(minx+width/2))*scale+cx+offset
            y2=(-(line["end"].y-(miny+height/2))*scale)+cy


            painter.drawLine(
                int(x1),
                int(y1),
                int(x2),
                int(y2)
            )