
import csv
import chardet
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def run_branch_and_bound_algorithm(csv_file):
    logger.info(f"Starting to process file: {csv_file}")
    try:
        professors, courses, timeslots = parse_csv(csv_file)
        logger.info(f"Parsed CSV. Professors: {len(professors)}, Courses: {len(courses)}, Timeslots: {len(timeslots)}")
        
        if not professors or not courses or not timeslots:
            raise ValueError("Parsing CSV resulted in empty data")
        
        schedule = create_schedule(professors, courses, timeslots)
        steps = [f"Created schedule with {len(schedule)} assignments"]
        
        logger.info(f"Finished creating schedule. Schedule length: {len(schedule)}")
        return schedule, steps
    except Exception as e:
        logger.error(f"Error in run_branch_and_bound_algorithm: {str(e)}")
        raise

def parse_csv(csv_file):
    professors = {}
    courses = {
        "Design and Analysis of Algorithms": 3,
        "Information Management": 2,
        "Operating Systems": 3,
        "Data Communications and Networking": 2,
        "Technical Documentations": 2
    }
    timeslots = {
        3: ["9:00 am - 12:00 pm", "12:00 pm - 3:00 pm", "3:00 pm - 6:00 pm", "6:00 pm - 9:00 pm", "7:00 am - 10:00 am"],
        2: ["9:00 am - 11:00 am", "11:00 am - 1:00 pm", "1:00 pm - 3:00 pm", "3:00 pm - 5:00 pm", "5:00 pm - 7:00 pm"]
    }

    try:
        with open(csv_file, 'rb') as rawdata:
            result = chardet.detect(rawdata.read(10000))
        
        logger.info(f"Detected encoding: {result['encoding']}")
        
        with open(csv_file, mode='r', newline='', encoding=result['encoding']) as file:
            sample = file.read(1024)
            file.seek(0)
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)
            logger.info(f"Detected delimiter: {dialect.delimiter}")
            
            csv_reader = csv.DictReader(file, dialect=dialect)
            
            logger.info(f"CSV columns: {csv_reader.fieldnames}")
            
            for row in csv_reader:
                if "Professor's Name" not in row:
                    raise KeyError("Column 'Professor's Name' not found in CSV file")
                
                professor_name = row["Professor's Name"]
                preferences = {}
                for course in courses:
                    key = f'Please rate your preference for teaching "{course}"  from 1 (least preferred) to 5 (most preferred).'
                    preferences[course] = int(row[key]) if key in row and row[key].strip() else 0

                available_timeslots = {}
                for duration, slots in timeslots.items():
                    available_timeslots[duration] = []
                    for slot in slots:
                        key = f'Please select timeslots based on your availability to teach this course. [{slot}]'
                        if key in row and row[key].strip():
                            available_timeslots[duration].append(slot)

                professors[professor_name] = {
                    'preferences': preferences,
                    'available_timeslots': available_timeslots
                }

        if not professors:
            raise ValueError("No professors were parsed from the CSV file")

        logger.info(f"Parsed {len(professors)} professors")
        for prof, data in professors.items():
            logger.info(f"Professor: {prof}")
            logger.info(f"Preferences: {data['preferences']}")
            logger.info(f"Available timeslots: {data['available_timeslots']}")

    except Exception as e:
        logger.error(f"Error in parsing CSV: {str(e)}")
        raise

    return professors, courses, timeslots

def create_schedule(professors, courses, timeslots):
    schedule = []
    professor_course_count = {prof: {course: 0 for course in courses} for prof in professors}
    professor_total_hours = {prof: 0 for prof in professors}

    for course, duration in courses.items():
        for _ in range(5):  
            assigned = False
            available_professors = sorted(
                [p for p in professors.keys() if professor_total_hours[p] + duration <= 5 and professor_course_count[p][course] < 3],
                key=lambda p: (-professors[p]['preferences'][course], p)
            )

            for prof in available_professors:
                available_slots = [
                    ts for ts in professors[prof]['available_timeslots'][duration] 
                    if ts not in [s['timeslot'] for s in schedule if s['professor'] == prof]
                ]
                if available_slots:
                    
                    timeslot = min(available_slots)
                    if timeslot in professors[prof]['available_timeslots'][duration]:
                        schedule.append({'professor': prof, 'course': course, 'timeslot': timeslot})
                        professor_course_count[prof][course] += 1
                        professor_total_hours[prof] += duration
                        assigned = True
                        break
                    else:
                        logger.warning(f"Professor {prof} is not available for timeslot {timeslot} in duration {duration}. Skipping.")
            
            if not assigned:
                logger.warning(f"No available professors for {course}. Skipping this assignment.")

    logger.info(f"Created schedule with {len(schedule)} assignments")
    return schedule


def branch_and_bound(professors, courses, timeslots):
    best_schedule = None
    best_score = float('-inf')
    steps = []

    def is_valid_schedule(schedule):
        prof_hours = {p: 0 for p in professors}
        course_count = {c: 0 for c in courses}
        for entry in schedule:
            duration = courses[entry['course']]
            prof_hours[entry['professor']] += duration
            course_count[entry['course']] += 1
            if prof_hours[entry['professor']] > 5:
                return False
            if course_count[entry['course']] > 5:
                return False
            if entry['timeslot'] not in professors[entry['professor']]['available_timeslots'][duration]:
                return False
        return True

    def calculate_score(schedule):
        score = 0
        for entry in schedule:
            prof = professors[entry['professor']]
            score += prof['preferences'][entry['course']]
        return score

    def prune(schedule):
        nonlocal best_schedule, best_score

        if len(schedule) == 25:  
            if is_valid_schedule(schedule):
                score = calculate_score(schedule)
                if score > best_score:
                    best_score = score
                    best_schedule = schedule.copy()
                    steps.append(f"New best schedule found with score {best_score}")
            return

        for prof in professors:
            for course, duration in courses.items():
                for timeslot in timeslots[duration]:
                    if timeslot in professors[prof]['available_timeslots'][duration] and timeslot not in [s['timeslot'] for s in schedule if s['professor'] == prof]:
                        new_entry = {'professor': prof, 'course': course, 'timeslot': timeslot}
                        schedule.append(new_entry)
                        prune(schedule)
                        schedule.pop()

    initial_schedule = []
    steps.append("Starting branch and bound algorithm")
    prune(initial_schedule)
    
    if best_schedule is None:
        logger.warning("No valid schedule found")
        return [], ["No valid schedule found"]
    
    steps.append(f"Optimal solution found with score {best_score}")

    return best_schedule, steps
