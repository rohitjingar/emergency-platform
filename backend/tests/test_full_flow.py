# tests/test_full_flow.py
import time
import os
import requests


def log(msg): print(f"\n{'='*50}\n{msg}\n{'='*50}")
def ok(msg): print(f"  ✅ {msg}")
def fail(msg): print(f"  ❌ {msg}")

BASE_URL = "http://localhost:8000"

# ── Auth helpers ─────────────────────────────────────

def register(email, password, role):
    r = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email, "password": password, "role": role
    })
    assert r.status_code == 200, f"Register failed: {r.text}"
    ok(f"Registered {email} as {role}")
    return r.json()

def login(email, password):
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email, "password": password
    })
    assert r.status_code == 200, f"Login failed: {r.text}"
    token = r.json()["access_token"]
    ok(f"Logged in as {email}")
    return token

def headers(token):
    return {"Authorization": f"Bearer {token}"}

# ── Test Flow ────────────────────────────────────────

def test_full_flow():


    log("STEP 1: Register users")
    register("affected1@test.com", "test123", "affected_user")
    register("volunteer1@test.com", "test123", "volunteer")

    log("STEP 2: Login")
    affected_token = login("affected1@test.com", "test123")
    volunteer_token = login("volunteer1@test.com", "test123")

    log("STEP 3: Setup volunteer COMPLETELY before incident")
    r = requests.post(f"{BASE_URL}/volunteers/register",
        json={"skills": ["flood", "rescue"], "radius_km": 15.0},
        headers=headers(volunteer_token)
    )
    assert r.status_code == 200, f"Volunteer register failed: {r.text}"
    ok("Volunteer profile created")

    r = requests.patch(f"{BASE_URL}/volunteers/location",
        json={"latitude": 26.9100, "longitude": 75.7850},
        headers=headers(volunteer_token)
    )
    assert r.status_code == 200, f"Location update failed: {r.text}"
    ok("Location updated")

    r = requests.patch(f"{BASE_URL}/volunteers/status",
        json={"status": "available"},
        headers=headers(volunteer_token)
    )
    assert r.status_code == 200, f"Status update failed: {r.text}"
    ok("Status set to available")

    # small delay — ensure Redis cache is populated before incident
    time.sleep(1)

    log("STEP 4: Submit incident")
    r = requests.post(f"{BASE_URL}/incidents/",
        json={
            "type": "flood",
            "description": "elderly woman trapped on rooftop, water rising fast",
            "latitude": 26.9124,
            "longitude": 75.7873,
            "priority": "high"
        },
        headers=headers(affected_token)
    )
    assert r.status_code == 200, f"Incident creation failed: {r.text}"
    incident = r.json()
    incident_id = incident["incident"]["id"]
    ok(f"Incident created: id={incident_id}, status={incident['incident']['status']}")
    assert incident["queued"] == True, "Job not queued!"
    ok("Job enqueued to Redis")

    log("STEP 5: Wait for triage + assignment (10 seconds)")
    for i in range(10):
        print(f"  Waiting... {i+1}s", end="\r")
        time.sleep(1)

    log("STEP 6: Check incident status")
    r = requests.get(f"{BASE_URL}/incidents/{incident_id}/status",
        headers=headers(affected_token)
    )
    assert r.status_code == 200, f"Status check failed: {r.text}"
    status = r.json()
    print(f"  Incident status:    {status['status']}")
    print(f"  Severity:           {status['severity']}")
    print(f"  Confidence:         {status['confidence']}")
    print(f"  Assigned volunteer: {status['assigned_volunteer_id']}")
    print(f"  Attempts:           {status['assignment_attempts']}")

    if status["status"] == "pending_assignment":
        ok("Volunteer found and notified")
    elif status["status"] == "searching":
        fail("No volunteer found yet — check worker terminals")
        return
    else:
        fail(f"Unexpected status: {status['status']}")
        return

    log("STEP 7: Check volunteer pending incidents")
    r = requests.get(f"{BASE_URL}/volunteers/my-pending",
        headers=headers(volunteer_token)
    )
    assert r.status_code == 200, f"My pending failed: {r.text}"
    pending = r.json()
    print(f"  Pending incidents: {pending['count']}")
    if pending["count"] > 0:
        ok("Volunteer sees pending incident")
        p = pending["pending_incidents"][0]
        print(f"  Type: {p['type']}, Severity: {p['severity']}")
    else:
        fail("Volunteer has no pending incidents")
        return

    log("STEP 8: Volunteer accepts incident")
    r = requests.post(
        f"{BASE_URL}/volunteers/incidents/{incident_id}/accept",
        headers=headers(volunteer_token)
    )
    assert r.status_code == 200, f"Accept failed: {r.text}"
    accept = r.json()
    ok(f"Incident accepted: status={accept['status']}")

    log("STEP 9: Verify incident is assigned")
    r = requests.get(f"{BASE_URL}/incidents/{incident_id}/status",
        headers=headers(affected_token)
    )
    status = r.json()
    assert status["status"] == "assigned", \
        f"Expected assigned, got {status['status']}"
    ok("Incident status = assigned ✅")

    log("STEP 10: Check notifications")
    r = requests.get(f"{BASE_URL}/notifications/my",
        headers=headers(affected_token)
    )
    notifs = r.json()
    print(f"  Affected user notifications: {notifs['count']}")
    for n in notifs["notifications"]:
        print(f"  [{n['type']}] {n['message'][:60]}...")
        ok(f"Notification: {n['type']}")

    r = requests.get(f"{BASE_URL}/notifications/my",
        headers=headers(volunteer_token)
    )
    notifs = r.json()
    print(f"  Volunteer notifications: {notifs['count']}")
    for n in notifs["notifications"]:
        print(f"  [{n['type']}] {n['message'][:60]}...")
        ok(f"Notification: {n['type']}")

    log("✅ FULL FLOW TEST PASSED")

# ── Decline Flow ─────────────────────────────────────

def test_decline_flow():
    log("DECLINE FLOW TEST")

    affected_token = login("affected1@test.com", "test123")
    volunteer_token = login("volunteer1@test.com", "test123")

    # reset volunteer to available
    r = requests.patch(f"{BASE_URL}/volunteers/status",
        json={"status": "available"},
        headers=headers(volunteer_token)
    )
    assert r.status_code == 200, f"Status reset failed: {r.text}"
    ok("Volunteer reset to available")

    time.sleep(1)  # ensure cache updated

    log("Submit new incident for decline test")
    r = requests.post(f"{BASE_URL}/incidents/",
        json={
            "type": "flood",
            "description": "person trapped, need rescue immediately",
            "latitude": 26.9200,
            "longitude": 75.7900,
            "priority": "high"
        },
        headers=headers(affected_token)
    )
    assert r.status_code == 200, f"Incident creation failed: {r.text}"
    incident_id = r.json()["incident"]["id"]
    ok(f"Incident created: id={incident_id}")

    log("Wait 10 seconds for assignment")
    for i in range(10):
        print(f"  Waiting... {i+1}s", end="\r")
        time.sleep(1)

    log("Check volunteer pending")
    r = requests.get(f"{BASE_URL}/volunteers/my-pending",
        headers=headers(volunteer_token)
    )
    pending = r.json()
    if pending["count"] == 0:
        fail("No pending incidents — worker may not have processed yet")
        return
    ok(f"Volunteer has {pending['count']} pending incident(s)")

    log("Volunteer declines with 30 min unavailability")
    r = requests.post(
        f"{BASE_URL}/volunteers/incidents/{incident_id}/decline",
        json={"unavailable_minutes": 30},
        headers=headers(volunteer_token)
    )
    assert r.status_code == 200, f"Decline failed: {r.text}"
    ok(f"Declined: {r.json()['message']}")

    log("Check incident status after decline (wait 3s)")
    time.sleep(3)
    r = requests.get(f"{BASE_URL}/incidents/{incident_id}/status",
        headers=headers(affected_token)
    )
    status = r.json()
    print(f"  Status after decline: {status['status']}")
    print(f"  Attempts: {status['assignment_attempts']}")
    ok(f"Status = {status['status']}")

    log("✅ DECLINE FLOW TEST COMPLETE")


if __name__ == "__main__":
    print("\n🚨 Emergency Platform — Full Flow Test\n")
    test_full_flow()
    print("\n")
    test_decline_flow()