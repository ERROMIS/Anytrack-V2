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

To load a video, click on the `Video` tab → `Launch from video`.  
The app supports common formats such as `.avi`, `.mp4`, etc.  

Internally, OpenCV handles the video input, so if a format works in OpenCV, it should work here.

### Using a connected camera

You can stream from a USB camera or integrated webcam.  
Go to `Video` → `Use live camera feed`.

Only the first available video source is used. If you have multiple devices, you may need to disable the others.  
Also, no other program must use the camera at the same time.

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
  - **Template Tracker** (uses OpenCV’s normalized cross-correlation)  
  - **Fixed Point** (manual point, useful for reference — currently the only active one)  

The KCF tracker button is no longer available due to stability issues.

Once created, click on the video to place the tracker.

### Defining a detection region

Control + Right-click (maybe..., it change on linux/mac and windows) and drag on the video to draw a green rectangle around the area where tracking should take place.  
This restricts the region the tracker will analyze on each frame.

### Switching between trackers

From the `Tracker` tab, hover over `Switch Trackers`.  
The selected tracker will be highlighted with an orange arrow.

### Modifying tracker size

After creating a tracker, you can adjust its size.  
Right-click on the tracker label in the list → `Edit tracker`.  
You’ll be able to change the width/height, and it will recenter automatically.  
No need to reselect it manually.

---

## Plotting Tracker Data

### Creating a plot

Click on the `Plots` tab → `Create a new plot`.  
You will be asked to:

- Name the plot  
- Select two trackers to calculate the distance between  
- Enter the FPS (frames per second) of the video  

The plot will appear in a new window (on the right side of the screen).

### Starting, pausing, resuming, and saving a graph

Once the plot appears:

- Click `Start Graph` to begin plotting  
  - All video controls (play, pause, seek) are locked while plotting
- Click `Pause Graph` to pause both the video and the graph
- While paused:
  - You can `Resume Plotting`
  - Or `Save Graph` (saves a `.csv` with distance/time data and a `.png` image of the visible graph)
  - Or `Clear Graph` (clears current plot and unlocks the video controls)

Graphs no longer start automatically — you have full control over when to begin.

### End of video behavior

When the video reaches the end:

- The video will pause automatically  
- Plotting will stop  
- The only available actions are `Save Graph` or `Clear Graph`

You cannot start a new graph until the current one is cleared.

---

If you encounter bugs or unexpected behavior, restart the application and reload your video.
Try pausing the video before closing the app, it might crash...
