from django.shortcuts import render, redirect
from django import forms
from .models import Registration
from django.contrib.auth.hashers import make_password
from django.contrib import messages  # Import messages framework
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import cv2
import numpy as np

# ==============================
# Views for rendering pages
# ==============================
def index(request):
    return render(request, 'myapp/public/index.html')

def dash(request):
    return render(request, 'myapp/public/dash.html')

def navigate(request):
    return render(request, 'myapp/public/navigate.html')

def camera(request):
    return render(request, 'myapp/public/camera.html')

def generatecode(request):
    return render(request, 'myapp/public/generatecode.html')

def room(request):
    return render(request, 'myapp/public/room.html')

def login(request):
    return render(request, 'myapp/public/login.html')


# ==============================
# Registration model form
# ==============================
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Registration
        fields = ['first_name', 'second_name', 'email', 'class_level', 'faculty', 'phone_number', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


# ==============================
# Registration view
# ==============================
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful!')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    return render(request, 'myapp/public/register.html', {'form': form})


# ==============================
# Example location mapping
# ==============================
LOCATION_MAPPING = {
    0: {"name": "Location A", "coords": (0, 0)},
    1: {"name": "Location B", "coords": (1, 0)},
    2: {"name": "Location C", "coords": (2, 0)},
    3: {"name": "Location D", "coords": (3, 0)},
    4: {"name": "Location E", "coords": (4, 0)},
    5: {"name": "Location F", "coords": (5, 0)},
    6: {"name": "Location G", "coords": (6, 0)},
    7: {"name": "Location H", "coords": (7, 0)},
    8: {"name": "Location I", "coords": (8, 0)},
    9: {"name": "Location J", "coords": (9, 0)},
}

# ==============================
# Camera calibration
# ==============================
camera_matrix = np.array([[800, 0, 320],
                          [0, 800, 240],
                          [0, 0, 1]], dtype=np.float32)
dist_coeffs = np.zeros((5, 1))
MARKER_SIZE = 0.05  # meters


# ==============================
# Generate ArUco codes
# ==============================
@csrf_exempt
def generate_aruco_codes(request):
    if request.method == 'POST':
        num_codes = 10
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        generated_files = []

        for i in range(num_codes):
            marker_img = cv2.aruco.generateImageMarker(aruco_dict, i, 200)
            filename = f'GuideMe/static/aruco_codes/aruco_code_{i}.png'
            cv2.imwrite(filename, marker_img)

            generated_files.append({
                'id': str(i),
                'location': LOCATION_MAPPING[i]['name'],
                'file': f'/static/aruco_codes/aruco_code_{i}.png'
            })

        return JsonResponse({'success': True, 'files': generated_files})

    return JsonResponse({'success': False}, status=400)


# ==============================
# Video Feed Generator
# ==============================
def generate_frames(camera_index):
    cap = cv2.VideoCapture(camera_index)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    last_arrow = None
    last_text = {"current": None, "next": None}

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = detector.detectMarkers(gray)

            if ids is not None:
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)

                rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                    corners, MARKER_SIZE, camera_matrix, dist_coeffs
                )
                closest_index = np.argmin(tvecs[:, 0, 2])
                marker_id = int(ids[closest_index][0])
                rvec, tvec = rvecs[closest_index], tvecs[closest_index]

                cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvec, tvec, 0.05)

                current_location = LOCATION_MAPPING.get(marker_id, {"name": "Unknown", "coords": (0, 0)})
                next_id = marker_id + 1 if marker_id + 1 in LOCATION_MAPPING else None

                if next_id is not None:
                    next_location = LOCATION_MAPPING[next_id]
                    dx = next_location['coords'][0] - current_location['coords'][0]
                    dy = next_location['coords'][1] - current_location['coords'][1]

                    scale = 5.0
                    arrow_3D = np.float32([[0, 0, 0], [dx * scale, dy * scale, 0]])
                    imgpts, _ = cv2.projectPoints(arrow_3D, rvec, tvec, camera_matrix, dist_coeffs)

                    pt1 = tuple(imgpts[0].ravel().astype(int))
                    pt2 = tuple(imgpts[1].ravel().astype(int))

                    last_arrow = (pt1, pt2)
                    last_text["current"] = current_location['name']
                    last_text["next"] = next_location['name']
                else:
                    last_arrow = None
                    last_text["current"] = current_location['name']
                    last_text["next"] = "End of Path"

            if last_arrow is not None:
                cv2.arrowedLine(frame, last_arrow[0], last_arrow[1], (0, 255, 0), 8, tipLength=0.4)

            if last_text["current"]:
                cv2.putText(frame, f"Current: {last_text['current']}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            if last_text["next"]:
                color = (255, 0, 0) if last_text["next"] != "End of Path" else (0, 0, 255)
                cv2.putText(frame, f"Next: {last_text['next']}",
                            (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()


# ==============================
# Video feed endpoint (auto switchable)
# ==============================
def video_feed(request):
    camera_index = request.session.get("camera_index", 0)  # default is 0
    return StreamingHttpResponse(generate_frames(camera_index),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


# ==============================
# Switch camera endpoint
# ==============================
@csrf_exempt
def switch_camera(request):
    """Toggle between default (0) and USB (1) camera"""
    current_index = request.session.get("camera_index", 0)
    new_index = 1 if current_index == 0 else 0
    request.session["camera_index"] = new_index
    return JsonResponse({"success": True, "camera_index": new_index})


# ==============================
# Scan uploaded image
# ==============================
@csrf_exempt
def scan_aruco(request):
    if request.method == 'POST':
        image_file = request.FILES['image']
        file_bytes = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        detector = cv2.aruco.ArucoDetector(aruco_dict, cv2.aruco.DetectorParameters())
        corners, ids, _ = detector.detectMarkers(gray)

        if ids is not None:
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, MARKER_SIZE, camera_matrix, dist_coeffs
            )
            closest_index = np.argmin(tvecs[:, 0, 2])
            marker_id = int(ids[closest_index][0])
            rvec, tvec = rvecs[closest_index], tvecs[closest_index]

            current_location = LOCATION_MAPPING.get(marker_id, {"name": "Unknown", "coords": (0, 0)})
            next_id = marker_id + 1 if marker_id + 1 in LOCATION_MAPPING else None

            arrow_proj = None
            if next_id is not None:
                next_location = LOCATION_MAPPING[next_id]
                dx = next_location['coords'][0] - current_location['coords'][0]
                dy = next_location['coords'][1] - current_location['coords'][1]

                scale = 5.0
                arrow_3D = np.float32([[0, 0, 0], [dx * scale, dy * scale, 0]])
                imgpts, _ = cv2.projectPoints(arrow_3D, rvec, tvec, camera_matrix, dist_coeffs)

                pt1 = tuple(imgpts[0].ravel().tolist())
                pt2 = tuple(imgpts[1].ravel().tolist())
                arrow_proj = {"start": pt1, "end": pt2}

            return JsonResponse({
                "success": True,
                "id": str(marker_id),
                "location": current_location['name'],
                "next_location": LOCATION_MAPPING[next_id]['name'] if next_id else "End of Path",
                "arrow_proj": arrow_proj
            })

        return JsonResponse({"success": False, "message": "No markers detected"})

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)
