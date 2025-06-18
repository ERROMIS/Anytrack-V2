# Tixier-Mita Laboratory – AnyTrack

## Authors (of software and summary)
- Thomas Wanchaï MENIER (2023)
- Maxime SIMORRE (2025)

## Developed thanks to
- Agnès TIXIER-MITA, Associate Professor at the Institute of Industrial Science (IIS)
- Gilgueng Hwang, Researcher at the IIS
- Hiroshi TOSHIYOSHI, Head of the Toshiyoshi Laboratory, IIS
- Alex DUFOUR, ENSEIRB-MATMECA, Bordeaux
- Gabriel FAURE, Engineering student at the University of Tokyo
- Universitary Institute of Technology (IUT) of Bordeaux-Gradignan
- Institute of Industrial Science, The University of Tokyo

## Guides
- [User Manual](./docs/USER_MANUAL.md)
- [Installation](./INSTALL.md)
- [Development Guide](./docs/DEV_MANUAL.md)

---

## Context

### About the project

AnyTrack is a Python-based video tracking tool designed to help researchers analyze the contraction of cardiomyocyte cells using video microscopy. The software allows users to define and track regions of interest (trackers) and measure the distance between them in real time or from recorded videos.

Originally developed by Thomas MENIER in 2023, the tool was improved in 2025 to enhance usability, fix critical bugs, and provide researchers with greater control over data collection and visualization. The tool is modular and extensible, allowing additional tracker types to be added with minimal effort.

AnyTrack was developed as part of an undergraduate internship at the Tixier-Mita Laboratory, in response to the need for lightweight and customizable alternatives to more complex tools like ImageJ, which may not be practical for real-time or embedded use cases.

---

### Main Features

- Track distance between two dynamic regions (trackers) in live or recorded video.
- Flexible architecture allowing new tracker types to be added easily.
- Multiple tracker types:
  - Template matching via Normalized Cross-Correlation
  - KCF (Kernelized Correlation Filter) tracker (OpenCV)
- Graph plotting system with pause/resume, CSV export, and snapshot saving.
- Video playback controls: play, pause, seek, contrast adjustment.
- Compatible with real-time feeds or prerecorded video.
- Optional Client/Server communication mode for Raspberry Pi integration.

---

### Improvements in 2025

Significant updates were made to enhance both the robustness and flexibility of the software:
- Manual tracker resizing at creation and during usage.
- Rewritten plotting system with start/pause/resume/save controls.
- Improved synchronization between plotting and video frames.
- Better error handling to prevent crashes with long videos.
- More reliable export of graphs and CSV data.
- Clearer GUI for plotting and playback.
- New detection of video end to avoid infinite looping.

These changes make AnyTrack much more usable in a research setting, while keeping it accessible for biology-focused users.

---

### Why not use ImageJ?

AnyTrack was developed from scratch due to time constraints and the need for a lightweight, targeted solution. The original author (MENIER) preferred this approach to ensure a working prototype could be delivered. Open-source alternatives like ImageJ were considered but not suitable for real-time integration or direct embedding with custom hardware like Raspberry Pi-based microscopes.

---

## <p id="client-server-protocol">Client–Server Protocol</p>

Originally, the tool was intended to interface with a real microscope to retrieve a live feed. However, due to hardware limitations, this was replaced with a simulated setup using a Raspberry Pi and camera module. The software can now act as a TCP client, receiving image data in real time from a server-like device.

A lightweight custom protocol defines how frames and metadata are exchanged. Developers can build their own compatible servers (e.g., on Raspberry Pi) to stream data into AnyTrack over a network connection.

See [protocol definition](src/comm_protocol/comm_protocol_definition.md) for details.

A full implementation guide for this protocol may be provided in future versions.
