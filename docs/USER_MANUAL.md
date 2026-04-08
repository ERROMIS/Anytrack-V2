# AnyTrack - User Manual

This guide provides an overview of the functionalities of the application.  
For developer-oriented documentation, see the [Development Manual](./DEV_MANUAL.md).

---

## Table of Contents

- Loading a Video Feed
  - From a video file
  - Using a connected camera
  - From a custom external server
- Tracker Management
  - Creating a new tracker
  - Placing a tracker
  - Defining a detection region
  - Switching between trackers
  - Modifying tracker size
- Plotting Tracker Data
  - Creating a plot
  - Starting, pausing, resuming, and saving a graph
  - End of video behavior

---

## Loading a Video Feed

### From a video file

Click `Video` → `Launch from video`.  
The app supports common formats such as `.avi`, `.mp4`, etc.  
Internally, OpenCV handles the video input, so any format OpenCV supports will work here.

### Using a connected camera

Go to `Video` → `Use live camera feed`.  
Only the first available video source is used. No other program must be using the camera at the same time.

### From a custom external server

It is possible to connect to an external device like a Raspberry Pi and receive its video feed via TCP.  
The setup is advanced and explained in a separate guide:  
[Custom integration setup](../custom_integrations/tixier_mita_lab/README.md)

---

## Tracker Management

### Creating a new tracker

Click `Tracker` → `New tracker`.  
In the pop-up window:

- Choose a name
- Choose a type:
  - **Pattern Tracker** — tracks a region using normalized cross-correlation (template matching). Use this for moving objects.
  - **Reference Tracker** — fixed reference point. Useful as a static anchor when measuring contraction relative to a fixed position.
- Set the tracker size (width × height in pixels)

The newly created tracker is automatically selected.

### Placing a tracker

Once a tracker is selected (highlighted with an orange arrow), **left-click** on the video to place it at that position.

### Defining a detection region

**Right-click and drag** on the video to draw a green rectangle.  
This restricts the area where the tracker will search on each frame, which improves both speed and accuracy.

### Switching between trackers

From the `Tracker` tab, hover over `Switch Trackers` and click the tracker you want to select.  
The selected tracker is highlighted with an orange arrow.

### Modifying tracker size

Right-click on the tracker label in the list → `Edit tracker`.  
You can change the width and height; the tracker will recenter automatically.

---

## Plotting Tracker Data

### Creating a plot

Click `Plots` → `Create a new plot`.  
You will be asked to:

- Name the plot
- Select two trackers to calculate the distance between
- Confirm or adjust the FPS (auto-detected from the video)

The plot panel appears on the right side of the screen.

### Starting, pausing, resuming, and saving a graph

Once the plot is created:

- Click **Start** to begin plotting — video controls are locked while recording
- Click **Pause** to pause both the video and the graph
- While paused:
  - **Resume** — continue plotting from where you left off
  - **Save** — exports a `.csv` with time/distance data and a `.png` image of the graph
  - **Clear** — resets the plot and unlocks video controls

### End of video behavior

When the video reaches the end:

- The video pauses automatically
- Plotting stops
- Only **Save** and **Clear** remain available

Clear the graph before starting a new recording session.

---

If you encounter bugs or unexpected behavior, restart the application and reload your video.
