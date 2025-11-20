import google.generativeai as genai
import json
import os
import time
import re
import requests
from dotenv import load_dotenv
from services.vector_service import VectorService
from models import File, Lesson, LearningObjective

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            print("❌ WARNING: GEMINI_API_KEY not found in environment!")
        else:
            print(f"✓ Gemini API key loaded: {self.api_key[:20]}...")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        self.vector_service = VectorService()
        
        # LM Studio configuration
        self.lm_studio_url = "http://localhost:1234/v1/chat/completions"
        self.lm_studio_model = "liquid/lfm2-1.2b"
    
    def _validate_component(self, component):
        """Validate that a component has all required fields"""
        if not component or not isinstance(component, dict):
            return False, "Component is not a valid dictionary"
        
        if 'type' not in component or 'data' not in component:
            return False, "Component missing 'type' or 'data' field"
        
        comp_type = component['type']
        data = component['data']
        
        # Validate practice_exercise specifically
        if comp_type == 'practice_exercise':
            if not data.get('accounts') or len(data.get('accounts', [])) == 0:
                return False, "practice_exercise must have at least one account"
            
            if not data.get('analysis_questions') or len(data.get('analysis_questions', [])) == 0:
                return False, "practice_exercise must have at least one analysis_question"
            
            # Check that accounts have content
            for acc in data.get('accounts', []):
                if not acc.get('text') or len(acc.get('text', '').strip()) < 50:
                    return False, f"Account '{acc.get('title', 'Unknown')}' has insufficient text content"
            
            # Check that questions exist
            for q in data.get('analysis_questions', []):
                if not q.get('question') or len(q.get('question', '').strip()) < 10:
                    return False, "analysis_questions must have substantive question text"
        
        return True, "Valid"
    
    def _call_llm(self, prompt, response_format='json', max_retries=3):
        """Call LLM with rate limiting, retry logic, and LM Studio fallback"""
        last_error = None
        
        print("\n" + "="*80)
        print("🤖 LLM PROMPT:")
        print("="*80)
        print(prompt)
        print("="*80 + "\n")
        
        for attempt in range(max_retries):
            try:
                print(f"Calling Gemini API (attempt {attempt + 1}/{max_retries})... (prompt length: {len(prompt)} chars)")
                response = self.model.generate_content(prompt)
                print("Gemini API response received")
                
                if response_format == 'json':
                    # Extract JSON from response
                    text = response.text
                    
                    print("\n" + "="*80)
                    print("✅ LLM RESPONSE (Raw):")
                    print("="*80)
                    print(text)
                    print("="*80 + "\n")
                    
                    # Remove markdown code blocks if present
                    if '```json' in text:
                        text = text.split('```json')[1].split('```')[0]
                    elif '```' in text:
                        text = text.split('```')[1].split('```')[0]
                    
                    parsed = json.loads(text.strip())
                    
                    print("\n" + "="*80)
                    print("📦 LLM RESPONSE (Parsed JSON):")
                    print("="*80)
                    print(json.dumps(parsed, indent=2))
                    print("="*80 + "\n")
                    
                    return parsed
                else:
                    print("\n" + "="*80)
                    print("✅ LLM RESPONSE (Text):")
                    print("="*80)
                    print(response.text)
                    print("="*80 + "\n")
                    return response.text
                    
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Check if it's a rate limit error (429 or ResourceExhausted)
                if 'resourceexhausted' in error_str or '429' in error_str or 'rate limit' in error_str:
                    # Extract retry delay from error message
                    retry_delay = self._extract_retry_delay(str(e))
                    
                    if attempt < max_retries - 1:
                        print(f"⚠️ Rate limit hit. Waiting {retry_delay} seconds before retry...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"⚠️ Rate limit exceeded after {max_retries} attempts. Falling back to LM Studio...")
                else:
                    print(f"❌ Gemini API error: {type(e).__name__}: {e}")
                    if attempt < max_retries - 1:
                        print(f"⚠️ Retrying in 2 seconds...")
                        time.sleep(2)
                        continue
        
        # If all retries failed, try LM Studio
        print("⚠️ Gemini API failed, attempting LM Studio fallback...")
        try:
            return self._call_lm_studio(prompt, response_format)
        except Exception as lm_error:
            print(f"❌ LM Studio fallback also failed: {lm_error}")
            print(f"⚠️ Using simple fallback response")
            import traceback
            traceback.print_exc()
            return self._fallback_response(prompt)
    
    def _extract_retry_delay(self, error_message):
        """Extract retry delay from error message, default to 30 seconds"""
        # Try to find patterns like "retry in 27.7s" or "retry after 30 seconds"
        patterns = [
            r'retry in ([\d.]+)s',
            r'retry after ([\d.]+) second',
            r'retry_after[:\s]+([\d.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message.lower())
            if match:
                delay = float(match.group(1))
                # Add 1 second buffer for safety
                return delay + 1
        
        # Default to 30 seconds if no delay found
        return 30
    
    def _call_lm_studio(self, prompt, response_format='json'):
        """Call LM Studio API as fallback"""
        try:
            print(f"📡 Calling LM Studio API at {self.lm_studio_url}")
            
            payload = {
                "model": self.lm_studio_model,
                "messages": [
                    {"role": "system", "content": "You are a helpful educational AI assistant. Respond in JSON format when requested."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(self.lm_studio_url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            text = result['choices'][0]['message']['content']
            
            print(f"✓ LM Studio response received (length: {len(text)} chars)")
            
            print("\n" + "="*80)
            print("✅ LM STUDIO RESPONSE (Raw):")
            print("="*80)
            print(text)
            print("="*80 + "\n")
            
            if response_format == 'json':
                # Remove markdown code blocks if present
                if '```json' in text:
                    text = text.split('```json')[1].split('```')[0]
                elif '```' in text:
                    text = text.split('```')[1].split('```')[0]
                
                parsed = json.loads(text.strip())
                
                print("\n" + "="*80)
                print("📦 LM STUDIO RESPONSE (Parsed JSON):")
                print("="*80)
                print(json.dumps(parsed, indent=2))
                print("="*80 + "\n")
                
                return parsed
            else:
                return text
                
        except Exception as e:
            print(f"❌ LM Studio error: {type(e).__name__}: {e}")
            raise
    
    def _fallback_response(self, prompt):
        """Fallback logic when all LLM calls fail - return simple default structures"""
        # Simplified fallback - return basic structures based on prompt content
        if 'curriculum' in prompt.lower() or 'lessons' in prompt.lower():
            return [{'lesson_number': 1, 'title': 'Introduction', 'plan': 'Overview of concepts', 'file_ids': [], 'objectives': []}]
        elif 'objectives' in prompt.lower():
            return ['Understand basic concepts', 'Apply learned knowledge', 'Practice skills']
        elif 'components' in prompt.lower():
            return [{'order': 0, 'type': 'info_card', 'data': {'title': 'Introduction', 'content': 'Welcome to the lesson'}}]
        return {}
    
    def generate_curriculum(self, module_id, files):
        """Generate lessons structure directly from uploaded files"""
        # Get file information
        file_info = []
        all_file_ids = []
        for file in files:
            all_file_ids.append(file.id)
            file_info.append({
                'id': file.id,
                'filename': file.filename,
                'type': file.file_type
            })
        
        # Query vector database for context (skip if no files)
        context = ""
        if all_file_ids:
            try:
                context = self.vector_service.get_files_context(all_file_ids)
            except Exception as e:
                print(f"Warning: Could not get file context: {e}")
                context = "No content available"
        
        prompt = f"""
You are an educational content organizer. Be CONCISE and focused.

Files: {json.dumps(file_info, indent=2)}
Content Context: {context}

Analyze the uploaded materials and create a curriculum with ONLY as many lessons as necessary to cover all the content.
Do NOT create arbitrary numbers of lessons - generate exactly what's needed based on the material.

IMPORTANT: 
- Lesson titles should be SHORT and CLEAR (4-8 words maximum)
- Focus on natural topic boundaries in the material
- Progressive difficulty: foundational → intermediate → advanced
- Each lesson should be substantial but focused on one clear theme
- Distribute files logically across lessons based on their content

Return ONLY a JSON array:
[
  {{"lesson_number": 1, "title": "Brief lesson title", "file_ids": [file IDs relevant to this lesson], "plan": "Brief 1-sentence overview"}},
  ...
]
"""
        
        lessons_data = self._call_llm(prompt, response_format='json')
        
        # Ensure all lessons have file_ids
        if isinstance(lessons_data, list) and all_file_ids:
            for lesson in lessons_data:
                if 'file_ids' not in lesson or not lesson['file_ids']:
                    # If no specific files assigned, use all files
                    lesson['file_ids'] = all_file_ids
        
        return lessons_data if isinstance(lessons_data, list) else []
    
    def generate_objectives(self, lesson_id, file_ids):
        """Generate SMART learning objectives for a lesson"""
        lesson = Lesson.query.get(lesson_id)
        if not lesson:
            print(f"⚠️ Lesson {lesson_id} not found")
            return []
        
        # Get context from files (with timeout protection)
        context = ""
        if file_ids:
            try:
                print(f"Getting context for file_ids: {file_ids}")
                context = self.vector_service.get_files_context(file_ids)
                print(f"Context retrieved: {len(context)} chars")
            except Exception as e:
                print(f"⚠️ Error getting file context: {e}")
                context = "No content available"
        else:
            print("No file_ids provided for context")
            context = "No specific content provided"
        
        prompt = f"""
You are an instructional designer. Be CONCISE and specific.

Lesson: {lesson.title}
Plan: {lesson.plan if lesson.plan else 'N/A'}
Content: {context[:500]}...

Create 3-5 SMART learning objectives that are:
- SPECIFIC and actionable (not vague)
- SHORT (one sentence each)
- Focused on key concepts only

Return ONLY a JSON array:
["objective 1", "objective 2", ...]
"""
        
        try:
            objectives = self._call_llm(prompt, response_format='json')
            return objectives if isinstance(objectives, list) else []
        except Exception as e:
            print(f"❌ Error generating objectives: {e}")
            # Return fallback objectives
            return [
                f"Understand the main concepts in {lesson.title}",
                f"Apply knowledge from this lesson",
                f"Practice relevant skills"
            ]
    
    def generate_lesson_components(self, lesson_id, insights):
        """Generate initial components for a lesson"""
        lesson = Lesson.query.get(lesson_id)
        objectives = LearningObjective.query.filter_by(lesson_id=lesson_id).order_by(LearningObjective.order).all()
        
        objectives_text = [obj.objective_text for obj in objectives]
        insights_text = json.dumps(insights, indent=2) if insights else "No prior insights"
        
        # Get relevant content from vector DB
        file_ids = json.loads(lesson.file_ids) if lesson.file_ids else []
        context = self.vector_service.query_relevant_content(objectives_text, file_ids)
        
        prompt = f"""
You are an adaptive learning system. Be CONCISE and focused.

Lesson: {lesson.title}
Objectives: {json.dumps(objectives_text, indent=2)}
Content: {context}
User Insights: {insights_text}

CRITICAL RULES - READ CAREFULLY:
1. ALL text must be BRIEF and to-the-point
2. info_card content: 2-4 sentences maximum (unless insights show user needs detail)
3. Explanations: 1-2 sentences maximum
4. NO unnecessary elaboration or "fluff"
5. Focus on ESSENTIAL information only

COMPONENT ORDERING PHILOSOPHY:
- Multiple teaching components in a row is GOOD (teach → teach → teach → test)
- Testing first is OK IF it's followed by teaching
- The key principle: Always ensure teaching material is available when needed
- Adaptive flow based on user's level

Suggested patterns:
- teach → teach → test (thorough explanation first)
- test → teach (assessment first, then instruction)
- teach → test → teach → test (alternating)
- teach → teach → teach → test (deep dive, then assessment)

Component types:
TEACHING:
- info_card: Brief explanations (title + 2-4 sentences) - Use to explain concepts
- flashcard: Quick Q&A (short front/back) - Use to reinforce key terms
- mindmap: Visual relationships - Use to show connections

TESTING:
- quiz: Single concept per question - Use to check understanding
- practice_exercise: Applied problems - Use to test application
- custom: Interactive React code - Use for engagement

CUSTOM COMPONENTS: Available libraries - React hooks, Three.js, Recharts, D3, Framer Motion, React Icons
- MUST call trackEvent() for interactions
- MUST call onComplete() when done
- Use h('element', {{props}}, children) syntax

Example: return function() {{ const [x, setX]=useState(0); return h('div', {{}}, h('button', {{onClick:()=>{{setX(x+1);trackEvent('click',{{count:x+1}});if(x>=4)onComplete();}}}}, 'Click')); }}

ADAPT TO USER:
- If insights show struggles: Use multiple teaching components before any test
- If insights show confidence: Can test first, then teach based on results
- If insights show preference: Match their learning style

Create 3-5 components in a logical learning flow.

Return ONLY JSON array:
[
  {{
    "order": 0,
    "type": "component_type",
    "data": {{
      // For info_card: {{"title": "Brief title", "content": "2-4 sentences MAX"}}
      // For flashcard: {{"front": "Short question", "back": "Brief answer"}}
      // For quiz: {{"question": "...", "options": ["A","B","C","D"], "correct": 0, "explanation": "REQUIRED - Explain why the correct answer is right (1-2 sentences)"}}
      // For mindmap: {{"central": "Main idea", "nodes": [{{"title": "Branch", "description": "Brief explanation of this concept", "nodes": [{{"title": "Sub-branch", "description": "Brief explanation"}}]}}]}}
      // For practice_exercise: {{
      //   "title": "Brief title",
      //   "instructions": "Clear, short instructions",
      //   "accounts": [{{"id": 1, "title": "Title", "text": "Passage text"}}],
      //   "analysis_questions": [{{"account_id": 1, "question": "Question"}}]
      // }}
    }}
  }}
]
"""
        
        components = self._call_llm(prompt, response_format='json')
        return components if isinstance(components, list) else []
    
    def generate_adaptive_batch(self, lesson_id, insights, recent_telemetry, evaluation_data=None):
        """Generate a BATCH of 2-3 adaptive components (teaching + testing) based on evaluation"""
        lesson = Lesson.query.get(lesson_id)
        objectives = LearningObjective.query.filter_by(lesson_id=lesson_id).all()
        
        telemetry_summary = json.dumps(recent_telemetry, indent=2) if recent_telemetry else "No recent telemetry"
        insights_text = json.dumps(insights, indent=2) if insights else "No insights"
        evaluation_text = json.dumps(evaluation_data, indent=2) if evaluation_data else "No evaluation data"
        
        # Get current component count for order numbering
        from models import LessonComponent
        current_count = LessonComponent.query.filter_by(lesson_id=lesson_id).count()
        
        # Get recent component types to avoid repetition
        recent_components = LessonComponent.query.filter_by(
            lesson_id=lesson_id
        ).order_by(LessonComponent.order.desc()).limit(5).all()
        recent_types = [c.component_type for c in recent_components]
        recent_types_summary = ', '.join(recent_types) if recent_types else 'None yet'
        
        prompt = f"""
You are an adaptive learning AI. Generate a BATCH of 2-3 diverse components to help the user master the learning objectives.

Lesson: {lesson.title}
Learning Objectives: {json.dumps([obj.objective_text for obj in objectives], indent=2)}
Performance Data: {telemetry_summary}
User Insights: {insights_text}
EVALUATION RESULTS: {evaluation_text}

RECENT COMPONENT TYPES (last 5): {recent_types_summary}
⚠️ Try to AVOID repeating the same types unless absolutely necessary!

YOUR GOAL: Create varied, engaging components that address the user's needs.

ANALYZE THE EVALUATION:
- What specific concepts do they struggle with?
- What's their learning style? (visual/reading/practice)
- Have they seen the same component type too many times?
- What would be the BEST way to help them understand?

COMPONENT SELECTION GUIDELINES (Be Creative!):
1. VARY the component types - don't repeat the same type if they just did it
2. Match their learning style:
   - Visual learners → mindmap, diagrams
   - Reading learners → info_card, flashcard
   - Practice learners → quiz, practice_exercise
3. Consider difficulty:
   - Struggling? Start with simple teaching (flashcard, info_card)
   - Doing well? Challenge them (practice_exercise, complex quiz)
4. Mix teaching and testing, but in any order that makes sense
5. Be strategic - if they failed a quiz, DON'T immediately give another quiz on the same thing

AVAILABLE COMPONENTS:
TEACHING (explain, clarify, show):
- info_card: Brief explanation with examples {{"title": "...", "content": "2-4 sentences"}}
- flashcard: Quick Q&A to reinforce {{"front": "question", "back": "answer"}}
- mindmap: Visual relationships {{"central": "main concept", "nodes": [{{"title": "...", "description": "Brief explanation", "nodes": [...]}}]}}
- custom: Interactive visualization (advanced, use sparingly)

TESTING (check understanding):
- quiz: Single multiple-choice question {{"question": "...", "options": [...], "correct": 0, "explanation": "REQUIRED - Explain why correct answer is right (1-2 sentences)"}}
- practice_exercise: Multi-question scenario analysis (use when they need deep practice)

BATCH STRATEGY (Pick what fits best):
- If they need concept clarification: info_card → flashcard → quiz
- If they're visual: mindmap → quiz
- If they need practice: info_card → practice_exercise
- If they're confident: quiz → flashcard (quick reinforcement)
- If they just failed practice_exercise: info_card → flashcard (rebuild foundation)

CRITICAL: 
- Include at least ONE testing component (quiz OR practice_exercise) in the batch
- Don't be predictable - vary your approach based on context
- Keep all content CONCISE and focused

Return a JSON array of 2-3 components:
[
  {{
    "order": {current_count},
    "type": "component_type",
    "data": {{...}}
  }},
  {{
    "order": {current_count + 1},
    "type": "component_type",
    "data": {{...}}
  }}
]

If all objectives are met (evaluation says should_continue is FALSE), return null.
"""
        
        components = self._call_llm(prompt, response_format='json')
        
        # Validate that we got a list and it has both teaching and testing
        if not components or components == 'null':
            return None
        
        if not isinstance(components, list):
            return None
        
        # Check if batch includes at least one testing component
        component_types = [c.get('type') for c in components]
        testing_types = ['quiz', 'practice_exercise']
        has_testing = any(t in testing_types for t in component_types)
        
        if not has_testing:
            print("⚠️ Warning: Batch doesn't include testing component, but continuing...")
        
        return components
    
    def generate_adaptive_component(self, lesson_id, insights, recent_telemetry, evaluation_data=None):
        """Generate next component based on evaluation and telemetry"""
        lesson = Lesson.query.get(lesson_id)
        objectives = LearningObjective.query.filter_by(lesson_id=lesson_id).all()
        
        telemetry_summary = json.dumps(recent_telemetry, indent=2) if recent_telemetry else "No recent telemetry"
        insights_text = json.dumps(insights, indent=2) if insights else "No insights"
        evaluation_text = json.dumps(evaluation_data, indent=2) if evaluation_data else "No evaluation data"
        
        prompt = f"""
You are an adaptive learning AI. Generate a component to help the user master the learning objectives.

Lesson: {lesson.title}
Learning Objectives: {json.dumps([obj.objective_text for obj in objectives], indent=2)}
Performance Data: {telemetry_summary}
User Insights: {insights_text}
EVALUATION RESULTS: {evaluation_text}

Based on the evaluation, determine what component to generate:

1. If evaluation shows WEAK AREAS → Generate TEACHING component on that specific area
2. If evaluation shows good understanding but LOW CONFIDENCE → Add reinforcement (quiz/flashcard)
3. If evaluation shows specific learning style → Use that component type
4. If evaluation says should_continue is FALSE → Return null (objectives met)

PRIORITY: Address weak_areas from evaluation first!

FLEXIBLE COMPONENT FLOW:
- Multiple teaching components in a row is ENCOURAGED for struggling students
- If user failed test, teach that specific concept
- Match the user's preferred learning style (from evaluation)
- Be concise - focus on gaps identified in evaluation

Component types:
TEACHING (use when user needs to learn):
- info_card: {{"title": "...", "content": "..."}}
- flashcard: {{"front": "...", "back": "..."}}
- mindmap: {{"central": "...", "nodes": [{{"title": "...", "description": "Brief explanation of this concept", "nodes": [{{"title": "...", "description": "Brief explanation"}}]}}]}}

TESTING (use to assess understanding):
- quiz: {{"question": "...", "options": [], "correct": 0, "explanation": "REQUIRED - Explain why the correct answer is right (1-2 sentences)"}}
- practice_exercise: {{
    "title": "Exercise title",
    "instructions": "Clear instructions for what to do",
    "accounts": [{{"id": 1, "title": "Passage/Account title", "text": "FULL TEXT CONTENT HERE - must be substantial"}}],
    "analysis_questions": [{{"account_id": 1, "question": "Question text here"}}]
  }}
- custom: {{"code": "return function() {{ ... }}"}}

CRITICAL for practice_exercise:
- MUST include at least 2-3 accounts with COMPLETE text (not summaries)
- Each account needs full content (at least 3-5 sentences)
- MUST include at least 2-3 analysis_questions
- Each question MUST reference an account_id
- Instructions must be clear and specific

Generate ONE component based on user's needs right now.

Return ONLY a JSON object:
{{
  "order": <next_order_number>,
  "type": "component_type",
  "data": {{...}}
}}

If all objectives are covered, return null.
"""
        
        component = self._call_llm(prompt, response_format='json')
        return component if component and component != 'null' else None
    
    def evaluate_learning_objectives(self, lesson_id, user_id):
        """
        Evaluate if user has met the learning objectives for this lesson.
        Returns: (objectives_met: bool, evaluation_data: dict, should_continue: bool)
        """
        from models import LessonComponent, Telemetry
        
        lesson = Lesson.query.get(lesson_id)
        objectives = LearningObjective.query.filter_by(lesson_id=lesson_id).all()
        
        # Get ALL telemetry for this lesson to analyze learning (including adaptive phase)
        all_telemetry = Telemetry.query.filter_by(
            user_id=user_id,
            lesson_id=lesson_id
        ).order_by(Telemetry.timestamp.desc()).limit(100).all()
        
        telemetry_data = [{
            'event_type': t.event_type,
            'event_data': json.loads(t.event_data) if isinstance(t.event_data, str) else t.event_data,
            'timestamp': t.timestamp.isoformat(),
            'component_id': t.component_id
        } for t in all_telemetry]
        
        # Get all components to see what was covered (structured + adaptive)
        components = LessonComponent.query.filter_by(lesson_id=lesson_id).order_by(LessonComponent.order).all()
        component_summary = [{
            'type': c.component_type,
            'order': c.order,
            'id': c.id
        } for c in components]
        
        # Separate structured vs adaptive components
        structured_count = len([c for c in components if c.order < 5])  # First 3-5 are structured
        adaptive_count = len(components) - structured_count
        
        prompt = f"""
You are an expert educational evaluator. Analyze if this student has met the learning objectives.

LESSON: {lesson.title}
LESSON PLAN: {lesson.plan}

LEARNING OBJECTIVES:
{json.dumps([obj.objective_text for obj in objectives], indent=2)}

COMPONENTS COMPLETED (Total: {len(components)}):
- Structured lesson components: {structured_count}
- Adaptive personalized components: {adaptive_count}

Component Details:
{json.dumps(component_summary, indent=2)}

STUDENT TELEMETRY (ALL Activity - Structured + Adaptive):
{json.dumps(telemetry_data[:50], indent=2)}

CRITICAL: Pay special attention to telemetry from ADAPTIVE components (higher order numbers).
These show how the student performed AFTER initial instruction on weak areas.

ANALYZE:
1. Performance on quizzes and practice exercises in BOTH structured AND adaptive phases
2. Did performance IMPROVE in adaptive phase compared to structured phase?
3. Time spent on components (rushed? struggling?)
4. Interaction patterns (skipping? re-reading? engaged?)
5. Coverage of all learning objectives across ALL components

EVALUATION CRITERIA:
- Has the student been exposed to ALL learning objectives?
- Did they demonstrate understanding on tests/quizzes (including adaptive ones)?
- Did adaptive components help improve weak areas?
- Are there STILL gaps in knowledge that need addressing?
- What is their preferred learning method? (visual/reading/practice/interactive)

Return JSON:
{{
  "objectives_met": true/false,
  "confidence": 0-100,
  "evaluation": {{
    "understood_concepts": ["concept1", "concept2"],
    "weak_areas": ["concept3"],
    "performance_summary": "Brief summary including improvement in adaptive phase",
    "learning_style_detected": "visual/reading/kinesthetic/mixed",
    "adaptive_phase_improvement": "none/slight/significant"
  }},
  "recommendation": {{
    "should_continue": true/false,
    "next_component_type": "quiz/info_card/practice_exercise/mindmap/null",
    "focus_area": "What to focus on if continuing",
    "reason": "Why should we continue or finish (mention adaptive phase results)"
  }}
}}

If objectives_met is TRUE and confidence > 70, set should_continue to FALSE.
If objectives_met is FALSE or confidence < 70, set should_continue to TRUE and suggest next component.
"""
        
        evaluation = self._call_llm(prompt, response_format='json')
        
        if not evaluation:
            # Fallback if LLM fails
            return False, {
                'objectives_met': False,
                'confidence': 0,
                'evaluation': {'performance_summary': 'Unable to evaluate'},
                'recommendation': {'should_continue': True, 'reason': 'Evaluation failed, continuing for safety'}
            }, True
        
        objectives_met = evaluation.get('objectives_met', False)
        should_continue = evaluation.get('recommendation', {}).get('should_continue', True)
        
        return objectives_met, evaluation, should_continue
    
    def grade_practice_exercise(self, component_data, user_answers, lesson_context=None):
        """Grade practice exercise answers using LLM"""
        print(f"🎓 Grading practice exercise with {len(user_answers)} answers")
        print(f"📝 User answers keys: {list(user_answers.keys())}")
        print(f"📋 Component data questions: {[q.get('account_id') for q in component_data.get('analysis_questions', [])]}")
        
        # Build context from accounts and questions
        accounts_text = "\n\n".join([
            f"Account {acc['id']} - {acc['title']}:\n{acc['text']}"
            for acc in component_data.get('accounts', [])
        ])
        
        questions_text = "\n\n".join([
            f"Question {i+1}: {q['question']}"
            for i, q in enumerate(component_data.get('analysis_questions', []))
        ])
        
        # Build answers text - answers are now indexed by question index (0, 1, 2, etc.)
        answers_text = "\n\n".join([
            f"Answer to Question {i+1}:\n{user_answers.get(str(i), user_answers.get(i, 'No answer provided'))}"
            for i, q in enumerate(component_data.get('analysis_questions', []))
        ])
        
        prompt = f"""
You are a fair and balanced educator grading student work. Be ACCURATE and CONSTRUCTIVE.

EXERCISE: {component_data.get('title', 'Practice Exercise')}
Instructions: {component_data.get('instructions', 'N/A')}

PASSAGES:
{accounts_text}

QUESTIONS:
{questions_text}

STUDENT ANSWERS:
{answers_text}

{"Context: " + lesson_context if lesson_context else ""}

GRADING PHILOSOPHY:
- Grade based on ACTUAL understanding demonstrated, not effort alone
- Be fair but not overly harsh
- Nonsense or completely wrong answers should score below 40
- Partial understanding deserves 40-60
- Good understanding with minor issues: 60-80
- Strong, accurate answers: 80-100

SCORING GUIDELINES (Be Accurate):
- 90-100: Excellent - demonstrates thorough, accurate understanding
- 80-89: Very Good - strong understanding with minor gaps
- 70-79: Good - solid grasp of concepts
- 60-69: Satisfactory - basic understanding, some gaps
- 50-59: Passing - minimal understanding, significant gaps
- 40-49: Poor - major misunderstandings
- Below 40: Very Poor - incorrect or nonsense

Grade EACH answer individually:
1. Score (0-100) - Based on correctness and understanding shown
2. Strengths (1 sentence) - What did they do well?
3. Weaknesses (1 sentence) - What needs improvement?
4. Feedback (1-2 sentences, constructive)

CRITICAL: Be honest about wrong answers. Nonsense = low score.

Return JSON - DO NOT calculate overall_score yourself, just grade each question:
{{
  "question_results": [
    {{
      "question_number": 1,
      "score": <0-100>,
      "strengths": "<what they did well, or 'N/A' if answer is wrong>",
      "weaknesses": "<what needs improvement>",
      "feedback": "<constructive, 1-2 sentences>"
    }}
  ],
  "next_steps": "<1 sentence recommendation>"
}}
"""
        
        try:
            result = self._call_llm(prompt, response_format='json')
            
            # Calculate overall score as average of question scores
            question_results = result.get('question_results', [])
            if question_results:
                total_score = sum(q.get('score', 0) for q in question_results)
                overall_score = total_score / len(question_results)
            else:
                overall_score = 0
            
            # Apply UK-style letter grading
            if overall_score >= 70:
                overall_grade = "A"
            elif overall_score >= 60:
                overall_grade = "B"
            elif overall_score >= 50:
                overall_grade = "C"
            elif overall_score >= 40:
                overall_grade = "D"
            else:
                overall_grade = "F"
            
            # Generate overall feedback based on performance
            if overall_score >= 70:
                overall_feedback = "Excellent work! You demonstrate a strong understanding of the concepts."
            elif overall_score >= 60:
                overall_feedback = "Good effort! You show solid understanding with room for improvement."
            elif overall_score >= 50:
                overall_feedback = "You're making progress. Review the feedback and keep practicing."
            elif overall_score >= 40:
                overall_feedback = "You need more practice with these concepts. Review the material carefully."
            else:
                overall_feedback = "Please review the material and try again. Don't hesitate to ask for help."
            
            result['overall_score'] = round(overall_score, 1)
            result['overall_grade'] = overall_grade
            result['overall_feedback'] = overall_feedback
            
            print(f"✅ Grading completed: Overall score {overall_score:.1f} ({overall_grade})")
            return result
        except Exception as e:
            print(f"❌ Error grading answers: {e}")
            # Return a basic fallback grading
            return {
                "overall_score": 50,
                "overall_grade": "C",
                "overall_feedback": "Unable to grade automatically. Please review your answers.",
                "question_results": [
                    {
                        "question_number": i + 1,
                        "score": 50,
                        "strengths": "You attempted the question",
                        "weaknesses": "Unable to evaluate",
                        "feedback": "Please try again or ask for help"
                    }
                    for i in range(len(component_data.get('analysis_questions', [])))
                ],
                "next_steps": "Review the lesson material and try to connect concepts more deeply"
            }
