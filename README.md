# RocketCv
## What Is this
RocketCV is a Python-based rocket builder and simulator that resolves the inconvenience of other simulators by doing all the calculations by uploading a simple DXF sketch file without you needing to enter all the dimension values manually. It gives a lightweight environment for simulating rockets from body and fin geometry and visualizing them in a CAD-style preview.

This project is still in a early foundation stage, it will eventually gain all the features required for a proper model rocket calculation and simulation.

## How To Install And Run
just run this in your terminal: (for now)

```bash
git clone https://github.com/yuanhaozhe2022-eng/rocketcv.git
cd RocketCV
pip install -r requirements.txt
python main.py
```



## How to use:
Use anything like:
* Fusion 360
* SolidWorks
* FreeCAD
* Onshape
* Then make a simple and accurate 2D sketch profile of the BODY TUBE from sideway
* Note: for the majority of CAD softwares, there's a "Use"  feature which allows you to select the edges from the part then turn them into a 2D plain sketch viewed from the orientation of the sketch face (whatever I think there's a lot of tutorials about this feature online you can just search it up.)
* Then export it as a DXF file

Same thing for the fin.

Lastly, upload it to RocketCv by clicking the buttons on the bottom right

And you can see the values getting entered into the software

Have fun =)

