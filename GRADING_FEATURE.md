# Practice Exercise Grading Feature

## Overview
Added AI-powered grading for practice exercise components using Google Gemini LLM.

## Implementation

### Backend Changes

1. **LLMService (`backend/services/llm_service.py`)**
   - Added `grade_practice_exercise()` method
   - Takes component data, user answers, and lesson context
   - Sends structured prompt to Gemini API for grading
   - Returns detailed grading results with scores and feedback

2. **TelemetryService (`backend/services/telemetry_service.py`)**
   - Added `track_event()` method to record telemetry events
   - Tracks grading results including scores and grades

3. **Lessons Routes (`backend/routes/lessons.py`)**
   - Added `POST /api/lessons/components/<id>/grade` endpoint
   - Validates user access and component type
   - Calls LLM grading service
   - Tracks results in telemetry
   - Returns grading results to frontend

### Frontend Changes

1. **PracticeExercise Component (`frontend/src/components/PracticeExercise.jsx`)**
   - Added `componentId` prop
   - Added grading state management (`grading`, `gradingResults`)
   - Modified submit handler to call grading API
   - Added comprehensive results display:
     - Overall score and grade (A-F) with color coding
     - Individual question feedback
     - Strengths and weaknesses for each answer
     - Constructive feedback
     - Next steps for improvement
   - Tracks grading results in telemetry

2. **Lesson Page (`frontend/src/pages/Lesson.jsx`)**
   - Updated to pass `componentId` to PracticeExercise components

## Grading Response Structure

```json
{
  "overall_score": 85,
  "overall_grade": "B",
  "overall_feedback": "Good work overall...",
  "question_results": [
    {
      "question_number": 1,
      "score": 90,
      "strengths": "Clear understanding...",
      "weaknesses": "Could expand on...",
      "feedback": "Consider adding..."
    }
  ],
  "next_steps": "Focus on practicing..."
}
```

## Telemetry Tracking

The grading feature tracks:
- `practice_exercise_graded` event with:
  - `component_id`
  - `overall_score`
  - `overall_grade`
  - `question_count`
  - `scores` array

## User Experience

1. Student answers all questions in practice exercise
2. Clicks "Submit Answers for Grading"
3. Loading spinner shows while LLM grades
4. Results displayed with:
   - Color-coded overall grade badge
   - Detailed feedback per question
   - Actionable next steps
5. All interactions tracked for adaptive learning

## Testing

To test:
1. Create a module with practice exercise components
2. Complete the exercise
3. Submit answers
4. Verify grading results appear
5. Check backend logs for telemetry tracking
