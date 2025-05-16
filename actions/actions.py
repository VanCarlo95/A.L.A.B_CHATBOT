from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction

class ActionSetActiveCollege(Action):
    def name(self) -> Text:
        return "action_set_active_college"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = tracker.latest_message.get('text', '').lower()
        
        # Enhanced college mappings with more context-aware keywords for all colleges
        college_keywords = {
            'ccs': [
                'ccs', 'computer', 'computing', 'it', 'information technology', 
                'programming', 'software', 'development', 'coding', 'cs', 
                'information systems', 'is', 'computer applications', 'ca',
                'college of computer studies'
            ],
            'coe': [
                'coe', 'engineering', 'engineer', 'mechanical', 'civil', 
                'electrical', 'chemical', 'industrial', 'college of engineering',
                'engineering college'
            ],
            'csm': [
                'csm', 'science', 'math', 'mathematics', 'biology', 'chemistry', 
                'physics', 'laboratory', 'college of science and mathematics',
                'science college'
            ],
            'ceba': [
                'ceba', 'business', 'accountancy', 'accounting', 'management', 
                'finance', 'economics', 'administration', 'college of economics and business administration',
                'economics college', 'business college'
            ],
            'cass': [
                'cass', 'arts', 'social sciences', 'sociology', 'psychology', 
                'political science', 'history', 'college of arts and social sciences',
                'arts college', 'social sciences college'
            ],
            'ced': [
                'ced', 'education', 'teaching', 'pedagogy', 'instructional', 
                'teacher', 'college of education', 'education college'
            ],
            'chs': [
                'chs', 'health', 'nursing', 'medical', 'healthcare', 
                'public health', 'college of health sciences', 'health college'
            ]
        }

        # Get current context
        current_college = tracker.get_slot('active_college')
        current_topic = tracker.get_slot('active_topic')
        conversation_stage = tracker.get_slot('conversation_stage')
        
        # Determine new college from message
        new_college = None
        for college, keywords in college_keywords.items():
            if any(keyword in message for keyword in keywords):
                new_college = college
                break

        events = []
        if new_college:
            # Handle college context switching
            if current_college and new_college != current_college:
                events.extend([
                    SlotSet("last_topic", current_college),
                    SlotSet("conversation_stage", "switching"),
                    SlotSet("active_topic", None)  # Clear previous topic
                ])
            events.extend([
                SlotSet("active_college", new_college),
                SlotSet("active_topic", f"{new_college}_general"),
                SlotSet("conversation_stage", "inquiring" if not conversation_stage else conversation_stage)
            ])
            
        return events

class ActionHandleFollowUp(Action):
    def name(self) -> Text:
        return "action_handle_follow_up"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        active_college = tracker.get_slot('active_college')
        active_topic = tracker.get_slot('active_topic')
        program = tracker.get_slot('program')
        
        # Enhanced follow-up mappings for all colleges
        follow_up_suggestions = {
            'ccs': {
                'programs_overview': [
                    "Program admission requirements",
                    "Program duration",
                    "Career opportunities"
                ],
                'facilities_info': [
                    "Laboratory equipment",
                    "Research facilities",
                    "Study areas",
                    "Usage policies"
                ],
                'program_specific': {
                    'bscs': ["Curriculum details", "Specialization tracks", "Research opportunities"],
                    'bsit': ["Industry certifications", "Technical skills", "Internship opportunities"],
                    'bsis': ["Business components", "Enterprise systems", "Industry partners"],
                    'bsca': ["Application development", "UI/UX design", "Project portfolio"]
                }
            },
            'coe': {
                'programs_overview': [
                    "Program admission requirements",
                    "Engineering specializations",
                    "Career prospects for engineers"
                ],
                'facilities_info': [
                    "Engineering laboratories",
                    "Workshop facilities",
                    "Research equipment"
                ],
                'program_specific': {
                    'mechanical': ["Thermodynamics", "Machine design", "Manufacturing"],
                    'civil': ["Structural engineering", "Environmental engineering", "Construction management"],
                    'electrical': ["Power systems", "Electronics", "Communications"],
                    'chemical': ["Process design", "Plant operations", "Materials science"],
                    'industrial': ["Operations research", "Management systems", "Production planning"]
                }
            },
            'chs': {
                'programs_overview': [
                    "Health sciences programs",
                    "Clinical requirements",
                    "Board exam preparation"
                ],
                'facilities_info': [
                    "Medical laboratories",
                    "Simulation facilities",
                    "Clinical practice areas"
                ],
                'program_specific': {
                    'nursing': ["Patient care", "Clinical rotations", "Healthcare administration"],
                    'pharmacy': ["Pharmaceutical sciences", "Clinical pharmacy", "Drug development"],
                    'public_health': ["Epidemiology", "Community health", "Health promotion"]
                }
            },
            'ceba': {
                'programs_overview': [
                    "Business programs",
                    "Economics specializations",
                    "Industry connections"
                ],
                'facilities_info': [
                    "Business resource center",
                    "Economics research facilities",
                    "Case study rooms"
                ],
                'program_specific': {
                    'business': ["Management", "Marketing", "Entrepreneurship"],
                    'economics': ["Macroeconomics", "Development economics", "Policy analysis"],
                    'accountancy': ["Financial accounting", "Audit", "Taxation"]
                }
            },
            'cass': {
                'programs_overview': [
                    "Arts programs",
                    "Social sciences offerings",
                    "Research focus"
                ],
                'facilities_info': [
                    "Arts studios",
                    "Social research laboratories",
                    "Performance spaces"
                ],
                'program_specific': {
                    'psychology': ["Clinical psychology", "Developmental psychology", "Research methods"],
                    'sociology': ["Social theory", "Research methods", "Community studies"],
                    'political_science': ["Governance", "International relations", "Policy studies"]
                }
            },
            'ced': {
                'programs_overview': [
                    "Education programs",
                    "Teaching specializations",
                    "Licensure preparation"
                ],
                'facilities_info': [
                    "Teaching laboratories",
                    "Demonstration classrooms",
                    "Educational technology"
                ],
                'program_specific': {
                    'elementary': ["Child development", "Teaching methods", "Curriculum development"],
                    'secondary': ["Subject specialization", "Adolescent education", "Assessment methods"],
                    'special_education': ["Inclusive education", "Intervention strategies", "Adaptive methods"]
                }
            },
            'csm': {
                'programs_overview': [
                    "Science programs",
                    "Mathematics specializations",
                    "Research opportunities"
                ],
                'facilities_info': [
                    "Science laboratories",
                    "Research facilities",
                    "Computing resources"
                ],
                'program_specific': {
                    'biology': ["Molecular biology", "Ecology", "Biotechnology"],
                    'chemistry': ["Organic chemistry", "Analytical chemistry", "Biochemistry"],
                    'mathematics': ["Pure mathematics", "Applied mathematics", "Statistics"],
                    'physics': ["Theoretical physics", "Applied physics", "Astronomy"]
                }
            }
        }
        
        # Service-specific follow-ups
        service_follow_ups = {
            'admission': [
                "Admission requirements",
                "Application process",
                "Document submission",
                "Transfer admission"
            ],
            'registrar': [
                "Transcript requests",
                "Document processing",
                "Academic records",
                "Enrollment procedures"
            ],
            'scholarship': [
                "Scholarship types",
                "Application requirements",
                "Deadlines",
                "Renewal process"
            ],
            'fablab': [
                "Available equipment",
                "Access procedures",
                "Project guidelines",
                "Costs and fees"
            ],
            'osds': [
                "Student assistance programs",
                "Counseling services",
                "Student organizations",
                "Housing information"
            ],
            'clinic': [
                "Medical services",
                "Dental services",
                "Health certificates",
                "Laboratory tests"
            ]
        }

        events = []
        response = None

        # Handle college-specific follow-ups
        if active_college in follow_up_suggestions:
            college_suggestions = follow_up_suggestions[active_college]
            
            # Handle program-specific follow-ups
            if program and 'program_specific' in college_suggestions:
                if program.lower() in college_suggestions['program_specific']:
                    suggestions = college_suggestions['program_specific'][program.lower()]
                    response = f"For {program.upper()}, would you like to know about:\n"
                    response += "\n".join(f"{i+1}. {suggestion}" for i, suggestion in enumerate(suggestions))
            
            # Handle topic-based follow-ups
            elif active_topic in college_suggestions:
                suggestions = college_suggestions[active_topic]
                response = "Would you like to know about:\n"
                response += "\n".join(f"{i+1}. {suggestion}" for i, suggestion in enumerate(suggestions))
        
        # Handle service-specific follow-ups
        elif active_topic in service_follow_ups:
            suggestions = service_follow_ups[active_topic]
            response = f"Regarding {active_topic}, would you like to know about:\n"
            response += "\n".join(f"{i+1}. {suggestion}" for i, suggestion in enumerate(suggestions))

        if response:
            dispatcher.utter_message(text=response)
            events.append(SlotSet("conversation_stage", "following_up"))
        
        return events

class ActionHandleProgramComparison(Action):
    def name(self) -> Text:
        return "action_handle_program_comparison"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = tracker.latest_message.get('text', '').lower()
        active_college = tracker.get_slot('active_college')
        
        # College-specific program mappings
        college_programs = {
            'ccs': ['bscs', 'bsit', 'bsis', 'bsca'],
            'coe': ['mechanical', 'civil', 'electrical', 'chemical', 'industrial'],
            'chs': ['nursing', 'pharmacy', 'medical technology', 'public health'],
            'ceba': ['business', 'economics', 'accountancy', 'finance', 'management'],
            'cass': ['psychology', 'sociology', 'political science', 'history', 'languages'],
            'ced': ['elementary', 'secondary', 'special education', 'physical education'],
            'csm': ['biology', 'chemistry', 'mathematics', 'physics', 'statistics']
        }
        
        events = []
        
        # Identify which programs to compare based on active college
        programs = college_programs.get(active_college, [])
        if not programs:
            # Handle case where active_college isn't set but we're in a comparison intent
            for college, progs in college_programs.items():
                mentioned = [prog for prog in progs if prog in message]
                if len(mentioned) >= 2:
                    programs = progs
                    active_college = college
                    events.append(SlotSet("active_college", active_college))
                    break
        
        # Check if any programs were mentioned
        mentioned_programs = [prog for prog in programs if prog in message]
        
        if len(mentioned_programs) >= 2:
            prog1, prog2 = mentioned_programs[:2]
            comparison_topic = f"compare_{prog1}_{prog2}"
            
            events.extend([
                SlotSet("active_topic", comparison_topic),
                SlotSet("program", f"{prog1}_vs_{prog2}"),
                SlotSet("conversation_stage", "comparing")
            ])
            
            # Generate a dynamic comparison response
            comparison_response = (
                f"I'll help you compare {prog1.upper()} and {prog2.upper()} programs. "
                f"They differ in several aspects including curriculum focus, "
                f"career paths, and specialization opportunities."
            )
            dispatcher.utter_message(text=comparison_response)
            
            # Add follow-up suggestion
            dispatcher.utter_message(
                text="Would you like to know about specific differences in curriculum, "
                     "job prospects, or difficulty level?"
            )
        elif active_college:
            # Give general comparison information for the college
            dispatcher.utter_message(
                text=f"I can help you compare different programs in the {active_college.upper()}. "
                     f"Which specific programs would you like to compare?"
            )
            
            # List available programs for comparison
            if programs:
                prog_list = ", ".join(prog.upper() for prog in programs)
                dispatcher.utter_message(text=f"Available programs: {prog_list}")
        
        return events

class ActionHandleProgramDifficulty(Action):
    def name(self) -> Text:
        return "action_handle_program_difficulty"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = tracker.latest_message.get('text', '').lower()
        active_college = tracker.get_slot('active_college')
        
        # College-specific program mappings
        college_programs = {
            'ccs': ['bscs', 'bsit', 'bsis', 'bsca'],
            'coe': ['mechanical', 'civil', 'electrical', 'chemical', 'industrial'],
            'chs': ['nursing', 'pharmacy', 'medical technology', 'public health'],
            'ceba': ['business', 'economics', 'accountancy', 'finance', 'management'],
            'cass': ['psychology', 'sociology', 'political science', 'history', 'languages'],
            'ced': ['elementary', 'secondary', 'special education', 'physical education'],
            'csm': ['biology', 'chemistry', 'mathematics', 'physics', 'statistics']
        }
        
        # Simple difficulty assessments for programs
        difficulty_info = {
            'bscs': "The BSCS program requires strong analytical skills and mathematical aptitude. It involves intensive programming and theoretical computer science concepts.",
            'bsit': "BSIT has a balanced mix of technical and practical components. While challenging, it focuses more on applied technology than theoretical aspects.",
            'bsis': "BSIS combines business knowledge with information systems concepts. The challenge comes from integrating business processes with technical solutions.",
            'bsca': "BSCA focuses on application development and multimedia. It requires creative skills alongside technical knowledge.",
            'mechanical': "Mechanical Engineering is math-intensive with complex physics concepts. It requires strong analytical skills for design and thermodynamics.",
            'civil': "Civil Engineering involves structural analysis, materials science, and environmental systems. It requires both theoretical knowledge and practical application.",
            'electrical': "Electrical Engineering is considered challenging due to abstract concepts in circuit analysis, electromagnetic theory, and signal processing.",
            'nursing': "Nursing combines scientific knowledge with clinical skills. The program is demanding due to intensive clinical rotations and comprehensive healthcare knowledge.",
            'pharmacy': "Pharmacy requires strong chemistry foundations and medical knowledge. The curriculum covers pharmaceutical sciences, clinical pharmacy, and patient care.",
            'economics': "Economics requires strong analytical and mathematical skills. Students must master economic theory, statistics, and applied economics methods.",
            'accountancy': "Accountancy is rigorous due to detailed accounting principles, taxation, and auditing standards that must be mastered.",
            'psychology': "Psychology balances research methodology with theoretical frameworks. The challenge lies in understanding complex human behavior and research design.",
            'elementary_education': "Elementary Education involves comprehensive teaching methodologies across multiple subjects. It requires strong pedagogical knowledge.",
            'physics': "Physics is one of the more challenging science programs due to advanced mathematics and abstract concepts in theoretical physics.",
            'mathematics': "Mathematics programs are abstract and require strong logical reasoning skills. Students progress from calculus to advanced topics like abstract algebra."
        }
        
        events = []
        
        # Identify which program difficulty is being asked about
        programs = college_programs.get(active_college, [])
        if not programs:
            # Handle case where active_college isn't set
            for college, progs in college_programs.items():
                mentioned = [prog for prog in progs if prog in message]
                if mentioned:
                    programs = progs
                    active_college = college
                    events.append(SlotSet("active_college", active_college))
                    break
        
        # Check if any specific program was mentioned
        mentioned_program = next((prog for prog in programs if prog in message), None)
        
        if mentioned_program:
            program_info = difficulty_info.get(mentioned_program, 
                f"The {mentioned_program} program has its own unique challenges. I can provide more specific information if needed.")
            
            dispatcher.utter_message(text=program_info)
            
            events.extend([
                SlotSet("program", mentioned_program),
                SlotSet("active_topic", "program_difficulty"),
                SlotSet("conversation_stage", "discussing_difficulty")
            ])
            
            # Add follow-up suggestion
            dispatcher.utter_message(
                text="Would you like to know about specific challenging courses, study tips, or compare with other programs?"
            )
        elif active_college:
            # Give general difficulty information for the college
            college_name_map = {
                'ccs': 'College of Computer Studies',
                'coe': 'College of Engineering',
                'chs': 'College of Health Sciences',
                'ceba': 'College of Economics and Business Administration',
                'cass': 'College of Arts and Social Sciences',
                'ced': 'College of Education',
                'csm': 'College of Science and Mathematics'
            }
            
            college_name = college_name_map.get(active_college, active_college.upper())
            
            dispatcher.utter_message(
                text=f"Programs in the {college_name} vary in difficulty. Each has unique challenges "
                     f"based on your skills and interests. Which specific program would you like to know about?"
            )
            
            # List available programs
            if programs:
                prog_list = ", ".join(prog.upper() for prog in programs)
                dispatcher.utter_message(text=f"Available programs: {prog_list}")
        
        return events

class ActionHandleFacilityAccess(Action):
    def name(self) -> Text:
        return "action_handle_facility_access"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = tracker.latest_message.get('text', '').lower()
        
        # Define facility keywords and corresponding information
        facilities = {
            'fablab': {
                'keywords': ['fablab', 'fab lab', 'fabrication', 'maker space', '3d printing'],
                'access_info': "To access the FAB LAB, students need to submit a request form available at the FAB LAB website. First-time users must attend an orientation session.",
                'usage_info': "The FAB LAB has 3D printers, laser cutters, CNC machines, and electronics workstations. Users must follow safety protocols and equipment guidelines.",
                'hours': "Monday-Friday: 8:00 AM - 5:00 PM, Saturday: 9:00 AM - 3:00 PM",
                'location': "Ground Floor, Innovation Center Building"
            },
            'library': {
                'keywords': ['library', 'books', 'research center', 'study space'],
                'access_info': "The library is accessible to all students with a valid ID. For special collections, request forms may be required.",
                'usage_info': "The library offers study areas, digital resources, book borrowing, and research assistance.",
                'hours': "Monday-Friday: 7:00 AM - 8:00 PM, Saturday: 8:00 AM - 5:00 PM",
                'location': "Main Campus, Library Building"
            },
            'computer_labs': {
                'keywords': ['computer lab', 'pc', 'computer room', 'it lab', 'ccs lab'],
                'access_info': "Computer labs are available for scheduled classes and open hours. CCS students can access labs with their ID during open hours.",
                'usage_info': "Labs provide computers with specialized software for programming, design, and other coursework.",
                'hours': "Monday-Friday: 7:00 AM - 8:00 PM (open hours vary by lab)",
                'location': "College of Computer Studies Building, various floors"
            },
            'engineering_labs': {
                'keywords': ['engineering lab', 'workshop', 'coe lab', 'engineering workshop'],
                'access_info': "Engineering labs require course enrollment or special permission. Safety orientation is mandatory.",
                'usage_info': "Labs contain specialized equipment for different engineering disciplines. Supervision may be required for equipment use.",
                'hours': "Monday-Friday: 8:00 AM - 5:00 PM (varies by specific lab)",
                'location': "College of Engineering Building, various floors"
            },
            'science_labs': {
                'keywords': ['science lab', 'biology lab', 'chemistry lab', 'physics lab', 'csm lab'],
                'access_info': "Science labs are accessible during scheduled class time or with professor permission. Safety training required.",
                'usage_info': "Labs provide equipment and materials for scientific experiments. Safety protocols must be strictly followed.",
                'hours': "Monday-Friday: 8:00 AM - 5:00 PM (varies by specific lab)",
                'location': "College of Science and Mathematics Building, various floors"
            },
            'clinic': {
                'keywords': ['clinic', 'health center', 'medical', 'nurse', 'doctor'],
                'access_info': "The campus clinic is open to all students and staff. Present your ID and fill out a consultation form.",
                'usage_info': "Provides basic medical services, consultations, first aid, and medical certificates.",
                'hours': "Monday-Friday: 8:00 AM - 5:00 PM",
                'location': "Health Services Building, Main Campus"
            }
        }
        
        events = []
        facility_found = False
        
        # Check for facility mentions
        for facility, info in facilities.items():
            if any(keyword in message for keyword in info['keywords']):
                facility_found = True
                
                # Check if asking about access specifically
                if any(word in message for word in ['access', 'enter', 'use', 'get into', 'permission']):
                    dispatcher.utter_message(text=info['access_info'])
                    dispatcher.utter_message(text=f"Hours: {info['hours']}")
                    dispatcher.utter_message(text=f"Location: {info['location']}")
                # Check if asking about usage
                elif any(word in message for word in ['use', 'equipment', 'tools', 'machine', 'operate']):
                    dispatcher.utter_message(text=info['usage_info'])
                # General information
                else:
                    dispatcher.utter_message(text=f"About the {facility.replace('_', ' ').title()}:")
                    dispatcher.utter_message(text=info['access_info'])
                    dispatcher.utter_message(text=info['usage_info'])
                    dispatcher.utter_message(text=f"Hours: {info['hours']}")
                    dispatcher.utter_message(text=f"Location: {info['location']}")
                
                events.extend([
                    SlotSet("active_topic", facility),
                    SlotSet("conversation_stage", "facility_info")
                ])
                break
        
        # If no specific facility was found but asking about facilities in general
        if not facility_found and any(word in message for word in ['facility', 'facilities', 'lab', 'laboratory', 'resource']):
            dispatcher.utter_message(
                text="MSU-IIT offers various facilities including the FAB LAB, library, computer labs, "
                     "engineering workshops, science laboratories, and health clinic. "
                     "Which specific facility would you like to know about?"
            )
            events.append(SlotSet("active_topic", "facilities_general"))
        
        return events

class ActionTrackLocationContext(Action):
    def name(self) -> Text:
        return "action_track_location_context"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = tracker.latest_message.get('text', '').lower()
        active_college = tracker.get_slot('active_college')
        
        # Location keywords for colleges and important places
        locations = {
            'ccs_building': ['ccs building', 'computer studies building', 'ccs location'],
            'coe_building': ['coe building', 'engineering building', 'coe location'],
            'chs_building': ['chs building', 'health sciences building', 'chs location'],
            'ceba_building': ['ceba building', 'business building', 'economics building', 'ceba location'],
            'cass_building': ['cass building', 'arts building', 'social sciences building', 'cass location'],
            'ced_building': ['ced building', 'education building', 'ced location'],
            'csm_building': ['csm building', 'science building', 'mathematics building', 'csm location'],
            'admin_building': ['admin building', 'administration', 'registrar', 'admissions'],
            'library': ['library', 'research center'],
            'cafeteria': ['cafeteria', 'canteen', 'food court'],
            'gym': ['gymnasium', 'gym', 'sports complex'],
            'auditorium': ['auditorium', 'theater', 'assembly hall']
        }
        
        # Location information
        location_info = {
            'ccs_building': "The College of Computer Studies building is located at the north side of the campus. It's a three-story building with computer labs on all floors.",
            'coe_building': "The College of Engineering building is at the eastern part of the campus. It houses specialized engineering laboratories and workshops.",
            'chs_building': "The College of Health Sciences building is near the campus clinic. It includes simulation labs and healthcare training facilities.",
            'ceba_building': "The College of Economics and Business Administration building is centrally located. It features case study rooms and a business resource center.",
            'cass_building': "The College of Arts and Social Sciences building is near the university theater. It has dedicated spaces for arts, performances, and social science research.",
            'ced_building': "The College of Education building is adjacent to the demonstration school. It includes teaching laboratories and educational technology resources.",
            'csm_building': "The College of Science and Mathematics building houses specialized science laboratories for biology, chemistry, and physics research.",
            'admin_building': "The Administration Building is the central hub for university administration, including the Registrar's Office, Admissions, and other administrative services.",
            'library': "The University Library is a multi-story building with study spaces, book collections, and digital resource centers. It's located at the heart of the campus.",
            'cafeteria': "The main cafeteria is on the ground floor of the Student Center, offering a variety of food options at affordable prices.",
            'gym': "The gymnasium and sports complex are located at the western side of the campus, featuring indoor courts, training areas, and an outdoor track.",
            'auditorium': "The main auditorium is part of the Cultural Center, capable of seating 1,000 people for performances, ceremonies, and large gatherings."
        }
        
        events = []
        location_found = False
        
        # Check for location mentions
        for location, keywords in locations.items():
            if any(keyword in message for keyword in keywords):
                location_found = True
                dispatcher.utter_message(text=location_info[location])
                
                events.extend([
                    SlotSet("active_location", location),
                    SlotSet("active_topic", "location_info")
                ])
                break
        
        # If asking about a dean's office or department office
        if 'dean' in message and 'office' in message and active_college:
            dean_office_info = {
                'ccs': "The Dean's Office of the College of Computer Studies is on the 3rd floor, Room 301.",
                'coe': "The Dean's Office of the College of Engineering is on the 2nd floor, Room 201.",
                'chs': "The Dean's Office of the College of Health Sciences is on the 2nd floor, Room 205.",
                'ceba': "The Dean's Office of the College of Economics and Business Administration is on the 2nd floor, Room 210.",
                'cass': "The Dean's Office of the College of Arts and Social Sciences is on the 2nd floor, Room 215.",
                'ced': "The Dean's Office of the College of Education is on the 2nd floor, Room 202.",
                'csm': "The Dean's Office of the College of Science and Mathematics is on the 2nd floor, Room 220."
            }
            
            if active_college in dean_office_info:
                dispatcher.utter_message(text=dean_office_info[active_college])
                events.extend([
                    SlotSet("active_location", f"{active_college}_dean_office"),
                    SlotSet("active_topic", "location_dean")
                ])
                location_found = True
        
        elif 'department' in message and 'office' in message and active_college:
            dept_office_info = {
                'ccs': "Department offices in the College of Computer Studies are located on the 2nd floor, Rooms 201-207.",
                'coe': "Department offices in the College of Engineering are distributed across the 1st and 2nd floors based on specialization.",
                'chs': "Health Sciences department offices are on the 1st floor, Rooms 101-110.",
                'ceba': "Economics and Business Administration department offices are located on the 1st floor, Rooms 105-115.",
                'cass': "Arts and Social Sciences department offices can be found on the 1st and 3rd floors.",
                'ced': "Education department offices are on the 1st floor, Rooms 101-108.",
                'csm': "Science and Mathematics department offices are located on the 1st floor, Rooms 110-120."
            }
            
            if active_college in dept_office_info:
                dispatcher.utter_message(text=dept_office_info[active_college])
                events.extend([
                    SlotSet("active_location", f"{active_college}_department_offices"),
                    SlotSet("active_location", f"{active_college}_department_offices"),
                    SlotSet("active_topic", "location_departments")
                ])
                location_found = True
        
        # If no specific location was found but asking about locations
        if not location_found and any(word in message for word in ['where', 'location', 'find', 'building', 'room']):
            if active_college:
                dispatcher.utter_message(
                    text=f"The {active_college.upper()} building has various facilities including classrooms, "
                         f"faculty offices, the Dean's Office, department offices, and specialized laboratories. "
                         f"Which specific location are you looking for?"
                )
            else:
                dispatcher.utter_message(
                    text="MSU-IIT has several key buildings including college buildings, the Administration Building, "
                         "Library, Cultural Center, Sports Complex, and Student Center. "
                         "Which specific location are you looking for?"
                )
            events.append(SlotSet("active_topic", "location_general"))
        
        return events

class ActionValidateProgramRequirements(Action):
    def name(self) -> Text:
        return "action_validate_program_requirements"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = tracker.latest_message.get('text', '').lower()
        active_college = tracker.get_slot('active_college')
        program = tracker.get_slot('program')
        
        # Program requirement information
        program_requirements = {
            # CCS Programs
            'bscs': {
                'admission': "For BSCS, admission requirements include good grades in Mathematics and Science subjects, passing the university entrance exam with a high score in analytical reasoning.",
                'curriculum': "The BSCS curriculum includes intensive programming courses, data structures, algorithms, software engineering, and computer architecture. A thesis project is required in the senior year.",
                'graduation': "To graduate, BSCS students must complete all required courses (approx. 150 units), maintain a satisfactory GPA, and successfully defend their thesis."
            },
            'bsit': {
                'admission': "BSIT admission requires passing the entrance exam with good scores in logical reasoning. Previous experience with computers is beneficial but not required.",
                'curriculum': "The BSIT curriculum balances technical knowledge with practical applications, including networking, web development, database management, and IT project management.",
                'graduation': "BSIT graduation requirements include completing approximately 145 units, a capstone project, and possibly industry certifications."
            },
            
            # COE Programs
            'mechanical': {
                'admission': "Mechanical Engineering requires strong mathematics and physics background, with high scores in these areas on the entrance exam.",
                'curriculum': "The curriculum includes thermodynamics, fluid mechanics, machine design, manufacturing processes, and engineering mathematics.",
                'graduation': "Graduation requires completing all engineering courses, laboratories, design projects, and a comprehensive final project."
            },
            'electrical': {
                'admission': "Electrical Engineering admission requires excellent mathematics and physics scores, with particular strength in calculus and electricity concepts.",
                'curriculum': "The curriculum covers circuit theory, electronics, electromagnetic fields, control systems, power systems, and communications engineering.",
                'graduation': "To graduate, students must complete all required courses, laboratory work, and a final engineering project."
            },
            
            # General college requirements
            'ccs': {
                'admission': "The College of Computer Studies admission requirements include a strong aptitude for logical and analytical thinking, demonstrated through good grades in mathematics and science subjects.",
                'curriculum': "CCS programs emphasize programming fundamentals, systems analysis, software development, and IT management, with specialized tracks in later years.",
                'graduation': "Graduation from CCS programs requires completing all required and elective courses, maintaining a satisfactory GPA, and fulfilling thesis or capstone requirements."
            },
            'coe': {
                'admission': "The College of Engineering requires strong mathematics and science backgrounds, high entrance exam scores, and good problem-solving abilities.",
                'curriculum': "Engineering programs include fundamental engineering sciences, specialized discipline courses, laboratory work, and design projects.",
                'graduation': "COE students must complete all technical requirements, laboratory courses, design projects, and satisfy general education requirements."
            },
            'chs': {
                'admission': "Health Sciences programs require good grades in biology and chemistry, strong entrance exam scores, and often interviews to assess aptitude for healthcare.",
                'curriculum': "CHS programs combine theoretical knowledge with clinical/practical training in healthcare settings.",
                'graduation': "Graduation requires completing all academic and clinical requirements, often with minimum grade requirements in major subjects."
            },
            'ceba': {
                'admission': "Business and Economics programs look for aptitude in mathematics, critical thinking, and communication skills.",
                'curriculum': "CEBA programs cover core business/economics principles, management techniques, analytical methods, and case studies.",
                'graduation': "Students must complete all required business courses, case analyses, and often internships or business projects."
            },
            'cass': {
                'admission': "Arts and Social Sciences programs evaluate communication skills, critical thinking, and social awareness.",
                'curriculum': "CASS curricula emphasize theoretical frameworks, research methodologies, and critical analysis in humanities and social sciences.",
                'graduation': "Graduation requires completing coursework, research papers, and often a thesis or creative project."
            },
            'ced': {
                'admission': "Education programs assess communication skills, aptitude for teaching, and often conduct interviews.",
                'curriculum': "CED programs include pedagogical theories, teaching methodologies, and extensive practice teaching experience.",
                'graduation': "Students must complete academic requirements, demonstration teaching, and field experiences with satisfactory performance."
            },
            'csm': {
                'admission': "Science and Mathematics programs require strong backgrounds in related subjects and high analytical scores on entrance exams.",
                'curriculum': "CSM curricula include theoretical foundations, laboratory work, research methodologies, and applications of scientific principles.",
                'graduation': "Graduation requires completing all science courses, laboratory requirements, and often research projects or theses."
            }
        }
        
        events = []
        
        # Determine what type of requirement information is being requested
        requirement_type = None
        if any(word in message for word in ['admission', 'requirements', 'qualify', 'enter', 'application']):
            requirement_type = 'admission'
        elif any(word in message for word in ['curriculum', 'subjects', 'courses', 'study', 'learn']):
            requirement_type = 'curriculum'
        elif any(word in message for word in ['graduate', 'graduation', 'finish', 'complete']):
            requirement_type = 'graduation'
        
        # Provide the requested information
        if program and program in program_requirements and requirement_type:
            dispatcher.utter_message(text=program_requirements[program][requirement_type])
            events.extend([
                SlotSet("active_topic", f"{program}_{requirement_type}"),
                SlotSet("conversation_stage", "providing_requirements")
            ])
        elif active_college and active_college in program_requirements and requirement_type:
            dispatcher.utter_message(text=program_requirements[active_college][requirement_type])
            events.extend([
                SlotSet("active_topic", f"{active_college}_{requirement_type}"),
                SlotSet("conversation_stage", "providing_requirements")
            ])
        elif requirement_type:
            dispatcher.utter_message(
                text="I can provide information about admission requirements, curriculum, or graduation requirements "
                     "for specific programs or colleges. Which program or college are you interested in?"
            )
            events.append(SlotSet("active_topic", "program_requirements_general"))
        
        return events

class ActionManageStudentPreferences(Action):
    def name(self) -> Text:
        return "action_manage_student_preferences"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = tracker.latest_message.get('text', '').lower()
        
        # Track student interests and preferences
        interests = []
        for interest, keywords in {
            'technical': ['programming', 'coding', 'software', 'development', 'technical'],
            'research': ['research', 'analysis', 'investigation', 'discovery', 'innovation'],
            'creative': ['design', 'creative', 'artistic', 'multimedia', 'visual'],
            'business': ['business', 'management', 'entrepreneurship', 'economics', 'finance'],
            'healthcare': ['health', 'medical', 'care', 'treatment', 'nursing'],
            'teaching': ['teach', 'education', 'training', 'instruction', 'teaching'],
            'sciences': ['science', 'laboratory', 'experiment', 'discovery', 'analysis'],
            'practical': ['hands-on', 'practical', 'implementation', 'applied', 'skills']
        }.items():
            if any(keyword in message for keyword in keywords):
                interests.append(interest)
        
        # Get program recommendations based on interests
        recommended_programs = []
        
        if 'technical' in interests:
            recommended_programs.extend(['BSCS', 'BSIT'])
        if 'research' in interests:
            recommended_programs.extend(['BSCS', 'Physics', 'Biology', 'Chemistry'])
        if 'creative' in interests:
            recommended_programs.extend(['BSCA', 'Fine Arts', 'Architecture'])
        if 'business' in interests:
            recommended_programs.extend(['BSIS', 'Business Administration', 'Economics'])
        if 'healthcare' in interests:
            recommended_programs.extend(['Nursing', 'Pharmacy', 'Public Health'])
        if 'teaching' in interests:
            recommended_programs.extend(['Education', 'Teaching'])
        if 'sciences' in interests:
            recommended_programs.extend(['Biology', 'Chemistry', 'Physics', 'Mathematics'])
        if 'practical' in interests:
            recommended_programs.extend(['BSIT', 'Engineering', 'Nursing'])
        
        events = []
        
        # If interests were detected, provide recommendations
        if interests:
            unique_recommendations = list(set(recommended_programs))
            if len(unique_recommendations) > 0:
                response = "Based on your interests in " + ", ".join(interests) + ", "
                response += "you might consider these programs: " + ", ".join(unique_recommendations[:5])
                
                dispatcher.utter_message(text=response)
                dispatcher.utter_message(
                    text="Would you like more specific information about any of these programs?"
                )
                
                events.extend([
                    SlotSet("active_topic", "program_recommendation"),
                    SlotSet("conversation_stage", "recommending")
                ])
        
        return events