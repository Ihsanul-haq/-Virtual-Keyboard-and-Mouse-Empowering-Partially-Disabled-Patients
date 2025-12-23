# Virtual Keyboard and Mouse Using Hand Gesture Recognition

## Overview
Traditional input devices such as physical keyboards and mice can be difficult or impossible to use for individuals with physical or motor impairments. This project introduces a **machine-learning–based virtual keyboard and mouse system** that enables touchless interaction with computers using hand gestures.

The system leverages **computer vision and deep learning techniques** to recognize hand gestures in real time and translate them into keyboard inputs and mouse actions. By using widely available hardware such as standard webcams, the solution is affordable, accessible, and easy to deploy.

---

## Key Features
- Touchless virtual keyboard and mouse control
- Real-time hand gesture recognition
- Supports essential actions such as clicking, scrolling, and zooming
- High accuracy and low latency performance
- Accessible and cost-effective solution using a common webcam
- Adaptable to different environments and lighting conditions

---

## Technologies Used
- **YOLOv8 (You Only Look Once v8)** for hand detection
- **Convolutional Neural Networks (CNNs)** for gesture classification
- **Python**
- **OpenCV**
- **PyAutoGUI** for keyboard and mouse control
- Real-time computer vision processing

---

## System Workflow
1. Capture real-time video input using a standard webcam.
2. Detect and track hand movements using YOLOv8.
3. Classify hand gestures using CNN-based models.
4. Map recognized gestures to keyboard inputs or mouse actions.
5. Execute actions such as typing, clicking, scrolling, or zooming.

---

## Performance
- Achieved an average accuracy of **92%**
- Real-time gesture recognition and response
- Smooth and reliable interaction without physical contact
- Optimized for real-world usage scenarios

---

## Applications
- Assistive technology for individuals with motor impairments
- Touchless computer interaction
- Human–computer interaction research
- Hands-free system control in hygienic or restricted environments

---

## Hardware Requirements
- Standard webcam
- Computer or laptop capable of running Python-based applications
- No specialized or expensive hardware required

---

## Conclusion
This project presents a **complete virtual keyboard and mouse solution** using real-time hand gesture recognition. By combining YOLOv8, CNNs, and computer vision techniques, the system enables accessible, accurate, and affordable touchless interaction with computers. The solution significantly improves usability for individuals with physical disabilities and offers an innovative alternative to traditional input methods.
