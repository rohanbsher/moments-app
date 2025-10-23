#!/usr/bin/env python3
"""
Create diverse test videos to validate the algorithm
Tests: sports, party, nature, meeting scenarios
"""

import cv2
import numpy as np
import os

def create_sports_video(output_path="test_sports_action.mp4", duration=120):
    """
    Simulate sports video: Slow start, high action middle, slow end
    Represents: Soccer game with goals, plays, celebrations
    """
    print(f"🏀 Creating sports/action test video: {duration}s")

    fps = 30
    width, height = 1280, 720
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total_frames = fps * duration

    for frame_idx in range(total_frames):
        time = frame_idx / fps

        # Create base frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Simulate game phases
        if time < 20:
            # Slow start: warmup, low activity
            motion_intensity = 20
            color = (30, 50, 30)  # Dark green (field)
            text = "Warmup - Low Activity"
        elif time < 40:
            # High action: goals, fast plays
            motion_intensity = 150
            color = (0, 255, 0)  # Bright green
            text = "GOAL! High Action"
        elif time < 70:
            # Medium activity: normal play
            motion_intensity = 60
            color = (50, 100, 50)
            text = "Normal Play"
        elif time < 90:
            # High action again: final push
            motion_intensity = 140
            color = (0, 200, 0)
            text = "Final Push - Exciting!"
        else:
            # End: celebration, slow down
            motion_intensity = 40
            color = (30, 80, 30)
            text = "Game Over - Cool Down"

        # Fill background
        frame[:] = color

        # Add moving elements (simulate players)
        num_objects = motion_intensity // 20
        for i in range(num_objects):
            x = int((frame_idx * (i + 1) * 3) % width)
            y = int(height / 2 + 100 * np.sin(frame_idx * 0.1 * (i + 1)))
            cv2.circle(frame, (x, y), 30, (255, 255, 255), -1)

        # Add text overlay
        cv2.putText(frame, text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(frame, f"Time: {int(time)}s", (50, height - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        out.write(frame)

        if frame_idx % 300 == 0:
            print(f"  Progress: {frame_idx}/{total_frames} frames ({time:.0f}s)")

    out.release()
    print(f"✅ Sports video created: {output_path}")
    return output_path


def create_party_video(output_path="test_party_celebration.mp4", duration=90):
    """
    Simulate party video: Varied activity with peaks (cake, dancing, toasts)
    Represents: Birthday party with celebrations, quiet moments
    """
    print(f"🎉 Creating party/celebration test video: {duration}s")

    fps = 30
    width, height = 1280, 720
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total_frames = fps * duration

    for frame_idx in range(total_frames):
        time = frame_idx / fps

        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Simulate party phases
        if time < 15:
            # Arrival: medium activity
            motion_intensity = 50
            color = (100, 50, 150)  # Purple
            text = "Guests Arriving"
        elif time < 25:
            # CAKE CUTTING: High activity, important moment
            motion_intensity = 180
            color = (0, 255, 255)  # Yellow (bright)
            text = "CAKE TIME! 🎂"
        elif time < 40:
            # Eating: low activity
            motion_intensity = 30
            color = (80, 40, 100)
            text = "Enjoying Food"
        elif time < 55:
            # DANCING: Very high activity
            motion_intensity = 200
            color = (255, 0, 255)  # Magenta (dancing lights)
            text = "DANCING! 💃"
        elif time < 70:
            # Socializing: medium activity
            motion_intensity = 60
            color = (100, 50, 120)
            text = "Chatting & Laughing"
        else:
            # Goodbye: low activity
            motion_intensity = 40
            color = (60, 30, 80)
            text = "Saying Goodbye"

        frame[:] = color

        # Add motion (people, decorations)
        num_objects = motion_intensity // 15
        for i in range(num_objects):
            x = int((frame_idx * (i + 2) * 5) % width)
            y = int(height / 2 + 150 * np.sin(frame_idx * 0.15 * (i + 1)))
            size = 20 + (motion_intensity // 10)
            cv2.circle(frame, (x, y), size, (255, 255, 0), -1)

        # Add confetti during high-energy moments
        if motion_intensity > 150:
            for _ in range(50):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                cv2.circle(frame, (x, y), 5, (255, 255, 255), -1)

        cv2.putText(frame, text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(frame, f"{int(time)}s", (50, height - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        out.write(frame)

        if frame_idx % 300 == 0:
            print(f"  Progress: {frame_idx}/{total_frames} frames ({time:.0f}s)")

    out.release()
    print(f"✅ Party video created: {output_path}")
    return output_path


def create_nature_video(output_path="test_nature_scenic.mp4", duration=100):
    """
    Simulate nature video: Mostly static with occasional wildlife
    Represents: Landscape video with occasional bird, animal movement
    """
    print(f"🏞️ Creating nature/scenic test video: {duration}s")

    fps = 30
    width, height = 1280, 720
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total_frames = fps * duration

    for frame_idx in range(total_frames):
        time = frame_idx / fps

        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Simulate nature scenes
        if time < 30:
            # Static landscape: mountains, sky
            motion_intensity = 10
            color = (139, 90, 43)  # Brown (mountains)
            text = "Mountain View - Calm"
        elif time < 45:
            # WILDLIFE APPEARS: Bird flying, deer
            motion_intensity = 120
            color = (100, 149, 237)  # Cornflower blue (sky)
            text = "Bird Flying! 🦅"
        elif time < 70:
            # Static again: sunset
            motion_intensity = 15
            color = (255, 140, 0)  # Orange (sunset)
            text = "Beautiful Sunset"
        else:
            # Water movement: river, waves
            motion_intensity = 50
            color = (30, 144, 255)  # Dodger blue (water)
            text = "Flowing River"

        frame[:] = color

        # Add gentle motion
        if motion_intensity > 100:
            # Wildlife movement
            x = int((frame_idx * 8) % width)
            y = int(height / 3 + 50 * np.sin(frame_idx * 0.05))
            cv2.circle(frame, (x, y), 40, (255, 255, 255), -1)
            cv2.putText(frame, "Wildlife", (x - 30, y + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        else:
            # Gentle swaying (wind, water)
            for i in range(5):
                x = int(width / 6 * (i + 1))
                y = int(height / 2 + 20 * np.sin(frame_idx * 0.02 + i))
                cv2.line(frame, (x, 0), (x, height), (200, 200, 200), 2)

        cv2.putText(frame, text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(frame, f"{int(time)}s", (50, height - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        out.write(frame)

        if frame_idx % 300 == 0:
            print(f"  Progress: {frame_idx}/{total_frames} frames ({time:.0f}s)")

    out.release()
    print(f"✅ Nature video created: {output_path}")
    return output_path


def create_meeting_video(output_path="test_meeting_presentation.mp4", duration=80):
    """
    Simulate meeting/presentation: Static with occasional slide changes
    Represents: Zoom call, presentation with minimal movement
    """
    print(f"💼 Creating meeting/presentation test video: {duration}s")

    fps = 30
    width, height = 1280, 720
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total_frames = fps * duration

    slide_number = 1

    for frame_idx in range(total_frames):
        time = frame_idx / fps

        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Simulate meeting phases
        if time < 15:
            # Intro: minimal movement
            motion_intensity = 5
            color = (40, 40, 40)  # Dark gray
            text = "Intro - Welcome"
        elif time < 30:
            # Slide presentation: static
            motion_intensity = 8
            color = (50, 50, 50)
            text = f"Slide {slide_number}: Data Analysis"
        elif time < 50:
            # Demo section: more movement
            motion_intensity = 40
            color = (60, 60, 60)
            text = "Live Demo - Screen Sharing"
        elif time < 65:
            # Q&A: Some movement
            motion_intensity = 25
            color = (45, 45, 45)
            text = "Q&A Session"
        else:
            # Closing: minimal
            motion_intensity = 10
            color = (35, 35, 35)
            text = "Closing Remarks"

        # Change slides every 15 seconds
        if int(time) % 15 == 0 and frame_idx % fps == 0:
            slide_number += 1

        frame[:] = color

        # Add minimal motion (cursor, slight camera movement)
        if motion_intensity > 30:
            # Cursor movement during demo
            x = int((frame_idx * 3) % width)
            y = int((frame_idx * 2) % height)
            cv2.circle(frame, (x, y), 10, (255, 255, 255), -1)

        # Add slide content
        cv2.rectangle(frame, (100, 200), (width - 100, height - 200), (80, 80, 80), -1)
        cv2.putText(frame, text, (150, 350), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        cv2.putText(frame, f"Time: {int(time)}s", (50, height - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)

        out.write(frame)

        if frame_idx % 300 == 0:
            print(f"  Progress: {frame_idx}/{total_frames} frames ({time:.0f}s)")

    out.release()
    print(f"✅ Meeting video created: {output_path}")
    return output_path


def main():
    print("\n" + "="*60)
    print("🎬 CREATING TEST VIDEOS FOR ALGORITHM VALIDATION")
    print("="*60 + "\n")

    videos = []

    # Create all test videos
    videos.append(create_sports_video())
    print()
    videos.append(create_party_video())
    print()
    videos.append(create_nature_video())
    print()
    videos.append(create_meeting_video())

    print("\n" + "="*60)
    print("✅ ALL TEST VIDEOS CREATED")
    print("="*60)
    print("\nCreated files:")
    for video in videos:
        size = os.path.getsize(video) / (1024 * 1024)
        print(f"  📹 {video} ({size:.1f} MB)")

    print("\n🎯 Next: Test these with fast_process.py")
    print("Example: python3 fast_process.py test_sports_action.mp4 highlights.mp4 30")

if __name__ == '__main__':
    main()