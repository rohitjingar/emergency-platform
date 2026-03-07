EMERGENCY_DOCS = [
    {
        "id": "electric_shock_1",
        "content": """Electric Shock First Aid - Red Cross Guidelines:
1. DO NOT touch the person if they are still in contact with electrical source
2. Call emergency services immediately (112/911)
3. Turn off the power source if safely possible
4. Once safe, check if person is breathing
5. If unconscious and not breathing, begin CPR immediately
6. Do not move the person unless in immediate danger
7. Treat for shock: keep person warm, lay flat, elevate legs slightly
8. Check for burns at entry and exit points of electricity
9. Do not apply ice to electrical burns
10. Keep person still until medical help arrives""",
        "metadata": {"source": "Red Cross", "category": "electric_shock", "severity": "critical"}
    },
    {
        "id": "flood_protocol_1",
        "content": """Flood Emergency Protocol - NDRF Guidelines:
1. Move immediately to higher ground, do not wait for instructions
2. Avoid walking in moving water — 6 inches can knock you down
3. Do not drive through flooded roads — turn around, don't drown
4. Disconnect electrical appliances if safe to do so
5. Avoid contact with floodwater — may be contaminated
6. Do not touch electrical equipment if wet or standing in water
7. Signal for help from roof or high point using bright cloth
8. Drink only bottled or boiled water after flooding
9. Watch for displaced animals especially snakes in floodwater
10. Wait for official all-clear before returning home""",
        "metadata": {"source": "NDRF", "category": "flood", "severity": "high"}
    },
    {
        "id": "fire_emergency_1",
        "content": """Fire Emergency Response - Red Cross Guidelines:
1. Activate nearest fire alarm immediately
2. Call fire services (101 in India / 911 in US)
3. Evacuate using stairs, never use elevator during fire
4. Feel door before opening — if hot, do not open
5. Stay low under smoke — cleaner air is near the floor
6. Close doors behind you to slow fire spread
7. If clothes catch fire: Stop, Drop, and Roll
8. Never re-enter burning building for belongings
9. Meet at designated assembly point outside
10. If trapped, seal gaps under doors with cloth, signal from window""",
        "metadata": {"source": "Red Cross", "category": "fire", "severity": "critical"}
    },
    {
        "id": "cardiac_arrest_1",
        "content": """Cardiac Arrest First Aid - WHO Guidelines:
1. Check for responsiveness — tap shoulders, shout
2. Call emergency services immediately (112)
3. Begin CPR: 30 chest compressions, 2 rescue breaths
4. Compress hard and fast — 2 inches deep, 100-120 per minute
5. Use AED if available — turn on and follow voice instructions
6. Do not stop CPR until medical help arrives
7. If untrained in CPR, do hands-only CPR (no rescue breaths)
8. Continue CPR even if person appears not to respond
9. Loosen tight clothing around neck and chest
10. Keep person on firm flat surface during CPR""",
        "metadata": {"source": "WHO", "category": "cardiac_arrest", "severity": "critical"}
    },
    {
        "id": "drowning_1",
        "content": """Drowning Response - WHO Guidelines:
1. Do not jump in water unless trained — throw rope or flotation device
2. Call emergency services immediately (112)
3. Once out of water, check for breathing
4. If not breathing: drowning CPR differs from standard CPR — see drowning_cpr_1
5. Do not do abdominal thrusts to remove water
6. Keep person warm — drowning victims lose body heat fast
7. Even if person seems fine, take to hospital — secondary drowning risk
8. Do not give food or water until fully conscious
9. Place unconscious breathing person in recovery position
10. Continue monitoring until medical help arrives""",
        "metadata": {"source": "WHO", "category": "drowning", "severity": "critical"}
    },
    {
        "id": "earthquake_1",
        "content": """Earthquake Emergency Protocol - NDRF Guidelines:
1. Drop, Cover, and Hold On immediately
2. Get under sturdy desk or table, protect head and neck
3. Stay away from windows, exterior walls, and heavy furniture
4. If outdoors, move away from buildings, trees, and power lines
5. Do not run outside during shaking — most injuries from falling debris
6. If in vehicle, pull over away from bridges and overpasses
7. After shaking stops, check for injuries before moving
8. Expect aftershocks — be prepared to Drop, Cover, Hold again
9. Check for gas leaks — if smell gas, evacuate and call authorities
10. Do not use elevators after earthquake""",
        "metadata": {"source": "NDRF", "category": "earthquake", "severity": "high"}
    },
    
    {
        "id": "burns_treatment_1",
        "content": """Burns First Aid - Red Cross Guidelines:
    Common questions: burn treatment, butter on burn, oil on burn, ice on burn,
    what to put on a burn, scald treatment, hot water burn, should I put butter on a burn,
    toothpaste on burn, home remedy for burn, burn blister treatment.

    CRITICAL — Common myths that cause harm:
    - DO NOT apply butter, oil, toothpaste, or any greasy substance to burns
    - DO NOT apply ice or ice-cold water — causes further tissue damage
    - DO NOT break blisters — increases infection risk
    - DO NOT remove clothing stuck to the burn

    Correct treatment:
    1. Call emergency services (112) for severe or large burns immediately
    2. Cool the burn under cool (not cold) running water for 10-20 minutes
    3. Remove jewellery or clothing near the burn — only if NOT stuck to skin
    4. Cover loosely with clean cling film or non-fluffy bandage
    5. Do not wrap tightly — swelling will occur
    6. For chemical burns: brush off dry chemical first, then cool with water 20+ mins
    7. For electrical burns: do not touch victim until power is off — see electric_shock_1
    8. Keep person warm — cooling a large burn area causes hypothermia
    9. Do not give food or drink if severe burn — surgery may be needed
    10. Severity guide: larger than palm of hand, or on face/hands/genitals = call 112""",
        "metadata": {"source": "Red Cross", "category": "burns", "severity": "high"}
    },

    {
        "id": "drowning_cpr_1",
        "content": """Drowning CPR Protocol - WHO Guidelines:
IMPORTANT: Drowning CPR is DIFFERENT from standard cardiac arrest CPR.

Standard CPR (cardiac arrest): start with 30 chest compressions first.
Drowning CPR: start with 5 RESCUE BREATHS first — then compressions.

Why the difference:
- Drowning causes oxygen deprivation first, cardiac arrest second
- The heart often still has oxygen but lungs are blocked
- Starting with rescue breaths addresses the root cause immediately

Drowning CPR Steps:
1. Call 112 immediately — do this first or assign someone
2. Lay victim flat on firm surface
3. Tilt head back, lift chin — unless spinal injury suspected
4. Give 5 full rescue breaths — watch chest rise with each
5. Check for pulse and breathing (10 seconds)
6. If no pulse: begin 30 compressions then 2 rescue breaths cycle
7. Compress 2 inches deep at 100-120 per minute
8. Continue until emergency services arrive
9. Do NOT perform abdominal thrusts to remove water — it delays CPR
10. After resuscitation: keep warm, take to hospital even if conscious — secondary drowning risk""",
        "metadata": {"source": "WHO", "category": "drowning_cpr", "severity": "critical"}
    },
    {
        "id": "spinal_injury_1",
        "content": """Spinal Injury First Aid - Red Cross Guidelines:
    Common questions: neck injury, back injury, spine injury, can't move neck,
    fell off bike, motorcycle accident neck, don't move injured person, paralysis prevention.

    Suspect spinal injury when: fall from height, road accident, bike accident,
    diving accident, heavy object fell on person, person unconscious after trauma,
    person cannot move neck or back, complaining of neck pain after fall.

    CRITICAL RULE: Do NOT move the person — movement can cause permanent paralysis.

    1. Call 112 immediately — spinal injury requires professional handling
    2. Keep the person completely still — head, neck, and body
    3. If person must be moved due to immediate danger: keep head, neck, body
    aligned as one unit — requires minimum 3 people
    4. Do not attempt to straighten the neck or back
    5. If unconscious but breathing: do NOT put in recovery position — maintain stillness
    6. If unconscious and not breathing: airway takes priority — use jaw thrust
    technique (not head tilt) to open airway without moving neck
    7. Jaw thrust: place fingers behind jaw angle, push jaw forward without tilting head
    8. If person vomits: log roll entire body as one unit to prevent choking
    9. Keep person warm — use blanket without moving them
    10. Reassure person — panic causes movement which worsens injury
    11. Do not remove helmet if motorcyclist — leave for medical professionals""",
        "metadata": {"source": "Red Cross", "category": "spinal_injury", "severity": "critical"}
    },
    {
        "id": "choking_1",
        "content": """Choking First Aid - Red Cross Guidelines:

Identify choking: person clutching throat, cannot speak/cry/cough effectively,
face turning red then blue, high-pitched noise or no sound when breathing.

For CONSCIOUS adult or child over 1 year:
1. Ask: "Are you choking?" — if they can speak, encourage coughing
2. Call 112 if object not dislodged quickly
3. Give 5 firm back blows: lean person forward, heel of hand between shoulder blades
4. Check mouth after each blow — remove visible object only (do not finger sweep)
5. If back blows fail: give 5 abdominal thrusts (Heimlich manoeuvre)
   - Stand behind person, arms around waist
   - One fist above navel, below breastbone
   - Second hand over fist — pull sharply inward and upward
6. Alternate 5 back blows and 5 abdominal thrusts until object dislodged or 112 arrives
7. If person becomes unconscious: lower to ground, call 112, begin CPR
8. During CPR: check mouth before rescue breaths — remove visible objects only

For INFANT under 1 year — different technique:
1. Hold face-down on forearm, support head
2. Give 5 back blows with 2 fingers between shoulder blades
3. Turn face-up, give 5 chest thrusts with 2 fingers on centre of chest
4. Never perform abdominal thrusts on infant

For PREGNANT or OBESE person:
- Use chest thrusts instead of abdominal thrusts
- Position hands on centre of chest, not abdomen""",
        "metadata": {"source": "Red Cross", "category": "choking", "severity": "critical"}
    },
    {
        "id": "snake_bite_1",
        "content": """Snake Bite First Aid - WHO Guidelines:
    Common questions: snake bite first aid, should I suck venom out of snake bite,
    sucking snake venom, snake bit my friend, bitten by snake what to do,
    cut the bite snake, tourniquet for snake bite, snake bite treatment India,
    how to treat snake bite, is sucking venom helpful.

    Most important rule: get to hospital immediately — antivenom is the only cure.

    DO NOT do these common myths that cause harm:
    - DO NOT cut the bite and suck out venom — causes infection, spreads venom faster
    - DO NOT apply tourniquet — cuts blood supply, causes tissue death
    - DO NOT apply ice — does not neutralise venom, causes cold injury
    - DO NOT apply electric shock — no evidence, causes burns
    - DO NOT give alcohol — accelerates venom absorption
    - DO NOT try to catch or kill the snake — causes more bites

    Correct steps:
    1. Call 112 immediately or get to nearest hospital — time is critical
    2. Keep person calm and still — movement increases venom spread through lymphatic system
    3. Immobilise bitten limb — splint like a fracture, keep below heart level
    4. Remove watches, rings, tight clothing near bite — swelling will occur
    5. Mark the edge of swelling with pen every 15 minutes — shows progression to doctors
    6. Note time of bite, snake appearance if safely possible — helps doctors choose antivenom
    7. Keep person lying down — reduces blood pressure and venom spread
    8. Do not give food, water, or any medication — may interfere with treatment
    9. If person stops breathing: begin CPR immediately
    10. Most Indian snakes: Big 4 are Cobra, Krait, Russell's Viper, Saw-scaled Viper
        — all treated with polyvalent antivenom available at government hospitals""",
        "metadata": {"source": "WHO", "category": "snake_bite", "severity": "critical"}
    },
    {
        "id": "road_accident_1",
        "content": """Road Accident First Aid - Red Cross + NDRF Guidelines:

At the scene:
1. Call 112 immediately — give location, number of casualties, visible injuries
2. Turn on hazard lights, place warning triangle 50m behind vehicle if safe
3. Do not move casualties unless immediate danger (fire, traffic) — spinal injury risk
4. Turn off ignition of crashed vehicles if accessible — fire prevention
5. Do not give food, water, or medication to injured — surgery may be needed

Assessing casualties:
6. Check consciousness: tap shoulders, shout "Can you hear me?"
7. Check breathing: look for chest rise, feel for breath (10 seconds)
8. If unconscious and not breathing: begin CPR — call 112 first
9. If unconscious but breathing: maintain position, monitor until help arrives
   (do not move to recovery position if spinal injury suspected)

Bleeding control:
10. Apply firm direct pressure to bleeding wounds — use cloth, bandage, or clothing
11. Do not remove embedded objects — press around them
12. Maintain pressure continuously — do not lift to check (breaks clot)
13. If limb bleeding uncontrollable: tourniquet 5-7cm above wound as last resort
    — note exact time applied, do not remove until medical help

Legal note (India):
Good Samaritan Law protects bystanders who help accident victims in good faith.
You cannot be held liable for providing first aid assistance at accident scene.""",
        "metadata": {"source": "Red Cross", "category": "road_accident", "severity": "critical"}
    },
]