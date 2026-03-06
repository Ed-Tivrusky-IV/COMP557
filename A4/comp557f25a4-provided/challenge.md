# Own Adventure

## Mirror Reflection

Add a bool "mirror" attribute in the material class. If true, we will calculate the specular reflection by using a mirror ray.

If the mirror ray find an intersection, we will multiply the specular parameter with the intersection's color.

You can find the corresponding JSON file: TwoSpherePlaneMirror.json, and png file: TwoSpherePlaneMirror.png.

## Cylinder

Add a new type "Cylinder" in the JSON file, and modify the code correspondingly in parser.py, scene.py, and geometry.py.

The JSON file is named Cylinder.json, and the output is Cylinder.png.

## Texture

I finished only a part of it, but don't have the time to implement the whole structure.

## A Novel Scene

I was trying to build a planet system using Texture for the sense of reality. However, due to the limited time, I didn't eventually finish the Texture feature.

The result is stored in Planets.json and Planets.png
