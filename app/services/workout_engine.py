from app.models.workout import WorkoutPlan, WorkoutDay, WorkoutExercise

class WorkoutEngine:
    """Rules-based personalized workout recommendation and progression engine."""

    @classmethod
    def generate_program(cls, user_id, profile):
        """
        Synthesizes user profile parameters into an evidence-based, customized workout plan.
        """
        days_count = max(2, min(6, profile.training_days_count or 3))
        experience = (profile.experience_level or 'beginner').lower()
        goal = (profile.primary_goal or 'general_fitness').lower()
        equipment_setting = (profile.equipment_setting or 'commercial_gym').lower()
        available_equipment = [e.lower() for e in (profile.available_equipment or [])]
        session_duration = profile.preferred_session_length or 45
        pain_movements = [p.lower() for p in (profile.pain_movements or [])]
        priority_muscles = [m.lower() for m in (profile.priority_muscle_groups or [])]

        is_bodyweight_only = equipment_setting == 'bodyweight_only' or ('barbells' not in available_equipment and 'dumbbells' not in available_equipment and 'cables' not in available_equipment and equipment_setting != 'commercial_gym')
        is_dumbbells_only = not is_bodyweight_only and ('dumbbells' in available_equipment or equipment_setting in ['home_gym', 'hostel_gym']) and 'barbells' not in available_equipment and 'cables' not in available_equipment

        is_return_to_training = 'return' in goal or 'rehab' in goal or (profile.physical_restrictions is not None and len(profile.physical_restrictions.strip()) > 5)

        # 1. Determine Split Type
        if is_return_to_training:
            split_type = 'conservative_return'
            title = f"Conservative Return to Training ({days_count} Days/Week)"
            progression = "Linear Volume Re-adaptation: RPE <= 6, prioritizing joint integrity and movement quality before adding load."
            recovery = "Allow at least 48 hours between sessions. If previous joint soreness persists, substitute session with 20-min gentle mobility walk."
        elif is_bodyweight_only:
            split_type = 'calisthenics_minimal'
            title = f"Full Body Calisthenics & Minimal Equipment ({days_count} Days/Week)"
            progression = "Repetition and Leverage Progression: Progress from standard reps to tempo control (3-second eccentrics) or harder leverage."
            recovery = "Prioritize shoulder and wrist mobility; maintain 7-8 hours sleep for nervous system recovery."
        elif days_count == 2:
            split_type = 'full_body_2day'
            title = "Two-Day Foundational Full Body Split"
            progression = "Double Progression: Hit top of rep target on all sets before increasing weight by 2.5kg."
            recovery = "Space training days with 2-3 rest days (e.g., Tuesday & Saturday)."
        elif days_count == 3:
            split_type = 'full_body_3day'
            title = "Three-Day Full Body Movement Synergy Split"
            progression = "Double Progression: Strive for 1 additional rep per session within the 8-12 rep range."
            recovery = "Trained on non-consecutive days (Mon / Wed / Fri or Tue / Thu / Sat)."
        elif days_count == 4:
            split_type = 'upper_lower_4day'
            title = "Four-Day Upper / Lower Periodized Split"
            progression = "Periodized Double Progression: Compound lifts progress linearly, accessories progress via rep accumulation."
            recovery = "Upper Mon/Thu, Lower Tue/Fri; weekends dedicated to active recovery, foam rolling, and mobility."
        elif days_count == 5:
            split_type = 'hybrid_5day'
            title = "Five-Day Upper / Lower / Push / Pull / Legs Split"
            progression = "Wave Progression: Increase volume on week 1-3, followed by a planned deload on week 4."
            recovery = "Crucial to monitor sleep and nutrition; hydrate with 3+ liters daily to avoid systemic fatigue."
        else: # 6 days
            split_type = 'ppl_6day'
            title = "Six-Day Push / Pull / Legs Hypertrophy Split"
            progression = "Volume Accumulation: Rotate heavy compound focus on Cycle 1 with moderate hypertrophy focus on Cycle 2."
            recovery = "High frequency requires strict adherence to sleep targets (>=8h) and protein replenishment."

        # Configure Plan Object
        plan = WorkoutPlan(
            user_id=user_id,
            title=title,
            split_type=split_type,
            duration_weeks=8,
            goal=profile.primary_goal,
            description=f"Personalized for {experience.title()} lifter with {equipment_setting.replace('_', ' ').title()} access. Aimed at {goal.replace('_', ' ').title()}.",
            progression_model=progression,
            recovery_guidelines=recovery,
            is_active=True
        )

        # 2. Build Days & Exercises
        days = cls._build_days(
            split_type=split_type,
            days_count=days_count,
            experience=experience,
            goal=goal,
            is_bodyweight_only=is_bodyweight_only,
            is_dumbbells_only=is_dumbbells_only,
            pain_movements=pain_movements,
            priority_muscles=priority_muscles,
            session_duration=session_duration,
            is_return_to_training=is_return_to_training
        )

        plan.days = days
        return plan

    @classmethod
    def _build_days(cls, split_type, days_count, experience, goal, is_bodyweight_only, is_dumbbells_only, pain_movements, priority_muscles, session_duration, is_return_to_training):
        days = []

        # Target reps and RPE based on goals
        if is_return_to_training:
            sets_compound = 2
            sets_accessory = 2
            rep_compound = "10-12"
            rep_accessory = "12-15"
            rpe_compound = "6 (4 RIR)"
            rest_sec = 90
        elif 'strength' in goal:
            sets_compound = 4
            sets_accessory = 3
            rep_compound = "5-6"
            rep_accessory = "8-10"
            rpe_compound = "8-8.5 (1-2 RIR)"
            rest_sec = 120
        elif 'hypertrophy' in goal or 'muscle_gain' in goal or 'body_recomp' in goal:
            sets_compound = 3
            sets_accessory = 3
            rep_compound = "8-10"
            rep_accessory = "10-12"
            rpe_compound = "7-8 (2 RIR)"
            rest_sec = 90
        else: # general fitness, fat loss, endurance
            sets_compound = 3
            sets_accessory = 3
            rep_compound = "10-12"
            rep_accessory = "12-15"
            rpe_compound = "7 (2-3 RIR)"
            rest_sec = 60

        # Helper to generate exercise with substitutions and pain checks
        def make_ex(name, muscle, equip, sets, reps, rpe, rest, cue, subs, order):
            # Pain movement substitutions
            has_knee_pain = any('knee' in p or 'squat' in p for p in pain_movements)
            has_back_pain = any('back' in p or 'deadlift' in p for p in pain_movements)
            has_shoulder_pain = any('shoulder' in p or 'overhead' in p for p in pain_movements)

            if has_knee_pain and ('squat' in name.lower() or 'lunge' in name.lower()):
                name = "Box Goblet Squat (Knee-Friendly)"
                equip = "Dumbbell" if not is_bodyweight_only else "Bodyweight"
                cue = "Sit hips back onto box or chair; keep shins vertical to eliminate anterior knee shear."
                subs = ["Glute Bridges", "Romanian Deadlift", "Hamstring Curl"]

            if has_back_pain and ('deadlift' in name.lower() or 'bent-over' in name.lower()):
                name = "Chest-Supported Dumbbell Row" if 'row' in name.lower() else "Dumbbell Hip Thrust"
                equip = "Dumbbell" if not is_bodyweight_only else "Bodyweight"
                cue = "Keep torso firmly supported to remove compressive shear from lower lumbar spine."
                subs = ["Cable Lat Pulldown", "Seated Cable Row", "Glute Bridge"]

            if has_shoulder_pain and ('overhead' in name.lower() or 'military' in name.lower() or 'bench press' in name.lower()):
                name = "Neutral-Grip Dumbbell Floor Press" if 'press' in name.lower() else "Cable Face Pull"
                equip = "Dumbbell" if not is_bodyweight_only else "Bodyweight"
                cue = "Keep palms facing inward (neutral grip); floor stops over-extension of glenohumeral joint."
                subs = ["Push-Up from Knees", "Resistance Band Press", "Light Incline DB Press"]

            # Equipment adaptations
            if is_bodyweight_only:
                equip = "Bodyweight"
                name_low = name.lower()
                if 'squat' in name_low or 'lunge' in name_low:
                    name = "Bodyweight Tempo Squat" if 'squat' in name_low else "Walking Bodyweight Lunges"
                    cue = "Descend smoothly for 3 seconds, pause at bottom, drive through mid-foot."
                elif 'press' in name_low or 'bench' in name_low or 'pushdown' in name_low:
                    if 'overhead' in name_low or 'shoulder' in name_low:
                        name = "Pike Push-Up"
                        cue = "Hips high in air, press floor away engaging front delts."
                    elif 'tricep' in name_low or 'pushdown' in name_low or 'extension' in name_low:
                        name = "Diamond Push-Up (or Chair Dips)"
                        cue = "Keep elbows tucked to prioritize triceps lockout."
                    else:
                        name = "Standard Push-Up (or Incline Push-Up)"
                        cue = "Lock core, elbows 45 degrees from torso, full chest touch."
                elif 'row' in name_low or 'pull' in name_low:
                    if 'face pull' in name_low or 'rear delt' in name_low:
                        name = "Prone Y-T-W Arm Retractions"
                        cue = "Lie on stomach, squeeze shoulder blades together in W shape."
                    else:
                        name = "Doorframe / Inverted Table Row"
                        cue = "Pinch shoulder blades together at peak contraction."
                elif 'deadlift' in name_low or 'hinge' in name_low:
                    name = "Single-Leg Glute Bridge & Hinge"
                    cue = "Drive through heel, squeeze glutes at the top."
                elif 'bicep' in name_low or 'curl' in name_low:
                    if 'leg curl' in name_low or 'hamstring' in name_low:
                        name = "Nordic Floor Hamstring Slider / Glute Bridge"
                        cue = "Slow eccentric control engaging hamstrings."
                    else:
                        name = "Doorframe Isometric Bicep Pull"
                        cue = "Supinated grip, pull elbows in towards ribs."
                elif 'raise' in name_low or 'delt' in name_low:
                    name = "Prone Lateral Floor Raise (Scaption)"
                    cue = "Thumbs pointed up, lift arms in 30-degree forward plane."
                elif 'calf' in name_low:
                    name = "Single-Leg Bodyweight Calf Raise"
                    cue = "Pause on toes for 2 seconds, full stretch at bottom."
                elif 'core' in name_low or 'abs' in name_low or 'plank' in name_low:
                    name = "Forearm Plank & Hollow Body Hold"
                    cue = "Brace abs tightly, prevent lower back sagging."

            elif is_dumbbells_only:
                if 'barbell' in name.lower():
                    name = name.replace("Barbell", "Dumbbell")
                    equip = "Dumbbell"
                elif 'cable' in name.lower():
                    name = name.replace("Cable", "Dumbbell")
                    equip = "Dumbbell"

            return WorkoutExercise(
                exercise_name=name,
                target_muscle=muscle,
                equipment=equip,
                sets=sets,
                reps=reps,
                rpe_target=rpe,
                rest_seconds=rest,
                technique_cue=cue,
                substitutions=subs,
                order_index=order
            )

        # Plan Templates
        if split_type in ['full_body_2day', 'full_body_3day', 'calisthenics_minimal', 'conservative_return']:
            # Full Body Days
            day_a = WorkoutDay(
                day_number=1,
                day_name="Day 1: Full Body Foundation A",
                focus="Quads, Chest, Upper Back & Core",
                warm_up="5 min dynamic warmup: Arm circles, Cat-Cow, Leg swings, Bodyweight squats.",
                cool_down="5 min cool-down: Standing quad stretch, Doorway chest stretch, Child's pose.",
                estimated_duration_min=session_duration,
                is_rest_day=False
            )
            day_a.exercises = [
                make_ex("Barbell Back Squat", "Quads & Glutes", "Barbell", sets_compound, rep_compound, rpe_compound, rest_sec, "Brace core, sit down between hips, drive through mid-foot.", ["Goblet Squat", "Leg Press", "Dumbbell Lunges"], 1),
                make_ex("Barbell Flat Bench Press", "Chest & Triceps", "Barbell", sets_compound, rep_compound, rpe_compound, rest_sec, "Plant feet firmly, retract scapulae, lower bar to mid-sternum.", ["Dumbbell Bench Press", "Push-Ups", "Dumbbell Floor Press"], 2),
                make_ex("Chest-Supported Dumbbell Row", "Upper Back & Lats", "Dumbbell", sets_accessory, rep_accessory, "7-8", rest_sec, "Lead with elbows, squeeze shoulder blades together at peak.", ["Barbell Bent Row", "Cable Seated Row", "Inverted Row"], 3),
                make_ex("Dumbbell Romanian Deadlift", "Hamstrings & Glutes", "Dumbbell", sets_accessory, rep_accessory, "7-8", rest_sec, "Hinge at hips, keep soft bend in knees, feel hamstring stretch.", ["Barbell RDL", "Single-Leg DB RDL", "Glute Bridge"], 4),
                make_ex("Standing Dumbbell Lateral Raise", "Lateral Deltoids", "Dumbbell", 3, "12-15", "8", 60, "Lead with elbows, slight forward lean, control the eccentric.", ["Cable Lateral Raise", "Resistance Band Lateral Raise"], 5),
                make_ex("Forearm Plank", "Core / Abs", "Bodyweight", 3, "30-45 sec", "7-8", 60, "Keep glutes squeezed and ribcage pulled toward pelvis.", ["Deadbug", "Hanging Knee Raise"], 6)
            ]
            days.append(day_a)

            day_b = WorkoutDay(
                day_number=2,
                day_name="Day 2: Full Body Foundation B",
                focus="Hamstrings, Back, Shoulders & Arms",
                warm_up="5 min dynamic warmup: Hip hinges, World's greatest stretch, Torso twists.",
                cool_down="5 min cool-down: Hamstring stretch, Cross-body shoulder stretch, Deep breathing.",
                estimated_duration_min=session_duration,
                is_rest_day=False
            )
            day_b.exercises = [
                make_ex("Barbell Conventional Deadlift", "Posterior Chain", "Barbell", sets_compound, rep_compound, rpe_compound, rest_sec + 30, "Bar against shins, lock lats, push floor away through heels.", ["Trap Bar Deadlift", "Dumbbell RDL", "Back Extension"], 1),
                make_ex("Overhead Dumbbell Press", "Shoulders & Triceps", "Dumbbell", sets_compound, rep_compound, rpe_compound, rest_sec, "Press vertically without arching lower back, lock out overhead.", ["Barbell Overhead Press", "Neutral DB Press", "Pike Push-Up"], 2),
                make_ex("Lat Pulldown (or Pull-Up)", "Lats & Biceps", "Cable", sets_accessory, rep_accessory, "7-8", rest_sec, "Pull bar towards collarbone, drive elbows down into your pockets.", ["Assisted Pull-Up", "Resistance Band Pulldown", "DB Pullover"], 3),
                make_ex("Bulgarian Split Squat", "Quads & Glutes", "Dumbbell", sets_accessory, "10 each leg", "7-8", rest_sec, "Back foot elevated on bench, drop back knee straight down.", ["Reverse Lunge", "Goblet Squat", "Step-Ups"], 4),
                make_ex("Incline Dumbbell Bicep Curl", "Biceps", "Dumbbell", 3, "10-12", "8", 60, "Keep elbows pinned back, rotate palms up at top.", ["Standing Barbell Curl", "Hammer Curl"], 5),
                make_ex("Triceps Cable Rope Pushdown", "Triceps", "Cable", 3, "10-12", "8", 60, "Flai rope out at bottom, lock elbows by sides.", ["Overhead DB Extension", "Diamond Push-Ups"], 6)
            ]
            days.append(day_b)

            if days_count >= 3:
                day_c = WorkoutDay(
                    day_number=3,
                    day_name="Day 3: Full Body Hypertrophy & Stability C",
                    focus="Full Body Balanced Symmetry",
                    warm_up="5 min dynamic warmup: Arm circles, Hip openers, Glute bridges.",
                    cool_down="5 min cool-down: Seated groin stretch, Cobra pose, Shoulder retractions.",
                    estimated_duration_min=session_duration,
                    is_rest_day=False
                )
                day_c.exercises = [
                    make_ex("Dumbbell Goblet Squat", "Quads & Core", "Dumbbell", sets_compound, rep_compound, rpe_compound, rest_sec, "Hold dumbbell tight to chest, elbows inside knees at bottom.", ["Leg Press", "Front Squat", "Wall Sit"], 1),
                    make_ex("Incline Dumbbell Bench Press", "Upper Chest", "Dumbbell", sets_compound, rep_compound, rpe_compound, rest_sec, "30-degree incline, smooth lower, explosive press to center.", ["Flat DB Press", "Incline Push-Ups"], 2),
                    make_ex("Seated Cable Row", "Mid Back & Rhomboids", "Cable", sets_accessory, rep_accessory, "7-8", rest_sec, "Sit tall, pull handles to belly button, stretch forward under control.", ["One-Arm DB Row", "Chest-Supported Row"], 3),
                    make_ex("Lying Hamstring Leg Curl", "Hamstrings", "Machine", sets_accessory, rep_accessory, "8", rest_sec, "Keep hips pressed into pad, curl heels to glutes.", ["Swiss Ball Leg Curl", "Nordic Curl", "DB RDL"], 4),
                    make_ex("Cable Face Pull", "Rear Delts & Rotator Cuff", "Cable", 3, "15-20", "8", 60, "Pull rope towards bridge of nose, rotate hands back.", ["Band Pull-Apart", "Dumbbell Reverse Fly"], 5),
                    make_ex("Hanging Knee Raise (or Captain's Chair)", "Lower Abs & Hip Flexors", "Bodyweight", 3, "12-15", "8", 60, "Roll pelvis up towards ribs, avoid swinging momentum.", ["Reverse Crunch", "Plank"], 6)
                ]
                days.append(day_c)

        elif split_type == 'upper_lower_4day':
            # 4-Day Upper / Lower
            d1 = WorkoutDay(day_number=1, day_name="Day 1: Upper Power A", focus="Chest, Back & Shoulders", warm_up="Dynamic warmup: Arm swings, band dislocates, push-up prep.", cool_down="Chest & Lat static stretches.", estimated_duration_min=session_duration)
            d1.exercises = [
                make_ex("Barbell Bench Press", "Chest", "Barbell", sets_compound, rep_compound, rpe_compound, rest_sec, "Drive through floor, bar path arched back over shoulders.", ["Dumbbell Bench Press", "Push-Ups"], 1),
                make_ex("Barbell Bent-Over Row", "Back", "Barbell", sets_compound, rep_compound, rpe_compound, rest_sec, "Torso at 45 degrees, pull bar to waist.", ["Dumbbell Row", "Cable Row"], 2),
                make_ex("Overhead Dumbbell Press", "Shoulders", "Dumbbell", sets_accessory, rep_accessory, "7-8", rest_sec, "Press overhead with active core.", ["Barbell OHP", "Arnold Press"], 3),
                make_ex("Lat Pulldown", "Lats", "Cable", sets_accessory, rep_accessory, "7-8", rest_sec, "Pull to chest, control negative.", ["Pull-Up", "Band Pulldown"], 4),
                make_ex("Incline Dumbbell Curl", "Biceps", "Dumbbell", 3, "10-12", "8", 60, "Full stretch at bottom.", ["Hammer Curl"], 5),
                make_ex("Triceps Cable Pushdown", "Triceps", "Cable", 3, "10-12", "8", 60, "Elbows tucked.", ["Overhead DB Extension"], 6)
            ]
            days.append(d1)

            d2 = WorkoutDay(day_number=2, day_name="Day 2: Lower Power A", focus="Quads, Hamstrings & Calves", warm_up="Dynamic warmup: Hip circles, leg swings, goblet mobility squats.", cool_down="Quad & Hamstring stretches.", estimated_duration_min=session_duration)
            d2.exercises = [
                make_ex("Barbell Back Squat", "Quads", "Barbell", sets_compound, rep_compound, rpe_compound, rest_sec, "Break at hips and knees simultaneously.", ["Goblet Squat", "Leg Press"], 1),
                make_ex("Romanian Deadlift", "Hamstrings", "Barbell", sets_compound, rep_compound, rpe_compound, rest_sec, "Push hips back, keep bar glued to legs.", ["Dumbbell RDL"], 2),
                make_ex("Bulgarian Split Squat", "Quads & Glutes", "Dumbbell", sets_accessory, "10 each leg", "7-8", rest_sec, "Upright torso for quad emphasis.", ["Walking Lunges"], 3),
                make_ex("Seated Leg Curl", "Hamstrings", "Machine", sets_accessory, rep_accessory, "8", 60, "Control the full range.", ["Lying Leg Curl"], 4),
                make_ex("Standing Calf Raise", "Calves", "Machine", 3, "12-15", "8", 60, "Pause at bottom stretch for 2 seconds.", ["Dumbbell Calf Raise"], 5),
                make_ex("Hanging Knee Raise", "Abs", "Bodyweight", 3, "12-15", "8", 60, "Curl hips up.", ["Cable Crunch"], 6)
            ]
            days.append(d2)

            d3 = WorkoutDay(day_number=3, day_name="Day 3: Upper Hypertrophy B", focus="Shoulders, Chest & Upper Back", warm_up="Dynamic warmup: Arm swings, face pulls.", cool_down="Shoulder & Chest stretches.", estimated_duration_min=session_duration)
            d3.exercises = [
                make_ex("Incline Dumbbell Bench Press", "Upper Chest", "Dumbbell", sets_compound, rep_compound, rpe_compound, rest_sec, "Elbows at 45 degrees, stretch at bottom.", ["Incline Barbell Press"], 1),
                make_ex("One-Arm Dumbbell Row", "Lats & Back", "Dumbbell", sets_compound, rep_compound, rpe_compound, rest_sec, "Pull towards hip crease.", ["Seated Cable Row"], 2),
                make_ex("Dumbbell Lateral Raise", "Side Delts", "Dumbbell", 4, "12-15", "8-9", 60, "Strict form, no swinging.", ["Cable Lateral Raise"], 3),
                make_ex("Cable Chest Flye", "Chest", "Cable", sets_accessory, rep_accessory, "8", 60, "Squeeze handles together.", ["Dumbbell Flye", "Push-Ups"], 4),
                make_ex("Dumbbell Hammer Curl", "Brachialis & Forearms", "Dumbbell", 3, "10-12", "8", 60, "Neutral grip throughout.", ["Cable Rope Curl"], 5),
                make_ex("Overhead Dumbbell Triceps Extension", "Long Head Triceps", "Dumbbell", 3, "10-12", "8", 60, "Deep tricep stretch behind head.", ["Skull Crushers"], 6)
            ]
            days.append(d3)

            d4 = WorkoutDay(day_number=4, day_name="Day 4: Lower Hypertrophy B", focus="Hamstrings, Glutes & Quads", warm_up="Dynamic warmup: Hip hinges, bodyweight squats.", cool_down="Hamstrings, Glutes & Lower back relief.", estimated_duration_min=session_duration)
            d4.exercises = [
                make_ex("Barbell Hip Thrust (or Trap Bar DL)", "Glutes & Hamstrings", "Barbell", sets_compound, rep_compound, rpe_compound, rest_sec, "Drive through heels, posterior pelvic tilt at top.", ["Dumbbell Hip Thrust"], 1),
                make_ex("Leg Press", "Quads", "Machine", sets_compound, rep_compound, rpe_compound, rest_sec, "Feet shoulder width, full depth without lifting lower back.", ["Goblet Squat"], 2),
                make_ex("Dumbbell Walking Lunges", "Quads & Glutes", "Dumbbell", sets_accessory, "12 steps/leg", "8", rest_sec, "Long stride for glutes, shorter for quads.", ["Reverse Lunges"], 3),
                make_ex("Lying Hamstring Leg Curl", "Hamstrings", "Machine", sets_accessory, rep_accessory, "8", 60, "Squeeze hamstrings at top.", ["Single Leg Curl"], 4),
                make_ex("Cable Woodchopper", "Obliques & Core", "Cable", 3, "12 each side", "8", 60, "Rotate through thoracic spine.", ["Russian Twists"], 5),
                make_ex("Seated Calf Raise", "Soleus", "Machine", 3, "15-20", "8", 60, "Slow 3-second descent.", ["Single-Leg Calf Raise"], 6)
            ]
            days.append(d4)

        else:
            # 5 or 6 day PPL
            # Push, Pull, Legs Days
            day_names = ["Push A", "Pull A", "Legs A", "Push B", "Pull B", "Legs B"][:days_count]
            for idx, d_name in enumerate(day_names, 1):
                if 'Push' in d_name:
                    d = WorkoutDay(day_number=idx, day_name=f"Day {idx}: {d_name}", focus="Chest, Shoulders & Triceps", warm_up="Arm swings, band face pulls.", cool_down="Chest stretch, tricep stretch.", estimated_duration_min=session_duration)
                    d.exercises = [
                        make_ex("Barbell Bench Press", "Chest", "Barbell", sets_compound, rep_compound, rpe_compound, rest_sec, "Full arch and leg drive.", ["Dumbbell Bench Press"], 1),
                        make_ex("Overhead Dumbbell Press", "Shoulders", "Dumbbell", sets_accessory, rep_accessory, "7-8", rest_sec, "Press high without lower back arch.", ["Barbell OHP"], 2),
                        make_ex("Dumbbell Incline Press", "Upper Chest", "Dumbbell", sets_accessory, rep_accessory, "7-8", rest_sec, "30-degree incline.", ["Dips"], 3),
                        make_ex("Dumbbell Lateral Raise", "Side Delts", "Dumbbell", 3, "12-15", "8", 60, "Lead with elbows.", ["Cable Lateral"], 4),
                        make_ex("Triceps Cable Pushdown", "Triceps", "Cable", 3, "10-12", "8", 60, "Full lock.", ["Overhead DB Extension"], 5)
                    ]
                elif 'Pull' in d_name:
                    d = WorkoutDay(day_number=idx, day_name=f"Day {idx}: {d_name}", focus="Back, Rear Delts & Biceps", warm_up="Band pull-aparts, thoracic rotations.", cool_down="Lat stretch, bicep stretch.", estimated_duration_min=session_duration)
                    d.exercises = [
                        make_ex("Barbell Bent-Over Row", "Back", "Barbell", sets_compound, rep_compound, rpe_compound, rest_sec, "Keep chest tall, pull to navel.", ["One-Arm DB Row"], 1),
                        make_ex("Lat Pulldown", "Lats", "Cable", sets_compound, rep_compound, rpe_compound, rest_sec, "Drive elbows down.", ["Pull-Ups"], 2),
                        make_ex("Cable Face Pull", "Rear Delts", "Cable", 3, "15-20", "8", 60, "Pull to eyes, external rotation.", ["Rear Delt Flye"], 3),
                        make_ex("Incline Dumbbell Bicep Curl", "Biceps", "Dumbbell", 3, "10-12", "8", 60, "Stretch at bottom.", ["Barbell Curl"], 4),
                        make_ex("Dumbbell Hammer Curl", "Forearms", "Dumbbell", 3, "10-12", "8", 60, "Strict neutral grip.", ["Cable Curl"], 5)
                    ]
                else:
                    d = WorkoutDay(day_number=idx, day_name=f"Day {idx}: {d_name}", focus="Quads, Hamstrings & Calves", warm_up="Goblet squat hold, leg swings.", cool_down="Quad and hamstring static stretches.", estimated_duration_min=session_duration)
                    d.exercises = [
                        make_ex("Barbell Back Squat", "Quads", "Barbell", sets_compound, rep_compound, rpe_compound, rest_sec, "Solid foot stability, hip depth.", ["Goblet Squat"], 1),
                        make_ex("Romanian Deadlift", "Hamstrings", "Barbell", sets_compound, rep_compound, rpe_compound, rest_sec, "Hinge back, feel stretch.", ["Dumbbell RDL"], 2),
                        make_ex("Leg Press", "Quads", "Machine", sets_accessory, rep_accessory, "8", rest_sec, "Controlled cadence.", ["Split Squat"], 3),
                        make_ex("Lying Hamstring Leg Curl", "Hamstrings", "Machine", sets_accessory, rep_accessory, "8", 60, "Full contraction.", ["Nordic Curl"], 4),
                        make_ex("Standing Calf Raise", "Calves", "Machine", 3, "12-15", "8", 60, "Pause at stretch.", ["Seated Calf Raise"], 5)
                    ]
                days.append(d)

        # Priority Muscle Group Adjustment: add an extra targeted exercise to Day 1 or Day 2
        if priority_muscles:
            target_p = priority_muscles[0]
            if target_p == 'arms' and days:
                days[0].exercises.append(
                    make_ex("Cable Rope Hammer Curl (Priority Accessory)", "Biceps & Forearms", "Cable" if not is_dumbbells_only else "Dumbbell", 3, "12", "8", 60, "Controlled tempo targeting priority arm development.", ["Dumbbell Curl"], len(days[0].exercises) + 1)
                )
            elif target_p in ['glutes', 'legs'] and days:
                days[0].exercises.append(
                    make_ex("Dumbbell Glute Hip Thrust (Priority Accessory)", "Glutes", "Dumbbell" if not is_bodyweight_only else "Bodyweight", 3, "12", "8", 60, "Squeeze glutes at top for 2 seconds.", ["Bodyweight Hip Thrust"], len(days[0].exercises) + 1)
                )
            elif target_p == 'chest' and len(days) > 1:
                days[1].exercises.append(
                    make_ex("Dumbbell Incline Hex Press (Priority Accessory)", "Inner & Upper Chest", "Dumbbell", 3, "12", "8", 60, "Press dumbbells together firmly throughout rep.", ["Push-Ups"], len(days[1].exercises) + 1)
                )

        return days
