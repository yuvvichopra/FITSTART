RESEARCH_SOURCES = [
    {
        "id": "acsm-guidelines",
        "name": "American College of Sports Medicine (ACSM)",
        "organization": "ACSM Guidelines for Exercise Testing and Prescription (11th Edition)",
        "url": "https://www.acsm.org/",
        "publication_year": "2021",
        "summary": "ACSM publishes consensus guidelines defining the frequency, intensity, time, and type (FITT principle) of cardiorespiratory and resistance exercise for apparently healthy adults.",
        "relevant_recommendations": [
            "Healthy adults should perform resistance training at least 2-3 days per week covering major muscle groups.",
            "2-4 sets of 8-12 repetitions per exercise at moderate-to-vigorous intensity (60-80% 1RM) optimize strength and hypertrophy in novice and intermediate lifters.",
            "Allow at least 48 hours of recovery between training the same muscle group.",
            "Incorporate 150-300 minutes of moderate-intensity or 75-150 minutes of vigorous-intensity aerobic physical activity per week."
        ],
        "limitations": "Generalized guidelines designed for healthy adult populations. Individuals with chronic cardiovascular, metabolic, or musculoskeletal conditions require individualized medical clearance.",
        "licensing_and_attribution": "Referenced for educational and methodological compliance under fair academic use. ACSM is a registered trademark of the American College of Sports Medicine."
    },
    {
        "id": "nsca-strength-conditioning",
        "name": "National Strength and Conditioning Association (NSCA)",
        "organization": "NSCA Essentials of Strength Training and Conditioning (4th Edition) & Position Statements",
        "url": "https://www.nsca.com/",
        "publication_year": "2016-2023",
        "summary": "The NSCA establishes scientific standards for periodization, progressive overload, resistance exercise technique, and recovery management for athletic and recreational lifters.",
        "relevant_recommendations": [
            "Progressive overload should be applied systematically via the 2-for-2 rule: if an athlete can perform 2 or more reps over the target rep goal in the final set for 2 consecutive workouts, increase load (2.5-5% for upper body, 5-10% for lower body).",
            "Periodization models (linear and undulating) improve strength and prevent overtraining and overuse injuries.",
            "Warm-up protocols should follow the RAMP framework: Raise body temperature, Activate musculature, Mobilize joints, Potentiate movement patterns."
        ],
        "limitations": "Load progression speeds must be dialed back if sleep, hydration, or psychological stressors impair systemic recovery.",
        "licensing_and_attribution": "Referenced for training architecture under scholarly fair use. NSCA is a registered trademark of the National Strength and Conditioning Association."
    },
    {
        "id": "icmr-nin-dietary-guidelines",
        "name": "ICMR - National Institute of Nutrition (NIN)",
        "organization": "Dietary Guidelines for Indians (ICMR-NIN, 2024)",
        "url": "https://www.nin.res.in/",
        "publication_year": "2024",
        "summary": "The Indian Council of Medical Research (ICMR) and National Institute of Nutrition (NIN) establish Recommended Dietary Allowances (RDA) and dietary guidelines tailored to Indian physiological requirements, regional staple diets, and metabolic profiles.",
        "relevant_recommendations": [
            "A balanced Indian plate should source macronutrients from diverse food groups: whole grains, pulses, dairy, vegetables, nuts, and healthy fats.",
            "Vegetarian and vegan diets require conscious pairing of cereals and pulses (such as dal-rice or roti-dal in a 3:1 to 4:1 ratio) to ensure a complete essential amino acid profile (lysine and methionine complementarity).",
            "Target daily dietary fiber of 30g per 2000 kcal through vegetables, legumes, and whole grains.",
            "Limit intake of ultra-processed foods, refined sugars (< 5% of daily calories), and trans fatty acids."
        ],
        "limitations": "RDAs are formulated to prevent deficiencies across general Indian sedentary and moderate-work populations; active strength trainees require higher protein densities (1.6-2.0 g/kg).",
        "licensing_and_attribution": "Public health guideline data published by Government of India / ICMR-NIN. Cited for public health education."
    },
    {
        "id": "who-physical-activity",
        "name": "World Health Organization (WHO)",
        "organization": "WHO Guidelines on Physical Activity and Sedentary Behaviour",
        "url": "https://www.who.int/publications/i/item/9789240015128",
        "publication_year": "2020",
        "summary": "Global public health recommendations detailing evidence-based physical activity thresholds to reduce all-cause mortality, cardiovascular disease, and metabolic disorders.",
        "relevant_recommendations": [
            "All adults should undertake 150–300 minutes of moderate-intensity, or 75–150 minutes of vigorous-intensity aerobic physical activity per week.",
            "Muscle-strengthening activities involving all major muscle groups should be performed on 2 or more days a week.",
            "Replacing sedentary time with physical activity of any intensity (including low-intensity walking) provides health benefits."
        ],
        "limitations": "Broad public health recommendations that do not dictate sport-specific training splits or hypertrophy periodization.",
        "licensing_and_attribution": "World Health Organization open access publication under Creative Commons Attribution-NonCommercial-ShareAlike 3.0 IGO (CC BY-NC-SA 3.0 IGO)."
    },
    {
        "id": "pubmed-protein-hypertrophy",
        "name": "Systematic Reviews on Protein & Hypertrophy (PubMed)",
        "organization": "Morton et al., British Journal of Sports Medicine (BJSM) & Schoenfeld et al.",
        "url": "https://pubmed.ncbi.nlm.nih.gov/28698222/",
        "publication_year": "2018",
        "summary": "Meta-analysis of 49 studies with 1,863 participants evaluating the effect of dietary protein supplementation on resistance training adaptations.",
        "relevant_recommendations": [
            "Protein intakes at or above 1.6 g/kg/day maximize gains in fat-free mass during resistance training; intakes up to 2.2 g/kg/day may be beneficial during hypocaloric fat-loss phases to preserve lean muscle.",
            "Distributing protein across 3-4 meals (0.4-0.5 g/kg per meal) provides optimal muscle protein synthesis (MPS) stimulation.",
            "Total daily protein intake is the primary driver of body composition outcomes, outweighing immediate pre/post-workout nutrient timing."
        ],
        "limitations": "Higher protein intakes beyond 1.62 g/kg/day showed diminishing returns in normocaloric resistance training for non-enhanced lifters.",
        "licensing_and_attribution": "Published in British Journal of Sports Medicine (BMJ Publishing Group). Scientific findings synthesized under standard citation guidelines."
    },
    {
        "id": "wger-open-fitness",
        "name": "wger - Open-Source Workout & Exercise Manager",
        "organization": "wger Community / AGPLv3",
        "url": "https://wger.de/",
        "publication_year": "2024",
        "summary": "An open-source, community-driven platform providing structured anatomical classifications for exercises, muscles, and movement patterns.",
        "relevant_recommendations": [
            "Hierarchical exercise taxonomy based on target muscle, primary movement, and equipment requirements facilitates seamless exercise substitution.",
            "Compound multi-joint movements should be placed first in training sessions when neural drive and stability are highest."
        ],
        "limitations": "Community-contributed descriptions vary in anatomical depth; verified cues have been standardized within FitStart.",
        "licensing_and_attribution": "wger is licensed under AGPLv3. FitStart references architectural taxonomy principles under permissive open-source guidelines."
    }
]

def get_all_sources():
    return RESEARCH_SOURCES

def get_source_by_id(source_id):
    for s in RESEARCH_SOURCES:
        if s["id"] == source_id:
            return s
    return None
