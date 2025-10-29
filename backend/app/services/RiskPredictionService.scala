package services

import models._
import repositories._
import javax.inject._
import scala.concurrent.{ExecutionContext, Future}
import java.time.Instant
import java.util.UUID
import play.api.Logger

@Singleton
class RiskPredictionService @Inject()(
  studentRepository: StudentRepository,
  enrollmentRepository: EnrollmentRepository,
  courseRepository: CourseRepository
)(implicit ec: ExecutionContext) {
  
  private val logger = Logger(this.getClass)
  
  // Weight factors for risk calculation
  private val GPA_WEIGHT = 0.35
  private val ATTENDANCE_WEIGHT = 0.25
  private val PREREQUISITE_WEIGHT = 0.20
  private val DIFFICULTY_WEIGHT = 0.20
  
  def predictRisk(studentId: UUID, courseId: UUID): Future[RiskPrediction] = {
    for {
      studentOpt <- studentRepository.findById(studentId)
      courseOpt <- courseRepository.findById(courseId)
      enrollments <- enrollmentRepository.findByStudentId(studentId)
    } yield {
      (studentOpt, courseOpt) match {
        case (Some(student), Some(course)) =>
          calculateRiskPrediction(student, course, enrollments)
        case _ =>
          throw new Exception("Student or course not found")
      }
    }
  }
  
  def predictRisksForStudent(studentId: UUID): Future[List[RiskPrediction]] = {
    for {
      studentOpt <- studentRepository.findById(studentId)
      enrollments <- enrollmentRepository.findByStudentId(studentId)
      currentEnrollments = enrollments.filter(_.status == CourseStatus.ENROLLED)
      courses <- Future.sequence(currentEnrollments.map(e => courseRepository.findById(e.courseId)))
      student = studentOpt.getOrElse(throw new Exception("Student not found"))
    } yield {
      courses.flatten.map { course =>
        calculateRiskPrediction(student, course, enrollments)
      }
    }
  }
  
  private def calculateRiskPrediction(
    student: Student,
    course: Course,
    enrollmentHistory: List[Enrollment]
  ): RiskPrediction = {
    
    // Calculate individual risk factors
    val gpaFactor = calculateGPAFactor(student.gpa)
    val attendanceFactor = calculateAttendanceFactor(enrollmentHistory)
    val prerequisiteFactor = calculatePrerequisiteFactor(course, enrollmentHistory)
    val difficultyFactor = calculateDifficultyFactor(course.difficulty, student.gpa)
    
    // Calculate weighted risk score (0.0 to 1.0, where 1.0 is highest risk)
    val riskScore = (
      gpaFactor * GPA_WEIGHT +
      attendanceFactor * ATTENDANCE_WEIGHT +
      prerequisiteFactor * PREREQUISITE_WEIGHT +
      difficultyFactor * DIFFICULTY_WEIGHT
    )
    
    // Determine risk level
    val riskLevel = riskScore match {
      case s if s < 0.35 => RiskLevel.LOW
      case s if s < 0.65 => RiskLevel.MEDIUM
      case _ => RiskLevel.HIGH
    }
    
    // Calculate confidence based on data availability
    val confidence = calculateConfidence(enrollmentHistory.length, student.semester)
    
    // Generate recommendations
    val recommendations = generateRecommendations(
      riskLevel, 
      gpaFactor, 
      attendanceFactor, 
      prerequisiteFactor, 
      difficultyFactor,
      course
    )
    
    // Predict grade
    val predictedGrade = predictGrade(riskScore, student.gpa)
    
    val factors = Map(
      "gpa" -> gpaFactor,
      "attendance" -> attendanceFactor,
      "prerequisites" -> prerequisiteFactor,
      "difficulty" -> difficultyFactor
    )
    
    RiskPrediction(
      id = UUID.randomUUID(),
      studentId = student.id,
      courseId = course.id,
      riskLevel = riskLevel,
      confidence = confidence,
      factors = factors,
      recommendations = recommendations,
      predictedGrade = Some(predictedGrade),
      createdAt = Instant.now()
    )
  }
  
  private def calculateGPAFactor(gpa: Double): Double = {
    // Higher GPA = lower risk
    // GPA range: 0.0 - 4.0, normalize to risk (inverse)
    Math.max(0.0, Math.min(1.0, (4.0 - gpa) / 4.0))
  }
  
  private def calculateAttendanceFactor(enrollments: List[Enrollment]): Double = {
    if (enrollments.isEmpty) return 0.5 // Neutral if no history
    
    val avgAttendance = enrollments.map(_.attendanceRate).sum / enrollments.length
    // Lower attendance = higher risk
    1.0 - avgAttendance
  }
  
  private def calculatePrerequisiteFactor(course: Course, enrollments: List[Enrollment]): Double = {
    if (course.prerequisites.isEmpty) return 0.0 // No prerequisites = no risk
    
    val completedCourses = enrollments
      .filter(_.status == CourseStatus.COMPLETED)
      .map(e => e.courseId.toString) // Simplified - would map to course codes
    
    val prerequisitesMet = course.prerequisites.count(prereq => 
      completedCourses.exists(_.contains(prereq))
    )
    
    val prerequisitesTotal = course.prerequisites.length
    val completionRate = if (prerequisitesTotal > 0) {
      prerequisitesMet.toDouble / prerequisitesTotal
    } else 0.0
    
    // Missing prerequisites = higher risk
    1.0 - completionRate
  }
  
  private def calculateDifficultyFactor(courseDifficulty: Double, studentGpa: Double): Double = {
    // Difficulty range: 1.0 - 5.0
    // Compare course difficulty with student's capability (GPA)
    val normalizedDifficulty = (courseDifficulty - 1.0) / 4.0 // Normalize to 0.0-1.0
    val studentCapability = studentGpa / 4.0 // Normalize GPA to 0.0-1.0
    
    // Risk increases when difficulty exceeds capability
    Math.max(0.0, normalizedDifficulty - studentCapability)
  }
  
  private def calculateConfidence(enrollmentCount: Int, semester: Int): Double = {
    // More historical data = higher confidence
    val historyFactor = Math.min(1.0, enrollmentCount / 10.0)
    val semesterFactor = Math.min(1.0, semester / 8.0)
    (historyFactor + semesterFactor) / 2.0
  }
  
  private def generateRecommendations(
    riskLevel: RiskLevel.RiskLevel,
    gpaFactor: Double,
    attendanceFactor: Double,
    prerequisiteFactor: Double,
    difficultyFactor: Double,
    course: Course
  ): List[String] = {
    val recommendations = scala.collection.mutable.ListBuffer[String]()
    
    riskLevel match {
      case RiskLevel.HIGH =>
        recommendations += "Consider postponing this course until prerequisites are completed"
        recommendations += "Speak with your academic advisor about course load"
      case RiskLevel.MEDIUM =>
        recommendations += "Allocate extra study time for this course"
        recommendations += "Form a study group with classmates"
      case RiskLevel.LOW =>
        recommendations += "Maintain current study habits"
        recommendations += "Consider taking on additional challenging courses"
    }
    
    // Factor-specific recommendations
    if (gpaFactor > 0.6) {
      recommendations += "Focus on improving overall GPA through easier electives"
      recommendations += "Seek tutoring services for challenging subjects"
    }
    
    if (attendanceFactor > 0.6) {
      recommendations += "Prioritize class attendance - aim for 90%+ attendance rate"
      recommendations += "Set reminders for all class sessions"
    }
    
    if (prerequisiteFactor > 0.5) {
      recommendations += s"Review prerequisite materials: ${course.prerequisites.mkString(", ")}"
      recommendations += "Consider auditing prerequisite courses if needed"
    }
    
    if (difficultyFactor > 0.6) {
      recommendations += "Start studying early and create a structured study schedule"
      recommendations += "Attend office hours regularly for additional support"
      recommendations += "Allocate 10-15 hours per week for this course"
    }
    
    recommendations.toList
  }
  
  private def predictGrade(riskScore: Double, gpa: Double): String = {
    // Combine risk score with GPA to predict grade
    val scoreFactor = 1.0 - riskScore
    val predictedScore = (scoreFactor * 0.6 + (gpa / 4.0) * 0.4) * 100
    
    predictedScore match {
      case s if s >= 90 => "A"
      case s if s >= 85 => "A-"
      case s if s >= 80 => "B+"
      case s if s >= 75 => "B"
      case s if s >= 70 => "B-"
      case s if s >= 65 => "C+"
      case s if s >= 60 => "C"
      case s if s >= 55 => "C-"
      case s if s >= 50 => "D"
      case _ => "F"
    }
  }
}