from PyQt6.QtWidgets import *
from preview import DXFPreview


class RocketUI(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Rocket Simulator"
        )

        self.setMinimumSize(
            900,600
        )

        self.setup()


    def setup(self):

        self.preview=DXFPreview()
        self.preview.setMinimumSize(
            500,500
        )


        self.length=QLineEdit()
        self.diameter=QLineEdit()
        self.wall=QLineEdit()
        self.density=QLineEdit()
        self.fin_count=QLineEdit()


        self.body_info=QLabel(
            "Body: none"
        )

        self.fin_info=QLabel(
            "Fin: none"
        )


        self.button_body=QPushButton(
            "Upload Body DXF"
        )

        self.button_fin=QPushButton(
            "Upload Fin DXF"
        )


        side=QVBoxLayout()


        side.addWidget(
            QLabel("Length")
        )
        side.addWidget(
            self.length
        )


        side.addWidget(
            QLabel("Diameter")
        )
        side.addWidget(
            self.diameter
        )


        side.addWidget(
            QLabel("Wall Thickness")
        )
        side.addWidget(
            self.wall
        )


        side.addWidget(
            QLabel("Density")
        )
        side.addWidget(
            self.density
        )


        side.addWidget(
            QLabel("Fin Count")
        )
        side.addWidget(
            self.fin_count
        )


        side.addWidget(
            self.body_info
        )

        side.addWidget(
            self.fin_info
        )

        side.addWidget(
            self.button_body
        )

        side.addWidget(
            self.button_fin
        )


        layout=QHBoxLayout()

        layout.addWidget(
            self.preview
        )

        layout.addLayout(
            side
        )

        self.setLayout(
            layout
        )


    def update_body(self,body):

        self.body_info.setText(
            f"Body: {body.length} x {body.diameter}"
        )

        self.length.setText(
            str(body.length)
        )

        self.diameter.setText(
            str(body.diameter)
        )


    def update_fins(self,fin):

        self.fin_info.setText(
            f"Fin: {fin.width} x {fin.height}"
        )


    def update_preview_body(self,data):

        self.preview.set_body(
            data
        )


    def update_preview_fin(self,data,count):

        self.preview.set_fin(
            data,
            count
        )