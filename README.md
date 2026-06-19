# RocketCv
## What Is this
RocketCV is a Python-based rocket builder and simulator that does all the calculations without you needing to enter all the values manually. It gives a lightweight environment for simulating rockets from body and fin geometry and visualizing them in a CAD-style preview.

This project is still in a early foundation stage, it will eventually gain all the features required for a proper model rocket calculation ans simulation.

## How To Install And Run
just run this in your terminal: (for now)

```bash
git clone https://github.com/yourname/RocketCV.git
cd RocketCV
pip install -r requirements.txt
python main.py```

# Versions
## V0.1
* THIS IS A TESTING VERSION, JUST TO SEE IF EVERYTHING IS WORKING OR NOT
* No calculation performed yet=(
* Import rocket body and fin DXF files
* Extract basic geometry (length(nose cone not included), diameter, width, height, and NO curves yet)
* Set number of fins
* CAD-style preview of rocket parts (again, no curves yet)
* Simple UI for loading and viewing components

## How to use:
Use anything like:
* Fusion 360
* SolidWorks
* FreeCAD
* Onshape
Then make a simple and accurate 2D sketch profile of the BODY TUBE from sideway
* Note: for the majority of CAD softwares, there's a "Use"  feature which allows you to select the edges from the part then turn them into a 2D plain sketch viewed from the orientation of the sketch face (whatever I think there's a lot of tutorials about this feature online you can just search it up.)
* Then export it as a DXF file

Same thing for the fin.

Lastly, upload it to RocketCv by clicking the buttons on the bottom right

And you can see the values getting entered into the software

Have fun =)

