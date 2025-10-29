package models

import play.api.libs.json._
import java.time.{Instant, LocalDate}
import java.util.UUID

// Enums
object RiskLevel extends Enumeration {
  type RiskLevel = Value
  val LOW, MEDIUM, HIGH = Value
  
  implicit val format: Format[RiskLevel] = Json.formatEnum(this)
}

object UserRole extends Enumeration {
  type UserRole = Value
  val STUDENT, ADMIN, LECTURER = Value
  
  implicit val format: Format[UserRole] = Json.formatEnum(this)
}

object CourseStatus extends Enumeration {
  type CourseStatus = Value
  val ENROLLED, COMPLETED, FAILED, DROPPED = Value
  
  implicit val format: Format[CourseStatus] = Json.formatEnum(this)
}

// Case Classes
case class Student(
  id: UUID,
  studentId: String,
  name: String,
  email: String,
  passwordHash: String,
  gpa: Double,
  semester: Int,
  createdAt: Instant,
  updatedAt: Instant
)

object Student {
  implicit val format: OFormat[Student] = Json.format[Student]
}

case class Course(
  id: UUID,
  courseCode: String,
  courseName: String,
  credits: Int,
  difficulty: Double, // 1.0 to 5.0
  prerequisites: List[String],
  description: String,
  createdAt: Instant
)

object Course {
  implicit val format: OFormat[Course] = Json.format[Course]
}

case class Enrollment(
  id: UUID,
  studentId: UUID,
  courseId: UUID,
  semester: Int,
  grade: Option[String],
  status: CourseStatus.CourseStatus,
  attendanceRate: Double,
  enrolledAt: Instant,
  completedAt: Option[Instant]
)

object Enrollment {
  implicit val format: OFormat[Enrollment] = Json.format[Enrollment]
}

case class RiskPrediction(
  id: UUID,
  studentId: UUID,
  courseId: UUID,
  riskLevel: RiskLevel.RiskLevel,
  confidence: Double, // 0.0 to 1.0
  factors: Map[String, Double],
  recommendations: List[String],
  predictedGrade: Option[String],
  createdAt: Instant
)

object RiskPrediction {
  implicit val format: OFormat[RiskPrediction] = Json.format[RiskPrediction]
}

case class CourseProgress(
  course: Course,
  enrollment: Enrollment,
  riskPrediction: Option[RiskPrediction]
)

object CourseProgress {
  implicit val format: OFormat[CourseProgress] = Json.format[CourseProgress]
}

case class StudentStats(
  student: Student,
  currentCourses: List[CourseProgress],
  completedCourses: Int,
  totalCredits: Int,
  averageAttendance: Double,
  riskDistribution: Map[String, Int]
)

object StudentStats {
  implicit val format: OFormat[StudentStats] = Json.format[StudentStats]
}

case class LoginRequest(
  email: String,
  password: String
)

object LoginRequest {
  implicit val format: OFormat[LoginRequest] = Json.format[LoginRequest]
}

case class LoginResponse(
  token: String,
  student: Student
)

object LoginResponse {
  implicit val format: OFormat[LoginResponse] = Json.format[LoginResponse]
}

case class ApiError(
  message: String,
  code: Option[String] = None
)

object ApiError {
  implicit val format: OFormat[ApiError] = Json.format[ApiError]
}