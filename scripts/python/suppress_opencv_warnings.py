#!/usr/bin/env python3
"""
Suppress OpenCV MSMF Warnings

Suppresses the repeated MSMF grabFrame errors that flood the terminal
when camera access fails.

Tags: #OPENCV #CAMERA #WARNINGS #SUPPRESS @LUMINA
"""

import os
import sys
import warnings

# Suppress OpenCV MSMF warnings
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'  # Only show errors, not warnings

# Suppress Python warnings from OpenCV
warnings.filterwarnings('ignore', category=UserWarning, module='cv2')
warnings.filterwarnings('ignore', message='.*MSMF.*')
warnings.filterwarnings('ignore', message='.*grabFrame.*')
warnings.filterwarnings('ignore', message='.*cap_msmf.*')

# Suppress stderr output from OpenCV (where MSMF warnings come from)
# This is a more aggressive approach - only use if needed
if os.environ.get('SUPPRESS_OPENCV_STDERR', 'false').lower() == 'true':
    import io
    from contextlib import redirect_stderr

    # Redirect OpenCV stderr to null
    class OpenCVErrorFilter:
        def __init__(self):
            self.original_stderr = sys.stderr
            self.filtered = False

        def write(self, text):
            try:
                # Filter out MSMF warnings
                if 'MSMF' in text or 'grabFrame' in text or 'cap_msmf' in text:
                    return  # Don't write MSMF warnings
                self.original_stderr.write(text)

            except Exception as e:
                self.logger.error(f"Error in write: {e}", exc_info=True)
                raise
        def flush(self):
            self.original_stderr.flush()

    sys.stderr = OpenCVErrorFilter()


def apply_opencv_warning_suppression():
    """Apply OpenCV warning suppression - call this at the start of scripts"""
    # Set environment variable
    os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'

    # Suppress warnings
    warnings.filterwarnings('ignore', category=UserWarning, module='cv2')
    warnings.filterwarnings('ignore', message='.*MSMF.*')
    warnings.filterwarnings('ignore', message='.*grabFrame.*')
    warnings.filterwarnings('ignore', message='.*cap_msmf.*')

    # Try to set OpenCV logging level directly if available
    try:
        import cv2
        # OpenCV 4.x has setLogLevel
        if hasattr(cv2, 'setLogLevel'):
            cv2.setLogLevel(cv2.LOG_LEVEL_ERROR)
        # Or use the C++ API if available
        if hasattr(cv2, 'utils'):
            cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
    except:
        pass


if __name__ == "__main__":
    print("=" * 80)
    print("🔇 OPENCV WARNING SUPPRESSION")
    print("=" * 80)
    print()
    print("This module suppresses OpenCV MSMF grabFrame warnings.")
    print()
    print("To use in your script:")
    print("   from suppress_opencv_warnings import apply_opencv_warning_suppression")
    print("   apply_opencv_warning_suppression()")
    print()
    print("Or set environment variable:")
    print("   OPENCV_LOG_LEVEL=ERROR")
    print()
    print("=" * 80)
