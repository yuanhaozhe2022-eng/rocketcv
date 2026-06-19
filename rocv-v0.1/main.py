from PyQt6.QtWidgets import QApplication,QFileDialog
from ui import RocketUI
from reader import read_dxf
from translation import analyze
from parts import Body,Fin,Rocket
from rocketstats import RocketStats
import sys


class App(RocketUI):

    def __init__(self):

        super().__init__()

        self.rocket=Rocket()

        self.stats=RocketStats(
            self.rocket
        )


        self.button_body.clicked.connect(
            self.load_body
        )

        self.button_fin.clicked.connect(
            self.load_fin
        )


    def load_body(self):

        file,_=QFileDialog.getOpenFileName(
            self,
            "Open Body DXF",
            "",
            "DXF Files (*.dxf)"
        )


        if file:

            data=read_dxf(file)

            self.update_preview_body(
                data
            )


            self.rocket.body=analyze(
                data,
                Body()
            )


            self.update_body(
                self.rocket.body
            )



    def load_fin(self):

        file,_=QFileDialog.getOpenFileName(
            self,
            "Open Fin DXF",
            "",
            "DXF Files (*.dxf)"
        )


        if file:

            data=read_dxf(file)


            fin=analyze(
                data,
                Fin()
            )


            if self.fin_count.text():

                fin.count=int(
                    self.fin_count.text()
                )


            self.rocket.set_fin(
                fin
            )


            self.update_preview_fin(
                data,
                fin.count
            )


            self.update_fins(
                fin
            )



app=QApplication(sys.argv)

window=App()

window.show()

sys.exit(app.exec())