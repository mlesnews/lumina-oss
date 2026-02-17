#!/usr/bin/env python3
"""Test ASUS IR camera access with different backends"""
import cv2

print("Testing ASUS IR camera access (index 1)...")
print()

# Test DirectShow
cap1 = cv2.VideoCapture(1, cv2.CAP_DSHOW)
if cap1.isOpened():
    ret, frame = cap1.read()
    if ret:
        print("✅ DirectShow: OPEN and working")
    else:
        print("⚠️  DirectShow: OPEN but can't read frame")
    cap1.release()
else:
    print("❌ DirectShow: Cannot open")

# Test MSMF
cap2 = cv2.VideoCapture(1, cv2.CAP_MSMF)
if cap2.isOpened():
    ret, frame = cap2.read()
    if ret:
        print("✅ MSMF: OPEN and working")
    else:
        print("⚠️  MSMF: OPEN but can't read frame")
    cap2.release()
else:
    print("❌ MSMF: Cannot open")

# Test default
cap3 = cv2.VideoCapture(1)
if cap3.isOpened():
    ret, frame = cap3.read()
    if ret:
        print("✅ Default: OPEN and working")
    else:
        print("⚠️  Default: OPEN but can't read frame")
    cap3.release()
else:
    print("❌ Default: Cannot open")
