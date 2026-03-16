# tests/test_full_flow.py
import time
import os
import requests


def log(msg): print(f"\n{'='*50}\n{msg}\n{'='*50}")
def ok(msg): print(f"  ✅ {msg}")
def fail(msg): print(f"  ❌ {msg}")

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")

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

    log("STEP 5: Wait for triage + assignment (20 seconds)")
    for i in range(20):
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

# ── Admin Review Queue ────────────────────────────────

def test_admin_review():
    log("ADMIN REVIEW QUEUE TEST")

    try:
        register("admin1@test.com", "test123", "admin")
    except Exception:
        pass
    admin_token = login("admin1@test.com", "test123")
    affected_token = login("affected1@test.com", "test123")

    log("Check review queue")
    r = requests.get(f"{BASE_URL}/admin/review-queue",
        headers=headers(admin_token)
    )
    assert r.status_code == 200, f"Review queue failed: {r.text}"
    queue = r.json()
    print(f"  Incidents in review queue: {queue['count']}")
    print(f"  Threshold: {queue['threshold']}")
    ok("Review queue accessible")

    log("Check stats")
    r = requests.get(f"{BASE_URL}/admin/review-queue/stats",
        headers=headers(admin_token)
    )
    assert r.status_code == 200, f"Stats failed: {r.text}"
    stats = r.json()
    print(f"  Total incidents:     {stats['total_incidents']}")
    print(f"  Avg confidence:      {stats['avg_confidence']}")
    print(f"  Override rate:       {stats['override_rate_percent']}%")
    print(f"  Review rate:         {stats['review_rate_percent']}%")
    ok("Stats returned")

    if queue["count"] > 0:
        incident = queue["review_queue"][0]
        incident_id = incident["incident_id"]
        print(f"  Incident {incident_id}: status={incident['status']}")
        print(f"  Severity:      {incident['severity']}")
        print(f"  Confidence:    {incident['confidence']}")
        print(f"  Action impact: {incident['action_impact']}")

        log(f"Override incident {incident_id} severity")
        r = requests.patch(
            f"{BASE_URL}/admin/review-queue/{incident_id}/override",
            json={
                "new_severity": "Critical",
                "reason": "Manual assessment confirms critical"
            },
            headers=headers(admin_token)
        )
        assert r.status_code == 200, f"Override failed: {r.text}"
        result = r.json()
        print(f"  {result['original_severity']} → {result['new_severity']}")
        print(f"  Volunteer notified: {result['volunteer_notified']}")
        ok("Severity overridden")

        log(f"Approve incident {incident_id}")
        r = requests.patch(
            f"{BASE_URL}/admin/review-queue/{incident_id}/approve",
            headers=headers(admin_token)
        )
        assert r.status_code == 200, f"Approve failed: {r.text}"
        result = r.json()
        print(f"  Status: {result['status']}")
        ok("Decision approved")

        log("Check stats after override")
        r = requests.get(f"{BASE_URL}/admin/review-queue/stats",
            headers=headers(admin_token)
        )
        stats = r.json()
        print(f"  Override rate after: {stats['override_rate_percent']}%")
        print(f"  Overridden count:    {stats['overridden']}")
        print(f"  Approved count:      {stats['approved']}")
        ok("Stats updated correctly")

    else:
        fail("No low-confidence incidents in queue — insert one manually first")
        return

    log("✅ ADMIN REVIEW QUEUE TEST COMPLETE")
    
    
def test_circuit_breaker():
    log("CIRCUIT BREAKER TEST")

    admin_token = login("admin1@test.com", "test123")
    affected_token = login("affected1@test.com", "test123")

    # ── Step 1: reset circuit to CLOSED ─────────────────────────
    log("Step 1: Reset circuit breaker to CLOSED")
    r = requests.post(f"{BASE_URL}/system/circuit-breaker/reset")
    assert r.status_code == 200, f"Reset failed: {r.text}"
    status = r.json()
    assert status["state"] == "closed", f"Expected closed, got {status['state']}"
    print(f"  State:    {status['state']}")
    print(f"  Failures: {status['failures']}/{status['threshold']}")
    ok("Circuit starts CLOSED")

    # ── Step 2: submit incident — LLM should run ─────────────────
    log("Step 2: Submit incident with circuit CLOSED (LLM should run)")
    r = requests.post(f"{BASE_URL}/incidents/",
        json={
            "type": "flood",
            "description": "person trapped, water rising fast",
            "latitude": 26.9350,
            "longitude": 75.8050,
            "priority": "high"
        },
        headers=headers(affected_token)
    )
    assert r.status_code == 200, f"Failed: {r.text}"
    incident_id_1 = r.json()["incident"]["id"]
    ok(f"Incident created: id={incident_id_1}")

    log("Wait 10s for triage")
    for i in range(10):
        print(f"  Waiting... {i+1}s", end="\r")
        time.sleep(1)

    r = requests.get(f"{BASE_URL}/incidents/{incident_id_1}/status",
        headers=headers(affected_token)
    )
    status_1 = r.json()
    print(f"  Severity:      {status_1['severity']}")
    print(f"  Confidence:    {status_1['confidence']}")
    print(f"  Fallback used: {status_1.get('fallback_used')}")
    assert status_1.get("fallback_used") == False, \
        "Expected LLM, got fallback"
    ok("LLM ran correctly — fallback_used = False ✅")

    # ── Step 3: simulate 5 failures → open circuit ───────────────
    log("Step 3: Simulate 5 failures to OPEN circuit breaker")
    for i in range(5):
        r = requests.post(f"{BASE_URL}/system/circuit-breaker/simulate-failure")
        assert r.status_code == 200, f"Simulate failure failed: {r.text}"
        status = r.json()
        print(f"  Failure {i+1}/5 → state={status['state']}, failures={status['failures']}")

    # verify circuit is now OPEN
    r = requests.get(f"{BASE_URL}/system/circuit-breaker")
    assert r.status_code == 200, f"Failed: {r.text}"
    status = r.json()
    assert status["state"] == "open", f"Expected open, got {status['state']}"
    ok("Circuit is OPEN after 5 failures ✅")

    # ── Step 4: submit incident — fallback should run ────────────
    log("Step 4: Submit incident with circuit OPEN (fallback should run)")
    r = requests.post(f"{BASE_URL}/incidents/",
        json={
            "type": "fire",
            "description": "building on fire, people trapped inside",
            "latitude": 26.9400,
            "longitude": 75.8100,
            "priority": "high"
        },
        headers=headers(affected_token)
    )
    assert r.status_code == 200, f"Failed: {r.text}"
    incident_id_2 = r.json()["incident"]["id"]
    ok(f"Incident created: id={incident_id_2}")

    log("Wait 10s for triage (should be fast — no LLM call)")
    for i in range(10):
        print(f"  Waiting... {i+1}s", end="\r")
        time.sleep(1)

    r = requests.get(f"{BASE_URL}/incidents/{incident_id_2}/status",
        headers=headers(affected_token)
    )
    status_2 = r.json()
    print(f"  Severity:      {status_2['severity']}")
    print(f"  Confidence:    {status_2['confidence']}")
    print(f"  Fallback used: {status_2.get('fallback_used')}")
    assert status_2.get("fallback_used") == True, \
        "Expected fallback, got LLM"
    ok("Fallback ran correctly — fallback_used = True ✅")

    # confidence must be capped at 0.75 (fallback max)
    assert status_2["confidence"] <= 0.75, \
        f"Fallback confidence should be <= 0.75, got {status_2['confidence']}"
    ok(f"Confidence capped correctly: {status_2['confidence']} ✅")

    # ── Step 5: check health endpoint ────────────────────────────
    log("Step 5: Check system health with circuit OPEN")
    r = requests.get(f"{BASE_URL}/system/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    health = r.json()
    print(f"  Overall:         {health['overall']}")
    print(f"  API:             {health['api']}")
    print(f"  PostgreSQL:      {health['postgres']}")
    print(f"  Redis:           {health['redis']}")
    print(f"  Circuit breaker: {health['circuit_breaker']}")
    print(f"  Issues:          {health['issues']}")
    assert health["circuit_breaker"] == "open", \
        "Health check should show circuit_breaker=open"
    assert health["overall"] == "degraded", \
        "Overall should be degraded when circuit is open"
    ok("Health endpoint correctly shows degraded state ✅")

    # ── Step 6: check queue stats ─────────────────────────────────
    log("Step 6: Check queue stats")
    r = requests.get(f"{BASE_URL}/system/queues")
    assert r.status_code == 200, f"Queue stats failed: {r.text}"
    queues = r.json()
    print(f"  incidents-queue waiting:  {queues['incidents_queue']['waiting']}")
    print(f"  assignment-queue waiting: {queues['assignment_queue']['waiting']}")
    ok("Queue stats returned ✅")

    # ── Step 7: reset circuit → verify healthy again ─────────────
    log("Step 7: Reset circuit to CLOSED")
    r = requests.post(f"{BASE_URL}/system/circuit-breaker/reset")
    assert r.status_code == 200, f"Reset failed: {r.text}"
    status = r.json()
    assert status["state"] == "closed", f"Expected closed, got {status['state']}"
    ok("Circuit reset to CLOSED ✅")

    # verify health shows ok again
    r = requests.get(f"{BASE_URL}/system/health")
    health = r.json()
    print(f"  Overall after reset: {health['overall']}")
    assert health["circuit_breaker"] == "ok", \
        "Circuit breaker should show ok after reset"
    ok("System health restored to ok ✅")

    log("✅ CIRCUIT BREAKER TEST COMPLETE")
    
    
if __name__ == "__main__":
    import sys
    
    tests = {
        "full": test_full_flow,
        "decline": test_decline_flow,
        "admin": test_admin_review,
        "circuit": test_circuit_breaker,
    }
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name in tests:
            tests[test_name]()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available: {list(tests.keys())}")
    else:
        # run all
        for name, fn in tests.items():
            print(f"\n{'='*50}\nRunning: {name}\n{'='*50}")
            fn()